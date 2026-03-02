from typing import List
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex

from Lab2.app.model.entities import ClientRecord


class ClientsTableModel(QAbstractTableModel):
    HEADERS = ["ФИО", "Номер счета", "Адрес прописки", "Мобильный", "Городской"]

    def __init__(self):
        super().__init__()
        self._rows: List[ClientRecord] = []

    def set_rows(self, rows: List[ClientRecord]) -> None:
        self.beginResetModel()
        self._rows = list(rows)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.HEADERS)

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return str(section + 1)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        r = self._rows[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            col = index.column()
            if col == 0:
                return r.fio_compact()
            if col == 1:
                return r.account_number
            if col == 2:
                return r.registration_address
            if col == 3:
                return r.mobile_phone
            if col == 4:
                return r.home_phone
        return None