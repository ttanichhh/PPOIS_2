from dataclasses import dataclass
from enum import Enum


class CriteriaMode(Enum):
    PHONE_OR_LASTNAME = "Телефон или фамилия"
    ACCOUNT_OR_ADDRESS = "Счет или адрес"
    FIO_AND_DIGITS_IN_PHONE = "ФИО и цифры в одном из номеров"


@dataclass(frozen=True)
class SearchCriteria:
    mode: CriteriaMode

    # Mode 1:
    last_name: str = ""
    phone: str = ""  # искать в mobile/home

    # Mode 2:
    account_number: str = ""
    address_part: str = ""

    # Mode 3:
    fio_last: str = ""
    fio_first: str = ""
    fio_middle: str = ""
    digits: str = ""  # подстрока цифр, например "23"