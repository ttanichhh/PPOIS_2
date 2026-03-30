import tkinter as tk
from tkinter import messagebox, ttk

from exceptions import MedicalAssistantError
from app.application import MedicalAssistantApp


class MedicalAssistantPresenter:
    """Presenter for the MVP GUI implementation."""

    def __init__(self, app: MedicalAssistantApp, view: "MedicalAssistantGUI") -> None:
        self.app = app
        self.view = view

    def refresh_all(self) -> None:
        selected_user_id = self.view.get_selected_user_id()
        self.view.show_users(self.app.get_users())
        self.view.show_areas(self.app.get_areas())
        self.view.show_status(self.app.get_system_status())
        if selected_user_id is not None:
            self.show_history(selected_user_id)
        elif self.view.get_selected_user_id() is not None:
            self.show_history(self.view.get_selected_user_id())

    def register_user(self, name: str, phone: str, age_text: str) -> None:
        user_id = self.app.register_user(name, phone, int(age_text))
        self.refresh_all()
        self.view.set_status_message(f"Пользователь зарегистрирован с ID: {user_id}")

    def show_history(self, user_id: int) -> None:
        history = self.app.get_user_history(user_id)
        self.view.show_history(history)

    def record_symptom(self, user_id: int, symptom: str, severity_text: str) -> None:
        message = self.app.record_symptom(user_id, symptom, int(severity_text))
        self.refresh_all()
        self.view.set_status_message(message)

    def give_advice(self, user_id: int, symptom: str) -> None:
        advice = self.app.give_advice(user_id, symptom)
        self.refresh_all()
        self.view.set_status_message(advice)

    def add_medication(self, user_id: int, name: str, dosage: str, schedule: str) -> None:
        message = self.app.add_medication_reminder(user_id, name, dosage, schedule)
        self.refresh_all()
        self.view.set_status_message(message)

    def show_medications(self, user_id: int) -> None:
        self.view.show_medications(self.app.get_medication_list(user_id))

    def show_clinics(self, area: str) -> None:
        self.view.show_clinics(self.app.get_clinics_by_area(area))

    def show_doctors(self, area: str) -> None:
        self.view.show_doctors(self.app.get_doctors_by_area(area))

    def consult_doctor(self, user_id: int, doctor_id: int, question: str) -> None:
        answer = self.app.consult_doctor(doctor_id, user_id, question)
        self.refresh_all()
        self.view.set_status_message(answer)

    def save(self) -> None:
        self.app.save()
        self.view.set_status_message("Данные сохранены")


