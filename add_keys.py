from pathlib import Path

NEW_KEYS = {
    "capacity": ("Capacity", "Capacite", "السعة"),
    "total_sales_col": ("Total Sales", "Total des ventes", "إجمالي المبيعات"),
    "total_paid_col": ("Paid", "Paye", "المدفوع"),
    "debt_col2": ("Debt", "Dette", "الدين"),
    "created_col": ("Created", "Cree le", "تاريخ الإنشاء"),
    "address_label": ("Address", "Adresse", "العنوان"),
    "city_label": ("City", "Ville", "المدينة"),
    "phone_label": ("Phone", "Telephone", "الهاتف"),
    "email_label": ("Email", "Email", "البريد الإلكتروني"),
    "website_label": ("Website", "Site web", "الموقع"),
    "optional": ("(optional)", "(optionnel)", "(اختياري)"),
    "today_section": ("Today", "Aujourd'hui", "اليوم"),
    "capacity_placeholder": ("e.g. 64GB, 20000mAh", "ex: 64GB, 20000mAh", "مثال: 64GB، 20000mAh"),
}


def main():
    path = Path(__file__).parent / "app" / "locales" / "translations.py"
    lines = path.read_text(encoding="utf-8").split("\n")

    en_idx = fr_idx = ar_idx = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s == '"en": {': en_idx = i
        elif s == '"fr": {': fr_idx = i
        elif s == '"ar": {': ar_idx = i

    if None in (en_idx, fr_idx, ar_idx):
        print("ERROR: could not find blocks")
        return

    def add_keys(start, end, idx):
        pos = end - 1
        while pos > start and lines[pos].strip() != "},":
            pos -= 1
        added = 0
        for k, v in NEW_KEYS.items():
            marker = f'"{k}":'
            exists = any(marker in lines[j] for j in range(start, end))
            if exists:
                continue
            new_line = '        "' + k + '": ' + repr(v[idx]) + ','
            lines.insert(pos, new_line)
            pos += 1
            added += 1
        return added

    ar_n = add_keys(ar_idx, len(lines), 2)
    fr_n = add_keys(fr_idx, ar_idx + ar_n, 1)
    en_n = add_keys(en_idx, fr_idx + fr_n, 0)

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Added: EN={en_n} FR={fr_n} AR={ar_n}")


if __name__ == "__main__":
    main()