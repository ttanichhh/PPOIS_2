from exceptions import InvalidDataFormatError


class Person:
    def __init__(self, name: str):
        self._name: str = name
        self._is_busy: bool = False

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value:
            raise InvalidDataFormatError("Name cannot be empty.")
        self._name = value

    @property
    def is_busy(self) -> bool:
        return self._is_busy

    @is_busy.setter
    def is_busy(self, value: bool):
        if not isinstance(value, bool):
            raise InvalidDataFormatError("is_busy must be a boolean.")
        self._is_busy = value

    def __str__(self) -> str:
        return self._name


class Director(Person):
    def __init__(self, name: str, style: str = "General"):
        super().__init__(name)
        self._style: str = style

    @property
    def style(self) -> str:
        return self._style

    @style.setter
    def style(self, value: str):
        if not value:
            raise InvalidDataFormatError("Style cannot be empty.")
        self._style = value

    def __str__(self) -> str:
        status = "Busy" if self._is_busy else "FREE"
        return f"Director: {self._name} [Style: {self._style}] [{status}]"


class Actor(Person):
    def __init__(self, name: str, rank: str = "Novice"):
        super().__init__(name)
        self._rank: str = rank

    @property
    def rank(self) -> str:
        return self._rank

    @rank.setter
    def rank(self, value: str):
        self._rank = value

    def __str__(self) -> str:
        status = "Busy" if self._is_busy else "FREE"
        return f"Actor: {self._name} [Rank: {self._rank}] [{status}]"