class StudioError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.msg: str = msg


class ResourceBusyError(StudioError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.msg: str = msg


class WorkflowOrderError(StudioError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.msg: str = msg


class InvalidDataFormatError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.msg: str = msg


class NoneObjectError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.msg: str = msg


class GenreMismatchError(StudioError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.msg: str = msg