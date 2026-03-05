from __future__ import annotations

import random
from pathlib import Path
from typing import List
from xml.dom import minidom

# ====== Настройки ======
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "demo_xml"   # Lab2/demo_xml
FILES = [
    ("clients_demo_1.xml", 60),
    ("clients_demo_2.xml", 60),
    ("clients_demo_3.xml", 60),
]
SEED = 42  # чтобы результаты были стабильные


# ====== Данные для генерации ======
LAST_NAMES = [
    "Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов", "Васильев", "Новиков", "Фёдоров", "Морозов",
    "Волков", "Алексеев", "Лебедев", "Семёнов", "Егоров", "Павлов", "Козлов", "Степанов", "Николаев", "Орлов",
    "Андреев", "Макаров", "Никитин", "Захаров", "Зайцев", "Соловьёв", "Борисов", "Яковлев", "Григорьев", "Романов",
]
FIRST_NAMES = [
    "Иван", "Пётр", "Алексей", "Дмитрий", "Андрей", "Сергей", "Михаил", "Никита", "Кирилл", "Павел",
    "Егор", "Максим", "Олег", "Владимир", "Антон", "Роман", "Виктор", "Юрий", "Константин", "Артур",
    "Мария", "Анна", "Екатерина", "Алина", "Виктория", "Дарья", "Полина", "София", "Ксения", "Татьяна",
]
MIDDLE_NAMES = [
    "Иванович", "Петрович", "Алексеевич", "Дмитриевич", "Андреевич", "Сергеевич", "Михайлович", "Никитич",
    "Кириллович", "Павлович", "Егорович", "Максимович", "Олегович", "Владимирович", "Антонович", "Романович",
    "Викторович", "Юрьевич", "Константинович", "Артурович",
    "Ивановна", "Петровна", "Алексеевна", "Дмитриевна", "Андреевна", "Сергеевна", "Михайловна", "Никитична",
    "Кирилловна", "Павловна", "Егоровна", "Максимовна", "Олеговна", "Владимировна", "Антоновна", "Романовна",
    "Викторовна", "Юрьевна", "Константиновна", "Артуровна",
]
CITIES = [
    "Минск", "Гродно", "Брест", "Витебск", "Гомель", "Могилёв",
    "Москва", "Санкт-Петербург", "Казань", "Екатеринбург", "Новосибирск",
    "Киев", "Львов", "Одесса",
]
STREETS = [
    "Ленина", "Победы", "Советская", "Парковая", "Школьная", "Центральная", "Мира", "Садовая", "Новая", "Зелёная",
    "Гагарина", "Пушкина", "Космонавтов", "Октябрьская", "Молодёжная",
]


def _make_fio(rng: random.Random) -> str:
    ln = rng.choice(LAST_NAMES)
    fn = rng.choice(FIRST_NAMES)
    mn = rng.choice(MIDDLE_NAMES)
    return f"{ln} {fn} {mn}"


def _make_address(rng: random.Random) -> str:
    city = rng.choice(CITIES)
    street = rng.choice(STREETS)
    house = rng.randint(1, 180)
    apt = rng.randint(1, 250)
    return f"{city}, ул. {street}, д. {house}, кв. {apt}"


def _digits(n: int, rng: random.Random) -> str:
    return "".join(str(rng.randint(0, 9)) for _ in range(n))


def _make_account(rng: random.Random) -> str:
    # Осмысленно: 20 цифр (часто так делают для "номер счета")
    # Можно представить как "40817..." но это не обязано быть реальным банковским форматом
    return "40817" + _digits(15, rng)


def _make_mobile(rng: random.Random) -> str:
    # Осмысленно: +375 (BY) + 9 цифр
    return "+375" + _digits(9, rng)


def _make_home(rng: random.Random) -> str:
    # Осмысленно: городской как 7-значный
    return _digits(7, rng)


def generate_records(count: int, rng: random.Random) -> List[dict]:
    # Гарантируем уникальность по ключу (fio + account + phones)
    seen = set()
    out: List[dict] = []

    while len(out) < count:
        fio = _make_fio(rng)
        acc = _make_account(rng)
        addr = _make_address(rng)
        mob = _make_mobile(rng)
        home = _make_home(rng)

        key = (fio, acc, mob, home)
        if key in seen:
            continue
        seen.add(key)

        out.append({
            "fio": fio,
            "account_number": acc,
            "registration_address": addr,
            "mobile_phone": mob,
            "home_phone": home,
        })

    return out


def export_xml(records: List[dict], file_path: Path) -> None:
    doc = minidom.Document()
    root = doc.createElement("clients")
    doc.appendChild(root)

    def add_text(parent, tag: str, text: str):
        el = doc.createElement(tag)
        el.appendChild(doc.createTextNode(text or ""))
        parent.appendChild(el)

    for r in records:
        client = doc.createElement("client")
        root.appendChild(client)
        add_text(client, "fio", r["fio"])
        add_text(client, "account_number", r["account_number"])
        add_text(client, "registration_address", r["registration_address"])
        add_text(client, "mobile_phone", r["mobile_phone"])
        add_text(client, "home_phone", r["home_phone"])

    file_path.parent.mkdir(parents=True, exist_ok=True)
    xml_bytes = doc.toprettyxml(indent="  ", encoding="utf-8")
    file_path.write_bytes(xml_bytes)


def main() -> None:
    rng = random.Random(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for filename, n in FILES:
        records = generate_records(n, rng)
        path = OUTPUT_DIR / filename
        export_xml(records, path)
        print(f"Generated {n} records -> {path}")


if __name__ == "__main__":
    main()