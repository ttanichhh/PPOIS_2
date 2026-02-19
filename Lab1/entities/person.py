from Lab1.exceptions import EmptyValueError

class Person:
    def __init__(self, person_id: int, name: str, phone: str) -> None:
        self._id: int = person_id
        self._name: str = name
        self._phone: str = phone

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value:
            raise EmptyValueError("Имя не может быть пустым")
        self._name = value

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str) -> None:
        if not value:
            raise EmptyValueError("Номер не может быть пустым")
        self._phone = value

    def __str__(self) -> str:
        return f"{self._name} (ID: {self._id}, тел: {self._phone})"