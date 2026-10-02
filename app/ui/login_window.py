import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QPainterPath

from app.db.user_repo import authenticate
from app.locales.translations import t, get_setting


def _get_avatar_path() -> Path:
    """Find the avatar image — works both from source and packaged .exe."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent.parent.parent

    assets = base / "data" / "assets"
    for name in ("avatar.png", "avatar.jpg", "avatar.jpeg", "logo.png", "logo.jpg"):
        p = assets / name
        if p.exists():
            return p
    return None


class LoginWindow(QDialog):
    """Dark mode login dialog with avatar."""

    def __init__(self, lang: str = "en"):
        super().__init__()
        self.lang = lang
        self.user = None

        L = lambda key: t(key, self.lang)

        # Read shop name from settings
        shop_name = get_setting("shop_name", "Phone Shop")

        self.setWindowTitle(L("welcome_back") + " - " + shop_name)
        self.setFixedSize(500, 720)

        # Dark gradient background
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a,
                    stop:0.5 #1e1b4b,
                    stop:1 #0f172a
                );
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 40, 40, 40)
        outer.setSpacing(0)

        # ---------- Avatar (circular) ----------
        avatar_path = _get_avatar_path()

        avatar_container = QHBoxLayout()
        avatar_container.addStretch()

        if avatar_path:
            pix = QPixmap(str(avatar_path))
            size = 140

            if not pix.isNull():
                pix = pix.scaled(size, size,
                                 Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                 Qt.TransformationMode.SmoothTransformation)

                rounded = QPixmap(size, size)
                rounded.fill(Qt.GlobalColor.transparent)
                painter = QPainter(rounded)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                path = QPainterPath()
                path.addEllipse(0, 0, size, size)
                painter.setClipPath(path)
                offset_x = (pix.width() - size) // 2
                offset_y = (pix.height() - size) // 2
                painter.drawPixmap(-offset_x, -offset_y, pix)
                painter.end()

                avatar_lbl = QLabel()
                avatar_lbl.setPixmap(rounded)
                avatar_lbl.setFixedSize(size + 16, size + 16)
                avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                avatar_lbl.setStyleSheet("""
                    border: 3px solid #0ea5e9;
                    border-radius: 78px;
                    background-color: #0f172a;
                    padding: 5px;
                """)
                avatar_container.addWidget(avatar_lbl)
            else:
                avatar_lbl = QLabel("📱")
                avatar_lbl.setFixedSize(140, 140)
                avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                avatar_lbl.setStyleSheet("""
                    background-color: #1e293b;
                    border: 3px solid #0ea5e9;
                    border-radius: 70px;
                    font-size: 56px;
                """)
                avatar_container.addWidget(avatar_lbl)
        else:
            avatar_lbl = QLabel("📱")
            avatar_lbl.setFixedSize(140, 140)
            avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            avatar_lbl.setStyleSheet("""
                background-color: #1e293b;
                border: 3px solid #0ea5e9;
                border-radius: 70px;
                font-size: 56px;
            """)
            avatar_container.addWidget(avatar_lbl)

        avatar_container.addStretch()
        outer.addLayout(avatar_container)

        outer.addSpacing(24)

        # ---------- Shop name (from settings) ----------
        title = QLabel(shop_name.upper())
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            color: #ffffff;
            font-size: 20px;
            font-weight: bold;
            letter-spacing: 2px;
            background: transparent;
        """)
        title.setWordWrap(True)
        outer.addWidget(title)

        # ---------- Subtitle (translated) ----------
        subtitle = QLabel(L("sign_in_to_continue"))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            color: #94a3b8;
            font-size: 13px;
            background: transparent;
            letter-spacing: 0.5px;
        """)
        outer.addWidget(subtitle)

        outer.addSpacing(40)

        # ---------- Username ----------
        user_lbl = QLabel(L("username_label"))
        user_lbl.setStyleSheet("""
            color: #94a3b8;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 1.5px;
            background: transparent;
        """)
        outer.addWidget(user_lbl)

        outer.addSpacing(6)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(L("enter_username"))
        self.username_input.setMinimumHeight(48)
        self.username_input.setStyleSheet(self._input_style())
        outer.addWidget(self.username_input)

        outer.addSpacing(18)

        # ---------- Password ----------
        pass_lbl = QLabel(L("password_label"))
        pass_lbl.setStyleSheet("""
            color: #94a3b8;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 1.5px;
            background: transparent;
        """)
        outer.addWidget(pass_lbl)

        outer.addSpacing(6)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(L("enter_password"))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(48)
        self.password_input.setStyleSheet(self._input_style())
        self.password_input.returnPressed.connect(self.on_login)
        outer.addWidget(self.password_input)

        outer.addSpacing(30)

        # ---------- Login button ----------
        self.login_btn = QPushButton("  " + L("sign_in") + "  →")
        self.login_btn.setMinimumHeight(50)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0ea5e9, stop:1 #8b5cf6
                );
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0284c7, stop:1 #7c3aed
                );
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0369a1, stop:1 #6d28d9
                );
            }
        """)
        self.login_btn.clicked.connect(self.on_login)
        outer.addWidget(self.login_btn)

        outer.addStretch()

        self.username_input.setFocus()

    def _input_style(self) -> str:
        return """
            QLineEdit {
                background-color: #1e293b;
                color: #ffffff;
                border: 1px solid #334155;
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 14px;
                selection-background-color: #0ea5e9;
                selection-color: white;
            }
            QLineEdit:hover {
                border: 1px solid #475569;
                background-color: #1e293b;
            }
            QLineEdit:focus {
                border: 2px solid #0ea5e9;
                background-color: #0f172a;
            }
        """

    def on_login(self):
        L = lambda key: t(key, self.lang)
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, L("missing_fields"),
                                L("please_enter_credentials"))
            return

        user = authenticate(username, password)
        if user:
            self.user = user
            self.accept()
        else:
            QMessageBox.warning(self, L("login_failed"),
                                L("invalid_credentials"))
            self.password_input.clear()
            self.password_input.setFocus()