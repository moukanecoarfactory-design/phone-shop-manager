"""
Reset all categories with a fresh, organized list.
- Deletes all existing categories
- Adds the full new list
- Products keep their data (category_id becomes NULL)
"""
from app.db.database import get_connection


# ============================================================
# MASTER CATEGORY LIST
# Format: (English, Arabic, French)
# ============================================================
CATEGORIES = [
    # --- Phone & Tablets ---
    ("Smartphone",          "هاتف ذكي",         "Smartphone"),
    ("Phones",              "هواتف",            "Téléphones"),
    ("Phone Holder",        "حامل هاتف",         "Support téléphone"),
    ("Screen Protector",    "حماية شاشة",       "Protection écran"),
    ("Phone Bag",           "حقيبة هاتف",        "Étui téléphone"),

    # --- Cables & Adapters ---
    ("Cables",              "كابلات",           "Câbles"),
    ("Cable Jack",          "كابل جاك",         "Câble Jack"),
    ("OTG V8",              "OTG V8",           "OTG V8"),
    ("OTG Type-C",          "OTG Type-C",       "OTG Type-C"),

    # --- Storage ---
    ("USB Flash Drive",     "فلاش USB",         "Clé USB"),
    ("SD Card",             "بطاقة SD",         "Carte SD"),
    ("Memory Card",         "بطاقة ذاكرة",      "Carte mémoire"),

    # --- Audio ---
    ("Earphones",           "سماعات",           "Écouteurs"),
    ("Headphones",          "سماعات رأس",       "Casque"),
    ("Speakers",            "مكبرات صوت",       "Enceintes"),
    ("Bluetooth Earphones", "سماعات بلوتوث",    "Écouteurs Bluetooth"),

    # --- Power ---
    ("Chargers",            "شواحن",            "Chargeurs"),
    ("Power Bank",          "بطارية محمولة",    "Batterie externe"),
    ("Batteries",           "بطاريات",          "Piles"),

    # --- Wearables & Gadgets ---
    ("Smart Watch",         "ساعة ذكية",        "Montre connectée"),
    ("Watch Straps",        "أحزمة الساعات",    "Bracelets de montre"),
    ("Camera",              "كاميرا",           "Caméra"),
    ("TV Box",              "صندوق تلفاز",      "Box TV"),

    # --- Computer ---
    ("PC Monitor",          "شاشة كمبيوتر",     "Écran PC"),
    ("Mouse & Keyboard",    "فأرة ولوحة مفاتيح", "Souris & Clavier"),
    ("PC Accessories",      "ملحقات الكمبيوتر",  "Accessoires PC"),

    # --- Gaming ---
    ("Gaming",              "الألعاب",          "Gaming"),
    ("Gaming Controller",   "يد تحكم",          "Manette de jeu"),

    # --- Protection ---
    ("Cases",               "أغطية",            "Coques"),
    ("Covers",              "أغلفة",            "Housses"),

    # --- Lighting ---
    ("LED & Lighting",      "إضاءة LED",        "LED & Éclairage"),

    # --- Other ---
    ("Other",               "أخرى",             "Autre"),
]


def main():
    conn = get_connection()
    cur = conn.cursor()

    # Count before
    before = cur.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    print(f"📊 Categories before: {before}")

    # Count products using categories
    products_with_cat = cur.execute(
        "SELECT COUNT(*) FROM products WHERE category_id IS NOT NULL"
    ).fetchone()[0]
    print(f"📦 Products with category: {products_with_cat}")

    # Delete all categories
    print(f"\n🗑️  Deleting all old categories...")
    cur.execute("UPDATE products SET category_id = NULL")
    cur.execute("DELETE FROM categories")
    print(f"   Done.")

    # Reset auto-increment
    cur.execute("DELETE FROM sqlite_sequence WHERE name='categories'")

    # Insert new categories
    print(f"\n➕ Adding new categories...")
    for name_en, name_ar, name_fr in CATEGORIES:
        cur.execute(
            "INSERT INTO categories (name_en, name_ar, name_fr) VALUES (?, ?, ?)",
            (name_en, name_ar, name_fr)
        )
        print(f"   ✅ {name_en}")

    conn.commit()

    # Count after
    after = cur.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    print(f"\n📊 Categories after: {after}")

    conn.close()

    print(f"\n🎉 Done! Restart the app to see the new categories.")


if __name__ == "__main__":
    main()