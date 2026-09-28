from typing import List, Optional
from app.db.database import get_connection
from app.core.models import Supplier


def get_suppliers(search: str = "", limit: int = 50, offset: int = 0) -> List[Supplier]:
    conn = get_connection()
    query = "SELECT * FROM suppliers WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR phone LIKE ?)"
        like = f"%{search}%"
        params += [like, like]

    query += " ORDER BY name LIMIT ? OFFSET ?"
    params += [limit, offset]

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_supplier(r) for r in rows]


def count_suppliers(search: str = "") -> int:
    conn = get_connection()
    query = "SELECT COUNT(*) FROM suppliers WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR phone LIKE ?)"
        like = f"%{search}%"
        params += [like, like]

    total = conn.execute(query, params).fetchone()[0]
    conn.close()
    return total


def get_supplier(sid: int) -> Optional[Supplier]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM suppliers WHERE id = ?", (sid,)).fetchone()
    conn.close()
    return _row_to_supplier(row) if row else None


def add_supplier(s: Supplier) -> int:
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO suppliers (name, phone, address, notes)
        VALUES (?, ?, ?, ?)
    """, (s.name, s.phone, s.address, s.notes))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_supplier(s: Supplier) -> None:
    conn = get_connection()
    conn.execute("""
        UPDATE suppliers SET name = ?, phone = ?, address = ?, notes = ?
        WHERE id = ?
    """, (s.name, s.phone, s.address, s.notes, s.id))
    conn.commit()
    conn.close()


def delete_supplier(sid: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM suppliers WHERE id = ?", (sid,))
    conn.commit()
    conn.close()


def _row_to_supplier(r) -> Supplier:
    return Supplier(
        id=r["id"], name=r["name"], phone=r["phone"] or "",
        address=r["address"] or "", notes=r["notes"] or ""
    )