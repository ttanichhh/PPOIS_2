from typing import List, Dict
from Lab1.entities.doctor import Doctor
from Lab1.entities.patient import Patient
from Lab1.entities.medical import Symptom, Medication, Recommendation, MedicalHistory
from Lab1.exceptions import NotFoundError
from Lab1.assistant.storage import DataStorage


class MedicalAssistant:
    def __init__(self, name: str, data_file: str) -> None:
        self._name: str = name
        self._data_file = data_file

        # Загружаем данные
        users, doctors, clinics, symptom_data = DataStorage.load_data(data_file)

        self._users: List[Patient] = users
        self._doctors: List[Doctor] = doctors
        self._doctors_by_id: Dict[int, Doctor] = {d.id: d for d in doctors}
        self._clinics: List[Dict] = clinics

        # Группируем клиники по районам
        self._clinics_by_area: Dict[str, List[Dict]] = {}
        for clinic in clinics:
            area = clinic.get("area")
            if area not in self._clinics_by_area:
                self._clinics_by_area[area] = []
            self._clinics_by_area[area].append(clinic)

        # Данные о симптомах
        self._symptom_advice = symptom_data.get("advice_map", {})

    @property
    def name(self) -> str:
        return self._name

    @property
    def users(self) -> List[Patient]:
        return self._users

    @property
    def doctors(self) -> List[Doctor]:
        return self._doctors

    # Регистрация пользователей
    def register_user(self, name: str, phone: str, age: int) -> int:
        user_id = len(self._users)
        user = Patient(user_id, name, phone, age)
        user.medical_history = MedicalHistory()
        self._users.append(user)
        return user_id

    # Операция записи симптомов
    def record_symptom(self, user_id: int, symptom_name: str, severity: int = 5) -> str:
        user = self._get_user_safe(user_id)

        symptom = Symptom(symptom_name, severity)
        user.medical_history.add_symptom(symptom)

        return f"Симптом '{symptom_name}' записан для пользователя {user.name}"

    # Операция предоставления медицинских советов
    def give_advice(self, user_id: int, symptom_name: str) -> str:
        user = self._get_user_safe(user_id)

        # Используем советы из symptom_data
        advice_text = self._symptom_advice.get(symptom_name.lower(),
                                     f"Обратитесь к врачу для симптома '{symptom_name}'")

        recommendation = Recommendation(advice_text)
        user.medical_history.add_recommendation(recommendation)

        return f"Совет: {advice_text}"

    # Операция напоминания о приеме лекарств
    def add_medication_reminder(self, user_id: int, med_name: str,
                                dosage: str, schedule: str) -> str:
        user = self._get_user_safe(user_id)

        medication = Medication(med_name, dosage, schedule)
        user.medical_history.add_medication(medication)

        return (f"Напоминание о приеме '{med_name}' ({dosage}) добавлено. "
                f"Расписание: {schedule}")

    def get_medication_list(self, user_id: int) -> List[Medication]:
        user = self._get_user_safe(user_id)
        return user.medical_history.medications

    # Операция поиска клиник по району
    def find_clinics_by_area(self, area: str) -> List[Dict]:
        """Поиск клиник по району"""
        return self._clinics_by_area.get(area.lower(), [])

    # Операция консультации с врачом
    def consult_doctor(self, doctor_id: int, user_id: int, question: str) -> str:
        doctor = self._get_doctor_safe(doctor_id)
        user = self._get_user_safe(user_id)

        # Ищем клинику по НАЗВАНИЮ
        clinic = None
        for c in self._clinics:
            if c.get("name") == doctor.clinic:
                clinic = c
                break

        clinic_name = clinic.get("name") if clinic else doctor.clinic
        clinic_address = clinic.get("address") if clinic else ""

        response = (f"Доктор {doctor.name} ({doctor.specialization}):\n"
                    f"На ваш вопрос '{question}' рекомендую записаться на прием "
                    f"в клинику '{clinic_name}'. {clinic_address}")

        recommendation = Recommendation(response, f"Доктор {doctor.name}")
        user.medical_history.add_recommendation(recommendation)

        return response

    # Вспомогательные методы
    def _get_user_safe(self, user_id: int) -> Patient:
        if 0 <= user_id < len(self._users):
            return self._users[user_id]
        raise NotFoundError(f"Пользователь с ID {user_id} не найден")

    def _get_doctor_safe(self, doctor_id: int) -> Doctor:
        # Ищем врача в словаре по ID
        doctor = self._doctors_by_id.get(doctor_id)
        if doctor:
            return doctor
        raise NotFoundError(f"Доктор с ID {doctor_id} не найден")

    def get_all_areas(self) -> List[str]:
        return list(self._clinics_by_area.keys())