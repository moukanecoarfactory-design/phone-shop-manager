from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDateEdit, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QTabWidget, QGraphicsDropShadowEffect,
    QMenu, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QAction

from app.db.report_repo import (
    get_sales_summary, get_sales_in_range, get_daily_breakdown,
    get_top_products_in_range, get_phones_sold_in_range
)
from app.db.product_repo import get_products, get_all_categories
from app.db.customer_repo import get_customers
from app.db.phone_unit_repo import get_phone_units
from app.db.payment_repo import get_all_debts, get_customer_debt
from app.core.export_utils import (
    export_sales, export_products, export_customers,
    export_phone_units, export_debts, open_file
)
from app.locales.translations import t, currency


class ReportsPage(QWidget):
    def __init__(self, lang: str = "en"):
        super().__init__()
        self.lang = lang
        L = lambda key: t(key, self.lang)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # ========== Header with Export button ==========
        header = QHBoxLayout()

        title = QLabel(L("reports_title"))
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #0f172a;
            background: transparent;
        """)
        header.addWidget(title)
        header.addStretch()

        # Export button with dropdown
        self.export_btn = QPushButton("📥  " + L("export"))
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.setMinimumHeight(42)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #16a34a, stop:1 #22c55e
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
                    stop:0 #15803d, stop:1 #16a34a
                );
            }
            QPushButton::menu-indicator { image: none; }
        """)
        self.export_btn.clicked.connect(self.show_export_menu)
        header.addWidget(self.export_btn)

        layout.addLayout(header)

        # ========== Date range card ==========
        date_card = QFrame()
        date_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        date_layout = QHBoxLayout(date_card)
        date_layout.setContentsMargins(18, 14, 18, 14)
        date_layout.setSpacing(10)

        from_lbl = QLabel(L("from_date"))
        from_lbl.setStyleSheet("color: #475569; font-weight: bold; font-size: 12px;")
        date_layout.addWidget(from_lbl)

        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.from_date.setMinimumHeight(38)
        self.from_date.setStyleSheet(self._date_style())
        date_layout.addWidget(self.from_date)

        date_layout.addSpacing(6)

        to_lbl = QLabel(L("to_date"))
        to_lbl.setStyleSheet("color: #475569; font-weight: bold; font-size: 12px;")
        date_layout.addWidget(to_lbl)

        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setMinimumHeight(38)
        self.to_date.setStyleSheet(self._date_style())
        date_layout.addWidget(self.to_date)

        date_layout.addSpacing(14)

        for label_key, days_back in [
            ("today_btn", 0),
            ("days_7", 7),
            ("days_30", 30),
            ("days_90", 90),
        ]:
            btn = QPushButton(L(label_key))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(38)
            btn.setStyleSheet(self._quick_btn_style())
            btn.clicked.connect(
                lambda checked=False, d=days_back: self._set_quick_range(d)
            )
            date_layout.addWidget(btn)

        date_layout.addStretch()

        apply_btn = QPushButton("🔍  " + L("apply").lstrip("🔍 "))
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.setMinimumHeight(40)
        apply_btn.setStyleSheet(self._primary_btn_style())
        apply_btn.clicked.connect(self.refresh)
        date_layout.addWidget(apply_btn)

        layout.addWidget(date_card)

        # ========== Summary cards ==========
        self.summary_layout = QHBoxLayout()
        self.summary_layout.setSpacing(14)
        layout.addLayout(self.summary_layout)

        # ========== Tabs ==========
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background-color: white;
                top: -1px;
            }
            QTabBar::tab {
                background-color: #f8fafc;
                color: #64748b;
                padding: 10px 22px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #e2e8f0;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #0ea5e9;
                border-bottom: 2px solid white;
            }
            QTabBar::tab:hover {
                background-color: #eef2ff;
                color: #4f46e5;
            }
        """)

        # Sales tab
        sales_tab = QWidget()
        st_layout = QVBoxLayout(sales_tab)
        st_layout.setContentsMargins(4, 4, 4, 4)
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels([
            L("sale_number"), L("date_col"), L("customer"),
            L("total_mad"), L("profit_mad")
        ])
        self._style_table(self.sales_table, stretch_col=2)
        st_layout.addWidget(self.sales_table)
        self.tabs.addTab(sales_tab, "  " + L("tab_sales") + "  ")

        # Daily tab
        daily_tab = QWidget()
        dt_layout = QVBoxLayout(daily_tab)
        dt_layout.setContentsMargins(4, 4, 4, 4)
        self.daily_table = QTableWidget()
        self.daily_table.setColumnCount(4)
        self.daily_table.setHorizontalHeaderLabels([
            L("date_col"), L("sales_col"), L("profit_col"), L("transactions_col")
        ])
        self._style_table(self.daily_table, stretch_col=0)
        dt_layout.addWidget(self.daily_table)
        self.tabs.addTab(daily_tab, "  " + L("tab_daily") + "  ")

        # Top products tab
        top_tab = QWidget()
        tt_layout = QVBoxLayout(top_tab)
        tt_layout.setContentsMargins(4, 4, 4, 4)
        self.top_table = QTableWidget()
        self.top_table.setColumnCount(5)
        self.top_table.setHorizontalHeaderLabels([
            L("product"), L("brand"), L("qty_sold_col"),
            L("revenue_col"), L("profit_col")
        ])
        self._style_table(self.top_table, stretch_col=0)
        tt_layout.addWidget(self.top_table)
        self.tabs.addTab(top_tab, "  " + L("tab_top_products") + "  ")

        # Phones sold tab
        phones_tab = QWidget()
        pt_layout = QVBoxLayout(phones_tab)
        pt_layout.setContentsMargins(4, 4, 4, 4)
        self.phones_table = QTableWidget()
        self.phones_table.setColumnCount(5)
        self.phones_table.setHorizontalHeaderLabels([
            L("product"), L("imei"), L("buy_price_col"),
            L("sell_price_col"), L("date_sold_col")
        ])
        self._style_table(self.phones_table, stretch_col=0)
        pt_layout.addWidget(self.phones_table)
        self.tabs.addTab(phones_tab, "  " + L("tab_phones_sold") + "  ")

        layout.addWidget(self.tabs, 1)

        self.refresh()

    # ---------- Styles ----------

    def _date_style(self) -> str:
        return """
            QDateEdit {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QDateEdit:hover { border: 1px solid #cbd5e1; }
            QDateEdit:focus { border: 1px solid #0ea5e9; }
        """

    def _quick_btn_style(self) -> str:
        return """
            QPushButton {
                background-color: #f8fafc;
                color: #475569;
                border: 1px solid #e2e8f0;
                padding: 6px 16px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #eef2ff;
                color: #4f46e5;
                border: 1px solid #c7d2fe;
            }
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

    def _style_table(self, table, stretch_col=0):
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setShowGrid(False)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: none;
                border-radius: 8px;
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
        hh = table.horizontalHeader()
        hh.setSectionResizeMode(stretch_col, QHeaderView.ResizeMode.Stretch)
        for col in range(table.columnCount()):
            if col != stretch_col:
                hh.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        table.verticalHeader().setDefaultSectionSize(40)

    # ---------- Quick ranges ----------

    def _set_quick_range(self, days_back: int):
        today = QDate.currentDate()
        if days_back == 0:
            self.from_date.setDate(today)
        else:
            self.from_date.setDate(today.addDays(-days_back + 1))
        self.to_date.setDate(today)
        self.refresh()

    # ---------- Refresh ----------

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def refresh(self):
        L = lambda key: t(key, self.lang)
        C = currency(self.lang)
        df = self.from_date.date().toString("yyyy-MM-dd")
        dt = self.to_date.date().toString("yyyy-MM-dd")

        # Summary cards
        summary = get_sales_summary(df, dt)
        self._clear_layout(self.summary_layout)

        cards_data = [
            ("💰", L("total_sales"), f"{summary['total']:.2f} {C}", "#0ea5e9"),
            ("📈", L("total_profit"), f"{summary['profit']:.2f} {C}", "#16a34a"),
            ("📊", L("sales_count"), str(summary["count"]), "#6366f1"),
            ("📉", L("average_sale"), f"{summary['avg_sale']:.2f} {C}", "#f59e0b"),
        ]

        for icon, title, value, color in cards_data:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border-radius: 12px;
                    border: 1px solid #e2e8f0;
                }}
            """)
            card.setMinimumHeight(110)

            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(18)
            shadow.setXOffset(0)
            shadow.setYOffset(2)
            shadow.setColor(QColor(0, 0, 0, 22))
            card.setGraphicsEffect(shadow)

            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 14, 16, 14)
            cl.setSpacing(6)

            top_row = QHBoxLayout()
            top_row.setSpacing(8)

            icon_lbl = QLabel(icon)
            icon_lbl.setFixedSize(34, 34)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet(f"""
                background-color: {color}22;
                border-radius: 9px;
                font-size: 16px;
            """)
            top_row.addWidget(icon_lbl)

            t_lbl = QLabel(title)
            t_lbl.setStyleSheet("""
                color: #64748b;
                font-size: 11px;
                font-weight: bold;
                background: transparent;
            """)
            top_row.addWidget(t_lbl)
            top_row.addStretch()

            cl.addLayout(top_row)

            v_lbl = QLabel(value)
            v_lbl.setStyleSheet(f"""
                color: {color};
                font-size: 20px;
                font-weight: bold;
                background: transparent;
            """)
            cl.addWidget(v_lbl)

            self.summary_layout.addWidget(card)

        # Sales tab
        sales = get_sales_in_range(df, dt, limit=500)
        self.sales_table.setRowCount(len(sales))
        for row, s in enumerate(sales):
            id_item = QTableWidgetItem(str(s["id"]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.sales_table.setItem(row, 0, id_item)

            self.sales_table.setItem(row, 1, QTableWidgetItem(str(s["sale_date"])))
            self.sales_table.setItem(row, 2, QTableWidgetItem(s["customer_name"] or "—"))

            t_item = QTableWidgetItem(f"{s['total']:.2f}")
            t_item.setForeground(QColor("#0ea5e9"))
            self.sales_table.setItem(row, 3, t_item)

            p_item = QTableWidgetItem(f"{s['profit']:.2f}")
            p_item.setForeground(QColor("#16a34a"))
            self.sales_table.setItem(row, 4, p_item)

        # Daily tab
        daily = get_daily_breakdown(df, dt)
        self.daily_table.setRowCount(len(daily))
        for row, d in enumerate(daily):
            self.daily_table.setItem(row, 0, QTableWidgetItem(str(d["day"])))

            s_item = QTableWidgetItem(f"{d['total']:.2f}")
            s_item.setForeground(QColor("#0ea5e9"))
            self.daily_table.setItem(row, 1, s_item)

            p_item = QTableWidgetItem(f"{d['profit']:.2f}")
            p_item.setForeground(QColor("#16a34a"))
            self.daily_table.setItem(row, 2, p_item)

            c_item = QTableWidgetItem(str(d["count"]))
            c_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.daily_table.setItem(row, 3, c_item)

        # Top products tab
        top = get_top_products_in_range(df, dt, limit=10)
        self.top_table.setRowCount(len(top))
        for row, p in enumerate(top):
            self.top_table.setItem(row, 0, QTableWidgetItem(p["name"]))
            self.top_table.setItem(row, 1, QTableWidgetItem(p["brand"] or ""))

            q_item = QTableWidgetItem(str(p["qty_sold"]))
            q_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top_table.setItem(row, 2, q_item)

            r_item = QTableWidgetItem(f"{p['revenue']:.2f}")
            r_item.setForeground(QColor("#0ea5e9"))
            self.top_table.setItem(row, 3, r_item)

            pf_item = QTableWidgetItem(f"{p['profit']:.2f}")
            pf_item.setForeground(QColor("#16a34a"))
            self.top_table.setItem(row, 4, pf_item)

        # Phones sold tab
        phones = get_phones_sold_in_range(df, dt)
        self.phones_table.setRowCount(len(phones))
        for row, p in enumerate(phones):
            name = p["product_name"] + (
                f" ({p['product_brand']})" if p["product_brand"] else "")
            self.phones_table.setItem(row, 0, QTableWidgetItem(name))
            self.phones_table.setItem(row, 1, QTableWidgetItem(p["imei"] or "—"))
            self.phones_table.setItem(row, 2, QTableWidgetItem(f"{p['buying_price']:.2f}"))
            self.phones_table.setItem(row, 3, QTableWidgetItem(f"{p['selling_price']:.2f}"))
            self.phones_table.setItem(row, 4, QTableWidgetItem(str(p["sale_date"])))

    # ---------- Export menu ----------

    def show_export_menu(self):
        L = lambda key: t(key, self.lang)
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px;
                font-size: 13px;
            }
            QMenu::item {
                padding: 10px 20px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #eef2ff;
                color: #4f46e5;
            }
        """)

        # Sales
        act_sales = menu.addAction("📊  " + L("tab_sales"))
        act_sales.triggered.connect(self.export_sales_clicked)

        # Products
        act_products = menu.addAction("📦  " + L("products"))
        act_products.triggered.connect(self.export_products_clicked)

        # Customers
        act_customers = menu.addAction("👥  " + L("customers_title"))
        act_customers.triggered.connect(self.export_customers_clicked)

        # Phone Units
        act_phones = menu.addAction("📱  " + L("phone_units_title"))
        act_phones.triggered.connect(self.export_phones_clicked)

        # Debts
        act_debts = menu.addAction("💵  " + L("customer_debts"))
        act_debts.triggered.connect(self.export_debts_clicked)

        # Show menu below the button
        menu.exec(self.export_btn.mapToGlobal(self.export_btn.rect().bottomLeft()))

    def export_sales_clicked(self):
        L = lambda key: t(key, self.lang)
        df = self.from_date.date().toString("yyyy-MM-dd")
        dt = self.to_date.date().toString("yyyy-MM-dd")

        sales = get_sales_in_range(df, dt, limit=10000)

        # Add items for each sale
        from app.db.sale_repo import get_sale_items
        for s in sales:
            items = get_sale_items(s["id"])
            s["items"] = [
                {
                    "name": (it["product_name"] or f"IMEI: {it['phone_imei']}"),
                    "qty": it["quantity"],
                }
                for it in items
            ]

        path = export_sales(sales)

        # Ask to open
        reply = QMessageBox.question(
            self, L("export_done"),
            L("export_done_msg").replace("{file}", path.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            open_file(path)

    def export_products_clicked(self):
        L = lambda key: t(key, self.lang)
        products = get_products(limit=100000)
        cats = {c.id: c.display_name(self.lang) for c in get_all_categories()}
        path = export_products(products, cats)

        reply = QMessageBox.question(
            self, L("export_done"),
            L("export_done_msg").replace("{file}", path.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            open_file(path)

    def export_customers_clicked(self):
        L = lambda key: t(key, self.lang)
        customers = get_customers(limit=100000)
        debts = {c.id: get_customer_debt(c.id) for c in customers}
        path = export_customers(customers, debts)

        reply = QMessageBox.question(
            self, L("export_done"),
            L("export_done_msg").replace("{file}", path.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            open_file(path)

    def export_phones_clicked(self):
        L = lambda key: t(key, self.lang)
        units = get_phone_units(limit=100000)

        # Add product name to each unit
        all_products = {p.id: p for p in get_products(limit=100000)}
        for u in units:
            if u.product_id and u.product_id in all_products:
                p = all_products[u.product_id]
                u.product_name = p.name + (f" ({p.brand})" if p.brand else "")
            else:
                u.product_name = "—"

        path = export_phone_units(units)

        reply = QMessageBox.question(
            self, L("export_done"),
            L("export_done_msg").replace("{file}", path.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            open_file(path)

    def export_debts_clicked(self):
        L = lambda key: t(key, self.lang)
        debts = get_all_debts()
        path = export_debts(debts)

        reply = QMessageBox.question(
            self, L("export_done"),
            L("export_done_msg").replace("{file}", path.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            open_file(path)