from dataclasses import dataclass
from enum import Enum


class CriteriaMode(Enum):
    PHONE_OR_LASTNAME = "Мобильный или фамилия"
    ACCOUNT_OR_ADDRESS = "Счет или адрес"
    FIO_AND_DIGITS_IN_PHONE = "ФИО и телефон"


@dataclass(frozen=True)
class SearchCriteria:
    mode: CriteriaMode

    # Mode 1:
    last_name: str = ""  # part of fio
    phone: str = ""      # mobile only, exact match

    # Mode 2:
    account_number: str = ""  # exact match
    address_part: str = ""    # exact match

    # Mode 3:
    fio_text: str = ""        # partial match
    phone_exact: str = ""     # exact match, checks mobile OR home