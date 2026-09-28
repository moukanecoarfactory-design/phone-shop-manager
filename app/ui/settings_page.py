import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFrame, QFormLayout, QMessageBox,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.db.database import DB_PATH
from app.locales.translations import (
    t, get_setting, set_setting, get_current_language
)


class SettingsPage(QWidget):
    def __init__(self, lang: str = "en"):
        super().__init__()
        self.lang = lang
        L = lambda key: t(key, self.lang)

        # Outer layout with scroll-friendly margins
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # ========== Header ==========
        header = QHBoxLayout()
        title = QLabel(L("settings_title"))
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #0f172a;
            background: transparent;
        """)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # ========== General card ==========
        general_card = self._make_card()

        gen_layout = QVBoxLayout(general_card)
        gen_layout.setContentsMargins(22, 18, 22, 20)
        gen_layout.setSpacing(10)

        gen_header = self._card_header("⚙️", L("general_settings"))
        gen_layout.addWidget(gen_header)

        gen_form = QFormLayout()
        gen_form.setSpacing(14)
        gen_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.shop_name_input = QLineEdit()
        self.shop_name_input.setMinimumHeight(40)
        self.shop_name_input.setStyleSheet(self._input_style())
        gen_form.addRow(self._label(L("shop_name")), self.shop_name_input)

        self.currency_input = QLineEdit()
        self.currency_input.setMinimumHeight(40)
        self.currency_input.setStyleSheet(self._input_style())
        gen_form.addRow(self._label(L("currency")), self.currency_input)

        self.language_combo = QComboBox()
        self.language_combo.setMinimumHeight(40)
        self.language_combo.setStyleSheet(self._input_style())
        self.language_combo.addItem("🇬🇧  English", "en")
        self.language_combo.addItem("🇫🇷  Français", "fr")
        self.language_combo.addItem("🇸🇦  العربية", "ar")
        gen_form.addRow(self._label(L("language")), self.language_combo)

        gen_layout.addLayout(gen_form)
        gen_layout.addSpacing(10)

        save_row = QHBoxLayout()
        save_row.addStretch()
        self.save_btn = QPushButton("💾  " + L("save_settings_btn").lstrip("💾 "))
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setMinimumHeight(42)
        self.save_btn.setStyleSheet(self._primary_btn_style())
        self.save_btn.clicked.connect(self.on_save)
        save_row.addWidget(self.save_btn)
        gen_layout.addLayout(save_row)

        layout.addWidget(general_card)

        # ========== Backup card ==========
        backup_card = self._make_card()
        bk_layout = QVBoxLayout(backup_card)
        bk_layout.setContentsMargins(22, 18, 22, 20)
        bk_layout.setSpacing(12)

        bk_header = self._card_header("📁", L("backup_settings"))
        bk_layout.addWidget(bk_header)

        backup_info = QLabel(L("backup_hint"))
        backup_info.setWordWrap(True)
        backup_info.setStyleSheet("""
            color: #64748b;
            font-size: 13px;
            background: transparent;
        """)
        bk_layout.addWidget(backup_info)

        bk_row = QHBoxLayout()
        bk_row.addStretch()
        self.backup_btn = QPushButton("📁  " + L("backup_btn").lstrip("📁 "))
        self.backup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.backup_btn.setMinimumHeight(42)
        self.backup_btn.setStyleSheet(self._success_btn_style())
        self.backup_btn.clicked.connect(self.on_backup)
        bk_row.addWidget(self.backup_btn)
        bk_layout.addLayout(bk_row)

        layout.addWidget(backup_card)

        # ========== About card ==========
        about_card = self._make_card()
        ab_layout = QVBoxLayout(about_card)
        ab_layout.setContentsMargins(22, 18, 22, 20)
        ab_layout.setSpacing(10)

        ab_header = self._card_header("ℹ️", L("about_settings"))
        ab_layout.addWidget(ab_header)

        about_text = QLabel(L("about_app_text"))
        about_text.setWordWrap(True)
        about_text.setStyleSheet("""
            color: #475569;
            font-size: 13px;
            background: transparent;
            line-height: 1.5;
        """)
        ab_layout.addWidget(about_text)

        layout.addWidget(about_card)

        layout.addStretch()

        self.load_settings()

    # ---------- Helpers ----------

    def _make_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 18))
        card.setGraphicsEffect(shadow)
        return card

    def _card_header(self, icon: str, text: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 6)
        h.setSpacing(10)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(32, 32)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("""
            background-color: #f1f5f9;
            border-radius: 8px;
            font-size: 16px;
        """)
        h.addWidget(icon_lbl)

        text_lbl = QLabel(text)
        text_lbl.setStyleSheet("""
            color: #0f172a;
            font-size: 15px;
            font-weight: bold;
            background: transparent;
        """)
        h.addWidget(text_lbl)
        h.addStretch()
        return w

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("""
            color: #334155;
            font-size: 13px;
            font-weight: bold;
            background: transparent;
        """)
        return lbl

    def _input_style(self) -> str:
        return """
            QLineEdit, QComboBox {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
            }
            QLineEdit:hover, QComboBox:hover { border: 1px solid #cbd5e1; }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #0ea5e9; }
        """

    def _primary_btn_style(self) -> str:
        return """
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0ea5e9, stop:1 #6366f1
                );
                color: white;
                border: none;
                padding: 10px 22px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0284c7, stop:1 #4f46e5
                );
            }
        """

    def _success_btn_style(self) -> str:
        return """
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #16a34a, stop:1 #22c55e
                );
                color: white;
                border: none;
                padding: 10px 22px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #15803d, stop:1 #16a34a
                );
            }
        """

    # ---------- Data ----------

    def load_settings(self):
        self.shop_name_input.setText(get_setting("shop_name", "My Phone Shop"))
        self.currency_input.setText(get_setting("currency", "MAD"))

        current_lang = get_current_language()
        idx = self.language_combo.findData(current_lang)
        if idx >= 0:
            self.language_combo.setCurrentIndex(idx)

    def on_save(self):
        L = lambda key: t(key, self.lang)
        shop_name = self.shop_name_input.text().strip() or "My Phone Shop"
        currency = self.currency_input.text().strip() or "MAD"
        language = self.language_combo.currentData()

        set_setting("shop_name", shop_name)
        set_setting("currency", currency)
        set_setting("language", language)

        QMessageBox.information(self, L("settings_saved_title"),
                                L("settings_saved_msg"))

    def on_backup(self):
        L = lambda key: t(key, self.lang)
        try:
            backups_dir = DB_PATH.parent / "backups"
            backups_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backups_dir / f"shop_backup_{timestamp}.db"
            shutil.copy2(DB_PATH, backup_file)

            QMessageBox.information(
                self, L("backup_complete"),
                L("backup_created").replace("{name}", backup_file.name)
                                   .replace("{folder}", str(backups_dir))
            )
        except Exception as e:
            QMessageBox.critical(
                self, L("backup_failed"),
                L("backup_error").replace("{err}", str(e))
            )