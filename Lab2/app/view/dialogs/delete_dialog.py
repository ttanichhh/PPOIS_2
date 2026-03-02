from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QLabel
)
from Lab2.app.model.search import SearchCriteria, CriteriaMode


class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удаление по условиям")
        self.resize(700, 260)

        self.mode = QComboBox()
        self.mode.addItem(CriteriaMode.PHONE_OR_LASTNAME.value, CriteriaMode.PHONE_OR_LASTNAME)
        self.mode.addItem(CriteriaMode.ACCOUNT_OR_ADDRESS.value, CriteriaMode.ACCOUNT_OR_ADDRESS)
        self.mode.addItem(CriteriaMode.FIO_AND_DIGITS_IN_PHONE.value, CriteriaMode.FIO_AND_DIGITS_IN_PHONE)

        self.btn_delete = QPushButton("Удалить")
        self.btn_close = QPushButton("Закрыть")

        top = QHBoxLayout()
        top.addWidget(QLabel("Режим:"))
        top.addWidget(self.mode, 1)
        top.addWidget(self.btn_delete)
        top.addWidget(self.btn_close)

        self.grp = QGroupBox("Условия удаления")
        self.form = QFormLayout(self.grp)

        # Fields
        self.ed_last_name = QLineEdit()
        self.ed_phone = QLineEdit()
        self.ed_account = QLineEdit()
        self.ed_addr = QLineEdit()
        self.ed_fio_last = QLineEdit()
        self.ed_fio_first = QLineEdit()
        self.ed_fio_middle = QLineEdit()
        self.ed_digits = QLineEdit()
        self.ed_digits.setPlaceholderText("например: 23")

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.grp)

        self.btn_close.clicked.connect(self.close)
        self.mode.currentIndexChanged.connect(self._rebuild_form)

        self._rebuild_form()

    def _rebuild_form(self):
        while self.form.rowCount():
            self.form.removeRow(0)

        mode: CriteriaMode = self.mode.currentData()

        if mode == CriteriaMode.PHONE_OR_LASTNAME:
            self.form.addRow("Фамилия (часть):", self.ed_last_name)
            self.form.addRow("Телефон (часть):", self.ed_phone)
        elif mode == CriteriaMode.ACCOUNT_OR_ADDRESS:
            self.form.addRow("Номер счета (часть):", self.ed_account)
            self.form.addRow("Адрес (часть):", self.ed_addr)
        elif mode == CriteriaMode.FIO_AND_DIGITS_IN_PHONE:
            self.form.addRow("Фамилия (можно часть):", self.ed_fio_last)
            self.form.addRow("Имя (можно часть):", self.ed_fio_first)
            self.form.addRow("Отчество (можно часть):", self.ed_fio_middle)
            self.form.addRow("Цифры в телефоне:", self.ed_digits)

    def get_criteria(self) -> SearchCriteria:
        mode: CriteriaMode = self.mode.currentData()
        return SearchCriteria(
            mode=mode,
            last_name=self.ed_last_name.text(),
            phone=self.ed_phone.text(),
            account_number=self.ed_account.text(),
            address_part=self.ed_addr.text(),
            fio_last=self.ed_fio_last.text(),
            fio_first=self.ed_fio_first.text(),
            fio_middle=self.ed_fio_middle.text(),
            digits=self.ed_digits.text(),
        )

    def validate(self) -> str:
        c = self.get_criteria()
        if c.mode == CriteriaMode.PHONE_OR_LASTNAME:
            if not (c.last_name.strip() or c.phone.strip()):
                return "Заполните телефон или фамилию (или оба)."
        elif c.mode == CriteriaMode.ACCOUNT_OR_ADDRESS:
            if not (c.account_number.strip() or c.address_part.strip()):
                return "Заполните счет или адрес (или оба)."
        elif c.mode == CriteriaMode.FIO_AND_DIGITS_IN_PHONE:
            fio_any = any([c.fio_last.strip(), c.fio_first.strip(), c.fio_middle.strip()])
            if not fio_any:
                return "Заполните хотя бы один элемент ФИО."
            if not c.digits.strip():
                return "Введите цифры для поиска в телефоне."
        return ""