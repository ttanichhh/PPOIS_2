import sys
from typing import List
from Lab1.assistant.medical_assistant import MedicalAssistant
from Lab1.assistant.storage import DataStorage
from Lab1.exceptions import MedicalAssistantError

DATA_FILE = "data.json"


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


def print_areas(assistant: MedicalAssistant) -> List[str]:
    areas = assistant.get_all_areas()

    print("\n--- ДОСТУПНЫЕ РАЙОНЫ ---")
    for i, area in enumerate(areas):
        print(f"  {i + 1}. {area}")
    return areas


def main() -> None:
    # Загрузка данных
    studio = MedicalAssistant("MedAssist", DATA_FILE)

    # Добавим тестовые данные
    if not studio.users:
        studio.register_user("Иван Петров", "+7(123)456-78-90", 35)
        studio.register_user("Мария Иванова", "+7(098)765-43-21", 28)

    while True:
        print_menu()
        choice = input("\nВыберите действие > ")

        try:
            if choice == "0":
                print("Выход из программы. До свидания!")
                sys.exit()

            elif choice == "1":
                name = input("Имя пользователя: ")
                phone = input("Телефон: ")
                age = int(input("Возраст: "))
                user_id = studio.register_user(name, phone, age)
                print(f"[OK] Пользователь зарегистрирован с ID: {user_id}")

            elif choice == "2":  # Показать всех пользователей
                if not studio.users:
                    print("Нет зарегистрированных пользователей")
                else:
                    print("\n--- ВСЕ ПОЛЬЗОВАТЕЛИ ---")
                    for user in studio.users:
                        print(f"  ID: {user.id} | {user.name} | {user.phone} | Возраст: {user.age}")
                        # Показываем количество симптомов и лекарств
                        symptoms_count = len(user.medical_history.symptoms)
                        meds_count = len(user.medical_history.medications)
                        print(f"     Симптомов: {symptoms_count}, Лекарств: {meds_count}")

            elif choice == "3":  # Показать медицинскую историю
                try:
                    user_id = int(input("ID пользователя: "))
                    user = None
                    for u in studio.users:
                        if u.id == user_id:
                            user = u
                            break

                    if not user:
                        print(f"Пользователь с ID {user_id} не найден")
                    else:
                        print(f"\n--- МЕДИЦИНСКАЯ ИСТОРИЯ: {user.name} ---")

                        # Симптомы
                        print(f"\n📋 СИМПТОМЫ ({len(user.medical_history.symptoms)}):")
                        if user.medical_history.symptoms:
                            for i, s in enumerate(user.medical_history.symptoms, 1):
                                print(f"  {i}. {s}")
                        else:
                            print("  Нет записанных симптомов")

                        # Лекарства
                        print(f"\n💊 ЛЕКАРСТВА ({len(user.medical_history.medications)}):")
                        if user.medical_history.medications:
                            for i, m in enumerate(user.medical_history.medications, 1):
                                print(f"  {i}. {m}")
                        else:
                            print("  Нет назначенных лекарств")

                        # Рекомендации
                        print(f"\n📝 РЕКОМЕНДАЦИИ ({len(user.medical_history.recommendations)}):")
                        if user.medical_history.recommendations:
                            for i, r in enumerate(user.medical_history.recommendations, 1):
                                print(f"  {i}. {r}")
                        else:
                            print("  Нет рекомендаций")

                except ValueError:
                    print("Ошибка: введите корректный ID")
                except Exception as e:
                    print(f"Ошибка: {e}")

            elif choice == "4":
                user_id = int(input("ID пользователя: "))
                symptom = input("Название симптома: ")
                severity = int(input("Тяжесть (1-10): "))
                result = studio.record_symptom(user_id, symptom, severity)
                print(f"[OK] {result}")

            elif choice == "5":
                user_id = int(input("ID пользователя: "))
                symptom = input("На какой симптом нужен совет? ")
                advice = studio.give_advice(user_id, symptom)
                print(f"\n{advice}")

            elif choice == "6":
                user_id = int(input("ID пользователя: "))
                med_name = input("Название лекарства: ")
                dosage = input("Дозировка: ")
                schedule = input("Расписание приема: ")
                result = studio.add_medication_reminder(user_id, med_name, dosage, schedule)
                print(f"[OK] {result}")

            elif choice == "7":
                user_id = int(input("ID пользователя: "))
                medications = studio.get_medication_list(user_id)
                if medications:
                    print("\n--- ВАШИ ЛЕКАРСТВА ---")
                    for i, med in enumerate(medications):
                        print(f"{i + 1}. {med}")
                else:
                    print("Лекарства не назначены")

            elif choice == "8":
                areas = print_areas(studio)
                if areas:
                    try:
                        num = int(input("Выберите номер района: "))
                        if 1 <= num <= len(areas):
                            selected_area = areas[num - 1]
                            clinics = studio.find_clinics_by_area(selected_area)
                            print(f"\n--- КЛИНИКИ В РАЙОНЕ '{selected_area.upper()}' ---")
                            for clinic in clinics:
                                print(f"\n🏥 {clinic.get('name')}")
                                print(f"   Адрес: {clinic.get('address')}")
                                # Показываем врачей в этой клинике
                                doctors_in_clinic = [d for d in studio.doctors if d.clinic == clinic.get('name')]
                                if doctors_in_clinic:
                                    specializations = [d.specialization for d in doctors_in_clinic]
                                    print(f"   Врачи: {', '.join(specializations)}")
                        else:
                            print("Неверный номер района")
                    except ValueError:
                        print("Ошибка: введите число")
                else:
                    print("Нет доступных районов")

            elif choice == "9":
                doctor_id = int(input("ID врача которого в выбрали: "))
                user_id = int(input("ID пользователя: "))
                question = input("Ваш вопрос к врачу: ")
                consultation = studio.consult_doctor(doctor_id, user_id, question)
                print(f"\n{consultation}")

            elif choice == "10":
                print_header()
                print(f"АССИСТЕНТ: {studio.name}")

                print("\n[ПОЛЬЗОВАТЕЛИ]")
                if not studio.users:
                    print("  Нет пользователей")
                for i, u in enumerate(studio.users):
                    print(f"  [{i}] {u}")

                print("\n[ВРАЧИ]")
                if not studio.doctors:
                    print("  Нет врачей")
                for i, d in enumerate(studio.doctors):
                    print(f"  [{i}] {d}")

            elif choice == "11":
                # Сохранение данных
                DataStorage.save_data(DATA_FILE, studio.users)
                print("[OK] Данные сохранены. Выход.")
                sys.exit()

            else:
                print("[ОШИБКА] Неверный выбор")

        except ValueError as ve:
            print(f"\n[ОШИБКА ВВОДА] Неверный формат данных: {ve}")
        except MedicalAssistantError as me:
            print(f"\n[ОШИБКА АССИСТЕНТА] {me}")
        except Exception as e:
            print(f"\n[СИСТЕМНАЯ ОШИБКА] {e}")


if __name__ == "__main__":
    main()