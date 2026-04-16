from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableView,
    QMessageBox, QTreeWidget, QTreeWidgetItem, QStackedWidget
)
from PySide6.QtGui import QAction

from app.view.table_model import ClientsTableModel
from app.view.pagination_widget import PaginationWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Клиенты")
        self.resize(1100, 650)

        # Actions
        self.act_new = QAction("Новый", self)
        self.act_open = QAction("Загрузить XML", self)
        self.act_save = QAction("Сохранить XML", self)
        self.act_open_db = QAction("Открыть БД", self)
        self.act_save_db = QAction("Сохранить БД как...", self)
        self.act_exit = QAction("Выход", self)

        self.act_add = QAction("Добавить запись", self)
        self.act_search = QAction("Поиск", self)
        self.act_delete = QAction("Удаление", self)
        self.act_table_view = QAction("Таблица", self)
        self.act_tree_view = QAction("Дерево", self)
        self.act_table_view.setCheckable(True)
        self.act_tree_view.setCheckable(True)
        self.act_table_view.setChecked(True)

        self.act_about = QAction("О программе", self)

        # Menu
        m_file = self.menuBar().addMenu("Файл")
        m_file.addAction(self.act_new)
        m_file.addSeparator()
        m_file.addAction(self.act_open_db)
        m_file.addAction(self.act_save_db)
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
        tb.addAction(self.act_open_db)
        tb.addAction(self.act_save_db)
        tb.addSeparator()
        tb.addAction(self.act_open)
        tb.addAction(self.act_save)
        tb.addSeparator()
        tb.addAction(self.act_add)
        tb.addAction(self.act_search)
        tb.addAction(self.act_delete)
        tb.addSeparator()
        tb.addAction(self.act_table_view)
        tb.addAction(self.act_tree_view)

        # Central
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        from PySide6.QtWidgets import QHeaderView

        self.table = QTableView()

        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(True)
        self.table.verticalHeader().setDefaultSectionSize(42)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)

        self.model = ClientsTableModel()
        self.table.setModel(self.model)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Элемент", "Значение"])
        self.tree.setAlternatingRowColors(True)
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.table)
        self.content_stack.addWidget(self.tree)

        self.pagination = PaginationWidget()

        layout.addWidget(self.content_stack)
        layout.addWidget(self.pagination)

        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.statusBar().showMessage("База данных не выбрана")


    def show_error(self, text: str, title: str = "Ошибка"):
        QMessageBox.critical(self, title, text)

    def show_info(self, text: str, title: str = "Информация"):
        QMessageBox.information(self, title, text)

    def set_table_mode(self):
        self.act_table_view.setChecked(True)
        self.act_tree_view.setChecked(False)
        self.content_stack.setCurrentWidget(self.table)

    def set_tree_mode(self):
        self.act_table_view.setChecked(False)
        self.act_tree_view.setChecked(True)
        self.content_stack.setCurrentWidget(self.tree)

    def set_database_label(self, db_path: str):
        self.statusBar().showMessage(f"Текущая БД: {db_path}")

    def set_tree_rows(self, rows):
        self.tree.clear()
        for idx, record in enumerate(rows, start=1):
            root = QTreeWidgetItem([f"Запись {idx}", record.fio])
            fields = [
                ("ФИО клиента", record.fio),
                ("Номер счета", record.account_number),
                ("Адрес прописки", record.registration_address),
                ("Мобильный телефон", record.mobile_phone),
                ("Городской телефон", record.home_phone),
            ]
            for field_name, value in fields:
                root.addChild(QTreeWidgetItem([field_name, value]))
            self.tree.addTopLevelItem(root)
        self.tree.expandAll()
