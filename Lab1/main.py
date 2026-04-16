import os
import sys

from assistant.medical_assistant import MedicalAssistant
from exceptions import MedicalAssistantError

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def print_header() -> None:
    print("\n" + "=" * 50)
    print("      ПЕРСОНАЛЬНЫЙ МЕДИЦИНСКИЙ АССИСТЕНТ      ")
    print("=" * 50)


def print_menu() -> None:
    print_header()
    print("\n--- ПОЛЬЗОВАТЕЛИ ---")
    print("1. Зарегистрировать пользователя")
    print("2. Показать всех пользователей")
    print("3. Показать медицинскую историю пользователя")

    print("\n--- МЕДИЦИНСКИЕ ОПЕРАЦИИ ---")
    print("4. Записать симптом")
    print("5. Получить медицинский совет")
    print("6. Добавить напоминание о лекарстве")
    print("7. Показать список лекарств")

    print("\n--- КЛИНИКИ И КОНСУЛЬТАЦИИ ---")
    print("8. Найти ближайшую клинику")
    print("9. Получить консультацию врача")

    print("\n--- СИСТЕМА ---")
    print("10. Показать статус системы")
    print("11. Сохранить и выйти")
    print("0. Выход")


def print_areas(assistant: MedicalAssistant) -> list[str]:
    areas = assistant.get_all_areas()
    print("\n--- ДОСТУПНЫЕ РАЙОНЫ ---")
    for index, area in enumerate(areas, start=1):
        print(f"{index}. {area}")
    return areas


def show_users(assistant: MedicalAssistant) -> None:
    if not assistant.users:
        print("Нет зарегистрированных пользователей")
        return

    print("\n--- ВСЕ ПОЛЬЗОВАТЕЛИ ---")
    for user in assistant.users:
        print(f"ID: {user.id} | {user.name} | {user.phone} | Возраст: {user.age}")
        print(
            f"  Симптомов: {len(user.medical_history.symptoms)}, "
            f"лекарств: {len(user.medical_history.medications)}, "
            f"рекомендаций: {len(user.medical_history.recommendations)}",
        )


def show_medical_history(assistant: MedicalAssistant, user_id: int) -> None:
    user = next((item for item in assistant.users if item.id == user_id), None)
    if user is None:
        print(f"Пользователь с ID {user_id} не найден")
        return

    print(f"\n--- МЕДИЦИНСКАЯ ИСТОРИЯ: {user.name} ---")

    print(f"\nСИМПТОМЫ ({len(user.medical_history.symptoms)}):")
    if user.medical_history.symptoms:
        for index, symptom in enumerate(user.medical_history.symptoms, start=1):
            print(f"{index}. {symptom}")
    else:
        print("Нет записанных симптомов")

    print(f"\nЛЕКАРСТВА ({len(user.medical_history.medications)}):")
    if user.medical_history.medications:
        for index, medication in enumerate(user.medical_history.medications, start=1):
            print(f"{index}. {medication}")
    else:
        print("Нет назначенных лекарств")

    print(f"\nРЕКОМЕНДАЦИИ ({len(user.medical_history.recommendations)}):")
    if user.medical_history.recommendations:
        for index, recommendation in enumerate(
            user.medical_history.recommendations,
            start=1,
        ):
            print(f"{index}. {recommendation}")
    else:
        print("Нет рекомендаций")


def choose_area(assistant: MedicalAssistant) -> str | None:
    areas = print_areas(assistant)
    if not areas:
        print("Нет доступных районов")
        return None

    number = int(input("Выберите номер района: "))
    if not 1 <= number <= len(areas):
        raise ValueError("Неверный номер района")
    return areas[number - 1]


