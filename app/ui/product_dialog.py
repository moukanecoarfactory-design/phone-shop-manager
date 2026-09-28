import shutil
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox,
    QSpinBox, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QMessageBox, QFrame,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QColor

from app.core.models import Product
from app.db.product_repo import get_all_categories
from app.locales.translations import t, currency


def _get_images_dir() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent.parent.parent
    d = base / "data" / "images"
    d.mkdir(parents=True, exist_ok=True)
    return d


IMAGES_DIR = _get_images_dir()


class ProductDialog(QDialog):
    """Modern Add/Edit product dialog."""

    def __init__(self, parent=None, product: Product = None, lang: str = "en"):
        super().__init__(parent)
        self.lang = lang
        self.product = product
        self.is_edit = product is not None
        self.selected_image_path = product.image_path if self.is_edit else ""

        L = lambda key: t(key, self.lang)
        C = currency(self.lang)

        self.setWindowTitle(L("edit_product_title") if self.is_edit
                            else L("add_product_title"))
        self.setMinimumWidth(560)

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

        # Icon + title
        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        icon_badge = QLabel("📦")
        icon_badge.setFixedSize(42, 42)
        icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_badge.setStyleSheet("""
            background-color: #eef2ff;
            border-radius: 10px;
            font-size: 20px;
        """)
        title_row.addWidget(icon_badge)

        title = QLabel(L("edit_product_title") if self.is_edit
                       else L("add_product_title"))
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

        # ---------- Image picker row ----------
        image_row = QHBoxLayout()
        image_row.setSpacing(12)

        self.image_preview = QLabel(L("no_image"))
        self.image_preview.setFixedSize(120, 120)
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setStyleSheet(self._image_placeholder_style())
        image_row.addWidget(self.image_preview)

        img_btns = QVBoxLayout()
        img_btns.setSpacing(8)

        self.choose_img_btn = QPushButton("📷  " + L("choose_image").lstrip("📷 "))
        self.choose_img_btn.setMinimumHeight(38)
        self.choose_img_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.choose_img_btn.setStyleSheet(self._secondary_btn_style())
        self.choose_img_btn.clicked.connect(self.on_choose_image)
        img_btns.addWidget(self.choose_img_btn)

        self.clear_img_btn = QPushButton("🗑  " + L("remove_image").lstrip("🗑 "))
        self.clear_img_btn.setMinimumHeight(38)
        self.clear_img_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_img_btn.setStyleSheet(self._danger_btn_style())
        self.clear_img_btn.clicked.connect(self.on_clear_image)
        img_btns.addWidget(self.clear_img_btn)

        img_btns.addStretch()
        image_row.addLayout(img_btns)
        image_row.addStretch()
        card_layout.addLayout(image_row)

        # ---------- Form ----------
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setMinimumHeight(40)
        self.name_input.setStyleSheet(self._input_style())
        form.addRow(self._label(L("name") + " *"), self.name_input)

        self.category_combo = QComboBox()
        self.category_combo.setMinimumHeight(40)
        self.category_combo.setStyleSheet(self._input_style())
        self.category_combo.addItem("— " + L("category") + " —", None)
        for cat in get_all_categories():
            self.category_combo.addItem(cat.display_name(lang), cat.id)
        form.addRow(self._label(L("category")), self.category_combo)

        self.brand_input = QLineEdit()
        self.brand_input.setMinimumHeight(40)
        self.brand_input.setStyleSheet(self._input_style())
        form.addRow(self._label(L("brand")), self.brand_input)

        # --- Price row (side by side) ---
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
        price_container.addWidget(self._label(L("buying_price")))
        price_container.addLayout(price_row)
        form.addRow("", self._wrap_row(price_container))

        # --- Qty row ---
        qty_row = QHBoxLayout()
        qty_row.setSpacing(10)

        self.qty_input = QSpinBox()
        self.qty_input.setMaximum(999999)
        self.qty_input.setMinimumHeight(40)
        self.qty_input.setStyleSheet(self._input_style())
        qty_row.addWidget(self.qty_input)

        self.low_stock_input = QSpinBox()
        self.low_stock_input.setMaximum(9999)
        self.low_stock_input.setValue(5)
        self.low_stock_input.setMinimumHeight(40)
        self.low_stock_input.setStyleSheet(self._input_style())
        qty_row.addWidget(self.low_stock_input)

        qty_container = QHBoxLayout()
        qty_container.addWidget(self._label(L("quantity") + " / " + L("low_stock_alert")))
        qty_container.addLayout(qty_row)
        form.addRow("", self._wrap_row(qty_container))

        self.barcode_input = QLineEdit()
        self.barcode_input.setMinimumHeight(40)
        self.barcode_input.setStyleSheet(self._input_style())
        form.addRow(self._label(L("barcode")), self.barcode_input)

        self.notes_input = QLineEdit()
        self.notes_input.setMinimumHeight(40)
        self.notes_input.setStyleSheet(self._input_style())
        form.addRow(self._label(L("notes")), self.notes_input)

        card_layout.addLayout(form)

        # ---------- Buttons ----------
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
            self._load_product(product)

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
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
            }
            QLineEdit:hover, QComboBox:hover,
            QSpinBox:hover, QDoubleSpinBox:hover { border: 1px solid #cbd5e1; }
            QLineEdit:focus, QComboBox:focus,
            QSpinBox:focus, QDoubleSpinBox:focus { border: 1px solid #0ea5e9; }
        """

    def _image_placeholder_style(self) -> str:
        return """
            border: 2px dashed #cbd5e1;
            border-radius: 10px;
            color: #94a3b8;
            background-color: #f8fafc;
            font-size: 12px;
        """

    def _image_loaded_style(self) -> str:
        return """
            border: 2px solid #0ea5e9;
            border-radius: 10px;
            background-color: white;
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

    def _danger_btn_style(self) -> str:
        return """
            QPushButton {
                background-color: #ffffff;
                color: #dc2626;
                border: 1px solid #fecaca;
                padding: 8px 18px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #fef2f2; border: 1px solid #fca5a5; }
        """

    # ---------- Load ----------

    def _load_product(self, p: Product):
        self.name_input.setText(p.name)
        if p.category_id is not None:
            idx = self.category_combo.findData(p.category_id)
            if idx >= 0:
                self.category_combo.setCurrentIndex(idx)
        self.brand_input.setText(p.brand)
        self.buying_input.setValue(p.buying_price)
        self.selling_input.setValue(p.selling_price)
        self.qty_input.setValue(p.quantity)
        self.low_stock_input.setValue(p.low_stock_alert)
        self.barcode_input.setText(p.barcode)
        self.notes_input.setText(p.notes)

        if p.image_path:
            self.selected_image_path = p.image_path
            self._update_preview()

    def _update_preview(self):
        L = lambda key: t(key, self.lang)
        if self.selected_image_path and Path(self.selected_image_path).exists():
            pix = QPixmap(self.selected_image_path)
            if not pix.isNull():
                pix = pix.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)
                self.image_preview.setPixmap(pix)
                self.image_preview.setStyleSheet(self._image_loaded_style())
                return
        self.image_preview.setText(L("no_image"))
        self.image_preview.setPixmap(QPixmap())
        self.image_preview.setStyleSheet(self._image_placeholder_style())

    def on_choose_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, t("choose_image", self.lang), "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if not file_path:
            return

        src = Path(file_path)
        dest = IMAGES_DIR / src.name
        counter = 1
        while dest.exists() and dest.resolve() != src.resolve():
            dest = IMAGES_DIR / f"{src.stem}_{counter}{src.suffix}"
            counter += 1

        try:
            if src.resolve() != dest.resolve():
                shutil.copy2(src, dest)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not copy image:\n{e}")
            return

        self.selected_image_path = str(dest)
        self._update_preview()

    def on_clear_image(self):
        self.selected_image_path = ""
        self._update_preview()

    def _on_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, t("missing_name", self.lang),
                                t("name_required", self.lang))
            return
        self.accept()

    def get_product(self) -> Product:
        return Product(
            id=self.product.id if self.is_edit else None,
            name=self.name_input.text().strip(),
            category_id=self.category_combo.currentData(),
            brand=self.brand_input.text().strip(),
            buying_price=self.buying_input.value(),
            selling_price=self.selling_input.value(),
            quantity=self.qty_input.value(),
            low_stock_alert=self.low_stock_input.value(),
            barcode=self.barcode_input.text().strip(),
            notes=self.notes_input.text().strip(),
            image_path=self.selected_image_path or "",
        )