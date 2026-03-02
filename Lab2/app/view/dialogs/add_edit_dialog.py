from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QVBoxLayout, QLabel
)
from Lab2.app.model.entities import ClientRecord


class AddEditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить запись")

        self.ed_last = QLineEdit()
        self.ed_first = QLineEdit()
        self.ed_middle = QLineEdit()
        self.ed_account = QLineEdit()
        self.ed_address = QLineEdit()
        self.ed_mobile = QLineEdit()
        self.ed_home = QLineEdit()

        hint = QLabel("Совет: номер счета и телефоны хранятся как строки (можно с +, пробелами).")
        hint.setWordWrap(True)

        form = QFormLayout()
        form.addRow("Фамилия:", self.ed_last)
        form.addRow("Имя:", self.ed_first)
        form.addRow("Отчество:", self.ed_middle)
        form.addRow("Номер счета:", self.ed_account)
        form.addRow("Адрес прописки:", self.ed_address)
        form.addRow("Мобильный:", self.ed_mobile)
        form.addRow("Городской:", self.ed_home)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Сохранить")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(hint)
        layout.addLayout(form)
        layout.addWidget(self.buttons)

    def get_record(self) -> ClientRecord:
        def norm(s: str) -> str:
            return (s or "").strip()

        return ClientRecord(
            last_name=norm(self.ed_last.text()),
            first_name=norm(self.ed_first.text()),
            middle_name=norm(self.ed_middle.text()),
            account_number=norm(self.ed_account.text()),
            registration_address=norm(self.ed_address.text()),
            mobile_phone=norm(self.ed_mobile.text()),
            home_phone=norm(self.ed_home.text()),
        )

    def validate(self) -> str:
        r = self.get_record()
        if not r.last_name:
            return "Фамилия обязательна."
        if not r.first_name:
            return "Имя обязательно."
        if not r.account_number:
            return "Номер счета обязателен."
        if not r.registration_address:
            return "Адрес прописки обязателен."
        if not (r.mobile_phone or r.home_phone):
            return "Укажите хотя бы один телефон (мобильный или городской)."
        return ""