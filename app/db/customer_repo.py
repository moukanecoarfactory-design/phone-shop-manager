from typing import List, Optional
from app.db.database import get_connection
from app.core.models import Customer


def get_customers(search: str = "", limit: int = 50, offset: int = 0) -> List[Customer]:
    conn = get_connection()
    query = "SELECT * FROM customers WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR phone LIKE ?)"
        like = f"%{search}%"
        params += [like, like]

    query += " ORDER BY name LIMIT ? OFFSET ?"
    params += [limit, offset]

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_customer(r) for r in rows]


def count_customers(search: str = "") -> int:
    conn = get_connection()
    query = "SELECT COUNT(*) FROM customers WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR phone LIKE ?)"
        like = f"%{search}%"
        params += [like, like]

    total = conn.execute(query, params).fetchone()[0]
    conn.close()
    return total


def get_customer(cid: int) -> Optional[Customer]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM customers WHERE id = ?", (cid,)).fetchone()
    conn.close()
    return _row_to_customer(row) if row else None


def add_customer(c: Customer) -> int:
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO customers (name, phone, address, notes)
        VALUES (?, ?, ?, ?)
    """, (c.name, c.phone, c.address, c.notes))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_customer(c: Customer) -> None:
    conn = get_connection()
    conn.execute("""
        UPDATE customers SET name = ?, phone = ?, address = ?, notes = ?
        WHERE id = ?
    """, (c.name, c.phone, c.address, c.notes, c.id))
    conn.commit()
    conn.close()


def delete_customer(cid: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM customers WHERE id = ?", (cid,))
    conn.commit()
    conn.close()


def _row_to_customer(r) -> Customer:
    return Customer(
        id=r["id"], name=r["name"], phone=r["phone"] or "",
        address=r["address"] or "", notes=r["notes"] or ""
    )