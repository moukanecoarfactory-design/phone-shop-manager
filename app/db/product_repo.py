from typing import List, Optional
from app.db.database import get_connection
from app.core.models import Product, Category


# ---------- Categories ----------

def get_all_categories() -> List[Category]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM categories ORDER BY name_en").fetchall()
    conn.close()
    return [Category(id=r["id"], name_en=r["name_en"],
                     name_ar=r["name_ar"], name_fr=r["name_fr"]) for r in rows]


# ---------- Products ----------

def get_products(search: str = "", category_id: Optional[int] = None,
                 limit: int = 50, offset: int = 0) -> List[Product]:
    """Fetch products with optional search & category filter, paginated."""
    conn = get_connection()
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR brand LIKE ? OR barcode LIKE ?)"
        like = f"%{search}%"
        params += [like, like, like]

    if category_id:
        query += " AND category_id = ?"
        params.append(category_id)

    query += " ORDER BY name LIMIT ? OFFSET ?"
    params += [limit, offset]

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [_row_to_product(r) for r in rows]


def count_products(search: str = "", category_id: Optional[int] = None) -> int:
    conn = get_connection()
    query = "SELECT COUNT(*) FROM products WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR brand LIKE ? OR barcode LIKE ?)"
        like = f"%{search}%"
        params += [like, like, like]

    if category_id:
        query += " AND category_id = ?"
        params.append(category_id)

    total = conn.execute(query, params).fetchone()[0]
    conn.close()
    return total


def get_product(product_id: int) -> Optional[Product]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    return _row_to_product(row) if row else None


def add_product(p: Product) -> int:
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO products
        (name, category_id, brand, capacity, buying_price, selling_price,
         quantity, low_stock_alert, supplier_id, barcode, notes, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (p.name, p.category_id, p.brand, p.capacity, p.buying_price,
          p.selling_price, p.quantity, p.low_stock_alert, p.supplier_id,
          p.barcode, p.notes, p.image_path))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_product(p: Product) -> None:
    conn = get_connection()
    conn.execute("""
        UPDATE products SET
            name = ?, category_id = ?, brand = ?, capacity = ?,
            buying_price = ?, selling_price = ?, quantity = ?,
            low_stock_alert = ?, supplier_id = ?, barcode = ?, notes = ?,
            image_path = ?
        WHERE id = ?
    """, (p.name, p.category_id, p.brand, p.capacity, p.buying_price,
          p.selling_price, p.quantity, p.low_stock_alert, p.supplier_id,
          p.barcode, p.notes, p.image_path, p.id))
    conn.commit()
    conn.close()


def delete_product(product_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def _row_to_product(r) -> Product:
    return Product(
        id=r["id"], name=r["name"], category_id=r["category_id"],
        brand=r["brand"] or "", capacity=r["capacity"] or "",
        buying_price=r["buying_price"],
        selling_price=r["selling_price"], quantity=r["quantity"],
        low_stock_alert=r["low_stock_alert"], supplier_id=r["supplier_id"],
        barcode=r["barcode"] or "", notes=r["notes"] or "",
        image_path=r["image_path"] or ""
    )


def get_product_image(pid: int) -> str:
    """Return the image_path of a product, or empty string."""
    conn = get_connection()
    row = conn.execute("SELECT image_path FROM products WHERE id = ?", (pid,)).fetchone()
    conn.close()
    return row["image_path"] if row and row["image_path"] else ""