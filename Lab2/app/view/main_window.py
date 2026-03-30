from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableView,
    QMessageBox
)
from PySide6.QtGui import QAction

from Lab2.app.view.table_model import ClientsTableModel
from Lab2.app.view.pagination_widget import PaginationWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Клиенты")
        self.resize(1100, 650)

        # Actions
        self.act_new = QAction("Новый", self)
        self.act_open = QAction("Загрузить XML", self)
        self.act_save = QAction("Сохранить XML", self)
        self.act_exit = QAction("Выход", self)

        self.act_add = QAction("Добавить запись", self)
        self.act_search = QAction("Поиск", self)
        self.act_delete = QAction("Удаление", self)

        self.act_about = QAction("О программе", self)

        # Menu
        m_file = self.menuBar().addMenu("Файл")
        m_file.addAction(self.act_new)
        m_file.addSeparator()
        m_file.addAction(self.act_open)
        m_file.addAction(self.act_save)
        m_file.addSeparator()
        m_file.addAction(self.act_exit)

        m_records = self.menuBar().addMenu("Записи")
        m_records.addAction(self.act_add)
        m_records.addAction(self.act_search)
        m_records.addAction(self.act_delete)

        m_help = self.menuBar().addMenu("Справка")
        m_help.addAction(self.act_about)

        # Toolbar
        tb = self.addToolBar("Панель")
        tb.setMovable(False)
        tb.addAction(self.act_open)
        tb.addAction(self.act_save)
        tb.addSeparator()
        tb.addAction(self.act_add)
        tb.addAction(self.act_search)
        tb.addAction(self.act_delete)

        # Central
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        from PySide6.QtWidgets import QHeaderView

        self.table = QTableView()

        # внешний вид
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(True)

        # высота строк
        self.table.verticalHeader().setDefaultSectionSize(42)

        # выделение строк
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)

        # ширина колонок
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # запрет редактирования
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)

        self.model = ClientsTableModel()
        self.table.setModel(self.model)

        self.pagination = PaginationWidget()

        layout.addWidget(self.table)
        layout.addWidget(self.pagination)

        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)


    def show_error(self, text: str, title: str = "Ошибка"):
        QMessageBox.critical(self, title, text)

    def show_info(self, text: str, title: str = "Информация"):
        QMessageBox.information(self, title, text)