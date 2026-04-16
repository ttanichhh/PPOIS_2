from __future__ import annotations

from entities.medical import MedicalHistory
from entities.person import Person
from exceptions import InvalidDataFormatError


class Patient(Person):
    def __init__(self, person_id: int, name: str, phone: str, age: int) -> None:
        super().__init__(person_id, name, phone)
        self.age = age
        self._medical_history: MedicalHistory | None = None

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if value <= 0:
            raise InvalidDataFormatError("Возраст должен быть положительным")
        self._age = value

    @property
    def medical_history(self) -> MedicalHistory:
        if self._medical_history is None:
            self._medical_history = MedicalHistory()
        return self._medical_history

    @medical_history.setter
    def medical_history(self, value: MedicalHistory) -> None:
        self._medical_history = value

    def __str__(self) -> str:
        return f"Пациент: {self._name} | Возраст: {self._age} | ID: {self._id}"
