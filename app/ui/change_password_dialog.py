from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt

from app.db.user_repo import change_password
from app.locales.translations import t


class ChangePasswordDialog(QDialog):
    """Dialog to change the current user's password."""

    def __init__(self, parent=None, user: dict = None, lang: str = "en"):
        super().__init__(parent)
        self.user = user or {}
        self.lang = lang
        L = lambda key: t(key, self.lang)

        self.setWindowTitle(L("change_password_title"))
        self.setFixedSize(440, 540)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #6366f1, stop:1 #8b5cf6
                );
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(30, 30, 30, 30)

        # White card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 16px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 20, 30, 30)
        card_layout.setSpacing(8)

        # Icon
        icon_row = QHBoxLayout()
        icon_row.addStretch()

        icon = QLabel("🔐")
        icon.setStyleSheet("""
            font-size: 44px;
            background-color: #eef2ff;
            border-radius: 40px;
            padding: 8px;
        """)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedSize(80, 80)
        icon_row.addWidget(icon)

        icon_row.addStretch()
        card_layout.addLayout(icon_row)

        card_layout.addSpacing(15)

        # Title
        title = QLabel(L("change_password_title"))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: #0f172a;
            font-size: 22px;
            font-weight: bold;
            background: transparent;
        """)
        card_layout.addWidget(title)

        # Subtitle
        username = self.user.get("username", "")
        if username:
            subtitle_text = L("for_user").replace("{user}", username)
        else:
            subtitle_text = ""
        subtitle = QLabel(subtitle_text)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            color: #64748b;
            font-size: 12px;
            background: transparent;
        """)
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(20)

        # Current password
        cur_lbl = QLabel(L("password_label"))
        cur_lbl.setStyleSheet("""
            color: #334155;
            font-size: 12px;
            font-weight: bold;
            background: transparent;
        """)
        card_layout.addWidget(cur_lbl)

        self.current_input = QLineEdit()
        self.current_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_input.setPlaceholderText(L("enter_password"))
        self.current_input.setMinimumHeight(38)
        self.current_input.setStyleSheet(self._input_style())
        card_layout.addWidget(self.current_input)

        card_layout.addSpacing(6)

        # New password
        new_lbl = QLabel(L("new_password_label"))
        new_lbl.setStyleSheet("""
            color: #334155;
            font-size: 12px;
            font-weight: bold;
            background: transparent;
        """)
        card_layout.addWidget(new_lbl)

        self.new_input = QLineEdit()
        self.new_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_input.setPlaceholderText(L("min_4_chars"))
        self.new_input.setMinimumHeight(38)
        self.new_input.setStyleSheet(self._input_style())
        card_layout.addWidget(self.new_input)

        card_layout.addSpacing(6)

        # Confirm
        conf_lbl = QLabel(L("confirm_password"))
        conf_lbl.setStyleSheet("""
            color: #334155;
            font-size: 12px;
            font-weight: bold;
            background: transparent;
        """)
        card_layout.addWidget(conf_lbl)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText(L("enter_password"))
        self.confirm_input.setMinimumHeight(38)
        self.confirm_input.setStyleSheet(self._input_style())
        self.confirm_input.returnPressed.connect(self.on_save)
        card_layout.addWidget(self.confirm_input)

        card_layout.addSpacing(18)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel_btn = QPushButton(L("cancel"))
        cancel_btn.setMinimumHeight(42)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("✓ " + L("save"))
        save_btn.setMinimumHeight(42)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6
                );
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4f46e5, stop:1 #7c3aed
                );
            }
        """)
        save_btn.clicked.connect(self.on_save)
        btn_row.addWidget(save_btn)

        card_layout.addLayout(btn_row)

        outer.addWidget(card)

    def _input_style(self) -> str:
        return """
            QLineEdit {
                background-color: #f8fafc;
                color: #0f172a;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                padding: 8px 14px;
                font-size: 14px;
            }
            QLineEdit:focus {
                background-color: #ffffff;
                border: 2px solid #6366f1;
            }
        """

    def on_save(self):
        L = lambda key: t(key, self.lang)
        current = self.current_input.text()
        new = self.new_input.text()
        confirm = self.confirm_input.text()

        if not current or not new or not confirm:
            QMessageBox.warning(self, L("missing_fields"),
                                L("fill_all_fields"))
            return

        if len(new) < 4:
            QMessageBox.warning(self, L("too_short"),
                                L("new_password_too_short"))
            return

        if new != confirm:
            QMessageBox.warning(self, L("mismatch"),
                                L("passwords_do_not_match"))
            return

        user_id = self.user.get("id")
        if not user_id:
            QMessageBox.critical(self, L("error_title"), L("user_not_identified"))
            return

        if change_password(user_id, current, new):
            QMessageBox.information(self, L("success_title"),
                                    L("password_changed"))
            self.accept()
        else:
            QMessageBox.warning(self, L("wrong_password"),
                                L("current_password_incorrect"))
            self.current_input.clear()
            self.current_input.setFocus()