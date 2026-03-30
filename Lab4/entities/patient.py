from exceptions import InvalidDataFormatError
from entities.person import Person

class Patient(Person):
    def __init__(self, person_id: int, name: str, phone: str, age: int) -> None:
        super().__init__(person_id, name, phone)
        self._age: int = age
        self._medical_history = None

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int) -> None:
        if value <= 0:
            raise InvalidDataFormatError("Возраст должен быть положительным")
        self._age = value

    @property
    def medical_history(self):
        return self._medical_history

    @medical_history.setter
    def medical_history(self, value) -> None:
        self._medical_history = value

    def __str__(self) -> str:
        return f"Пациент: {self._name} | Возраст: {self._age} | ID: {self._id}"
