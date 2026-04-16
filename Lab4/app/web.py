from __future__ import annotations

from typing import Any
from flask import Flask, flash, redirect, render_template, request, url_for

from app.application import MedicalAssistantApp
from exceptions import MedicalAssistantError


def create_web_app(app_service: MedicalAssistantApp) -> Flask:
    web_app = Flask(__name__, template_folder="../templates", static_folder="../static")
    web_app.config["SECRET_KEY"] = "med-assistant-lab4"

    def build_context() -> dict[str, Any]:
        users = app_service.get_users()
        areas = app_service.get_areas()
        user_ids = {user["id"] for user in users}

        selected_user_id = request.args.get("user_id", type=int) #request позволяет получить данные запроса.
        if selected_user_id not in user_ids and users:
            selected_user_id = users[0]["id"]

        selected_area = request.args.get("area")
        if selected_area not in areas and areas:
            selected_area = areas[0]

        history = None
        medications = []
        if selected_user_id is not None and users:
            history = app_service.get_user_history(selected_user_id)
            medications = app_service.get_medication_list(selected_user_id)

        clinics = app_service.get_clinics_by_area(selected_area) if selected_area else []
        doctors = app_service.get_doctors_by_area(selected_area) if selected_area else []

        return {
            "users": users,
            "areas": areas,
            "history": history,
            "medications": medications,
            "clinics": clinics,
            "doctors": doctors,
            "selected_user_id": selected_user_id,
            "selected_area": selected_area,
            "status": app_service.get_system_status(),
        }

    def redirect_to_index(user_id: int | None = None, area: str | None = None):
        query: dict[str, Any] = {}
        if user_id is not None:
            query["user_id"] = user_id
        if area:
            query["area"] = area
        return redirect(url_for("index", **query))

    def persist_success(message: str) -> None:
        app_service.save()
        flash(message, "success")

    @web_app.get("/")
    def index():
        return render_template("index.html", **build_context())

    @web_app.post("/users")
    def register_user():
        try:
            user_id = app_service.register_user(
                request.form["name"],
                request.form["phone"],
                int(request.form["age"]),
            )
            persist_success(f"Пользователь зарегистрирован с ID: {user_id}")
            return redirect_to_index(user_id=user_id)
        except (ValueError, MedicalAssistantError) as error:
            flash(str(error), "error")
            return redirect_to_index()

    @web_app.post("/symptoms")
    def record_symptom():
        user_id = request.form.get("user_id", type=int)
        try:
            message = app_service.record_symptom(
                user_id,
                request.form["symptom"],
                int(request.form["severity"]),
            )
            persist_success(message)
        except (ValueError, MedicalAssistantError) as error:
            flash(str(error), "error")
        return redirect_to_index(user_id=user_id)

    @web_app.post("/advice")
    def give_advice():
        user_id = request.form.get("user_id", type=int)
        try:
            advice = app_service.give_advice(user_id, request.form["symptom"])
            persist_success(advice)
        except MedicalAssistantError as error:
            flash(str(error), "error")
        return redirect_to_index(user_id=user_id)

    @web_app.post("/medications")
    def add_medication():
        user_id = request.form.get("user_id", type=int)
        try:
            message = app_service.add_medication_reminder(
                user_id,
                request.form["name"],
                request.form["dosage"],
                request.form["schedule"],
            )
            persist_success(message)
        except MedicalAssistantError as error:
            flash(str(error), "error")
        return redirect_to_index(user_id=user_id)

    @web_app.post("/consultations")
    def consult_doctor():
        user_id = request.form.get("user_id", type=int)
        doctor_id = request.form.get("doctor_id", type=int)
        area = request.form.get("area")
        try:
            answer = app_service.consult_doctor(doctor_id, user_id, request.form["question"])
            persist_success(answer)
        except MedicalAssistantError as error:
            flash(str(error), "error")
        return redirect_to_index(user_id=user_id, area=area)

    @web_app.post("/save")
    def save():
        app_service.save()
        flash("Данные сохранены", "success")
        return redirect_to_index(
            user_id=request.form.get("user_id", type=int),
            area=request.form.get("area"),
        )

    return web_app


def run_web(app_service: MedicalAssistantApp, host: str = "127.0.0.1", port: int = 5000) -> None:
    web_app = create_web_app(app_service)
    web_app.run(host=host, port=port, debug=False)
