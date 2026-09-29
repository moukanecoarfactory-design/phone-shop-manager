"""
Add HDD and SSD categories to all databases.
Run once: python add_hdd_ssd.py
"""
from app.db.database import get_connection


NEW_CATEGORIES = [
    ("HDD",   "قرص صلب",   "Disque dur HDD"),
    ("SSD",   "قرص SSD",   "Disque SSD"),
]


def main():
    conn = get_connection()
    cur = conn.cursor()

    added = 0
    for name_en, name_ar, name_fr in NEW_CATEGORIES:
        row = cur.execute(
            "SELECT id FROM categories WHERE name_en = ?", (name_en,)
        ).fetchone()

        if row:
            print(f"⏭️  Skipped (exists): {name_en}")
            continue

        cur.execute(
            "INSERT INTO categories (name_en, name_ar, name_fr) VALUES (?, ?, ?)",
            (name_en, name_ar, name_fr)
        )
        print(f"✅ Added: {name_en}")
        added += 1

    conn.commit()
    conn.close()

    print(f"\n📊 Total added: {added}")
    print(f"🎉 Done!")


if __name__ == "__main__":
    main()