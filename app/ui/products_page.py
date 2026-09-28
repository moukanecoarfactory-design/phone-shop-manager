from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QMessageBox, QHeaderView, QAbstractItemView, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPixmap, QIcon

from app.db.product_repo import (
    get_products, count_products, add_product,
    update_product, delete_product, get_all_categories, get_product
)
from app.ui.product_dialog import ProductDialog
from app.locales.translations import t


PAGE_SIZE = 50
THUMB_SIZE = 48


class ProductsPage(QWidget):
    def __init__(self, lang: str = "en", is_admin: bool = True):
        super().__init__()
        self.lang = lang
        self.is_admin = is_admin
        self.current_page = 0
        self.total_count = 0

        L = lambda key: t(key, self.lang)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # ========== Header ==========
        header = QHBoxLayout()

        title = QLabel(L("products"))
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #0f172a;
            background: transparent;
        """)
        header.addWidget(title)
        header.addStretch()

        self.add_btn = QPushButton("＋  " + L("add_product").lstrip("+ "))
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setMinimumHeight(40)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0ea5e9, stop:1 #6366f1
                );
                color: white;
                border: none;
                padding: 10px 20px;
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
        """)
        self.add_btn.clicked.connect(self.on_add)
        self.add_btn.setVisible(self.is_admin)
        header.addWidget(self.add_btn)

        layout.addLayout(header)

        # ========== Filters ==========
        filters = QHBoxLayout()
        filters.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  " + L("search_products"))
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet(self._input_style())
        self.search_input.textChanged.connect(self.on_search_changed)
        filters.addWidget(self.search_input, 2)

        self.category_filter = QComboBox()
        self.category_filter.setMinimumHeight(40)
        self.category_filter.setStyleSheet(self._input_style())
        self.category_filter.addItem(L("all_categories"), None)
        for cat in get_all_categories():
            self.category_filter.addItem(cat.display_name(lang), cat.id)
        self.category_filter.currentIndexChanged.connect(self.on_search_changed)
        filters.addWidget(self.category_filter, 1)

        layout.addLayout(filters)

        # ========== Table container (rounded card) ==========
        table_card = QFrame()
        table_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            L("image"), L("id"), L("name"), L("category"), L("brand"),
            L("buy_price"), L("sell_price"), L("qty"), L("profit")
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setIconSize(QSize(THUMB_SIZE, THUMB_SIZE))
        if self.is_admin:
            self.table.doubleClicked.connect(self.on_edit)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 12px;
                font-size: 13px;
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #475569;
                padding: 12px 8px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-weight: bold;
                font-size: 11px;
                text-transform: uppercase;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                background-color: #eef2ff;
                color: #0f172a;
            }
        """)

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 66)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        for col in [1, 3, 4, 5, 6, 7, 8]:
            hh.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(THUMB_SIZE + 18)

        table_layout.addWidget(self.table)

        layout.addWidget(table_card, 1)

        # ========== Bottom bar ==========
        bottom = QHBoxLayout()
        bottom.setSpacing(8)

        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedSize(40, 40)
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.setStyleSheet(self._pagination_style())
        self.prev_btn.clicked.connect(self.on_prev)
        bottom.addWidget(self.prev_btn)

        self.page_label = QLabel(f"{L('page')} 1")
        self.page_label.setStyleSheet("""
            color: #475569;
            font-size: 13px;
            font-weight: bold;
            padding: 8px 14px;
        """)
        bottom.addWidget(self.page_label)

        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedSize(40, 40)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.setStyleSheet(self._pagination_style())
        self.next_btn.clicked.connect(self.on_next)
        bottom.addWidget(self.next_btn)

        bottom.addStretch()

        self.edit_btn = QPushButton("✏  " + L("edit_product").lstrip("✏ "))
        self.edit_btn.setMinimumHeight(40)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setStyleSheet(self._secondary_btn_style())
        self.edit_btn.clicked.connect(self.on_edit)
        self.edit_btn.setVisible(self.is_admin)
        bottom.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑  " + L("delete_product").lstrip("🗑 "))
        self.delete_btn.setMinimumHeight(40)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet(self._danger_btn_style())
        self.delete_btn.clicked.connect(self.on_delete)
        self.delete_btn.setVisible(self.is_admin)
        bottom.addWidget(self.delete_btn)

        layout.addLayout(bottom)

        self.refresh()

    # ---------- Styles ----------

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
            QLineEdit:hover, QComboBox:hover {
                border: 1px solid #cbd5e1;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #0ea5e9;
            }
        """

    def _pagination_style(self) -> str:
        return """
            QPushButton {
                background-color: #f8fafc;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #e2e8f0; }
            QPushButton:disabled { color: #cbd5e1; }
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
            QPushButton:hover {
                background-color: #f8fafc;
                border: 1px solid #cbd5e1;
            }
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
            QPushButton:hover {
                background-color: #fef2f2;
                border: 1px solid #fca5a5;
            }
        """

    # ---------- Data ----------

    def refresh(self):
        search = self.search_input.text().strip()
        cat_id = self.category_filter.currentData()

        self.total_count = count_products(search, cat_id)
        products = get_products(
            search=search, category_id=cat_id,
            limit=PAGE_SIZE, offset=self.current_page * PAGE_SIZE
        )

        self.table.setRowCount(len(products))
        categories = {c.id: c.display_name(self.lang) for c in get_all_categories()}

        for row, p in enumerate(products):
            cat_name = categories.get(p.category_id, "—")

            img_item = QTableWidgetItem()
            if p.image_path and Path(p.image_path).exists():
                pix = QPixmap(p.image_path)
                if not pix.isNull():
                    scaled = pix.scaled(THUMB_SIZE, THUMB_SIZE,
                                        Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
                    img_item.setIcon(QIcon(scaled))
            img_item.setData(Qt.ItemDataRole.UserRole, p.id)
            self.table.setItem(row, 0, img_item)

            id_item = QTableWidgetItem(str(p.id))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, id_item)

            self.table.setItem(row, 2, QTableWidgetItem(p.name))
            self.table.setItem(row, 3, QTableWidgetItem(cat_name))
            self.table.setItem(row, 4, QTableWidgetItem(p.brand))
            self.table.setItem(row, 5, QTableWidgetItem(f"{p.buying_price:.2f}"))
            self.table.setItem(row, 6, QTableWidgetItem(f"{p.selling_price:.2f}"))

            qty_item = QTableWidgetItem(str(p.quantity))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 7, qty_item)

            profit_item = QTableWidgetItem(f"{p.profit:.2f}")
            profit_item.setForeground(QColor("#16a34a"))
            self.table.setItem(row, 8, profit_item)

            if p.is_low_stock:
                for col in range(1, 9):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor("#fef2f2"))
                        item.setForeground(QColor("#991b1b"))

        self._update_pagination_ui()

    def _update_pagination_ui(self):
        L = lambda key: t(key, self.lang)
        total_pages = max(1, (self.total_count + PAGE_SIZE - 1) // PAGE_SIZE)
        self.page_label.setText(
            f"{L('page')} {self.current_page + 1} / {total_pages}"
            f"  ·  {self.total_count} {L('products_label')}"
        )
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled((self.current_page + 1) * PAGE_SIZE < self.total_count)

    def on_search_changed(self):
        self.current_page = 0
        self.refresh()

    def on_prev(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.refresh()

    def on_next(self):
        if (self.current_page + 1) * PAGE_SIZE < self.total_count:
            self.current_page += 1
            self.refresh()

    def _selected_product_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return self.table.item(rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)

    def on_add(self):
        if not self.is_admin:
            return
        dlg = ProductDialog(self, product=None, lang=self.lang)
        if dlg.exec():
            add_product(dlg.get_product())
            self.refresh()

    def on_edit(self):
        if not self.is_admin:
            return
        L = lambda key: t(key, self.lang)
        pid = self._selected_product_id()
        if pid is None:
            QMessageBox.information(self, L("no_selection"),
                                    L("select_product_first"))
            return
        p = get_product(pid)
        if not p:
            return
        dlg = ProductDialog(self, product=p, lang=self.lang)
        if dlg.exec():
            update_product(dlg.get_product())
            self.refresh()

    def on_delete(self):
        if not self.is_admin:
            return
        L = lambda key: t(key, self.lang)
        pid = self._selected_product_id()
        if pid is None:
            QMessageBox.information(self, L("no_selection"),
                                    L("select_product_first"))
            return

        p = get_product(pid)
        confirm = QMessageBox.question(
            self, L("confirm_delete"),
            L("delete_confirm_msg").format(name=p.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            delete_product(pid)
            self.refresh()