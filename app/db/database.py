import sys
import sqlite3
import hashlib
from pathlib import Path


def _get_data_dir() -> Path:
    """
    Return the folder where the database + images should live.
    - If running as a packaged .exe (PyInstaller): use the folder that
      contains the .exe itself.
    - Otherwise (running via python main.py): use the project's data/ folder.
    """
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent.parent.parent

    data_dir = base / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


DB_DIR = _get_data_dir()
DB_PATH = DB_DIR / "shop.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    conn = get_connection()
    cur = conn.cursor()

    # ---------- Categories ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_en TEXT NOT NULL,
            name_ar TEXT,
            name_fr TEXT
        )
    """)

    # ---------- Users (for login) ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'admin',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------- Suppliers ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            notes TEXT
        )
    """)

    # ---------- Products ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            brand TEXT,
            buying_price REAL NOT NULL DEFAULT 0,
            selling_price REAL NOT NULL DEFAULT 0,
            quantity INTEGER NOT NULL DEFAULT 0,
            low_stock_alert INTEGER NOT NULL DEFAULT 5,
            supplier_id INTEGER,
            barcode TEXT,
            notes TEXT,
            image_path TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
        )
    """)

    # ---------- Phone Units ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phone_units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            imei TEXT UNIQUE,
            buying_price REAL NOT NULL DEFAULT 0,
            selling_price REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'in_stock',
            supplier_id INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
        )
    """)

    # ---------- Customers ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ---------- Sales ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            total REAL NOT NULL DEFAULT 0,
            profit REAL NOT NULL DEFAULT 0,
            paid REAL NOT NULL DEFAULT 0,
            sale_date TEXT DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
        )
    """)

    # ---------- Sale Items ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER,
            phone_unit_id INTEGER,
            quantity INTEGER NOT NULL DEFAULT 1,
            unit_price REAL NOT NULL DEFAULT 0,
            unit_cost REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
            FOREIGN KEY (phone_unit_id) REFERENCES phone_units(id) ON DELETE SET NULL
        )
    """)

    # ---------- Settings ----------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # ---------- Default categories ----------
    cur.execute("SELECT COUNT(*) FROM categories")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO categories (name_en, name_ar, name_fr) VALUES (?, ?, ?)",
            [
                ("Phones",    "هواتف",    "Téléphones"),
                ("Chargers",  "شواحن",    "Chargeurs"),
                ("Earphones", "سماعات",   "Écouteurs"),
                ("Cables",    "كابلات",   "Câbles"),
                ("Cases",     "أغطية",    "Coques"),
                ("Other",     "أخرى",     "Autre"),
            ],
        )

    # ---------- Default admin user ----------
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        default_pw = hashlib.sha256("admin".encode()).hexdigest()
        cur.execute(
            "INSERT INTO users (username, password_hash, full_name, role) "
            "VALUES (?, ?, ?, ?)",
            ("admin", default_pw, "Administrator", "admin")
        )
        print("Default user created: admin / admin")

    # ---------- Default settings ----------
    cur.execute("SELECT COUNT(*) FROM settings WHERE key='language'")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO settings (key, value) VALUES (?, ?)",
            [
                ("language", "en"),
                ("shop_name", "My Phone Shop"),
                ("currency", "MAD"),
            ],
        )

    # ---------- Migration: add image_path if missing ----------
    cur.execute("PRAGMA table_info(products)")
    columns = [row[1] for row in cur.fetchall()]
    if "image_path" not in columns:
        cur.execute("ALTER TABLE products ADD COLUMN image_path TEXT")
        print("Migration: added image_path column to products table.")

    # ---------- Make sure images folder exists ----------
    IMAGES_DIR = DB_DIR / "images"
    IMAGES_DIR.mkdir(exist_ok=True)

    conn.commit()
    conn.close()
    print(f"Database ready at: {DB_PATH}")


if __name__ == "__main__":
    init_database()