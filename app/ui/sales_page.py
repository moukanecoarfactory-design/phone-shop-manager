from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.db.sale_repo import (
    get_sales, count_sales, delete_sale, get_sale, get_sale_items
)
from app.ui.new_sale_window import NewSaleWindow
from app.locales.translations import t, currency
from app.ui.receipt_dialog import ReceiptDialog


PAGE_SIZE = 50


class SalesPage(QWidget):
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

        title = QLabel(L("sales_title"))
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #0f172a;
            background: transparent;
        """)
        header.addWidget(title)
        header.addStretch()

        # New Sale button (both admin + cashier)
        self.new_btn = QPushButton("🛒  " + L("new_sale").lstrip("+ "))
        self.new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_btn.setMinimumHeight(42)
        self.new_btn.setStyleSheet(self._primary_btn_style())
        self.new_btn.clicked.connect(self.on_new_sale)
        header.addWidget(self.new_btn)

        layout.addLayout(header)

        # ========== Search ==========
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  " + L("search_sales"))
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet(self._input_style())
        self.search_input.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search_input)

        # ========== Table card ==========
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            L("sale_number"), L("date"), L("customer"),
            L("total_mad"), L("profit_mad"), L("notes")
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.doubleClicked.connect(self.on_view)
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
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        for col in [0, 1, 3, 4]:
            hh.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(44)

        table_layout.addWidget(self.table)
        layout.addWidget(table_card, 1)

        # ========== Bottom ==========
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

        # View button (everyone)
        self.view_btn = QPushButton("👁  " + L("view").lstrip("👁 "))
        self.view_btn.setMinimumHeight(40)
        self.view_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_btn.setStyleSheet(self._secondary_btn_style())
        self.view_btn.clicked.connect(self.on_view)
        bottom.addWidget(self.view_btn)

        # Delete button (admin only)
        self.delete_btn = QPushButton("🗑  " + L("delete_sale").lstrip("🗑 "))
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

    # ---------- Data ----------

    def refresh(self):
        L = lambda key: t(key, self.lang)
        search = self.search_input.text().strip()
        self.total_count = count_sales(search)
        sales = get_sales(search, PAGE_SIZE, self.current_page * PAGE_SIZE)

        self.table.setRowCount(len(sales))
        for row, s in enumerate(sales):
            id_item = QTableWidgetItem(str(s["id"]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, id_item)

            date_item = QTableWidgetItem(str(s["sale_date"]))
            self.table.setItem(row, 1, date_item)

            self.table.setItem(row, 2, QTableWidgetItem(s["customer_name"] or "-"))

            total_item = QTableWidgetItem(f"{s['total']:.2f}")
            total_item.setForeground(QColor("#0ea5e9"))
            self.table.setItem(row, 3, total_item)

            profit_item = QTableWidgetItem(f"{s['profit']:.2f}")
            profit_item.setForeground(QColor("#16a34a"))
            self.table.setItem(row, 4, profit_item)

            self.table.setItem(row, 5, QTableWidgetItem(s["notes"] or ""))
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, s["id"])

        self._update_pagination_ui()

    def _update_pagination_ui(self):
        L = lambda key: t(key, self.lang)
        total_pages = max(1, (self.total_count + PAGE_SIZE - 1) // PAGE_SIZE)
        self.page_label.setText(
            f"{L('page')} {self.current_page + 1} / {total_pages}"
            f"  ·  {self.total_count} {L('sales_label')}"
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

    def _selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return self.table.item(rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)

    def on_new_sale(self):
        dlg = NewSaleWindow(self, lang=self.lang)
        if dlg.exec():
            self.refresh()

    def on_view(self):
        L = lambda key: t(key, self.lang)
        C = currency(self.lang)
        sale_id = self._selected_id()
        if sale_id is None:
            QMessageBox.information(self, L("no_selection"),
                                    L("select_sale_first"))
            return

        sale = get_sale(sale_id)
        items_raw = get_sale_items(sale_id)

        receipt_items = []
        for it in items_raw:
            if it["product_name"]:
                name = it["product_name"]
                if it["product_brand"]:
                    name += " (" + it["product_brand"] + ")"
                qty = it["quantity"]
            elif it["phone_imei"]:
                name = "IMEI: " + it["phone_imei"]
                qty = 1
            else:
                name = "?"
                qty = it["quantity"]

            receipt_items.append({
                "name": name,
                "qty": qty,
                "price": it["unit_price"],
                "subtotal": it["unit_price"] * qty,
            })

        receipt = ReceiptDialog(
            self,
            sale=sale,
            items=receipt_items,
            customer_name=sale.get("customer_name") or "",
            cashier_name="admin",
            lang=self.lang,
            currency_symbol=C,
            change=0.0,
        )
        receipt.exec()
   

    def on_delete(self):
        if not self.is_admin:
            return
        L = lambda key: t(key, self.lang)
        sale_id = self._selected_id()
        if sale_id is None:
            QMessageBox.information(self, L("no_selection"),
                                    L("select_sale_first"))
            return
        confirm = QMessageBox.question(
            self, L("confirm_delete"),
            L("delete_sale_confirm").format(id=sale_id),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            delete_sale(sale_id)
            self.refresh()