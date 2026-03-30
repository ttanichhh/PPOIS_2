from exceptions import MedicalAssistantError
from app.application import MedicalAssistantApp


def print_header() -> None:
    print("\n" + "=" * 50)
    print("      ПЕРСОНАЛЬНЫЙ МЕДИЦИНСКИЙ АССИСТЕНТ      ")
    print("=" * 50)


def print_menu() -> None:
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
    print("0. Выход без сохранения")


def print_areas(app: MedicalAssistantApp) -> list[str]:
    areas = app.get_areas()
    print("\n--- ДОСТУПНЫЕ РАЙОНЫ ---")
    for index, area in enumerate(areas, start=1):
        print(f"  {index}. {area}")
    return areas


def run_cli(app: MedicalAssistantApp) -> None:
    while True:
        print_menu()
        choice = input("\nВыберите действие > ")

        try:
            if choice == "0":
                print("Выход из программы. До свидания!")
                return

            if choice == "1":
                name = input("Имя пользователя: ")
                phone = input("Телефон: ")
                age = int(input("Возраст: "))
                user_id = app.register_user(name, phone, age)
                print(f"[OK] Пользователь зарегистрирован с ID: {user_id}")
                continue

            if choice == "2":
                users = app.get_users()
                if not users:
                    print("Нет зарегистрированных пользователей")
                    continue
                print("\n--- ВСЕ ПОЛЬЗОВАТЕЛИ ---")
                for user in users:
                    print(
                        f"  ID: {user['id']} | {user['name']} | {user['phone']} | "
                        f"Возраст: {user['age']}"
                    )
                    print(
                        "     "
                        f"Симптомов: {user['symptoms_count']}, "
                        f"Лекарств: {user['medications_count']}, "
                        f"Рекомендаций: {user['recommendations_count']}"
                    )
                continue

            if choice == "3":
                user_id = int(input("ID пользователя: "))
                history = app.get_user_history(user_id)
                print(f"\n--- МЕДИЦИНСКАЯ ИСТОРИЯ: {history['user'].name} ---")
                print(f"\n СИМПТОМЫ ({len(history['symptoms'])}):")
                if history["symptoms"]:
                    for index, symptom in enumerate(history["symptoms"], start=1):
                        print(f"  {index}. {symptom}")
                else:
                    print("  Нет записанных симптомов")
                print(f"\n ЛЕКАРСТВА ({len(history['medications'])}):")
                if history["medications"]:
                    for index, medication in enumerate(history["medications"], start=1):
                        print(f"  {index}. {medication}")
                else:
                    print("  Нет назначенных лекарств")
                print(f"\n РЕКОМЕНДАЦИИ ({len(history['recommendations'])}):")
                if history["recommendations"]:
                    for index, recommendation in enumerate(
                        history["recommendations"], start=1
                    ):
                        print(f"  {index}. {recommendation}")
                else:
                    print("  Нет рекомендаций")
                continue

            if choice == "4":
                user_id = int(input("ID пользователя: "))
                symptom = input("Название симптома: ")
                severity = int(input("Тяжесть (1-10): "))
                print(f"[OK] {app.record_symptom(user_id, symptom, severity)}")
                continue

            if choice == "5":
                user_id = int(input("ID пользователя: "))
                symptom = input("На какой симптом нужен совет? ")
                print(f"\n{app.give_advice(user_id, symptom)}")
                continue

            if choice == "6":
                user_id = int(input("ID пользователя: "))
                med_name = input("Название лекарства: ")
                dosage = input("Дозировка: ")
                schedule = input("Расписание приема: ")
                print(f"[OK] {app.add_medication_reminder(user_id, med_name, dosage, schedule)}")
                continue

            if choice == "7":
                user_id = int(input("ID пользователя: "))
                medications = app.get_medication_list(user_id)
                if medications:
                    print("\n--- ВАШИ ЛЕКАРСТВА ---")
                    for index, medication in enumerate(medications, start=1):
                        print(f"{index}. {medication}")
                else:
                    print("Лекарства не назначены")
                continue

            if choice == "8":
                areas = print_areas(app)
                if not areas:
                    print("Нет доступных районов")
                    continue
                num = int(input("Выберите номер района: "))
                if not (1 <= num <= len(areas)):
                    print("Неверный номер района")
                    continue
                selected_area = areas[num - 1]
                clinics = app.get_clinics_by_area(selected_area)
                print(f"\n--- КЛИНИКИ В РАЙОНЕ '{selected_area.upper()}' ---")
                for item in clinics:
                    clinic = item["clinic"]
                    print(f"\n{clinic.get('name')}")
                    print(f"   Адрес: {clinic.get('address')}")
                    if item["doctors"]:
                        specializations = [doctor.specialization for doctor in item["doctors"]]
                        print(f"   Врачи: {', '.join(specializations)}")
                continue

            if choice == "9":
                user_id = int(input("ID пользователя: "))
                areas = print_areas(app)
                if not areas:
                    print("Нет доступных районов")
                    continue
                area_num = int(input("Выберите номер района: "))
                if not (1 <= area_num <= len(areas)):
                    print("Неверный номер района")
                    continue
                selected_area = areas[area_num - 1]
                doctors = app.get_doctors_by_area(selected_area)
                if not doctors:
                    print("В этом районе нет доступных врачей для записи")
                    continue
                print(f"\n--- ЗАПИСЬ: район '{selected_area.upper()}' ---")
                for index, doctor in enumerate(doctors, start=1):
                    print(
                        f"   {index}. {doctor.name} | {doctor.specialization} | "
                        f"{doctor.clinic} (ID врача: {doctor.id})"
                    )
                doc_num = int(input("\nВыберите номер врача: "))
                if not (1 <= doc_num <= len(doctors)):
                    print("Неверный номер врача")
                    continue
                question = input("Ваш вопрос к врачу: ")
                print(f"\n{app.consult_doctor(doctors[doc_num - 1].id, user_id, question)}")
                continue

            if choice == "10":
                status = app.get_system_status()
                print_header()
                print(f"АССИСТЕНТ: {status['assistant_name']}")
                print("\n[ПОЛЬЗОВАТЕЛИ]")
                if not status["users"]:
                    print("  Нет пользователей")
                for index, user in enumerate(status["users"]):
                    print(f"  [{index}] {user}")
                print("\n[ВРАЧИ]")
                if not status["doctors"]:
                    print("  Нет врачей")
                for index, doctor in enumerate(status["doctors"]):
                    print(f"  [{index}] {doctor}")
                continue

            if choice == "11":
                app.save()
                print("[OK] Данные сохранены. Выход.")
                return

            print("[ОШИБКА] Неверный выбор")
        except ValueError as error:
            print(f"\n[ОШИБКА ВВОДА] Неверный формат данных: {error}")
        except MedicalAssistantError as error:
            print(f"\n[ОШИБКА АССИСТЕНТА] {error}")
        except Exception as error:
            print(f"\n[СИСТЕМНАЯ ОШИБКА] {error}")
