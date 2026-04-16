from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QVBoxLayout, QLabel
)
from app.model.entities import ClientRecord


class AddEditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить запись")

        self.ed_fio = QLineEdit()
        self.ed_account = QLineEdit()
        self.ed_address = QLineEdit()
        self.ed_mobile = QLineEdit()
        self.ed_home = QLineEdit()

        self.ed_fio.setPlaceholderText("например: Иванов Иван Иванович")
        self.ed_account.setPlaceholderText("точно как храните (поиск по счету — точный)")
        self.ed_address.setPlaceholderText("точно как храните (поиск по адресу — точный)")
        self.ed_mobile.setPlaceholderText("например: +79161234567")
        self.ed_home.setPlaceholderText("например: 80171234567")

        hint = QLabel(
            "Режимы поиска по ТЗ:\n"
            "1) мобильный (полностью) ИЛИ фамилия\n"
            "2) счет (можно часть) ИЛИ адрес (можно часть)\n"
            "3) ФИО (часть) И телефон (полностью, моб или домашний)\n"
        )
        hint.setWordWrap(True)

        form = QFormLayout()
        form.addRow("ФИО:", self.ed_fio)
        form.addRow("Номер счета:", self.ed_account)
        form.addRow("Адрес прописки:", self.ed_address)
        form.addRow("Мобильный:", self.ed_mobile)
        form.addRow("Городской:", self.ed_home)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Сохранить")
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(hint)
        layout.addLayout(form)
        layout.addWidget(self.buttons)

    @staticmethod
    def _norm(s: str) -> str:
        return (s or "").strip()

    def get_record(self) -> ClientRecord:
        return ClientRecord(
            fio=self._norm(self.ed_fio.text()),
            account_number=self._norm(self.ed_account.text()),
            registration_address=self._norm(self.ed_address.text()),
            mobile_phone=self._norm(self.ed_mobile.text()),
            home_phone=self._norm(self.ed_home.text()),
        )

    def validate(self) -> str:
        r = self.get_record()
        if not r.fio:
            return "ФИО обязательно."
        if not r.account_number:
            return "Номер счета обязателен."
        if not r.registration_address:
            return "Адрес прописки обязателен."
        if not (r.mobile_phone or r.home_phone):
            return "Укажите хотя бы один телефон (мобильный или городской)."
        return ""
