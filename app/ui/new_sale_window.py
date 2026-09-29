from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QLineEdit,
    QHeaderView, QAbstractItemView, QMessageBox, QFrame,
    QTabWidget, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.db.customer_repo import get_customers
from app.db.product_repo import get_products
from app.db.phone_unit_repo import get_phone_units
from app.db.sale_repo import create_sale
from app.locales.translations import t, currency


class NewSaleWindow(QDialog):
    """Window to create a new sale with a cart (products + phone units)."""

    def __init__(self, parent=None, lang: str = "en"):
        super().__init__(parent)
        self.lang = lang
        L = lambda key: t(key, self.lang)

        self.setWindowTitle(L("new_sale"))
        self.resize(1050, 680)

        self.cart = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # ---------- Customer ----------
        top = QHBoxLayout()
        top.addWidget(QLabel(L("customer") + ":"))
        self.customer_combo = QComboBox()
        self.customer_combo.addItem(L("walk_in"), None)
        for c in get_customers(limit=10000):
            self.customer_combo.addItem(f"{c.name} ({c.phone})", c.id)
        top.addWidget(self.customer_combo, 1)
        layout.addLayout(top)

        # ---------- Middle ----------
        mid = QHBoxLayout()

        # LEFT panel with tabs
        left_panel = QFrame()
        left_panel.setStyleSheet("QFrame { background: #f8fafc; border-radius: 8px; }")
        left_layout = QVBoxLayout(left_panel)

        self.tabs = QTabWidget()

        # --- Products tab ---
        products_tab = QWidget()
        pt_layout = QVBoxLayout(products_tab)
        pt_layout.setContentsMargins(6, 6, 6, 6)

        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText(L("search_products_sale"))
        self.product_search.textChanged.connect(self.on_product_search)
        pt_layout.addWidget(self.product_search)

        self.product_list = QTableWidget()
        self.product_list.setColumnCount(3)
        self.product_list.setHorizontalHeaderLabels([
            L("product"), L("sell_price"), L("qty")
        ])
        self._style_table(self.product_list, stretch_col=0)
        self.product_list.doubleClicked.connect(self.on_add_product_to_cart)
        pt_layout.addWidget(self.product_list)

        self.add_product_btn = QPushButton(L("add_product_to_cart"))
        self.add_product_btn.setStyleSheet(self._btn_style("#0ea5e9"))
        self.add_product_btn.clicked.connect(self.on_add_product_to_cart)
        pt_layout.addWidget(self.add_product_btn)

        self.tabs.addTab(products_tab, L("products_tab"))

        # --- Phone Units tab ---
        phones_tab = QWidget()
        ph_layout = QVBoxLayout(phones_tab)
        ph_layout.setContentsMargins(6, 6, 6, 6)

        self.phone_search = QLineEdit()
        self.phone_search.setPlaceholderText(L("search_phones_sale"))
        self.phone_search.textChanged.connect(self.on_phone_search)
        ph_layout.addWidget(self.phone_search)

        self.phone_list = QTableWidget()
        self.phone_list.setColumnCount(4)
        self.phone_list.setHorizontalHeaderLabels([
            L("product"), L("imei"), L("buy_price"), L("sell_price")
        ])
        self._style_table(self.phone_list, stretch_col=0)
        self.phone_list.doubleClicked.connect(self.on_add_phone_to_cart)
        ph_layout.addWidget(self.phone_list)

        self.add_phone_btn = QPushButton(L("add_phone_to_cart"))
        self.add_phone_btn.setStyleSheet(self._btn_style("#0ea5e9"))
        self.add_phone_btn.clicked.connect(self.on_add_phone_to_cart)
        ph_layout.addWidget(self.add_phone_btn)

        self.tabs.addTab(phones_tab, L("phones_tab"))

        left_layout.addWidget(self.tabs)

        mid.addWidget(left_panel, 1)

        # RIGHT: cart
        right_panel = QFrame()
        right_panel.setStyleSheet("QFrame { background: #f8fafc; border-radius: 8px; }")
        right_layout = QVBoxLayout(right_panel)

        right_layout.addWidget(QLabel(L("cart")))

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels([
            L("item"), L("qty"), L("unit_price"), L("subtotal"), L("profit")
        ])
        self._style_table(self.cart_table, stretch_col=0)
        right_layout.addWidget(self.cart_table)

        remove_row = QHBoxLayout()
        self.remove_btn = QPushButton(L("remove_selected"))
        self.remove_btn.clicked.connect(self.on_remove_from_cart)
        remove_row.addWidget(self.remove_btn)
        remove_row.addStretch()
        right_layout.addLayout(remove_row)

        # Totals
        totals_frame = QFrame()
        totals_frame.setStyleSheet("""
            QFrame {
                background: #1e293b;
                border-radius: 8px;
                padding: 8px;
            }
            QLabel { color: white; font-size: 14px; }
        """)
        totals_layout = QVBoxLayout(totals_frame)
        self.total_label = QLabel(L("total_label").replace("{total}", "0.00"))
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        totals_layout.addWidget(self.total_label)
        self.profit_label = QLabel(L("profit_label").replace("{profit}", "0.00"))
        self.profit_label.setStyleSheet("font-size: 14px; color: #86efac;")
        totals_layout.addWidget(self.profit_label)
        right_layout.addWidget(totals_frame)

        mid.addWidget(right_panel, 1)

        layout.addLayout(mid, 1)

        # ---------- Bottom ----------
        bottom = QHBoxLayout()
        bottom.addStretch()

        cancel_btn = QPushButton(L("cancel"))
        cancel_btn.clicked.connect(self.reject)
        bottom.addWidget(cancel_btn)

        self.complete_btn = QPushButton(L("complete_sale"))
        self.complete_btn.setStyleSheet(self._btn_style("#16a34a"))
        self.complete_btn.clicked.connect(self.on_complete_sale)
        bottom.addWidget(self.complete_btn)

        layout.addLayout(bottom)

        self.refresh_product_list()
        self.refresh_phone_list()
        self.refresh_cart()

    def _btn_style(self, color: str) -> str:
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 18px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {color}cc; }}
        """

    def _style_table(self, table, stretch_col=0):
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setStyleSheet("""
            QTableWidget {
                background: white;
                gridline-color: #e2e8f0;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #334155;
                color: white;
                padding: 6px;
                border: none;
            }
        """)
        hh = table.horizontalHeader()
        hh.setSectionResizeMode(stretch_col, QHeaderView.ResizeMode.Stretch)
        for col in range(1, table.columnCount()):
            hh.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)

    # ---------- Products ----------

    def on_product_search(self, text: str = ""):
        self.refresh_product_list(text)

    def refresh_product_list(self, search: str = ""):
        products = get_products(search=search, limit=200, offset=0)
        self.product_list.setRowCount(len(products))

        for row, p in enumerate(products):
            display_name = p.name
            if p.capacity:
                display_name += f" [{p.capacity}]"
            name_item = QTableWidgetItem(display_name)
            name_item.setData(Qt.ItemDataRole.UserRole, p)
            price_item = QTableWidgetItem(f"{p.selling_price:.2f}")
            stock_item = QTableWidgetItem(str(p.quantity))

            if p.quantity <= 0:
                for item in (name_item, price_item, stock_item):
                    item.setBackground(QColor("#fee2e2"))
                    item.setForeground(QColor("#991b1b"))
            elif p.is_low_stock:
                for item in (name_item, price_item, stock_item):
                    item.setBackground(QColor("#fef3c7"))
                    item.setForeground(QColor("#92400e"))

            self.product_list.setItem(row, 0, name_item)
            self.product_list.setItem(row, 1, price_item)
            self.product_list.setItem(row, 2, stock_item)
    def on_add_product_to_cart(self):
        L = lambda key: t(key, self.lang)
        rows = self.product_list.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, L("no_selection"),
                                    L("select_product_first"))
            return

        row = rows[0].row()
        product = self.product_list.item(row, 0).data(Qt.ItemDataRole.UserRole)

        if product.quantity <= 0:
            QMessageBox.warning(self, L("out_of_stock"),
                                L("no_stock_msg").replace("{name}", product.name))
            return

        for it in self.cart:
            if it.get("product_id") == product.id:
                if it["quantity"] + 1 > product.quantity:
                    QMessageBox.warning(self, L("not_enough_stock"),
                                        L("only_x_in_stock").replace("{qty}", str(product.quantity)))
                    return
                it["quantity"] += 1
                self.refresh_cart()
                return

        # Build display name with brand + capacity
        display_name = product.name
        if product.brand:
            display_name += f" ({product.brand})"
        if product.capacity:
            display_name += f" [{product.capacity}]"

        self.cart.append({
            "product_id": product.id,
            "phone_unit_id": None,
            "name": display_name,
            "quantity": 1,
            "unit_price": product.selling_price,
            "unit_cost": product.buying_price,
        })
        self.refresh_cart()

    # ---------- Phone units ----------

    def on_phone_search(self, text: str = ""):
        self.refresh_phone_list(text)

    def refresh_phone_list(self, search: str = ""):
        units = get_phone_units(search=search, status="in_stock",
                                limit=200, offset=0)
        in_cart_ids = {it.get("phone_unit_id") for it in self.cart
                       if it.get("phone_unit_id")}
        units = [u for u in units if u.id not in in_cart_ids]

        all_products = {p.id: p for p in get_products(limit=10000)}

        self.phone_list.setRowCount(len(units))
        for row, u in enumerate(units):
            product_label = "—"
            if u.product_id and u.product_id in all_products:
                p = all_products[u.product_id]
                product_label = p.name + (f" ({p.brand})" if p.brand else "")

            name_item = QTableWidgetItem(product_label)
            name_item.setData(Qt.ItemDataRole.UserRole, u)
            imei_item = QTableWidgetItem(u.imei or "—")
            buy_item = QTableWidgetItem(f"{u.buying_price:.2f}")
            sell_item = QTableWidgetItem(f"{u.selling_price:.2f}")

            for item in (name_item, imei_item, buy_item, sell_item):
                item.setBackground(QColor("#dcfce7"))
                item.setForeground(QColor("#166534"))

            self.phone_list.setItem(row, 0, name_item)
            self.phone_list.setItem(row, 1, imei_item)
            self.phone_list.setItem(row, 2, buy_item)
            self.phone_list.setItem(row, 3, sell_item)

    def on_add_phone_to_cart(self):
        L = lambda key: t(key, self.lang)
        rows = self.phone_list.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, L("no_selection"),
                                    L("select_phone_first"))
            return

        row = rows[0].row()
        unit = self.phone_list.item(row, 0).data(Qt.ItemDataRole.UserRole)

        name = f"📱 IMEI: {unit.imei or '?'}"
        if unit.product_id:
            for p in get_products(limit=10000):
                if p.id == unit.product_id:
                    name = f"📱 {p.name}"
                    if unit.imei:
                        name += f" (IMEI: {unit.imei})"
                    break

        self.cart.append({
            "product_id": None,
            "phone_unit_id": unit.id,
            "name": name,
            "quantity": 1,
            "unit_price": unit.selling_price,
            "unit_cost": unit.buying_price,
        })
        self.refresh_cart()
        self.refresh_phone_list(self.phone_search.text().strip())

    # ---------- Cart ----------

    def refresh_cart(self):
        L = lambda key: t(key, self.lang)
        self.cart_table.setRowCount(len(self.cart))
        total = 0.0
        profit = 0.0

        for row, it in enumerate(self.cart):
            subtotal = it["unit_price"] * it["quantity"]
            item_profit = (it["unit_price"] - it["unit_cost"]) * it["quantity"]
            total += subtotal
            profit += item_profit

            self.cart_table.setItem(row, 0, QTableWidgetItem(it["name"]))
            self.cart_table.setItem(row, 1, QTableWidgetItem(str(it["quantity"])))
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"{it['unit_price']:.2f}"))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{subtotal:.2f}"))
            self.cart_table.setItem(row, 4, QTableWidgetItem(f"{item_profit:.2f}"))

        self.total_label.setText(
            L("total_label").replace("{total}", f"{total:.2f}")
        )
        self.profit_label.setText(
            L("profit_label").replace("{profit}", f"{profit:.2f}")
        )

    def on_remove_from_cart(self):
        rows = self.cart_table.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        removed = self.cart[row]
        del self.cart[row]
        self.refresh_cart()
        if removed.get("phone_unit_id"):
            self.refresh_phone_list(self.phone_search.text().strip())

    # ---------- Complete ----------

    def on_complete_sale(self):
        L = lambda key: t(key, self.lang)
        if not self.cart:
            QMessageBox.warning(self, L("empty_cart"), L("empty_cart_msg"))
            return

        customer_id = self.customer_combo.currentData()

        try:
            sale_id = create_sale(customer_id, self.cart)
        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 f"{L('could_not_save')}\n{e}")
            return

        QMessageBox.information(self, L("sale_completed"),
                                L("sale_completed_msg").replace("{id}", str(sale_id)))
        self.accept()
