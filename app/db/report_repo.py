from app.db.database import get_connection


def get_sales_summary(date_from: str, date_to: str) -> dict:
    """
    Returns {total, profit, count, avg_sale} for sales between
    date_from and date_to (YYYY-MM-DD strings, inclusive).
    """
    conn = get_connection()
    row = conn.execute("""
        SELECT
            COALESCE(SUM(total), 0) AS total,
            COALESCE(SUM(profit), 0) AS profit,
            COUNT(*) AS count
        FROM sales
        WHERE DATE(sale_date) BETWEEN ? AND ?
    """, (date_from, date_to)).fetchone()
    conn.close()

    count = row["count"]
    avg = row["total"] / count if count else 0
    return {
        "total": row["total"],
        "profit": row["profit"],
        "count": count,
        "avg_sale": avg,
    }


def get_sales_in_range(date_from: str, date_to: str, limit: int = 500) -> list:
    """List all sales in range, newest first."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.id, s.sale_date, s.total, s.profit,
               c.name AS customer_name
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        WHERE DATE(s.sale_date) BETWEEN ? AND ?
        ORDER BY s.id DESC
        LIMIT ?
    """, (date_from, date_to, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_daily_breakdown(date_from: str, date_to: str) -> list:
    """Returns one row per day with total sales and profit."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT DATE(sale_date) AS day,
               SUM(total) AS total,
               SUM(profit) AS profit,
               COUNT(*) AS count
        FROM sales
        WHERE DATE(sale_date) BETWEEN ? AND ?
        GROUP BY DATE(sale_date)
        ORDER BY day DESC
    """, (date_from, date_to)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_top_products_in_range(date_from: str, date_to: str,
                              limit: int = 10) -> list:
    """Top-selling products (accessories) in range."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.name, p.brand,
               SUM(si.quantity) AS qty_sold,
               SUM(si.quantity * si.unit_price) AS revenue,
               SUM(si.quantity * (si.unit_price - si.unit_cost)) AS profit
        FROM sale_items si
        JOIN products p ON si.product_id = p.id
        JOIN sales s ON si.sale_id = s.id
        WHERE DATE(s.sale_date) BETWEEN ? AND ?
        GROUP BY p.id
        ORDER BY qty_sold DESC
        LIMIT ?
    """, (date_from, date_to, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_phones_sold_in_range(date_from: str, date_to: str) -> list:
    """List of phone units sold in range."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT pu.imei, pu.selling_price, pu.buying_price,
               p.name AS product_name, p.brand AS product_brand,
               s.sale_date
        FROM sale_items si
        JOIN phone_units pu ON si.phone_unit_id = pu.id
        JOIN products p ON pu.product_id = p.id
        JOIN sales s ON si.sale_id = s.id
        WHERE DATE(s.sale_date) BETWEEN ? AND ?
        ORDER BY s.sale_date DESC
    """, (date_from, date_to)).fetchall()
    conn.close()
    return [dict(r) for r in rows]