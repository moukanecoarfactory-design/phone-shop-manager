from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QFrame,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.core.models import Supplier
from app.locales.translations import t


class SupplierDialog(QDialog):
    """Modern Add/Edit supplier dialog."""

    def __init__(self, parent=None, supplier: Supplier = None, lang: str = "en"):
        super().__init__(parent)
        self.lang = lang
        self.supplier = supplier
        self.is_edit = supplier is not None

        L = lambda key: t(key, self.lang)

        self.setWindowTitle(L("edit_supplier_title") if self.is_edit
                            else L("add_supplier_title"))
        self.setMinimumWidth(480)

        self.setStyleSheet("QDialog { background-color: #f1f5f9; }")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)

        # Card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 14px;
                border: 1px solid #e2e8f0;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(22)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 22)
        card_layout.setSpacing(12)

        # Header
        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        icon_badge = QLabel("🏭")
        icon_badge.setFixedSize(42, 42)
        icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_badge.setStyleSheet("""
            background-color: #eef2ff;
            border-radius: 10px;
            font-size: 20px;
        """)
        title_row.addWidget(icon_badge)

        title = QLabel(L("edit_supplier_title") if self.is_edit
                       else L("add_supplier_title"))
        title.setStyleSheet("""
            color: #0f172a;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        """)
        title_row.addWidget(title)
        title_row.addStretch()
        card_layout.addLayout(title_row)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #e2e8f0; border: none;")
        card_layout.addWidget(divider)

        # Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(40)
        self.name_input.setStyleSheet(self._input_style())
        form.addRow(self._label(L("name") + " *"), self.name_input)

        self.phone_input = QLineEdit()
        self.phone_input.setMinimumHeight(40)
        self.phone_input.setStyleSheet(self._input_style())
        form.addRow(self._label(L("phone")), self.phone_input)

        self.address_input = QLineEdit()
        self.address_input.setMinimumHeight(40)
        self.address_input.setStyleSheet(self._input_style())
        form.addRow(self._label(L("address")), self.address_input)

        self.notes_input = QLineEdit()
        self.notes_input.setMinimumHeight(40)
        self.notes_input.setStyleSheet(self._input_style())
        form.addRow(self._label(L("notes")), self.notes_input)

        card_layout.addLayout(form)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel_btn = QPushButton(L("cancel"))
        cancel_btn.setMinimumHeight(42)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(self._secondary_btn_style())
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        ok_btn = QPushButton("✓  " + L("save"))
        ok_btn.setMinimumHeight(42)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.setStyleSheet(self._primary_btn_style())
        ok_btn.clicked.connect(self._on_accept)
        btn_row.addWidget(ok_btn)

        card_layout.addLayout(btn_row)

        outer.addWidget(card)

        if self.is_edit:
            self.name_input.setText(supplier.name)
            self.phone_input.setText(supplier.phone)
            self.address_input.setText(supplier.address)
            self.notes_input.setText(supplier.notes)

    # ---------- Styles ----------

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
            QLineEdit {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
            }
            QLineEdit:hover { border: 1px solid #cbd5e1; }
            QLineEdit:focus { border: 1px solid #0ea5e9; }
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
                padding: 10px 24px;
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

    def _secondary_btn_style(self) -> str:
        return """
            QPushButton {
                background-color: #ffffff;
                color: #475569;
                border: 1px solid #e2e8f0;
                padding: 8px 18px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #f8fafc; border: 1px solid #cbd5e1; }
        """

    def _on_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, t("missing_name", self.lang),
                                t("name_required_supplier", self.lang))
            return
        self.accept()

    def get_supplier(self) -> Supplier:
        return Supplier(
            id=self.supplier.id if self.is_edit else None,
            name=self.name_input.text().strip(),
            phone=self.phone_input.text().strip(),
            address=self.address_input.text().strip(),
            notes=self.notes_input.text().strip(),
        )