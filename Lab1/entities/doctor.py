from Lab1.exceptions import EmptyValueError
from Lab1.entities.person import Person

class Doctor(Person):
    def __init__(self, person_id: int, name: str, phone: str,
                 specialization: str, clinic: str) -> None:
        super().__init__(person_id, name, phone)
        self._specialization: str = specialization
        self._clinic: str = clinic

    @property
    def specialization(self) -> str:
        return self._specialization

    @specialization.setter
    def specialization(self, value: str) -> None:
        if not value:
            raise EmptyValueError("Специализация не может быть пустой")
        self._specialization = value

    @property
    def clinic(self) -> str:
        return self._clinic

    @clinic.setter
    def clinic(self, value: str) -> None:
        if not value:
            raise EmptyValueError("Клиника не может быть пустой")
        self._clinic = value

    def __str__(self) -> str:
        return f"Доктор: {self._name} | {self._specialization} | Клиника: {self._clinic}"