class MedicalAssistantGUI:
    def __init__(self, app: MedicalAssistantApp) -> None:
        self.app = app
        self.root = tk.Tk()
        self.root.title("Персональный медицинский ассистент")
        self.root.geometry("1180x760")

        self.status_var = tk.StringVar(value="Система готова к работе")
        self.area_var = tk.StringVar()
        self.doctor_var = tk.StringVar()
        self._doctor_map: dict[str, int] = {}

        self.presenter = MedicalAssistantPresenter(app, self)
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.presenter.refresh_all()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(
            container,
            text="Персональный медицинский ассистент",
            font=("Helvetica", 20, "bold"),
        )
        header.pack(anchor=tk.W, pady=(0, 12))

        notebook = ttk.Notebook(container)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.users_tab = ttk.Frame(notebook, padding=12)
        self.operations_tab = ttk.Frame(notebook, padding=12)
        self.clinics_tab = ttk.Frame(notebook, padding=12)
        self.status_tab = ttk.Frame(notebook, padding=12)

        notebook.add(self.users_tab, text="Пользователи")
        notebook.add(self.operations_tab, text="Медицинские операции")
        notebook.add(self.clinics_tab, text="Клиники и врачи")
        notebook.add(self.status_tab, text="Состояние системы")

        self._build_users_tab()
        self._build_operations_tab()
        self._build_clinics_tab()
        self._build_status_tab()

        footer = ttk.Frame(container)
        footer.pack(fill=tk.X, pady=(12, 0))
        ttk.Label(footer, textvariable=self.status_var).pack(side=tk.LEFT)
        ttk.Button(footer, text="Сохранить", command=self._handle(self.presenter.save)).pack(
            side=tk.RIGHT
        )

    def _build_users_tab(self) -> None:
        form = ttk.LabelFrame(self.users_tab, text="Регистрация пользователя", padding=12)
        form.pack(fill=tk.X, pady=(0, 12))

        self.name_entry = self._add_labeled_entry(form, "Имя", 0)
        self.phone_entry = self._add_labeled_entry(form, "Телефон", 1)
        self.age_entry = self._add_labeled_entry(form, "Возраст", 2)
        ttk.Button(
            form,
            text="Зарегистрировать",
            command=self._handle(
                lambda: self.presenter.register_user(
                    self.name_entry.get(),
                    self.phone_entry.get(),
                    self.age_entry.get(),
                )
            ),
        ).grid(row=0, column=2, rowspan=3, padx=(16, 0), sticky="ns")

        main = ttk.Frame(self.users_tab)
        main.pack(fill=tk.BOTH, expand=True)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        users_frame = ttk.LabelFrame(main, text="Пользователи", padding=8)
        users_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        users_frame.rowconfigure(0, weight=1)
        users_frame.columnconfigure(0, weight=1)

        columns = ("id", "name", "phone", "age", "symptoms", "medications", "recommendations")
        self.users_tree = ttk.Treeview(users_frame, columns=columns, show="headings", height=14)
        headings = {
            "id": "ID",
            "name": "Имя",
            "phone": "Телефон",
            "age": "Возраст",
            "symptoms": "Симптомы",
            "medications": "Лекарства",
            "recommendations": "Рекомендации",
        }
        widths = {
            "id": 60,
            "name": 180,
            "phone": 140,
            "age": 80,
            "symptoms": 90,
            "medications": 90,
            "recommendations": 120,
        }
        for column in columns:
            self.users_tree.heading(column, text=headings[column])
            self.users_tree.column(column, width=widths[column], anchor=tk.CENTER)
        self.users_tree.grid(row=0, column=0, sticky="nsew")
        self.users_tree.bind("<<TreeviewSelect>>", self._on_user_selected)

        history_frame = ttk.LabelFrame(main, text="Медицинская история", padding=8)
        history_frame.grid(row=0, column=1, sticky="nsew")
        history_frame.rowconfigure(0, weight=1)
        history_frame.columnconfigure(0, weight=1)
        self.history_text = tk.Text(history_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.history_text.grid(row=0, column=0, sticky="nsew")

    def _build_operations_tab(self) -> None:
        frame = self.operations_tab
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        symptom_box = ttk.LabelFrame(frame, text="Запись симптома и совет", padding=12)
        symptom_box.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        self.symptom_entry = self._add_labeled_entry(symptom_box, "Симптом", 0)
        self.severity_entry = self._add_labeled_entry(symptom_box, "Тяжесть (1-10)", 1)
        ttk.Button(
            symptom_box,
            text="Записать симптом",
            command=self._handle(
                lambda: self.presenter.record_symptom(
                    self._require_selected_user_id(),
                    self.symptom_entry.get(),
                    self.severity_entry.get(),
                )
            ),
        ).grid(row=2, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(
            symptom_box,
            text="Получить совет",
            command=self._handle(
                lambda: self.presenter.give_advice(
                    self._require_selected_user_id(),
                    self.symptom_entry.get(),
                )
            ),
        ).grid(row=2, column=1, sticky="ew", pady=(8, 0))

        medication_box = ttk.LabelFrame(frame, text="Лекарства", padding=12)
        medication_box.grid(row=0, column=1, sticky="nsew", pady=(0, 8))
        self.med_name_entry = self._add_labeled_entry(medication_box, "Название", 0)
        self.med_dosage_entry = self._add_labeled_entry(medication_box, "Дозировка", 1)
        self.med_schedule_entry = self._add_labeled_entry(medication_box, "Расписание", 2)
        ttk.Button(
            medication_box,
            text="Добавить напоминание",
            command=self._handle(
                lambda: self.presenter.add_medication(
                    self._require_selected_user_id(),
                    self.med_name_entry.get(),
                    self.med_dosage_entry.get(),
                    self.med_schedule_entry.get(),
                )
            ),
        ).grid(row=3, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(
            medication_box,
            text="Показать лекарства",
            command=self._handle(
                lambda: self.presenter.show_medications(self._require_selected_user_id())
            ),
        ).grid(row=3, column=1, sticky="ew", pady=(8, 0))

        self.medications_text = self._build_text_panel(frame, "Список лекарств", 1, 0, 2)

    def _build_clinics_tab(self) -> None:
        top = ttk.Frame(self.clinics_tab)
        top.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(top, text="Район").pack(side=tk.LEFT)
        self.area_combo = ttk.Combobox(top, textvariable=self.area_var, state="readonly", width=24)
        self.area_combo.pack(side=tk.LEFT, padx=8)
        ttk.Button(top, text="Показать клиники", command=self._handle(self._load_clinics)).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(top, text="Показать врачей", command=self._handle(self._load_doctors)).pack(
            side=tk.LEFT
        )

        middle = ttk.Frame(self.clinics_tab)
        middle.pack(fill=tk.BOTH, expand=True)
        middle.columnconfigure(0, weight=1)
        middle.columnconfigure(1, weight=1)
        middle.rowconfigure(0, weight=1)

        self.clinics_text = self._build_text_panel(middle, "Клиники", 0, 0, 1)
        self.doctors_text = self._build_text_panel(middle, "Врачи", 0, 1, 1)

        consult = ttk.LabelFrame(self.clinics_tab, text="Консультация с врачом", padding=12)
        consult.pack(fill=tk.X, pady=(12, 0))
        ttk.Label(consult, text="Врач").grid(row=0, column=0, sticky=tk.W)
        self.doctor_combo = ttk.Combobox(
            consult, textvariable=self.doctor_var, state="readonly", width=48
        )
        self.doctor_combo.grid(row=0, column=1, sticky="ew", padx=8)
        consult.columnconfigure(1, weight=1)
        self.question_entry = self._add_labeled_entry(consult, "Вопрос", 1)
        ttk.Button(
            consult,
            text="Получить консультацию",
            command=self._handle(self._consult_selected_doctor),
        ).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))

    def _build_status_tab(self) -> None:
        self.status_text = tk.Text(self.status_tab, wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True)

    def _add_labeled_entry(self, parent: ttk.Widget, label: str, row: int) -> ttk.Entry:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, pady=4, padx=(0, 8))
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=1, sticky="ew", pady=4)
        parent.columnconfigure(1, weight=1)
        return entry

    def _build_text_panel(
        self, parent: ttk.Widget, title: str, row: int, column: int, columnspan: int
    ) -> tk.Text:
        panel = ttk.LabelFrame(parent, text=title, padding=8)
        panel.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=4, pady=4)
        parent.rowconfigure(row, weight=1)
        parent.columnconfigure(column, weight=1)
        text = tk.Text(panel, wrap=tk.WORD, state=tk.DISABLED, height=14)
        text.pack(fill=tk.BOTH, expand=True)
        return text

    def _handle(self, callback):
        def wrapped() -> None:
            try:
                callback()
            except ValueError as error:
                messagebox.showerror("Ошибка ввода", str(error))
            except MedicalAssistantError as error:
                messagebox.showerror("Ошибка ассистента", str(error))
            except Exception as error:
                messagebox.showerror("Системная ошибка", str(error))

        return wrapped

    def _set_text(self, widget: tk.Text, text: str) -> None:
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)

    def _on_user_selected(self, _event=None) -> None:
        user_id = self.get_selected_user_id()
        if user_id is not None:
            self.presenter.show_history(user_id)

    def _load_clinics(self) -> None:
        self.presenter.show_clinics(self.area_var.get())

    def _load_doctors(self) -> None:
        self.presenter.show_doctors(self.area_var.get())

    def _consult_selected_doctor(self) -> None:
        doctor_id = self._doctor_map.get(self.doctor_var.get())
        if doctor_id is None:
            raise ValueError("Сначала выберите врача из списка")
        self.presenter.consult_doctor(
            self._require_selected_user_id(), doctor_id, self.question_entry.get()
        )

    def _require_selected_user_id(self) -> int:
        user_id = self.get_selected_user_id()
        if user_id is None:
            raise ValueError("Сначала выберите пользователя на вкладке 'Пользователи'")
        return user_id

    def get_selected_user_id(self) -> int | None:
        selection = self.users_tree.selection()
        if not selection:
            return None
        values = self.users_tree.item(selection[0], "values")
        return int(values[0]) if values else None

    def show_users(self, users: list[dict]) -> None:
        current_selection = self.get_selected_user_id()
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        selected_item = None
        for user in users:
            item = self.users_tree.insert(
                "",
                tk.END,
                values=(
                    user["id"],
                    user["name"],
                    user["phone"],
                    user["age"],
                    user["symptoms_count"],
                    user["medications_count"],
                    user["recommendations_count"],
                ),
            )
            if current_selection == user["id"]:
                selected_item = item
        if not selected_item and self.users_tree.get_children():
            selected_item = self.users_tree.get_children()[0]
        if selected_item:
            self.users_tree.selection_set(selected_item)

    def show_history(self, history: dict) -> None:
        user = history["user"]
        lines = [f"Пациент: {user.name} | ID: {user.id} | Возраст: {user.age}", ""]
        lines.append(f"Симптомы ({len(history['symptoms'])}):")
        if history["symptoms"]:
            lines.extend(
                f"  {index}. {item}" for index, item in enumerate(history["symptoms"], start=1)
            )
        else:
            lines.append("  Нет записанных симптомов")
        lines.append("")
        lines.append(f"Лекарства ({len(history['medications'])}):")
        if history["medications"]:
            lines.extend(
                f"  {index}. {item}" for index, item in enumerate(history["medications"], start=1)
            )
        else:
            lines.append("  Нет назначенных лекарств")
        lines.append("")
        lines.append(f"Рекомендации ({len(history['recommendations'])}):")
        if history["recommendations"]:
            lines.extend(
                f"  {index}. {item}"
                for index, item in enumerate(history["recommendations"], start=1)
            )
        else:
            lines.append("  Нет рекомендаций")
        self._set_text(self.history_text, "\n".join(lines))

    def show_medications(self, medications: list) -> None:
        if not medications:
            self._set_text(self.medications_text, "Лекарства не назначены")
            return
        self._set_text(
            self.medications_text,
            "\n".join(f"{index}. {item}" for index, item in enumerate(medications, start=1)),
        )

    def show_areas(self, areas: list[str]) -> None:
        self.area_combo["values"] = areas
        if areas and not self.area_var.get():
            self.area_var.set(areas[0])

    def show_clinics(self, clinics: list[dict]) -> None:
        if not clinics:
            self._set_text(self.clinics_text, "В выбранном районе клиники не найдены")
            return
        lines = []
        for item in clinics:
            clinic = item["clinic"]
            doctors = item["doctors"]
            lines.append(f"{clinic.get('name')}")
            lines.append(f"  Адрес: {clinic.get('address')}")
            lines.append(f"  Район: {clinic.get('area')}")
            if doctors:
                lines.append(
                    "  Врачи: "
                    + ", ".join(f"{doctor.name} ({doctor.specialization})" for doctor in doctors)
                )
            lines.append("")
        self._set_text(self.clinics_text, "\n".join(lines).strip())

    def show_doctors(self, doctors: list) -> None:
        if not doctors:
            self._doctor_map.clear()
            self.doctor_combo["values"] = []
            self._set_text(self.doctors_text, "В выбранном районе врачи не найдены")
            return
        labels = []
        self._doctor_map.clear()
        lines = []
        for doctor in doctors:
            label = f"{doctor.name} | {doctor.specialization} | {doctor.clinic}"
            labels.append(label)
            self._doctor_map[label] = doctor.id
            lines.append(f"{label} | тел. {doctor.phone} | ID: {doctor.id}")
        self.doctor_combo["values"] = labels
        self.doctor_var.set(labels[0])
        self._set_text(self.doctors_text, "\n".join(lines))

    def show_status(self, status: dict) -> None:
        lines = [
            f"Ассистент: {status['assistant_name']}",
            f"Пользователей: {len(status['users'])}",
            f"Врачей: {len(status['doctors'])}",
            f"Районов обслуживания: {', '.join(status['areas']) if status['areas'] else 'нет'}",
            "",
            "Пользователи:",
        ]
        if status["users"]:
            lines.extend(f"  {index}. {user}" for index, user in enumerate(status["users"], start=1))
        else:
            lines.append("  Нет пользователей")
        lines.append("")
        lines.append("Врачи:")
        if status["doctors"]:
            lines.extend(
                f"  {index}. {doctor}" for index, doctor in enumerate(status["doctors"], start=1)
            )
        else:
            lines.append("  Нет врачей")
        self._set_text(self.status_text, "\n".join(lines))

    def set_status_message(self, message: str) -> None:
        self.status_var.set(message)

    def _on_close(self) -> None:
        if messagebox.askyesno("Выход", "Сохранить данные перед выходом?"):
            self.presenter.save()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def run_gui(app: MedicalAssistantApp) -> None:
    gui = MedicalAssistantGUI(app)
    gui.run()
