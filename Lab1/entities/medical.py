from __future__ import annotations

from datetime import datetime

from exceptions import EmptyValueError, InvalidDataFormatError


class Symptom:
    def __init__(self, name: str, severity: int = 5, date: str | None = None) -> None:
        if not name.strip():
            raise EmptyValueError("Название симптома не может быть пустым")
        self._name = name.strip()
        self.severity = severity
        self._date = date or datetime.now().strftime("%Y-%m-%d %H:%M")

    @property
    def name(self) -> str:
        return self._name

    @property
    def severity(self) -> int:
        return self._severity

    @severity.setter
    def severity(self, value: int) -> None:
        if not 1 <= value <= 10:
            raise InvalidDataFormatError("Тяжесть должна быть от 1 до 10")
        self._severity = value

    @property
    def date(self) -> str:
        return self._date

    def __str__(self) -> str:
        return f"Симптом: {self._name} | Тяжесть: {self._severity}/10 | {self._date}"


class Medication:
    def __init__(self, name: str, dosage: str, schedule: str) -> None:
        if not name.strip():
            raise EmptyValueError("Название лекарства не может быть пустым")
        if not dosage.strip():
            raise EmptyValueError("Дозировка не может быть пустой")
        if not schedule.strip():
            raise EmptyValueError("Расписание не может быть пустым")

        self._name = name.strip()
        self._dosage = dosage.strip()
        self._schedule = schedule.strip()

    @property
    def name(self) -> str:
        return self._name

    @property
    def dosage(self) -> str:
        return self._dosage

    @property
    def schedule(self) -> str:
        return self._schedule

    def __str__(self) -> str:
        return f"Лекарство: {self._name} | {self._dosage} | Прием: {self._schedule}"


class Recommendation:
    def __init__(
        self,
        text: str,
        source: str = "Ассистент",
        date: str | None = None,
    ) -> None:
        if not text.strip():
            raise EmptyValueError("Текст рекомендации не может быть пустым")
        self._text = text.strip()
        self._source = source.strip() or "Ассистент"
        self._date = date or datetime.now().strftime("%Y-%m-%d %H:%M")

    @property
    def text(self) -> str:
        return self._text

    @property
    def source(self) -> str:
        return self._source

    @property
    def date(self) -> str:
        return self._date

    def __str__(self) -> str:
        return f"Совет: {self._text} | Источник: {self._source} | {self._date}"


class MedicalHistory:
    def __init__(self) -> None:
        self._symptoms: list[Symptom] = []
        self._medications: list[Medication] = []
        self._recommendations: list[Recommendation] = []

    @property
    def symptoms(self) -> list[Symptom]:
        return self._symptoms

    @property
    def medications(self) -> list[Medication]:
        return self._medications

    @property
    def recommendations(self) -> list[Recommendation]:
        return self._recommendations

    def add_symptom(self, symptom: Symptom) -> None:
        self._symptoms.append(symptom)

    def add_medication(self, medication: Medication) -> None:
        self._medications.append(medication)

    def add_recommendation(self, recommendation: Recommendation) -> None:
        self._recommendations.append(recommendation)

    def __str__(self) -> str:
        return (
            f"Медицинская история: {len(self._symptoms)} симптомов, "
            f"{len(self._medications)} лекарств, "
            f"{len(self._recommendations)} рекомендаций"
        )
