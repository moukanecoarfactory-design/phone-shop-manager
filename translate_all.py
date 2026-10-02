"""
Translate all remaining dialogs and messages.
Replaces hardcoded English text with t() calls.
"""
from pathlib import Path


BASE = Path(__file__).parent / "app" / "ui"


# ============================================================
# Replacements per file
# Format: file → [(old, new), ...]
# ============================================================
REPLACEMENTS = {
    "change_password_dialog.py": [
        # Imports
        ('from app.db.user_repo import change_password',
         'from app.db.user_repo import change_password\nfrom app.locales.translations import t'),
        # __init__ start
        ('        self.user = user or {}',
         '        self.user = user or {}\n        L = lambda key: t(key, self.lang)'),
        # Title
        ('self.setWindowTitle("Change Password")',
         'self.setWindowTitle(L("change_password_title"))'),
        ('title = QLabel("Change Password")',
         'title = QLabel(L("change_password_title"))'),
        # Labels
        ('cur_lbl = QLabel("Current Password")',
         'cur_lbl = QLabel(L("password_label"))'),
        ('new_lbl = QLabel("New Password")',
         'new_lbl = QLabel("New " + L("password_label"))'),
        ('conf_lbl = QLabel("Confirm New Password")',
         'conf_lbl = QLabel(L("confirm_password"))'),
        # Placeholders
        ('self.current_input.setPlaceholderText("Enter current password")',
         'self.current_input.setPlaceholderText(L("enter_password"))'),
        ('self.new_input.setPlaceholderText("Minimum 4 characters")',
         'self.new_input.setPlaceholderText("(min 4)")'),
        ('self.confirm_input.setPlaceholderText("Repeat new password")',
         'self.confirm_input.setPlaceholderText(L("enter_password"))'),
        # Buttons
        ('cancel_btn = QPushButton("Cancel")',
         'cancel_btn = QPushButton(L("cancel"))'),
        ('save_btn = QPushButton("Update Password")',
         'save_btn = QPushButton("✓ " + L("save"))'),
        # Messages
        ('QMessageBox.warning(self, "Missing Fields",\n                                "Please fill all fields.")',
         'QMessageBox.warning(self, L("missing_fields"),\n                                L("fill_all_fields"))'),
        ('QMessageBox.warning(self, "Too Short",\n                                "New password must be at least 4 characters.")',
         'QMessageBox.warning(self, L("too_short"),\n                                L("new_password_too_short"))'),
        ('QMessageBox.warning(self, "Mismatch",\n                                "New password and confirmation do not match.")',
         'QMessageBox.warning(self, L("mismatch"),\n                                L("passwords_do_not_match"))'),
        ('QMessageBox.critical(self, "Error", "User not identified.")',
         'QMessageBox.critical(self, L("error_title"), L("user_not_identified"))'),
        ('QMessageBox.information(self, "Success",\n                                    "✅ Password changed successfully!")',
         'QMessageBox.information(self, L("success_title"),\n                                    L("password_changed"))'),
        ('QMessageBox.warning(self, "Wrong Password",\n                                "Current password is incorrect.")',
         'QMessageBox.warning(self, L("wrong_password"),\n                                L("current_password_incorrect"))'),
    ],

    "main_window.py": [
        # Logout confirmation
        ('QMessageBox.question(\n            self, "Logout",\n            "Are you sure you want to logout?",',
         'QMessageBox.question(\n            self, L("logout"),\n            L("confirm_logout"),'),
    ],

    "users_page.py": [
        # Need to add lang-aware L to on_add's dialog
        ('QMessageBox.warning(self, "Missing Fields",\n                                "Username and password are required.")',
         'QMessageBox.warning(self, L("missing_fields"),\n                                L("fill_all_fields"))'),
        ('QMessageBox.warning(self, "Too Short", L("password_too_short"))',
         'QMessageBox.warning(self, L("too_short"), L("password_too_short"))'),
        ('QMessageBox.warning(self, "Mismatch", L("password_mismatch"))',
         'QMessageBox.warning(self, L("mismatch"), L("password_mismatch"))'),
        ('QMessageBox.warning(self, "Exists", L("username_taken"))',
         'QMessageBox.warning(self, L("not_allowed"), L("username_taken"))'),
        ('QMessageBox.information(self, "No Selection",\n                                    "Please select a user first.")',
         'QMessageBox.information(self, L("no_selection"),\n                                    L("please_select_user"))'),
        ('QMessageBox.warning(self, "Not Allowed", L("cannot_delete_self"))',
         'QMessageBox.warning(self, L("not_allowed"), L("cannot_delete_self_users"))'),
        ('QMessageBox.warning(self, "Not Allowed",\n                                "Cannot delete the last admin.")',
         'QMessageBox.warning(self, L("not_allowed"),\n                                L("cannot_delete_last_admin"))'),
    ],

    "receipt_dialog.py": [
        # Title
        ('self.setWindowTitle("Receipt")',
         'self.setWindowTitle(L("print_receipt_title"))'),
        # Header
        ('title = QLabel("Sale Complete!")',
         'title = QLabel(L("sale_complete_title"))'),
        # Info
        ('info = QLabel(\n            "💡 Click a button below to save or print the receipt PDF.\\n"\n            "The receipt will open in your default PDF viewer."\n        )',
         'info = QLabel(L("click_to_save_print"))'),
        # Buttons
        ('close_btn = QPushButton("Close")',
         'close_btn = QPushButton(L("close"))'),
        ('save_btn = QPushButton("💾  Save PDF")',
         'save_btn = QPushButton(L("save_pdf"))'),
        ('open_btn = QPushButton("🖨  Open Receipt")',
         'open_btn = QPushButton(L("open_receipt"))'),
        # Messages
        ('QMessageBox.information(\n            self, "Receipt Saved",\n            f"✅ Receipt saved as PDF:\\n\\n"\n            f"{self.pdf_path}\\n\\n"\n            f"Folder: {self.pdf_path.parent}"\n        )',
         'QMessageBox.information(\n            self, L("receipt_saved_title"),\n            L("receipt_saved_msg") + f"\\n\\n{self.pdf_path}\\n\\nFolder: {self.pdf_path.parent}"\n        )'),
        ('QMessageBox.warning(\n                self, "Cannot Open PDF",\n                f"Could not open the PDF file:\\n\\n{e}\\n\\n"\n                f"Location: {self.pdf_path}"\n            )',
         'QMessageBox.warning(\n                self, L("cannot_open_pdf"),\n                f"{e}\\n\\nLocation: {self.pdf_path}"\n            )'),
    ],

    "product_dialog.py": [
        ('QMessageBox.warning(self, "Error", f"Could not copy image:\\n{e}")',
         'QMessageBox.warning(self, L("error_title"),\n                                L("image_copy_failed") + f"\\n{e}")'),
    ],

    "new_sale_window.py": [
        ('QMessageBox.critical(self, "Error",\n                                 f"{L(\'could_not_save\')}\\n{e}")',
         'QMessageBox.critical(self, L("error_title"),\n                                 f"{L(\'could_not_save\')}\\n{e}")'),
    ],
}


def apply_replacements():
    total_changes = 0
    file_changes = {}

    for filename, replacements in REPLACEMENTS.items():
        file_path = BASE / filename

        if not file_path.exists():
            print(f"⚠️  File not found: {filename}")
            continue

        content = file_path.read_text(encoding="utf-8")
        original = content
        changes = 0

        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                changes += 1

        if changes > 0:
            # Backup
            backup_path = file_path.with_suffix(".py.bak")
            if not backup_path.exists():
                backup_path.write_text(original, encoding="utf-8")

            file_path.write_text(content, encoding="utf-8")
            file_changes[filename] = changes
            total_changes += changes

    print("📊 Summary:")
    for filename, count in file_changes.items():
        print(f"   ✅ {filename}: {count} changes")
    print(f"\n🎉 Total changes: {total_changes}")


if __name__ == "__main__":
    apply_replacements()