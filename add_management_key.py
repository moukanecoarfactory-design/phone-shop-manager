"""
Add 'management_system' translation key to all 3 languages.
Run once: python add_management_key.py
"""
from pathlib import Path


def main():
    path = Path(__file__).parent / "app" / "locales" / "translations.py"

    if not path.exists():
        print(f"❌ Not found: {path}")
        return

    content = path.read_text(encoding="utf-8")

    # Check if already added
    if '"management_system"' in content:
        print("✅ 'management_system' already exists. Nothing to do.")
        return

    # Add to EN
    content = content.replace(
        '    "en": {',
        '    "en": {\n        "management_system": "Management System",',
        1
    )

    # Add to FR
    content = content.replace(
        '    "fr": {',
        '    "fr": {\n        "management_system": "Système de gestion",',
        1
    )

    # Add to AR
    content = content.replace(
        '    "ar": {',
        '    "ar": {\n        "management_system": "نظام الإدارة",',
        1
    )

    path.write_text(content, encoding="utf-8")
    print("✅ 'management_system' added to all 3 languages")


if __name__ == "__main__":
    main()