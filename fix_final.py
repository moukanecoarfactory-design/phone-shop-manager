from pathlib import Path

NEW_KEYS = {
    "export": ("Export", "Exporter", "تصدير"),
    "export_done": ("Export Complete", "Exportation terminée", "اكتمل التصدير"),
    "export_done_msg": ("File saved: {file}", "Fichier enregistré : {file}", "تم حفظ الملف: {file}"),
    "admin_role_badge": ("👑 Admin", "👑 Administrateur", "👑 مدير"),
    "cashier_role_badge": ("👤 Cashier", "👤 Caissier", "👤 كاشير"),
}


def main():
    # 1. Add keys to translations
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
    print(f"Translations added: EN={en_n} FR={fr_n} AR={ar_n}")

    # 2. Fix reports_page.py - "export" hardcoded
    rp = Path(__file__).parent / "app" / "ui" / "reports_page.py"
    content = rp.read_text(encoding="utf-8")
    if '"📥  " + L("export")' in content or 'L("export")' in content:
        print("reports_page already uses L(export) ✅")
    else:
        old = 'self.export_btn = QPushButton("📥  Export")'
        new = 'self.export_btn = QPushButton("📥  " + L("export"))'
        if old in content:
            content = content.replace(old, new)
            rp.write_text(content, encoding="utf-8")
            print("reports_page: fixed ✅")
        else:
            for i, line in enumerate(content.split("\n")):
                if "export_btn" in line and "QPushButton" in line:
                    print(f"  Line {i+1}: {line.strip()}")

    # 3. Fix main_window.py - role text hardcoded
    mw = Path(__file__).parent / "app" / "ui" / "main_window.py"
    content = mw.read_text(encoding="utf-8")
    old = 'role_text = "👑 Admin" if self.is_admin else "👤 Cashier"'
    new = 'role_text = L("admin_role_badge") if self.is_admin else L("cashier_role_badge")'
    if old in content:
        content = content.replace(old, new)
        mw.write_text(content, encoding="utf-8")
        print("main_window: role text fixed ✅")
    else:
        print("main_window: role pattern not found")
        for i, line in enumerate(content.split("\n")):
            if "role_text" in line and "Admin" in line:
                print(f"  Line {i+1}: {line.strip()}")


if __name__ == "__main__":
    main()
