import math
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QDialog

from Lab2.app.view.main_window import MainWindow
from Lab2.app.view.dialogs.add_edit_dialog import AddEditDialog
from Lab2.app.view.dialogs.search_dialog import SearchDialog
from Lab2.app.view.dialogs.delete_dialog import DeleteDialog

from Lab2.app.model.repository import ClientRepository
from Lab2.app.model.xml_export_dom import export_clients_to_xml_dom
from Lab2.app.model.xml_import_sax import import_clients_from_xml_sax


class MainController:
    def __init__(self):
        self.view = MainWindow()
        self.repo = ClientRepository()

        self.page_index = 0
        self.page_size = 10
        self.total_records = 0

        # Wire actions
        v = self.view
        v.act_exit.triggered.connect(v.close)
        v.act_about.triggered.connect(lambda: v.show_info(
            "Учебное приложение (MVC) на Python + PySide6 + SQLite + XML (DOM/SAX).\n"
            "Функции: добавление, поиск, удаление, пагинация, импорт/экспорт."
        ))

        v.act_add.triggered.connect(self.on_add)
        v.act_search.triggered.connect(self.on_search)
        v.act_delete.triggered.connect(self.on_delete)

        v.act_new.triggered.connect(self.on_new_clear_db)
        v.act_save.triggered.connect(self.on_export_xml)
        v.act_open.triggered.connect(self.on_import_xml)

        # Pagination
        v.pagination.first_clicked.connect(self.on_first)
        v.pagination.prev_clicked.connect(self.on_prev)
        v.pagination.next_clicked.connect(self.on_next)
        v.pagination.last_clicked.connect(self.on_last)
        v.pagination.page_size_changed.connect(self.on_page_size_changed)

        # Initial load
        self.reload_page()

    def show(self):
        self.view.show()

    # -------- Pagination helpers --------
    def total_pages(self) -> int:
        if self.total_records <= 0:
            return 1
        return max(1, math.ceil(self.total_records / self.page_size))

    def clamp_page(self):
        tp = self.total_pages()
        self.page_index = max(0, min(self.page_index, tp - 1))

    def reload_page(self):
        self.clamp_page()
        rows, total = self.repo.get_page(self.page_index, self.page_size)
        self.total_records = total
        self.view.model.set_rows(rows)
        self.view.pagination.set_info(self.page_index + 1, self.total_pages(), self.total_records)

    def on_first(self):
        self.page_index = 0
        self.reload_page()

    def on_prev(self):
        self.page_index -= 1
        self.reload_page()

    def on_next(self):
        self.page_index += 1
        self.reload_page()

    def on_last(self):
        self.page_index = self.total_pages() - 1
        self.reload_page()

    def on_page_size_changed(self, n: int):
        self.page_size = max(1, int(n))
        self.page_index = 0
        self.reload_page()

    # -------- Actions --------
    def on_add(self):
        dlg = AddEditDialog(self.view)
        result = dlg.exec()

        if result == QDialog.DialogCode.Accepted:
            err = dlg.validate()
            if err:
                self.view.show_error(err)
                return
            self.repo.add(dlg.get_record())
            self.reload_page()

    def on_search(self):
        dlg = SearchDialog(self.view)

        # local pagination state for search dialog
        state = {"page_index": 0, "page_size": int(dlg.pagination.page_size.currentText()), "total": 0}

        def load_search():
            err = dlg.validate()
            if err:
                self.view.show_error(err, "Ошибка условий поиска")
                return

            criteria = dlg.get_criteria()
            # clamp
            if state["page_size"] <= 0:
                state["page_size"] = 10
            if state["page_index"] < 0:
                state["page_index"] = 0

            rows, total = self.repo.search_page(criteria, state["page_index"], state["page_size"])
            state["total"] = total

            # compute pages
            total_pages = max(1, math.ceil(total / state["page_size"])) if total > 0 else 1
            state["page_index"] = max(0, min(state["page_index"], total_pages - 1))

            dlg.table_model.set_rows(rows)
            dlg.pagination.set_info(state["page_index"] + 1, total_pages, total)

        def tp():
            if state["total"] <= 0:
                return 1
            return max(1, math.ceil(state["total"] / state["page_size"]))

        dlg.btn_find.clicked.connect(lambda: (state.__setitem__("page_index", 0), load_search()))
        dlg.btn_clear.clicked.connect(lambda: (state.__setitem__("page_index", 0), dlg.table_model.set_rows([]), dlg.pagination.set_info(1, 1, 0)))

        dlg.pagination.first_clicked.connect(lambda: (state.__setitem__("page_index", 0), load_search()))
        dlg.pagination.prev_clicked.connect(lambda: (state.__setitem__("page_index", state["page_index"] - 1), load_search()))
        dlg.pagination.next_clicked.connect(lambda: (state.__setitem__("page_index", state["page_index"] + 1), load_search()))
        dlg.pagination.last_clicked.connect(lambda: (state.__setitem__("page_index", tp() - 1), load_search()))
        dlg.pagination.page_size_changed.connect(lambda n: (state.__setitem__("page_size", int(n)), state.__setitem__("page_index", 0), load_search()))

        dlg.exec()

    def on_delete(self):
        dlg = DeleteDialog(self.view)

        def do_delete():
            err = dlg.validate()
            if err:
                self.view.show_error(err, "Ошибка условий удаления")
                return
            deleted = self.repo.delete_by_criteria(dlg.get_criteria())
            if deleted > 0:
                self.view.show_info(f"Удалено записей: {deleted}")
            else:
                self.view.show_info("Записей по заданным условиям не найдено.")
            self.reload_page()

        dlg.btn_delete.clicked.connect(do_delete)
        dlg.exec()

    def on_new_clear_db(self):
        # простое "Новый": очищаем БД
        self.repo.clear_all()
        self.page_index = 0
        self.reload_page()
        self.view.show_info("База очищена. Записи удалены.")

    def on_export_xml(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self.view,
            "Сохранить XML",
            "clients.xml",
            "XML files (*.xml)"
        )
        if not file_path:
            return

        # export all records (без пагинации)
        # читаем из БД всё
        all_records = []
        idx = 0
        page_size = 500
        while True:
            rows, total = self.repo.get_page(idx, page_size)
            all_records.extend(rows)
            if len(all_records) >= total:
                break
            idx += 1

        try:
            export_clients_to_xml_dom(all_records, file_path)
            self.view.show_info(f"Сохранено записей: {len(all_records)}")
        except Exception as e:
            self.view.show_error(f"Не удалось сохранить XML:\n{e}")

    def on_import_xml(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            "Загрузить XML",
            "",
            "XML files (*.xml)"
        )
        if not file_path:
            return
        try:
            records = import_clients_from_xml_sax(file_path)
            if not records:
                self.view.show_info("В файле нет записей.")
                return
            self.repo.add_many(records)
            self.page_index = 0
            self.reload_page()
            self.view.show_info(f"Загружено и добавлено записей: {len(records)}")
        except Exception as e:
            self.view.show_error(f"Не удалось загрузить XML:\n{e}")