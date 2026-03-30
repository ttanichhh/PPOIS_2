from datetime import datetime
from typing import List
from exceptions import InvalidDataFormatError


class Symptom:
    def __init__(self, name: str, severity: int = 5, date: str = None) -> None:
        self._name: str = name
        if not 1 <= severity <= 10:
            raise InvalidDataFormatError("Тяжесть должна быть от 1 до 10")
        self._severity: int = severity
        if date:
            self._date: str = date
        else:
            self._date: str = datetime.now().strftime("%Y-%m-%d %H:%M")

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

    @date.setter
    def date(self, value: str) -> None:
        self._date = value

    def __str__(self) -> str:
        return f"Симптом: {self._name} | Тяжесть: {self._severity}/10 | {self._date}"


class Medication:
    def __init__(self, name: str, dosage: str, schedule: str) -> None:
        self._name: str = name
        self._dosage: str = dosage
        self._schedule: str = schedule

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
    def __init__(self, text: str, source: str = "Ассистент", date: str = None) -> None:
        self._text: str = text
        self._source: str = source
        if date:
            self._date: str = date
        else:
            self._date: str = datetime.now().strftime("%Y-%m-%d %H:%M")

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
        self._symptoms: List[Symptom] = []
        self._medications: List[Medication] = []
        self._recommendations: List[Recommendation] = []

    @property
    def symptoms(self) -> List[Symptom]:
        return self._symptoms

    @property
    def medications(self) -> List[Medication]:
        return self._medications

    @property
    def recommendations(self) -> List[Recommendation]:
        return self._recommendations

    def add_symptom(self, symptom: Symptom) -> None:
        self._symptoms.append(symptom)

    def add_medication(self, medication: Medication) -> None:
        self._medications.append(medication)

    def add_recommendation(self, recommendation: Recommendation) -> None:
        self._recommendations.append(recommendation)

    def __str__(self) -> str:
        return (f"Медицинская история: {len(self._symptoms)} симптомов, "
                f"{len(self._medications)} лекарств, {len(self._recommendations)} советов")
