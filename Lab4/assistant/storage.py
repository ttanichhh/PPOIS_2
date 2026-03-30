import json
import os
from typing import List, Dict, Tuple
from entities.doctor import Doctor
from entities.patient import Patient
from entities.medical import Symptom, Medication, Recommendation, MedicalHistory


class DataStorage:
    @staticmethod
    def save_data(filename: str, users: List[Patient]) -> None:
        # Сохраняем только пользователей (врачи/клиники/симптомы неизменны)
        data = {
            "users": [
                {
                    "id": u.id,
                    "name": u.name,
                    "phone": u.phone,
                    "age": u.age,
                    "symptoms": [
                        {
                            "name": s.name,
                            "severity": s.severity,
                            "date": s.date
                        }
                        for s in u.medical_history.symptoms
                    ],
                    "medications": [
                        {
                            "name": m.name,
                            "dosage": m.dosage,
                            "schedule": m.schedule
                        }
                        for m in u.medical_history.medications
                    ],
                    "recommendations": [
                        {
                            "text": r.text,
                            "source": r.source,
                            "date": r.date
                        }
                        for r in u.medical_history.recommendations
                    ]
                }
                for u in users
            ]
        }

        # Загружаем существующий файл, чтобы сохранить клиники, врачей и симптомы
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                full_data = json.load(f)
            full_data["users"] = data["users"]
        else:
            # Если файла нет, создаем структуру с базовыми данными
            full_data = {
                "clinics": [],
                "doctors": [],
                "symptoms": [],
                "users": data["users"]
            }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_data(filename: str) -> Tuple[List[Patient], List[Doctor], List[Dict], Dict]:
        if not os.path.exists(filename):
            return [], [], [], {"symptom_map": {}, "advice_map": {}, "symptom_list": []}

        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Загружаем клиники как словари
        clinics = data.get("clinics", [])
        clinic_name_by_id = {
            c["id"]: c["name"]
            for c in clinics
            if "id" in c and "name" in c
        }

        # Загружаем врачей
        doctors = []
        for d in data.get("doctors", []):
            clinic_id = d.get("clinic_id")
            clinic_name = clinic_name_by_id.get(clinic_id, f"Клиника #{clinic_id}")

            doctor = Doctor(
                d["id"],
                d["name"],
                d["phone"],
                d["specialization"],
                clinic_name  # <-- теперь doctor.clinic = ИМЯ клиники
            )
            doctors.append(doctor)

        # Загружаем симптомы
        symptoms_data = data.get("symptoms", [])
        symptom_map = {}
        advice_map = {}
        for s in symptoms_data:
            symptom_map[s["name"]] = s["specialization"]
            advice_map[s["name"]] = s["advice"]

        # Загружаем пользователей
        users = []
        for u in data.get("users", []):
            user = Patient(
                u["id"],
                u["name"],
                u["phone"],
                u["age"]
            )

            medical_history = MedicalHistory()

            for s in u.get("symptoms", []):
                symptom = Symptom(s["name"], s["severity"])
                symptom._date = s["date"]
                medical_history.add_symptom(symptom)

            for m in u.get("medications", []):
                medication = Medication(m["name"], m["dosage"], m["schedule"])
                medical_history.add_medication(medication)

            for r in u.get("recommendations", []):
                recommendation = Recommendation(r["text"], r["source"])
                recommendation._date = r["date"]
                medical_history.add_recommendation(recommendation)

            user.medical_history = medical_history
            users.append(user)

        return users, doctors, clinics, {  # 4 элемента
            "symptom_map": symptom_map,
            "advice_map": advice_map,
            "symptom_list": list(symptom_map.keys())
        }
