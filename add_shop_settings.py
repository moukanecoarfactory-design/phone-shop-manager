from app.db.database import get_connection

DEFAULTS = [
    ("shop_address", "Youssoufia Ouest 13 N°3"),
    ("shop_city", "Rabat, Morocco"),
    ("shop_phone", "+212 672 048 326"),
    ("shop_email", ""),
    ("shop_website", ""),
]

conn = get_connection()
for k, v in DEFAULTS:
    conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))
conn.commit()

print("Current settings:")
rows = conn.execute("SELECT key, value FROM settings ORDER BY key").fetchall()
for r in rows:
    print(f"  {r['key']} = {r['value']}")
conn.close()