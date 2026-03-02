from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox, QSizePolicy
from PySide6.QtCore import Signal


class PaginationWidget(QWidget):
    first_clicked = Signal()
    prev_clicked = Signal()
    next_clicked = Signal()
    last_clicked = Signal()
    page_size_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.btn_first = QPushButton("⏮")
        self.btn_prev = QPushButton("◀")
        self.btn_next = QPushButton("▶")
        self.btn_last = QPushButton("⏭")

        for b in (self.btn_first, self.btn_prev, self.btn_next, self.btn_last):
            b.setFixedWidth(44)

        self.page_info = QLabel("стр. 1 из 1 • записей 0")
        self.page_info.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.page_size = QComboBox()
        self.page_size.addItems(["5", "10", "20", "50"])
        self.page_size.setCurrentText("10")

        layout.addWidget(self.btn_first)
        layout.addWidget(self.btn_prev)
        layout.addWidget(self.btn_next)
        layout.addWidget(self.btn_last)
        layout.addSpacing(12)
        layout.addWidget(self.page_info)
        layout.addSpacing(12)
        layout.addWidget(QLabel("на странице:"))
        layout.addWidget(self.page_size)

        self.btn_first.clicked.connect(self.first_clicked.emit)
        self.btn_prev.clicked.connect(self.prev_clicked.emit)
        self.btn_next.clicked.connect(self.next_clicked.emit)
        self.btn_last.clicked.connect(self.last_clicked.emit)
        self.page_size.currentTextChanged.connect(lambda t: self.page_size_changed.emit(int(t)))

    def set_info(self, current_page_1based: int, total_pages: int, total_records: int) -> None:
        total_pages = max(total_pages, 1)
        current_page_1based = max(1, min(current_page_1based, total_pages))
        self.page_info.setText(f"стр. {current_page_1based} из {total_pages} • записей {total_records}")