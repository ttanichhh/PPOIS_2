from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox,
    QPushButton, QGroupBox, QLabel, QWidget, QFormLayout
)

from Lab2.app.model.search import SearchCriteria, CriteriaMode


class DeleteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удаление по условиям")
        self.resize(720, 280)

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
        grp_layout = QVBoxLayout(self.grp)

        # Mode 1
        self.ed_last_name = QLineEdit()
        self.ed_last_name.setPlaceholderText("например: Иванов")
        self.ed_mobile = QLineEdit()
        self.ed_mobile.setPlaceholderText("мобильный полностью")

        self.w_mode1 = QWidget()
        f1 = QFormLayout(self.w_mode1)
        f1.addRow("Фамилия:", self.ed_last_name)
        f1.addRow("Мобильный (полностью):", self.ed_mobile)
        hint1 = QLabel("Условие: мобильный ИЛИ фамилия.")
        hint1.setWordWrap(True)
        f1.addRow(hint1)

        # Mode 2
        self.ed_account = QLineEdit()
        self.ed_account.setPlaceholderText("можно часть")
        self.ed_addr = QLineEdit()
        self.ed_addr.setPlaceholderText("можно часть")

        self.w_mode2 = QWidget()
        f2 = QFormLayout(self.w_mode2)
        f2.addRow("Номер счета (можно часть):", self.ed_account)
        f2.addRow("Адрес (можно часть):", self.ed_addr)
        hint2 = QLabel("Условие: счет ИЛИ адрес (по части).")
        hint2.setWordWrap(True)
        f2.addRow(hint2)

        # Mode 3
        self.ed_fio = QLineEdit()
        self.ed_fio.setPlaceholderText("можно часть")
        self.ed_phone_exact = QLineEdit()
        self.ed_phone_exact.setPlaceholderText("полностью: моб ИЛИ домашний")

        self.w_mode3 = QWidget()
        f3 = QFormLayout(self.w_mode3)
        f3.addRow("ФИО (можно часть):", self.ed_fio)
        f3.addRow("Телефон (полностью):", self.ed_phone_exact)
        hint3 = QLabel("Условие: ФИО И телефон.")
        hint3.setWordWrap(True)
        f3.addRow(hint3)

        grp_layout.addWidget(self.w_mode1)
        grp_layout.addWidget(self.w_mode2)
        grp_layout.addWidget(self.w_mode3)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.grp)

        self.btn_close.clicked.connect(self.close)
        self.mode.currentIndexChanged.connect(self._apply_mode)

        self._apply_mode()

    def _apply_mode(self):
        mode: CriteriaMode = self.mode.currentData()
        self.w_mode1.setVisible(mode == CriteriaMode.PHONE_OR_LASTNAME)
        self.w_mode2.setVisible(mode == CriteriaMode.ACCOUNT_OR_ADDRESS)
        self.w_mode3.setVisible(mode == CriteriaMode.FIO_AND_DIGITS_IN_PHONE)

    def get_criteria(self) -> SearchCriteria:
        mode: CriteriaMode = self.mode.currentData()
        return SearchCriteria(
            mode=mode,
            last_name=self.ed_last_name.text(),
            phone=self.ed_mobile.text(),
            account_number=self.ed_account.text(),
            address_part=self.ed_addr.text(),
            fio_text=self.ed_fio.text(),
            phone_exact=self.ed_phone_exact.text(),
        )

    def validate(self) -> str:
        c = self.get_criteria()

        if c.mode == CriteriaMode.PHONE_OR_LASTNAME:
            if not (c.last_name.strip() or c.phone.strip()):
                return "Заполните фамилию или мобильный (или оба)."

        elif c.mode == CriteriaMode.ACCOUNT_OR_ADDRESS:
            if not (c.account_number.strip() or c.address_part.strip()):
                return "Заполните номер счета (можно часть) или адрес (можно часть)."

        elif c.mode == CriteriaMode.FIO_AND_DIGITS_IN_PHONE:
            if not c.fio_text.strip():
                return "Введите ФИО (можно часть)."
            if not c.phone_exact.strip():
                return "Введите телефон полностью (моб или домашний)."

        return ""