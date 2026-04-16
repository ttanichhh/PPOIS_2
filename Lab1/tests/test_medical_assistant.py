import json
import os
import tempfile
import unittest

from assistant.medical_assistant import MedicalAssistant
from assistant.state import AssistantStatus
from entities.medical import Medication, Symptom
from exceptions import EmptyValueError, InvalidDataFormatError, NotFoundError


def build_dataset() -> dict:
    return {
        "clinics": [
            {
                "id": 0,
                "name": "Городская больница №1",
                "address": "ул. Ленина, 10",
                "area": "центр",
                "doctor_ids": [0, 1],
            },
            {
                "id": 1,
                "name": "Поликлиника №3",
                "address": "ул. Северная, 5",
                "area": "север",
                "doctor_ids": [2],
            },
        ],
        "doctors": [
            {
                "id": 0,
                "name": "Анна Сергеевна Петрова",
                "phone": "+7(111)222-33-01",
                "specialization": "Терапевт",
                "clinic_id": 0,
            },
            {
                "id": 1,
                "name": "Петр Иванович Васильев",
                "phone": "+7(222)333-44-01",
                "specialization": "Кардиолог",
                "clinic_id": 0,
            },
            {
                "id": 2,
                "name": "Иван Петрович Сидоров",
                "phone": "+7(111)222-33-02",
                "specialization": "Терапевт",
                "clinic_id": 1,
            },
        ],
        "symptoms": [
            {
                "name": "головная боль",
                "specialization": "Невролог",
                "advice": "Отдохните в темной комнате",
            },
            {
                "name": "температура",
                "specialization": "Терапевт",
                "advice": "Пейте много жидкости",
            },
        ],
        "users": [],
        "system_state": {
            "status": "STARTUP",
            "last_action": "Тестовая инициализация",
        },
    }


class MedicalAssistantTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".json",
            delete=False,
            encoding="utf-8",
        )
        json.dump(build_dataset(), self.temp_file, ensure_ascii=False, indent=2)
        self.temp_file.close()
        self.assistant = MedicalAssistant("TestAssist", self.temp_file.name)

    def tearDown(self) -> None:
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_initial_status_after_startup_is_ready(self) -> None:
        self.assertEqual(self.assistant.status, AssistantStatus.READY)

    def test_register_user_creates_medical_history(self) -> None:
        user_id = self.assistant.register_user("Новый пользователь", "+375291112233", 25)

        self.assertEqual(user_id, 0)
        self.assertEqual(len(self.assistant.users), 1)
        self.assertEqual(self.assistant.users[0].medical_history.symptoms, [])
        self.assertEqual(self.assistant.status, AssistantStatus.READY)

    def test_record_symptom_updates_history_and_persists_data(self) -> None:
        user_id = self.assistant.register_user("Иван", "+375291112244", 30)
        message = self.assistant.record_symptom(user_id, "головная боль", 8)

        self.assertIn("записан", message)
        self.assertEqual(len(self.assistant.users[0].medical_history.symptoms), 1)

        reloaded = MedicalAssistant("Reloaded", self.temp_file.name)
        self.assertEqual(len(reloaded.users[0].medical_history.symptoms), 1)
        self.assertEqual(reloaded.users[0].medical_history.symptoms[0].severity, 8)

    def test_give_advice_adds_recommendation(self) -> None:
        user_id = self.assistant.register_user("Мария", "+375291112255", 22)
        advice = self.assistant.give_advice(user_id, "температура")

        self.assertIn("Пейте много жидкости", advice)
        self.assertEqual(len(self.assistant.users[0].medical_history.recommendations), 1)

    def test_find_clinics_by_area(self) -> None:
        clinics = self.assistant.find_clinics_by_area("центр")
        self.assertEqual(len(clinics), 1)
        self.assertEqual(clinics[0]["name"], "Городская больница №1")

    def test_consult_doctor_adds_doctor_recommendation(self) -> None:
        user_id = self.assistant.register_user("Олег", "+375291112266", 40)
        response = self.assistant.consult_doctor(0, user_id, "У меня температура")

        self.assertIn("Доктор Анна Сергеевна Петрова", response)
        self.assertEqual(len(self.assistant.users[0].medical_history.recommendations), 1)

    def test_shutdown_persists_terminated_state(self) -> None:
        self.assistant.shutdown()
        reloaded = MedicalAssistant("Reloaded", self.temp_file.name)
        self.assertEqual(reloaded.status, AssistantStatus.READY)
        self.assertIn("Возобновление работы", reloaded.last_action)

    def test_missing_user_raises_not_found_error(self) -> None:
        with self.assertRaises(NotFoundError):
            self.assistant.record_symptom(999, "кашель", 5)


class EntityValidationTestCase(unittest.TestCase):
    def test_symptom_severity_validation(self) -> None:
        with self.assertRaises(InvalidDataFormatError):
            Symptom("кашель", 11)

    def test_medication_empty_name_validation(self) -> None:
        with self.assertRaises(EmptyValueError):
            Medication("", "100 мг", "утром")


if __name__ == "__main__":
    unittest.main()
