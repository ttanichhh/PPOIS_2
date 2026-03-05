import sqlite3
from pathlib import Path
from typing import List, Tuple

from Lab2.app.model.entities import ClientRecord
from Lab2.app.model.search import SearchCriteria, CriteriaMode


class ClientRepository:
    """
    SQLite repository.
    DB is stored inside Lab2/clients.sqlite3 (absolute path),
    so data is saved regardless of where you run the app from.
    """
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
                    fio TEXT NOT NULL,
                    account_number TEXT NOT NULL,
                    registration_address TEXT NOT NULL,
                    mobile_phone TEXT NOT NULL,
                    home_phone TEXT NOT NULL
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clients_fio ON clients(fio);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clients_account ON clients(account_number);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clients_mobile ON clients(mobile_phone);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clients_home ON clients(home_phone);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clients_address ON clients(registration_address);")

    # ---------- CRUD ----------
    def add(self, r: ClientRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO clients
                   (fio, account_number, registration_address, mobile_phone, home_phone)
                   VALUES (?, ?, ?, ?, ?)""",
                (r.fio, r.account_number, r.registration_address, r.mobile_phone, r.home_phone)
            )

    def add_many(self, records: List[ClientRecord]) -> None:
        if not records:
            return
        with self._connect() as conn:
            conn.executemany(
                """INSERT INTO clients
                   (fio, account_number, registration_address, mobile_phone, home_phone)
                   VALUES (?, ?, ?, ?, ?)""",
                [(r.fio, r.account_number, r.registration_address, r.mobile_phone, r.home_phone) for r in records]
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
                """SELECT fio, account_number, registration_address, mobile_phone, home_phone
                   FROM clients
                   ORDER BY fio, account_number
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
            SELECT fio, account_number, registration_address, mobile_phone, home_phone
            FROM clients
        """
        base_count = "SELECT COUNT(*) AS c FROM clients"

        with self._connect() as conn:
            total = conn.execute(f"{base_count} {where_sql}", params).fetchone()["c"]
            rows = conn.execute(
                f"""{base_select} {where_sql}
                    ORDER BY fio, account_number
                    LIMIT ? OFFSET ?""",
                (*params, page_size, offset)
            ).fetchall()

        records = [ClientRecord(**dict(row)) for row in rows]
        return records, int(total)

    # ---------- Delete ----------
    def delete_by_criteria(self, criteria: SearchCriteria):
        where_sql, params = self._build_where(criteria)

        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT fio, account_number, registration_address, mobile_phone, home_phone
                FROM clients
                {where_sql}
                """,
                params
            ).fetchall()

            records = [ClientRecord(**dict(row)) for row in rows]

            conn.execute(f"DELETE FROM clients {where_sql}", params)

        return records

    # ---------- WHERE builder ----------
    @staticmethod
    def _norm_phone(s: str) -> str:
        return "".join(ch for ch in (s or "") if ch.isdigit())

    @staticmethod
    def _digits_expr(col: str) -> str:
        return (
            f"REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE({col}, '+', ''), '(', ''), ')', ''), '-', ''), ' ', ''), '.', '')"
        )

    def _build_where(self, c: SearchCriteria) -> Tuple[str, tuple]:
        # Mode 1: mobile OR last name
        if c.mode == CriteriaMode.PHONE_OR_LASTNAME:
            phone = (c.phone or "").strip()
            last = (c.last_name or "").strip()

            clauses = []
            params: list = []

            # телефон
            if phone:
                p = self._norm_phone(phone)
                if not p:
                    return "WHERE 1=0", ()
                mob = self._digits_expr("mobile_phone")
                clauses.append(f"({mob} = ?)")
                params.append(p)

            # фамилия: точное совпадение, берём 1-е слово из fio
            if last:
                last_sql = (
                    "LOWER(TRIM(SUBSTR(fio, 1, "
                    "CASE WHEN INSTR(fio, ' ') = 0 THEN LENGTH(fio) ELSE INSTR(fio, ' ') - 1 END"
                    ")))"
                )
                clauses.append(f"({last_sql} = LOWER(?))")
                params.append(last)

            if not clauses:
                return "WHERE 1=0", ()

            # ВАЖНО: OR между телефоном и фамилией
            return "WHERE (" + " OR ".join(clauses) + ")", tuple(params)

        # Mode 2: account OR address (exact)
        if c.mode == CriteriaMode.ACCOUNT_OR_ADDRESS:
            acc = (c.account_number or "").strip()
            addr = (c.address_part or "").strip()

            clauses = []
            params: list = []

            # СЧЁТ: по части (LIKE)
            if acc:
                clauses.append("(account_number LIKE ?)")
                params.append(f"%{acc}%")

            # АДРЕС: по части, без учета регистра
            if addr:
                clauses.append("(LOWER(registration_address) LIKE LOWER(?))")
                params.append(f"%{addr}%")

            if not clauses:
                return "WHERE 1=0", ()

            # ИЛИ между заполненными условиями:
            return "WHERE (" + " OR ".join(clauses) + ")", tuple(params)

        # Mode 3: fio AND (mobile OR home) exact phone
        if c.mode == CriteriaMode.FIO_AND_DIGITS_IN_PHONE:
            fio = (c.fio_text or "").strip()
            phone = (c.phone_exact or "").strip()

            if not fio or not phone:
                return "WHERE 1=0", ()

            p = self._norm_phone(phone)
            if not p:
                return "WHERE 1=0", ()

            fio_sql = "(LOWER(fio) LIKE LOWER(?))"
            params: list = [f"%{fio}%"]

            mob = self._digits_expr("mobile_phone")
            home = self._digits_expr("home_phone")
            phone_sql = f"({mob} = ? OR {home} = ?)"
            params.extend([p, p])

            return f"WHERE {fio_sql} AND {phone_sql}", tuple(params)

        return "WHERE 1=0", ()