import os
from typing import Any

from assistant.medical_assistant import MedicalAssistant
from assistant.storage import DataStorage


class MedicalAssistantApp:
    """Shared application service for both CLI and web interfaces."""

    def __init__(self, data_file: str) -> None:
        self.data_file = data_file
        self.assistant = MedicalAssistant("MedAssist", data_file)
        self._bootstrap_demo_data()

    def _bootstrap_demo_data(self) -> None:
        if self.assistant.users:
            return
        self.assistant.register_user("Иван Петров", "+7(123)456-78-90", 35)
        self.assistant.register_user("Мария Иванова", "+7(098)765-43-21", 28)

    def save(self) -> None:
        DataStorage.save_data(self.data_file, self.assistant.users)

    def register_user(self, name: str, phone: str, age: int) -> int:
        return self.assistant.register_user(name, phone, age)

    def get_users(self) -> list[dict[str, Any]]:
        users = []
        for user in self.assistant.users:
            history = user.medical_history
            users.append(
                {
                    "id": user.id,
                    "name": user.name,
                    "phone": user.phone,
                    "age": user.age,
                    "symptoms_count": len(history.symptoms),
                    "medications_count": len(history.medications),
                    "recommendations_count": len(history.recommendations),
                }
            )
        return users

    def get_user_history(self, user_id: int) -> dict[str, Any]:
        user = self.assistant._get_user_safe(user_id)
        history = user.medical_history
        return {
            "user": user,
            "symptoms": list(history.symptoms),
            "medications": list(history.medications),
            "recommendations": list(history.recommendations),
        }

    def record_symptom(self, user_id: int, symptom: str, severity: int) -> str:
        return self.assistant.record_symptom(user_id, symptom, severity)

    def give_advice(self, user_id: int, symptom: str) -> str:
        return self.assistant.give_advice(user_id, symptom)

    def add_medication_reminder(
        self, user_id: int, med_name: str, dosage: str, schedule: str
    ) -> str:
        return self.assistant.add_medication_reminder(user_id, med_name, dosage, schedule)

    def get_medication_list(self, user_id: int) -> list[Any]:
        return list(self.assistant.get_medication_list(user_id))

    def get_areas(self) -> list[str]:
        return self.assistant.get_all_areas()

    def get_clinics_by_area(self, area: str) -> list[dict[str, Any]]:
        clinics = []
        for clinic in self.assistant.find_clinics_by_area(area):
            doctor_ids = clinic.get("doctor_ids", [])
            doctors = [
                self.assistant._doctors_by_id[doctor_id]
                for doctor_id in doctor_ids
                if doctor_id in self.assistant._doctors_by_id
            ]
            clinics.append({"clinic": clinic, "doctors": doctors})
        return clinics

    def get_doctors_by_area(self, area: str) -> list[Any]:
        return self.assistant.get_doctors_by_area(area)

    def consult_doctor(self, doctor_id: int, user_id: int, question: str) -> str:
        return self.assistant.consult_doctor(doctor_id, user_id, question)

    def get_system_status(self) -> dict[str, Any]:
        return {
            "assistant_name": self.assistant.name,
            "users": list(self.assistant.users),
            "doctors": list(self.assistant.doctors),
            "areas": self.get_areas(),
        }


def default_data_file() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.json")
