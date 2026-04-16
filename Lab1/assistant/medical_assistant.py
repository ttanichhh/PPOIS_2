from __future__ import annotations

from typing import Any

from assistant.state import AssistantStateMachine, AssistantStatus
from assistant.storage import JsonStorage, StorageProtocol
from entities.doctor import Doctor
from entities.medical import MedicalHistory, Medication, Recommendation, Symptom
from entities.patient import Patient
from exceptions import NotFoundError


class MedicalAssistant:
    """Основной сервис приложения."""

    def __init__(
        self,
        name: str,
        data_file: str,
        storage: StorageProtocol | None = None,
    ) -> None:
        self._name = name
        self._storage = storage or JsonStorage(data_file)

        data = self._storage.load()
        self._users = data["users"]
        self._doctors = data["doctors"]
        self._clinics = data["clinics"]
        self._symptom_advice = data["symptom_advice"]
        self._doctors_by_id = {doctor.id: doctor for doctor in self._doctors}
        self._state_machine = AssistantStateMachine.from_dict(data["system_state"])
        self.start_session()

    @property
    def name(self) -> str:
        return self._name

    @property
    def users(self) -> list[Patient]:
        return self._users

    @property
    def doctors(self) -> list[Doctor]:
        return self._doctors

    @property
    def status(self) -> AssistantStatus:
        return self._state_machine.status

    @property
    def last_action(self) -> str:
        return self._state_machine.last_action

    def start_session(self) -> None:
        if self.status == AssistantStatus.TERMINATED:
            self._state_machine.force_ready("Возобновление работы после прошлого завершения")
        elif self.status == AssistantStatus.ERROR:
            self._state_machine.force_ready("Восстановление после ошибки")
        elif self.status == AssistantStatus.STARTUP:
            self._state_machine.transition(
                AssistantStatus.READY,
                "Система готова к работе",
            )
        self.save()

    def register_user(self, name: str, phone: str, age: int) -> int:
        self._state_machine.transition(
            AssistantStatus.MANAGING_USERS,
            "Регистрация пользователя",
        )
        user_id = self._generate_user_id()
        patient = Patient(user_id, name, phone, age)
        patient.medical_history = MedicalHistory()
        self._users.append(patient)
        self._finish_action("Пользователь зарегистрирован")
        return user_id

    def record_symptom(self, user_id: int, symptom_name: str, severity: int = 5) -> str:
        self._state_machine.transition(
            AssistantStatus.RECORDING_SYMPTOM,
            "Запись симптома",
        )
        user = self._get_user_safe(user_id)
        symptom = Symptom(symptom_name, severity)
        user.medical_history.add_symptom(symptom)
        self._finish_action(f"Симптом '{symptom_name}' записан")
        return f"Симптом '{symptom_name}' записан для пользователя {user.name}"

    def give_advice(self, user_id: int, symptom_name: str) -> str:
        self._state_machine.transition(
            AssistantStatus.PROVIDING_ADVICE,
            "Формирование рекомендации",
        )
        user = self._get_user_safe(user_id)
        advice_text = self._symptom_advice.get(
            symptom_name.strip().lower(),
            f"Обратитесь к врачу для симптома '{symptom_name}'",
        )
        recommendation = Recommendation(advice_text)
        user.medical_history.add_recommendation(recommendation)
        self._finish_action(f"Рекомендация по симптому '{symptom_name}' сформирована")
        return f"Совет: {advice_text}"

    def add_medication_reminder(
        self,
        user_id: int,
        med_name: str,
        dosage: str,
        schedule: str,
    ) -> str:
        self._state_machine.transition(
            AssistantStatus.MANAGING_MEDICATIONS,
            "Добавление напоминания о лекарстве",
        )
        user = self._get_user_safe(user_id)
        medication = Medication(med_name, dosage, schedule)
        user.medical_history.add_medication(medication)
        self._finish_action(f"Напоминание по лекарству '{med_name}' добавлено")
        return (
            f"Напоминание о приеме '{med_name}' ({dosage}) добавлено. "
            f"Расписание: {schedule}"
        )

    def get_medication_list(self, user_id: int) -> list[Medication]:
        user = self._get_user_safe(user_id)
        return user.medical_history.medications

    def find_clinics_by_area(self, area: str) -> list[dict[str, Any]]:
        self._state_machine.transition(
            AssistantStatus.SEARCHING_CLINICS,
            "Поиск клиник",
        )
        key = area.strip().lower()
        clinics = [
            clinic for clinic in self._clinics
            if clinic.get("area", "").strip().lower() == key
        ]
        self._finish_action(f"Поиск клиник по району '{area}' завершен")
        return clinics

    def consult_doctor(self, doctor_id: int, user_id: int, question: str) -> str:
        self._state_machine.transition(
            AssistantStatus.CONSULTING_DOCTOR,
            "Консультация с врачом",
        )
        doctor = self._get_doctor_safe(doctor_id)
        user = self._get_user_safe(user_id)
        clinic = next(
            (clinic for clinic in self._clinics if clinic.get("name") == doctor.clinic),
            None,
        )
        clinic_name = clinic.get("name") if clinic else doctor.clinic
        clinic_address = clinic.get("address") if clinic else ""

        response = (
            f"Доктор {doctor.name} ({doctor.specialization}):\n"
            f"На ваш вопрос '{question}' рекомендую записаться на прием "
            f"в клинику '{clinic_name}'. {clinic_address}"
        )
        user.medical_history.add_recommendation(
            Recommendation(response, f"Доктор {doctor.name}"),
        )
        self._finish_action(f"Консультация с врачом {doctor.name} завершена")
        return response

    def get_all_areas(self) -> list[str]:
        areas = {
            clinic.get("area", "").strip().lower()
            for clinic in self._clinics
            if clinic.get("area", "").strip()
        }
        return sorted(areas)

    def get_doctors_by_area(self, area: str) -> list[Doctor]:
        clinics = self.find_clinics_by_area(area)
        doctor_ids: set[int] = set()
        for clinic in clinics:
            doctor_ids.update(clinic.get("doctor_ids", []))
        return [self._doctors_by_id[doctor_id] for doctor_id in sorted(doctor_ids)]

    def save(self) -> None:
        self._storage.save(
            users=self._users,
            doctors=self._doctors,
            clinics=self._clinics,
            system_state=self._state_machine.to_dict(),
        )

    def shutdown(self) -> None:
        self._state_machine.transition(
            AssistantStatus.SAVING,
            "Подготовка к завершению программы",
        )
        self.save()
        self._state_machine.transition(
            AssistantStatus.TERMINATED,
            "Программа завершена штатно",
        )
        self.save()

    def handle_error(self, error: Exception) -> None:
        self._state_machine.move_to_error(str(error))
        self.save()
        self._state_machine.force_ready("Возврат в рабочее состояние после ошибки")
        self.save()

    def get_status_report(self) -> str:
        return (
            f"Состояние: {self.status.value}\n"
            f"Последнее действие: {self.last_action}\n"
            f"Пользователей: {len(self.users)}\n"
            f"Врачей: {len(self.doctors)}\n"
            f"Районов с клиниками: {len(self.get_all_areas())}"
        )

    def _generate_user_id(self) -> int:
        if not self._users:
            return 0
        return max(user.id for user in self._users) + 1

    def _finish_action(self, action: str) -> None:
        self._state_machine.transition(AssistantStatus.READY, action)
        self.save()

    def _get_user_safe(self, user_id: int) -> Patient:
        user = next((item for item in self._users if item.id == user_id), None)
        if user is None:
            raise NotFoundError(f"Пользователь с ID {user_id} не найден")
        return user

    def _get_doctor_safe(self, doctor_id: int) -> Doctor:
        doctor = self._doctors_by_id.get(doctor_id)
        if doctor is None:
            raise NotFoundError(f"Доктор с ID {doctor_id} не найден")
        return doctor
