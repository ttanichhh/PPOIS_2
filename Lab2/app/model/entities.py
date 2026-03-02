from dataclasses import dataclass


@dataclass(frozen=True)
class ClientRecord:
    last_name: str
    first_name: str
    middle_name: str
    account_number: str
    registration_address: str
    mobile_phone: str
    home_phone: str

    def fio_compact(self) -> str:
        parts = [self.last_name.strip(), self.first_name.strip(), self.middle_name.strip()]
        return " ".join([p for p in parts if p])