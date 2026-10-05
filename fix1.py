from pathlib import Path

NEW_KEYS = {
    "paid_at_checkout": ("Paid (at checkout)", "Payé (à la caisse)", "المدفوع (عند الدفع)"),
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
    print(f"Added: EN={en_n} FR={fr_n} AR={ar_n}")


if __name__ == "__main__":
    main()