from typing import List, Optional
from app.db.database import get_connection
from app.core.models import PhoneUnit


def get_phone_units(search: str = "", status: str = "",
                    limit: int = 50, offset: int = 0) -> List[PhoneUnit]:
    conn = get_connection()
    query = """
        SELECT pu.* FROM phone_units pu
        LEFT JOIN products p ON pu.product_id = p.id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (pu.imei LIKE ? OR p.name LIKE ?)"
        like = f"%{search}%"
        params += [like, like]

    if status:
        query += " AND pu.status = ?"
        params.append(status)

    query += " ORDER BY pu.id DESC LIMIT ? OFFSET ?"
    params += [limit, offset]

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_unit(r) for r in rows]


def count_phone_units(search: str = "", status: str = "") -> int:
    conn = get_connection()
    query = """
        SELECT COUNT(*) FROM phone_units pu
        LEFT JOIN products p ON pu.product_id = p.id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (pu.imei LIKE ? OR p.name LIKE ?)"
        like = f"%{search}%"
        params += [like, like]

    if status:
        query += " AND pu.status = ?"
        params.append(status)

    total = conn.execute(query, params).fetchone()[0]
    conn.close()
    return total


def get_phone_unit(uid: int) -> Optional[PhoneUnit]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM phone_units WHERE id = ?", (uid,)).fetchone()
    conn.close()
    return _row_to_unit(row) if row else None


def add_phone_unit(u: PhoneUnit) -> int:
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO phone_units
        (product_id, imei, buying_price, selling_price, status, supplier_id, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (u.product_id, u.imei, u.buying_price, u.selling_price,
          u.status, u.supplier_id, u.notes))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_phone_unit(u: PhoneUnit) -> None:
    conn = get_connection()
    conn.execute("""
        UPDATE phone_units SET
            product_id = ?, imei = ?, buying_price = ?, selling_price = ?,
            status = ?, supplier_id = ?, notes = ?
        WHERE id = ?
    """, (u.product_id, u.imei, u.buying_price, u.selling_price,
          u.status, u.supplier_id, u.notes, u.id))
    conn.commit()
    conn.close()


def delete_phone_unit(uid: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM phone_units WHERE id = ?", (uid,))
    conn.commit()
    conn.close()


def imei_exists(imei: str, exclude_id: Optional[int] = None) -> bool:
    """Check if an IMEI is already used (for validation)."""
    if not imei.strip():
        return False
    conn = get_connection()
    if exclude_id:
        row = conn.execute(
            "SELECT id FROM phone_units WHERE imei = ? AND id != ?",
            (imei, exclude_id)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT id FROM phone_units WHERE imei = ?", (imei,)
        ).fetchone()
    conn.close()
    return row is not None


def _row_to_unit(r) -> PhoneUnit:
    return PhoneUnit(
        id=r["id"], product_id=r["product_id"], imei=r["imei"] or "",
        buying_price=r["buying_price"], selling_price=r["selling_price"],
        status=r["status"] or "in_stock", supplier_id=r["supplier_id"],
        notes=r["notes"] or ""
    )