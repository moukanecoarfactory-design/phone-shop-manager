"""
Add payments table for tracking customer debts.
Run once: python add_payments_table.py
"""
from app.db.database import get_connection


def main():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            sale_id INTEGER,
            amount REAL NOT NULL DEFAULT 0,
            payment_date TEXT DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE SET NULL
        )
    """)

    # Also add 'paid' column to sales if not exists (for tracking)
    cur.execute("PRAGMA table_info(sales)")
    columns = [row[1] for row in cur.fetchall()]

    if "paid" not in columns:
        cur.execute("ALTER TABLE sales ADD COLUMN paid REAL NOT NULL DEFAULT 0")
        # Set paid = total for existing sales (already fully paid)
        cur.execute("UPDATE sales SET paid = total")
        print("✅ Added 'paid' column to sales table")

    conn.commit()
    conn.close()
    print("✅ Payments table ready")


if __name__ == "__main__":
    main()