"""
Add all missing translation keys for v2.1 final fixes.
Run once: python add_final_translations.py
"""
from pathlib import Path


NEW_KEYS = {
    # Capacity
    "capacity": ("Capacity", "Capacité", "السعة"),

    # Debts page
    "total_sales_col": ("Total Sales", "Total des ventes", "إجمالي المبيعات"),
    "total_paid_col": ("Paid", "Payé", "المدفوع"),
    "debt_col2": ("Debt", "Dette", "الدين"),

    # Users page
    "created_col": ("Created", "Créé le", "تاريخ الإنشاء"),

    # Settings labels
    "address_label": ("Address", "Adresse", "العنوان"),
    "city_label": ("City", "Ville", "المدينة"),
    "phone_label": ("Phone", "Téléphone", "الهاتف"),
    "email_label": ("Email", "Email", "البريد الإلكتروني"),
    "website_label": ("Website", "Site web", "الموقع"),
    "optional": ("(optional)", "(optionnel)", "(اختياري)"),

    # Dashboard
    "today_section": ("Today", "Aujourd'hui", "اليوم"),
    "this_month_section": ("This Month", "Ce mois-ci", "هذا الشهر"),
    "inventory_section": ("Inventory", "Inventaire", "المخزون"),
    "top_selling_section": (
        "Top 5 Selling Products (this month)",
        "Top 5 des ventes (ce mois)",
        "أفضل 5 منتجات مبيعاً (هذا الشهر)"
    ),
    "low_stock_section": (
        "Low Stock Alerts",
        "Alertes stock faible",
        "تنبيهات نقص المخزون"
    ),

    # Placeholder text for capacity
    "capacity_placeholder": (
        "e.g. 64GB, 20000mAh",
        "ex: 64GB, 20000mAh",
        "مثال: 64GB، 20000mAh"
    ),
}


def main():
    path = Path(__file__).parent / "app" / "locales" / "translations.py"
    lines = path.read_text(encoding="utf-8").split("\n")

    en_start = fr_start = ar_start = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s == '"en": {': en_start = i
        elif s == '"fr": {': fr_start = i
        elif s == '"ar": {': ar_start = i

    if None in (en_start, fr_start, ar_start):
        print("❌ Could not find all language blocks")
        return

    def insert_before_close(block_start, block_end, idx):
        pos = block_end - 1
        while pos > block_start and lines[pos].strip() != "},":
            pos -= 1
        added = 0
        for k, v in NEW_KEYS.items():
            # Skip if key already exists in this block
            key_marker = f'"{k}":'
            already = any(key_marker in lines[j] for j in range(block_start, block_end))
            if already:
                continue
            lines.insert(pos, f'        "{k}": {repr(v[idx])},')
            pos += 1
            added += 1
        return added

    ar_added = insert_before_close(ar_start, len(lines), 2)
    fr_added = insert_before_close(fr_start, ar_start + ar_added, 1)
    en_added = insert_before_close(en_start, fr_start + fr_added, 0)

    path.write_text("\n".join(lines), encoding="utf-8")

    print(f"✅ Added keys:")
    print(f"   EN: {en_added}")
    print(f"   FR: {fr_added}")
    print(f"   AR: {ar_added}")


if __name__ == "__main__":
    main()