def consult_with_doctor(assistant: MedicalAssistant, user_id: int) -> None:
    selected_area = choose_area(assistant)
    if selected_area is None:
        return

    clinics = assistant.find_clinics_by_area(selected_area)
    if not clinics:
        print(f"В районе '{selected_area}' нет клиник")
        return

    numbered_doctors = []
    print(f"\n--- ДОСТУПНЫЕ ВРАЧИ В РАЙОНЕ '{selected_area.upper()}' ---")
    for clinic in clinics:
        print(f"\n{clinic.get('name')}")
        print(f"Адрес: {clinic.get('address')}")
        for doctor_id in clinic.get("doctor_ids", []):
            doctor = next(
                (item for item in assistant.doctors if item.id == doctor_id),
                None,
            )
            if doctor is None:
                continue
            numbered_doctors.append(doctor)
            print(
                f"{len(numbered_doctors)}. {doctor.name} "
                f"({doctor.specialization})",
            )

    if not numbered_doctors:
        print("В этом районе нет доступных врачей")
        return

    doctor_number = int(input("\nВыберите номер врача: "))
    if not 1 <= doctor_number <= len(numbered_doctors):
        raise ValueError("Неверный номер врача")

    question = input("Ваш вопрос к врачу: ")
    response = assistant.consult_doctor(
        numbered_doctors[doctor_number - 1].id,
        user_id,
        question,
    )
    print(f"\n{response}")


def main() -> None:
    assistant = MedicalAssistant("MedAssist", DATA_FILE)

    if not assistant.users:
        assistant.register_user("Иван Петров", "+7(123)456-78-90", 35)
        assistant.register_user("Мария Иванова", "+7(098)765-43-21", 28)

    while True:
        print_menu()
        choice = input("\nВыберите действие > ").strip()

        try:
            if choice == "0":
                print("Выход из программы. До свидания!")
                sys.exit()

            if choice == "1":
                name = input("Имя пользователя: ")
                phone = input("Телефон: ")
                age = int(input("Возраст: "))
                user_id = assistant.register_user(name, phone, age)
                print(f"[OK] Пользователь зарегистрирован с ID: {user_id}")

            elif choice == "2":
                show_users(assistant)

            elif choice == "3":
                show_medical_history(assistant, int(input("ID пользователя: ")))

            elif choice == "4":
                user_id = int(input("ID пользователя: "))
                symptom = input("Название симптома: ")
                severity = int(input("Тяжесть (1-10): "))
                print(assistant.record_symptom(user_id, symptom, severity))

            elif choice == "5":
                user_id = int(input("ID пользователя: "))
                symptom = input("На какой симптом нужен совет? ")
                print(assistant.give_advice(user_id, symptom))

            elif choice == "6":
                user_id = int(input("ID пользователя: "))
                med_name = input("Название лекарства: ")
                dosage = input("Дозировка: ")
                schedule = input("Расписание приема: ")
                print(
                    assistant.add_medication_reminder(
                        user_id,
                        med_name,
                        dosage,
                        schedule,
                    ),
                )

            elif choice == "7":
                medications = assistant.get_medication_list(
                    int(input("ID пользователя: ")),
                )
                if not medications:
                    print("Лекарства не назначены")
                for index, medication in enumerate(medications, start=1):
                    print(f"{index}. {medication}")

            elif choice == "8":
                selected_area = choose_area(assistant)
                if selected_area is None:
                    continue
                clinics = assistant.find_clinics_by_area(selected_area)
                if not clinics:
                    print("Клиники не найдены")
                    continue
                print(f"\n--- КЛИНИКИ В РАЙОНЕ '{selected_area.upper()}' ---")
                for clinic in clinics:
                    print(f"{clinic.get('name')} | {clinic.get('address')}")

            elif choice == "9":
                consult_with_doctor(
                    assistant,
                    int(input("ID пользователя: ")),
                )

            elif choice == "10":
                print("\n--- СТАТУС СИСТЕМЫ ---")
                print(assistant.get_status_report())

            elif choice == "11":
                assistant.shutdown()
                print("[OK] Данные сохранены. Выход.")
                sys.exit()

            else:
                print("[ОШИБКА] Неверный выбор")

        except ValueError as error:
            assistant.handle_error(error)
            print(f"\n[ОШИБКА ВВОДА] {error}")
        except MedicalAssistantError as error:
            assistant.handle_error(error)
            print(f"\n[ОШИБКА АССИСТЕНТА] {error}")
        except Exception as error:
            assistant.handle_error(error)
            print(f"\n[СИСТЕМНАЯ ОШИБКА] {error}")


if __name__ == "__main__":
    main()
