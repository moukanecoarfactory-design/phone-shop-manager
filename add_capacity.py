"""
Add 'capacity' column to products table.
Run once: python add_capacity.py
"""
from app.db.database import get_connection


def main():
    conn = get_connection()
    cur = conn.cursor()

    # Check if column exists
    cur.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in cur.fetchall()]

    if "capacity" in columns:
        print("✅ Column 'capacity' already exists. Nothing to do.")
    else:
        cur.execute("ALTER TABLE products ADD COLUMN capacity TEXT")
        conn.commit()
        print("✅ Added 'capacity' column to products table.")
        print("   New column: capacity (TEXT)")

    # Show all columns
    cur.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in cur.fetchall()]
    print(f"\n📋 Products table columns:")
    for c in columns:
        print(f"   • {c}")

    conn.close()


if __name__ == "__main__":
    main()