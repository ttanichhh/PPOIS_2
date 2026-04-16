from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AssistantStatus(str, Enum):
    STARTUP = "Запуск"
    READY = "Ожидание команды"
    MANAGING_USERS = "Управление пользователями"
    RECORDING_SYMPTOM = "Запись симптомов"
    PROVIDING_ADVICE = "Предоставление рекомендаций"
    MANAGING_MEDICATIONS = "Управление лекарствами"
    SEARCHING_CLINICS = "Поиск клиник"
    CONSULTING_DOCTOR = "Консультация с врачом"
    SAVING = "Сохранение состояния"
    ERROR = "Ошибка"
    TERMINATED = "Завершение"


ALLOWED_TRANSITIONS: dict[AssistantStatus, set[AssistantStatus]] = {
    AssistantStatus.STARTUP: {AssistantStatus.READY, AssistantStatus.ERROR},
    AssistantStatus.READY: {
        AssistantStatus.MANAGING_USERS,
        AssistantStatus.RECORDING_SYMPTOM,
        AssistantStatus.PROVIDING_ADVICE,
        AssistantStatus.MANAGING_MEDICATIONS,
        AssistantStatus.SEARCHING_CLINICS,
        AssistantStatus.CONSULTING_DOCTOR,
        AssistantStatus.SAVING,
        AssistantStatus.ERROR,
    },
    AssistantStatus.MANAGING_USERS: {AssistantStatus.READY, AssistantStatus.ERROR},
    AssistantStatus.RECORDING_SYMPTOM: {AssistantStatus.READY, AssistantStatus.ERROR},
    AssistantStatus.PROVIDING_ADVICE: {AssistantStatus.READY, AssistantStatus.ERROR},
    AssistantStatus.MANAGING_MEDICATIONS: {AssistantStatus.READY, AssistantStatus.ERROR},
    AssistantStatus.SEARCHING_CLINICS: {AssistantStatus.READY, AssistantStatus.ERROR},
    AssistantStatus.CONSULTING_DOCTOR: {AssistantStatus.READY, AssistantStatus.ERROR},
    AssistantStatus.SAVING: {AssistantStatus.TERMINATED, AssistantStatus.READY, AssistantStatus.ERROR},
    AssistantStatus.ERROR: {AssistantStatus.READY, AssistantStatus.TERMINATED},
    AssistantStatus.TERMINATED: {AssistantStatus.STARTUP, AssistantStatus.READY},
}


@dataclass
class AssistantStateMachine:
    status: AssistantStatus = AssistantStatus.STARTUP
    last_action: str = "Инициализация системы"

    def transition(self, new_status: AssistantStatus, action: str) -> None:
        allowed = ALLOWED_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(
                f"Недопустимый переход состояния: {self.status.value} -> {new_status.value}",
            )
        self.status = new_status
        self.last_action = action

    def move_to_error(self, error_message: str) -> None:
        self.status = AssistantStatus.ERROR
        self.last_action = error_message

    def force_ready(self, action: str) -> None:
        self.status = AssistantStatus.READY
        self.last_action = action

    def to_dict(self) -> dict[str, str]:
        return {
            "status": self.status.name,
            "last_action": self.last_action,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str] | None) -> "AssistantStateMachine":
        if not data:
            return cls()
        status_name = data.get("status", AssistantStatus.STARTUP.name)
        last_action = data.get("last_action", "Инициализация системы")
        status = AssistantStatus[status_name]
        return cls(status=status, last_action=last_action)
