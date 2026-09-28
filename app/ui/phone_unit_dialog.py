from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox,
    QFrame, QWidget, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.core.models import PhoneUnit
from app.db.product_repo import get_products
from app.db.supplier_repo import get_suppliers
from app.db.phone_unit_repo import imei_exists
from app.locales.translations import t, currency


class PhoneUnitDialog(QDialog):
    """Modern Add/Edit phone unit dialog."""

    def __init__(self, parent=None, unit: PhoneUnit = None, lang: str = "en"):
        super().__init__(parent)
        self.lang = lang
        self.unit = unit
        self.is_edit = unit is not None

        L = lambda key: t(key, self.lang)
        C = currency(self.lang)

        self.setWindowTitle(L("edit_phone_unit_title") if self.is_edit
                            else L("add_phone_unit_title"))
        self.setMinimumWidth(520)

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

        icon_badge = QLabel("📱")
        icon_badge.setFixedSize(42, 42)
        icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_badge.setStyleSheet("""
            background-color: #eef2ff;
            border-radius: 10px;
            font-size: 20px;
        """)
        title_row.addWidget(icon_badge)

        title = QLabel(L("edit_phone_unit_title") if self.is_edit
                       else L("add_phone_unit_title"))
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

        # Product
        self.product_combo = QComboBox()
        self.product_combo.setMinimumHeight(40)
        self.product_combo.setStyleSheet(self._input_style())
        self.product_combo.addItem(L("select_product"), None)
        for p in get_products(limit=10000):
            label = p.name + (f" ({p.brand})" if p.brand else "")
            self.product_combo.addItem(label, p.id)
        form.addRow(self._label(L("product_label") + " *"), self.product_combo)

        # IMEI
        self.imei_input = QLineEdit()
        self.imei_input.setPlaceholderText(L("imei"))
        self.imei_input.setMinimumHeight(40)
        self.imei_input.setStyleSheet(self._input_style())
        form.addRow(self._label(L("imei")), self.imei_input)

        # Prices side by side
        price_row = QHBoxLayout()
        price_row.setSpacing(10)

        self.buying_input = QDoubleSpinBox()
        self.buying_input.setMaximum(999999)
        self.buying_input.setDecimals(2)
        self.buying_input.setSuffix(" " + C)
        self.buying_input.setMinimumHeight(40)
        self.buying_input.setStyleSheet(self._input_style())
        price_row.addWidget(self.buying_input)

        self.selling_input = QDoubleSpinBox()
        self.selling_input.setMaximum(999999)
        self.selling_input.setDecimals(2)
        self.selling_input.setSuffix(" " + C)
        self.selling_input.setMinimumHeight(40)
        self.selling_input.setStyleSheet(self._input_style())
        price_row.addWidget(self.selling_input)

        price_container = QHBoxLayout()
        price_container.addWidget(self._label(L("buying_price") + " / " + L("selling_price")))
        price_container.addLayout(price_row)
        form.addRow("", self._wrap_row(price_container))

        # Status
        self.status_combo = QComboBox()
        self.status_combo.setMinimumHeight(40)
        self.status_combo.setStyleSheet(self._input_style())
        self.status_combo.addItem("🟢  " + L("in_stock"), "in_stock")
        self.status_combo.addItem("🔴  " + L("sold"), "sold")
        self.status_combo.addItem("🟡  " + L("returned"), "returned")
        form.addRow(self._label(L("status")), self.status_combo)

        # Supplier
        self.supplier_combo = QComboBox()
        self.supplier_combo.setMinimumHeight(40)
        self.supplier_combo.setStyleSheet(self._input_style())
        self.supplier_combo.addItem(L("none"), None)
        for s in get_suppliers(limit=10000):
            self.supplier_combo.addItem(s.name, s.id)
        form.addRow(self._label(L("supplier")), self.supplier_combo)

        # Notes
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
            self._load_unit(unit)

    # ---------- Helpers ----------

    def _wrap_row(self, inner_layout) -> QWidget:
        w = QWidget()
        w.setLayout(inner_layout)
        w.setStyleSheet("background: transparent;")
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
            QLineEdit, QComboBox, QDoubleSpinBox {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
            }
            QLineEdit:hover, QComboBox:hover,
            QDoubleSpinBox:hover { border: 1px solid #cbd5e1; }
            QLineEdit:focus, QComboBox:focus,
            QDoubleSpinBox:focus { border: 1px solid #0ea5e9; }
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

    # ---------- Load / Save ----------

    def _load_unit(self, u: PhoneUnit):
        if u.product_id is not None:
            idx = self.product_combo.findData(u.product_id)
            if idx >= 0:
                self.product_combo.setCurrentIndex(idx)
        self.imei_input.setText(u.imei)
        self.buying_input.setValue(u.buying_price)
        self.selling_input.setValue(u.selling_price)

        idx = self.status_combo.findData(u.status)
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)

        if u.supplier_id is not None:
            idx = self.supplier_combo.findData(u.supplier_id)
            if idx >= 0:
                self.supplier_combo.setCurrentIndex(idx)

        self.notes_input.setText(u.notes)

    def _on_accept(self):
        L = lambda key: t(key, self.lang)
        if self.product_combo.currentData() is None:
            QMessageBox.warning(self, L("missing_name"),
                                L("select_product_first_msg"))
            return

        imei = self.imei_input.text().strip()
        exclude = self.unit.id if self.is_edit else None
        if imei and imei_exists(imei, exclude):
            QMessageBox.warning(self, L("duplicate_imei"),
                                L("imei_already_used").format(imei=imei))
            return

        self.accept()

    def get_unit(self) -> PhoneUnit:
        return PhoneUnit(
            id=self.unit.id if self.is_edit else None,
            product_id=self.product_combo.currentData(),
            imei=self.imei_input.text().strip(),
            buying_price=self.buying_input.value(),
            selling_price=self.selling_input.value(),
            status=self.status_combo.currentData(),
            supplier_id=self.supplier_combo.currentData(),
            notes=self.notes_input.text().strip(),
        )