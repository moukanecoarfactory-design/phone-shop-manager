from typing import List, Optional, Dict
from app.db.database import get_connection


def get_sales(search: str = "", limit: int = 50, offset: int = 0) -> List[Dict]:
    """Return sale rows joined with customer name."""
    conn = get_connection()
    query = """
        SELECT s.*, c.name AS customer_name
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (c.name LIKE ? OR CAST(s.id AS TEXT) LIKE ?)"
        like = f"%{search}%"
        params += [like, like]

    query += " ORDER BY s.id DESC LIMIT ? OFFSET ?"
    params += [limit, offset]

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def count_sales(search: str = "") -> int:
    conn = get_connection()
    query = """
        SELECT COUNT(*) FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (c.name LIKE ? OR CAST(s.id AS TEXT) LIKE ?)"
        like = f"%{search}%"
        params += [like, like]

    total = conn.execute(query, params).fetchone()[0]
    conn.close()
    return total


def get_sale(sale_id: int) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("""
        SELECT s.*, c.name AS customer_name
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        WHERE s.id = ?
    """, (sale_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_sale_items(sale_id: int) -> List[Dict]:
    """Return items in a sale, with product or phone_unit info."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT si.*,
               p.name AS product_name,
               p.brand AS product_brand,
               pu.imei AS phone_imei
        FROM sale_items si
        LEFT JOIN products p ON si.product_id = p.id
        LEFT JOIN phone_units pu ON si.phone_unit_id = pu.id
        WHERE si.sale_id = ?
        ORDER BY si.id
    """, (sale_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_sale(sale_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM sales WHERE id = ?", (sale_id,))
    conn.commit()
    conn.close()


def create_sale(customer_id: Optional[int], items: List[Dict],
                notes: str = "") -> int:
    """
    Create a sale from items.
    Each item: {'product_id': x, 'phone_unit_id': y, 'quantity': n,
                'unit_price': p, 'unit_cost': c}
    - For products: reduces product.quantity
    - For phone_units: sets status='sold'
    """
    conn = get_connection()
    cur = conn.cursor()

    total = sum(it["unit_price"] * it["quantity"] for it in items)
    profit = sum((it["unit_price"] - it["unit_cost"]) * it["quantity"]
                 for it in items)

    cur.execute("""
        INSERT INTO sales (customer_id, total, profit, paid, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (customer_id, total, profit, total, notes))
    sale_id = cur.lastrowid

    for it in items:
        cur.execute("""
            INSERT INTO sale_items
            (sale_id, product_id, phone_unit_id, quantity, unit_price, unit_cost)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sale_id, it.get("product_id"), it.get("phone_unit_id"),
              it.get("quantity", 1), it["unit_price"], it["unit_cost"]))

        # Reduce stock for products
        if it.get("product_id"):
            cur.execute("""
                UPDATE products SET quantity = quantity - ?
                WHERE id = ?
            """, (it["quantity"], it["product_id"]))

        # Mark phone unit as sold
        if it.get("phone_unit_id"):
            cur.execute("""
                UPDATE phone_units SET status = 'sold'
                WHERE id = ?
            """, (it["phone_unit_id"],))

    conn.commit()
    conn.close()
    return sale_id