from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import Any

from entities.doctor import Doctor
from entities.medical import MedicalHistory, Medication, Recommendation, Symptom
from entities.patient import Patient


class StorageProtocol(ABC):
    @abstractmethod
    def load(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def save(
        self,
        users: list[Patient],
        doctors: list[Doctor],
        clinics: list[dict[str, Any]],
        system_state: dict[str, str],
    ) -> None:
        raise NotImplementedError


class JsonStorage(StorageProtocol):
    def __init__(self, filename: str) -> None:
        self._filename = filename

    def load(self) -> dict[str, Any]:
        if not os.path.exists(self._filename):
            return self._empty_dataset()

        with open(self._filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        clinics = data.get("clinics", [])
        clinic_name_by_id = {
            clinic["id"]: clinic["name"]
            for clinic in clinics
            if "id" in clinic and "name" in clinic
        }
        doctors = self._load_doctors(data, clinic_name_by_id)
        users = self._load_users(data)
        symptom_advice = {
            item["name"].strip().lower(): item["advice"]
            for item in data.get("symptoms", [])
            if item.get("name") and item.get("advice")
        }

        return {
            "users": users,
            "doctors": doctors,
            "clinics": clinics,
            "symptom_advice": symptom_advice,
            "system_state": data.get("system_state", {}),
        }

    def save(
        self,
        users: list[Patient],
        doctors: list[Doctor],
        clinics: list[dict[str, Any]],
        system_state: dict[str, str],
    ) -> None:
        full_data = self._read_raw_data()
        full_data["users"] = [self._serialize_user(user) for user in users]
        full_data["doctors"] = [
            {
                "id": doctor.id,
                "name": doctor.name,
                "phone": doctor.phone,
                "specialization": doctor.specialization,
                "clinic_id": self._get_clinic_id(clinics, doctor.clinic),
            }
            for doctor in doctors
        ]
        full_data["clinics"] = clinics
        full_data["system_state"] = system_state

        with open(self._filename, "w", encoding="utf-8") as file:
            json.dump(full_data, file, ensure_ascii=False, indent=2)

    def _read_raw_data(self) -> dict[str, Any]:
        if not os.path.exists(self._filename):
            return {
                "users": [],
                "doctors": [],
                "clinics": [],
                "symptoms": [],
                "system_state": {},
            }
        with open(self._filename, "r", encoding="utf-8") as file:
            return json.load(file)

    def _load_doctors(
        self,
        data: dict[str, Any],
        clinic_name_by_id: dict[int, str],
    ) -> list[Doctor]:
        doctors: list[Doctor] = []
        for item in data.get("doctors", []):
            clinic_id = item.get("clinic_id")
            clinic_name = clinic_name_by_id.get(clinic_id, f"Клиника #{clinic_id}")
            doctors.append(
                Doctor(
                    item["id"],
                    item["name"],
                    item["phone"],
                    item["specialization"],
                    clinic_name,
                ),
            )
        return doctors

    def _load_users(self, data: dict[str, Any]) -> list[Patient]:
        users: list[Patient] = []
        for item in data.get("users", []):
            patient = Patient(
                item["id"],
                item["name"],
                item["phone"],
                item["age"],
            )
            medical_history = MedicalHistory()

            for symptom_data in item.get("symptoms", []):
                symptom = Symptom(
                    symptom_data["name"],
                    symptom_data["severity"],
                    symptom_data["date"],
                )
                medical_history.add_symptom(symptom)

            for medication_data in item.get("medications", []):
                medical_history.add_medication(
                    Medication(
                        medication_data["name"],
                        medication_data["dosage"],
                        medication_data["schedule"],
                    ),
                )

            for recommendation_data in item.get("recommendations", []):
                medical_history.add_recommendation(
                    Recommendation(
                        recommendation_data["text"],
                        recommendation_data["source"],
                        recommendation_data["date"],
                    ),
                )

            patient.medical_history = medical_history
            users.append(patient)
        return users

    def _serialize_user(self, user: Patient) -> dict[str, Any]:
        return {
            "id": user.id,
            "name": user.name,
            "phone": user.phone,
            "age": user.age,
            "symptoms": [
                {
                    "name": symptom.name,
                    "severity": symptom.severity,
                    "date": symptom.date,
                }
                for symptom in user.medical_history.symptoms
            ],
            "medications": [
                {
                    "name": medication.name,
                    "dosage": medication.dosage,
                    "schedule": medication.schedule,
                }
                for medication in user.medical_history.medications
            ],
            "recommendations": [
                {
                    "text": recommendation.text,
                    "source": recommendation.source,
                    "date": recommendation.date,
                }
                for recommendation in user.medical_history.recommendations
            ],
        }

    def _get_clinic_id(self, clinics: list[dict[str, Any]], clinic_name: str) -> int | None:
        for clinic in clinics:
            if clinic.get("name") == clinic_name:
                return clinic.get("id")
        return None

    def _empty_dataset(self) -> dict[str, Any]:
        return {
            "users": [],
            "doctors": [],
            "clinics": [],
            "symptom_advice": {},
            "system_state": {},
        }
