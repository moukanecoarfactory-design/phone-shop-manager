from app.db.database import get_connection


def get_today_sales_summary() -> dict:
    """Return {total, profit, count} for today's sales."""
    conn = get_connection()
    row = conn.execute("""
        SELECT
            COALESCE(SUM(total), 0) AS total,
            COALESCE(SUM(profit), 0) AS profit,
            COUNT(*) AS count
        FROM sales
        WHERE DATE(sale_date) = DATE('now', 'localtime')
    """).fetchone()
    conn.close()
    return {"total": row["total"], "profit": row["profit"], "count": row["count"]}


def get_month_sales_summary() -> dict:
    """Return {total, profit, count} for this month's sales."""
    conn = get_connection()
    row = conn.execute("""
        SELECT
            COALESCE(SUM(total), 0) AS total,
            COALESCE(SUM(profit), 0) AS profit,
            COUNT(*) AS count
        FROM sales
        WHERE strftime('%Y-%m', sale_date) = strftime('%Y-%m', 'now', 'localtime')
    """).fetchone()
    conn.close()
    return {"total": row["total"], "profit": row["profit"], "count": row["count"]}


def get_counts() -> dict:
    """Return counts of products, phones, customers, suppliers."""
    conn = get_connection()
    products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    phones_in_stock = conn.execute(
        "SELECT COUNT(*) FROM phone_units WHERE status = 'in_stock'"
    ).fetchone()[0]
    customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    suppliers = conn.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0]
    low_stock = conn.execute(
        "SELECT COUNT(*) FROM products WHERE quantity <= low_stock_alert"
    ).fetchone()[0]
    conn.close()
    return {
        "products": products,
        "phones_in_stock": phones_in_stock,
        "customers": customers,
        "suppliers": suppliers,
        "low_stock": low_stock,
    }


def get_low_stock_products(limit: int = 10) -> list:
    """Return products at or below their low stock alert."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT id, name, brand, quantity, low_stock_alert
        FROM products
        WHERE quantity <= low_stock_alert
        ORDER BY (quantity - low_stock_alert) ASC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_top_selling_products(limit: int = 5) -> list:
    """Return top-selling products this month."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.id, p.name, p.brand,
               SUM(si.quantity) AS qty_sold,
               SUM(si.quantity * si.unit_price) AS revenue
        FROM sale_items si
        JOIN products p ON si.product_id = p.id
        JOIN sales s ON si.sale_id = s.id
        WHERE strftime('%Y-%m', s.sale_date) = strftime('%Y-%m', 'now', 'localtime')
        GROUP BY p.id
        ORDER BY qty_sold DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]