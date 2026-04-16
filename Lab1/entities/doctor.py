from entities.person import Person
from exceptions import EmptyValueError


class Doctor(Person):
    def __init__(
        self,
        person_id: int,
        name: str,
        phone: str,
        specialization: str,
        clinic: str,
    ) -> None:
        super().__init__(person_id, name, phone)
        self.specialization = specialization
        self.clinic = clinic

    @property
    def specialization(self) -> str:
        return self._specialization

    @specialization.setter
    def specialization(self, value: str) -> None:
        if not value.strip():
            raise EmptyValueError("Специализация не может быть пустой")
        self._specialization = value.strip()

    @property
    def clinic(self) -> str:
        return self._clinic

    @clinic.setter
    def clinic(self, value: str) -> None:
        if not value.strip():
            raise EmptyValueError("Клиника не может быть пустой")
        self._clinic = value.strip()

    def __str__(self) -> str:
        return f"Доктор: {self._name} | {self._specialization} | Клиника: {self._clinic}"
