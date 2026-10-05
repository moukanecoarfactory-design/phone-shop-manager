from pathlib import Path

# Fix dashboard to use today_section and add total_debts key
NEW_KEYS = {
    "total_debts": ("Total Debts", "Total des dettes", "إجمالي الديون"),
}


def main():
    # 1. Add total_debts to translations
    path = Path(__file__).parent / "app" / "locales" / "translations.py"
    lines = path.read_text(encoding="utf-8").split("\n")

    en_idx = fr_idx = ar_idx = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s == '"en": {': en_idx = i
        elif s == '"fr": {': fr_idx = i
        elif s == '"ar": {': ar_idx = i

    def add_block(start, end, idx):
        pos = end - 1
        while pos > start and lines[pos].strip() != "},":
            pos -= 1
        n = 0
        for k, v in NEW_KEYS.items():
            marker = '"' + k + '":'
            if any(marker in lines[j] for j in range(start, end)):
                continue
            lines.insert(pos, '        "' + k + '": ' + repr(v[idx]) + ',')
            pos += 1
            n += 1
        return n

    ar_n = add_block(ar_idx, len(lines), 2)
    fr_n = add_block(fr_idx, ar_idx + ar_n, 1)
    en_n = add_block(en_idx, fr_idx + fr_n, 0)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Translations: EN={en_n} FR={fr_n} AR={ar_n}")

    # 2. Fix dashboard_page.py - "today" section → "today_section"
    dash = Path(__file__).parent / "app" / "ui" / "dashboard_page.py"
    content = dash.read_text(encoding="utf-8")
    old = 'make_section_header("📅", L("today"))'
    new = 'make_section_header("📅", L("today_section"))'
    if old in content:
        content = content.replace(old, new)
        dash.write_text(content, encoding="utf-8")
        print("Dashboard: 'today' → 'today_section' ✅")
    else:
        print("Dashboard: pattern not found - checking...")
        for i, line in enumerate(content.split("\n")):
            if "today" in line and "make_section_header" in line:
                print(f"  Line {i+1}: {line.strip()}")

    # 3. Fix dashboard_page.py - "total_debts" reference
    old2 = 'L("total_debts")'
    if old2 in content:
        print("Dashboard already uses total_debts ✅")
    else:
        print("Dashboard doesn't use total_debts - may need to check manually")


if __name__ == "__main__":
    main()