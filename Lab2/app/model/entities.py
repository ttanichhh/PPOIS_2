from dataclasses import dataclass


@dataclass(frozen=True)
class ClientRecord:
    fio: str
    account_number: str
    registration_address: str
    mobile_phone: str
    home_phone: str