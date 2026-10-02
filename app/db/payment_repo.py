"""
Payment repository — tracks customer payments and debts.
"""
from typing import List, Optional, Dict
from app.db.database import get_connection


# ============================================================
# PAYMENTS
# ============================================================

def add_payment(customer_id: int, amount: float,
                sale_id: Optional[int] = None,
                notes: str = "") -> int:
    """Record a payment from a customer."""
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO payments (customer_id, sale_id, amount, notes)
        VALUES (?, ?, ?, ?)
    """, (customer_id, sale_id, amount, notes))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_customer_payments(customer_id: int) -> List[Dict]:
    """Return all payments for a customer, newest first."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT p.*, s.id AS sale_ref
        FROM payments p
        LEFT JOIN sales s ON p.sale_id = s.id
        WHERE p.customer_id = ?
        ORDER BY p.payment_date DESC, p.id DESC
    """, (customer_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_total_paid(customer_id: int) -> float:
    """Sum of all payments by a customer."""
    conn = get_connection()
    row = conn.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM payments WHERE customer_id = ?
    """, (customer_id,)).fetchone()
    conn.close()
    return row["total"] if row else 0.0


def delete_payment(payment_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
    conn.commit()
    conn.close()


# ============================================================
# DEBTS (computed)
# ============================================================

def get_customer_debt(customer_id: int) -> float:
    """
    Total debt = sum of sales total - sum of payments.
    Returns 0 if no debt.
    """
    conn = get_connection()

    # Total sales for this customer
    sales_row = conn.execute("""
        SELECT COALESCE(SUM(total), 0) AS total
        FROM sales WHERE customer_id = ?
    """, (customer_id,)).fetchone()
    total_sales = sales_row["total"] if sales_row else 0.0

    # Total paid by this customer
    paid_row = conn.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM payments WHERE customer_id = ?
    """, (customer_id,)).fetchone()
    total_paid = paid_row["total"] if paid_row else 0.0

    conn.close()

    debt = total_sales - total_paid
    return max(0.0, debt)  # Never negative


def get_all_debts() -> List[Dict]:
    """
    Return list of customers with outstanding debts.
    Each item: {customer_id, name, phone, total_sales, total_paid, debt}
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT
            c.id AS customer_id,
            c.name,
            c.phone,
            COALESCE((
                SELECT SUM(s.total) FROM sales s WHERE s.customer_id = c.id
            ), 0) AS total_sales,
            COALESCE((
                SELECT SUM(p.amount) FROM payments p WHERE p.customer_id = c.id
            ), 0) AS total_paid
        FROM customers c
    """).fetchall()
    conn.close()

    result = []
    for r in rows:
        debt = r["total_sales"] - r["total_paid"]
        if debt > 0.01:  # Only customers who owe money
            result.append({
                "customer_id": r["customer_id"],
                "name": r["name"],
                "phone": r["phone"] or "",
                "total_sales": r["total_sales"],
                "total_paid": r["total_paid"],
                "debt": debt,
            })

    # Sort by debt amount (highest first)
    result.sort(key=lambda x: x["debt"], reverse=True)
    return result


def get_total_debts() -> float:
    """Sum of all customer debts."""
    total = 0.0
    for d in get_all_debts():
        total += d["debt"]
    return total


# ============================================================
# Update customer with a quick "pay debt" (no specific sale)
# ============================================================

def pay_customer_debt(customer_id: int, amount: float,
                      notes: str = "Debt payment") -> int:
    """Register a debt payment (not tied to a specific sale)."""
    return add_payment(customer_id, amount, sale_id=None, notes=notes)