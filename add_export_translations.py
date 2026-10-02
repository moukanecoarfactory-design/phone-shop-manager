"""Add export translation keys."""
from pathlib import Path


NEW_KEYS = {
    "export":          ("Export", "Exporter", "تصدير"),
    "export_done":     ("Export Complete", "Exportation terminée", "اكتمل التصدير"),
    "export_done_msg": (
        "File saved: {file}\n\nOpen it now?",
        "Fichier enregistré : {file}\n\nOuvrir maintenant ?",
        "تم حفظ الملف: {file}\n\nهل تريد فتحه الآن؟"
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
        print("❌ Blocks not found")
        return

    def insert_before_close(block_start, block_end, idx):
        pos = block_end - 1
        while pos > block_start and lines[pos].strip() != "},":
            pos -= 1
        new_lines = [
            f'        "{k}": {repr(v[idx])},'
            for k, v in NEW_KEYS.items()
        ]
        for j, ln in enumerate(new_lines):
            lines.insert(pos + j, ln)
        return len(new_lines)

    ar_added = insert_before_close(ar_start, len(lines), 2)
    fr_added = insert_before_close(fr_start, ar_start + ar_added, 1)
    en_added = insert_before_close(en_start, fr_start + fr_added, 0)

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ EN: {en_added}, FR: {fr_added}, AR: {ar_added}")


if __name__ == "__main__":
    main()