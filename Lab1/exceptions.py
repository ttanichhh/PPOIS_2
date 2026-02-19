class MedicalAssistantError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.msg: str = msg


class EmptyValueError(MedicalAssistantError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.msg: str = msg


class NotFoundError(MedicalAssistantError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.msg: str = msg


class AlreadyExistsError(MedicalAssistantError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.msg: str = msg


class InvalidDataFormatError(MedicalAssistantError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.msg: str = msg