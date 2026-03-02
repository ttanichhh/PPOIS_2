import sqlite3
from typing import List, Tuple
from pathlib import Path

from Lab2.app.model.entities import ClientRecord
from Lab2.app.model.search import SearchCriteria, CriteriaMode

class ClientRepository:
    def __init__(self, db_path: str | None = None):
        if db_path is None:
            base_dir = Path(__file__).resolve().parents[2]  # .../PPOIS_2/Lab2
            db_path = str(base_dir / "clients.sqlite3")
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    last_name TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    middle_name TEXT NOT NULL,
                    account_number TEXT NOT NULL,
                    registration_address TEXT NOT NULL,
                    mobile_phone TEXT NOT NULL,
                    home_phone TEXT NOT NULL
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clients_last_name ON clients(last_name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clients_account ON clients(account_number);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clients_mobile ON clients(mobile_phone);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clients_home ON clients(home_phone);")

    # ---------- CRUD ----------
    def add(self, r: ClientRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO clients
                   (last_name, first_name, middle_name, account_number, registration_address, mobile_phone, home_phone)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (r.last_name, r.first_name, r.middle_name, r.account_number,
                 r.registration_address, r.mobile_phone, r.home_phone)
            )

    def add_many(self, records: List[ClientRecord]) -> None:
        if not records:
            return
        with self._connect() as conn:
            conn.executemany(
                """INSERT INTO clients
                   (last_name, first_name, middle_name, account_number, registration_address, mobile_phone, home_phone)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                [(r.last_name, r.first_name, r.middle_name, r.account_number,
                  r.registration_address, r.mobile_phone, r.home_phone) for r in records]
            )

    def clear_all(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM clients")

    # ---------- Paging (all) ----------
    def get_page(self, page_index: int, page_size: int) -> Tuple[List[ClientRecord], int]:
        page_index = max(page_index, 0)
        page_size = max(page_size, 1)
        offset = page_index * page_size

        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) AS c FROM clients").fetchone()["c"]
            rows = conn.execute(
                """SELECT last_name, first_name, middle_name, account_number, registration_address, mobile_phone, home_phone
                   FROM clients
                   ORDER BY last_name, first_name, middle_name, account_number
                   LIMIT ? OFFSET ?""",
                (page_size, offset)
            ).fetchall()

        records = [ClientRecord(**dict(row)) for row in rows]
        return records, int(total)

    # ---------- Search paging ----------
    def search_page(self, criteria: SearchCriteria, page_index: int, page_size: int) -> Tuple[List[ClientRecord], int]:
        where_sql, params = self._build_where(criteria)
        page_index = max(page_index, 0)
        page_size = max(page_size, 1)
        offset = page_index * page_size

        base_select = """
            SELECT last_name, first_name, middle_name, account_number, registration_address, mobile_phone, home_phone
            FROM clients
        """
        base_count = "SELECT COUNT(*) AS c FROM clients"

        with self._connect() as conn:
            total = conn.execute(f"{base_count} {where_sql}", params).fetchone()["c"]
            rows = conn.execute(
                f"""{base_select} {where_sql}
                    ORDER BY last_name, first_name, middle_name, account_number
                    LIMIT ? OFFSET ?""",
                (*params, page_size, offset)
            ).fetchall()

        records = [ClientRecord(**dict(row)) for row in rows]
        return records, int(total)

    # ---------- Delete ----------
    def delete_by_criteria(self, criteria: SearchCriteria) -> int:
        where_sql, params = self._build_where(criteria)
        with self._connect() as conn:
            cur = conn.execute(f"DELETE FROM clients {where_sql}", params)
            return int(cur.rowcount)

    # ---------- WHERE builder ----------

    def _build_where(self, c: SearchCriteria) -> Tuple[str, tuple]:
        # IMPORTANT: условия по ТЗ "или" / "и" реализуем так, как описано в UI.
        # Mode 1: по номеру телефона ИЛИ фамилии (если заполнены оба — удаляем/ищем по (phone OR lastname))
        if c.mode == CriteriaMode.PHONE_OR_LASTNAME:
            phone = (c.phone or "").strip()
            last = (c.last_name or "").strip()

            clauses = []
            params = []

            if phone:
                clauses.append("(mobile_phone LIKE ? OR home_phone LIKE ?)")
                like = f"%{phone}%"
                params.extend([like, like])

            if last:
                clauses.append("(last_name LIKE ?)")
                params.append(f"%{last}%")

            if not clauses:
                # пустые условия -> ничего не находим/не удаляем
                return "WHERE 1=0", ()

            # "ИЛИ" между заполненными условиями:
            return "WHERE (" + " OR ".join(clauses) + ")", tuple(params)

        # Mode 2: по номеру счета ИЛИ адресу
        if c.mode == CriteriaMode.ACCOUNT_OR_ADDRESS:
            acc = (c.account_number or "").strip()
            addr = (c.address_part or "").strip()

            clauses = []
            params = []

            if acc:
                clauses.append("(account_number LIKE ?)")
                params.append(f"%{acc}%")

            if addr:
                clauses.append("(registration_address LIKE ?)")
                params.append(f"%{addr}%")

            if not clauses:
                return "WHERE 1=0", ()

            return "WHERE (" + " OR ".join(clauses) + ")", tuple(params)

        # Mode 3: по ФИО и цифрам в одном из номеров
        if c.mode == CriteriaMode.FIO_AND_DIGITS_IN_PHONE:
            fio_clauses = []
            params = []

            ln = (c.fio_last or "").strip()
            fn = (c.fio_first or "").strip()
            mn = (c.fio_middle or "").strip()
            digits = (c.digits or "").strip()

            if ln:
                fio_clauses.append("(last_name LIKE ?)")
                params.append(f"%{ln}%")
            if fn:
                fio_clauses.append("(first_name LIKE ?)")
                params.append(f"%{fn}%")
            if mn:
                fio_clauses.append("(middle_name LIKE ?)")
                params.append(f"%{mn}%")

            # ФИО может быть частичным, но хотя бы что-то должно быть заполнено:
            if not fio_clauses:
                return "WHERE 1=0", ()

            if not digits:
                return "WHERE 1=0", ()

            # Условие: (любой из заполненных элементов ФИО совпал) AND (digits в одном из номеров)
            fio_sql = "(" + " OR ".join(fio_clauses) + ")"
            phone_sql = "(mobile_phone LIKE ? OR home_phone LIKE ?)"
            like_digits = f"%{digits}%"
            params.extend([like_digits, like_digits])

            return f"WHERE {fio_sql} AND {phone_sql}", tuple(params)

        return "WHERE 1=0", ()