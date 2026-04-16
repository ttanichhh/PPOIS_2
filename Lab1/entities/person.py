from exceptions import EmptyValueError


class Person:
    def __init__(self, person_id: int, name: str, phone: str) -> None:
        self._id = person_id
        self.name = name
        self.phone = phone

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value.strip():
            raise EmptyValueError("Имя не может быть пустым")
        self._name = value.strip()

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        if not value.strip():
            raise EmptyValueError("Номер не может быть пустым")
        self._phone = value.strip()

    def __str__(self) -> str:
        return f"{self._name} (ID: {self._id}, тел: {self._phone})"
