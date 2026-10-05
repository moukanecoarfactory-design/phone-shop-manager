from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QScrollArea, QPushButton, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.db.dashboard_repo import (
    get_today_sales_summary, get_month_sales_summary,
    get_counts, get_low_stock_products, get_top_selling_products,
    get_total_debts
)
from app.locales.translations import t, currency


# ============ Modern Stat Card ============
class StatCard(QFrame):
    """A single modern statistic card with icon badge."""

    def __init__(self, icon: str, title: str, value: str,
                 color: str = "#0ea5e9", subtitle: str = ""):
        super().__init__()
        self.setObjectName("statCard")
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }}
        """)
        self.setMinimumHeight(120)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        icon_badge = QLabel(icon)
        icon_badge.setFixedSize(38, 38)
        icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_badge.setStyleSheet(f"""
            background-color: {color}22;
            color: {color};
            border-radius: 10px;
            font-size: 18px;
            font-weight: bold;
        """)
        top_row.addWidget(icon_badge)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"""
            color: #64748b;
            font-size: 12px;
            font-weight: bold;
            background: transparent;
            letter-spacing: 0.3px;
        """)
        top_row.addWidget(title_lbl)
        top_row.addStretch()

        layout.addLayout(top_row)

        value_lbl = QLabel(value)
        value_lbl.setStyleSheet(f"""
            color: {color};
            font-size: 22px;
            font-weight: bold;
            background: transparent;
        """)
        layout.addWidget(value_lbl)

        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setStyleSheet("""
                color: #94a3b8;
                font-size: 11px;
                background: transparent;
            """)
            layout.addWidget(sub_lbl)
        else:
            layout.addStretch()


# ============ Section Header ============
def make_section_header(icon: str, text: str) -> QWidget:
    """Create a modern section header with icon."""
    container = QWidget()
    container.setStyleSheet("background: transparent;")
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 16, 0, 4)
    layout.setSpacing(10)

    icon_lbl = QLabel(icon)
    icon_lbl.setFixedSize(32, 32)
    icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    icon_lbl.setStyleSheet("""
        background-color: #f1f5f9;
        border-radius: 8px;
        font-size: 16px;
    """)
    layout.addWidget(icon_lbl)

    text_lbl = QLabel(text)
    text_lbl.setStyleSheet("""
        color: #0f172a;
        font-size: 16px;
        font-weight: bold;
        background: transparent;
    """)
    layout.addWidget(text_lbl)

    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFixedHeight(1)
    line.setStyleSheet("background-color: #e2e8f0; border: none;")
    layout.addWidget(line, 1)

    return container


class DashboardPage(QWidget):
    def __init__(self, lang: str = "en"):
        super().__init__()
        self.lang = lang

        L = lambda key: t(key, self.lang)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(14)

        # Top header
        header = QHBoxLayout()

        title = QLabel(L("dashboard"))
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #0f172a;
            background: transparent;
        """)
        header.addWidget(title)
        header.addStretch()

        self.refresh_btn = QPushButton(L("refresh"))
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.setStyleSheet("""
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
        self.refresh_btn.clicked.connect(self.refresh)
        header.addWidget(self.refresh_btn)

        outer.addLayout(header)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.content = QWidget()
        self.content.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(12)

        # ---------- Today ----------
        self.content_layout.addWidget(make_section_header("📅", L("today_section")))
        self.today_grid = QGridLayout()
        self.today_grid.setSpacing(14)
        self.content_layout.addLayout(self.today_grid)

        # ---------- This Month ----------
        self.content_layout.addWidget(make_section_header("📆", L("this_month")))
        self.month_grid = QGridLayout()
        self.month_grid.setSpacing(14)
        self.content_layout.addLayout(self.month_grid)

        # ---------- Inventory ----------
        self.content_layout.addWidget(make_section_header("📦", L("inventory")))
        self.inv_grid = QGridLayout()
        self.inv_grid.setSpacing(14)
        self.content_layout.addLayout(self.inv_grid)

        # ---------- Top Selling ----------
        self.content_layout.addWidget(make_section_header("🔥", L("top_selling")))
        self.top_table = QTableWidget()
        self.top_table.setColumnCount(3)
        self.top_table.setHorizontalHeaderLabels([
            L("product"), L("qty_sold"), L("revenue")
        ])
        self._style_table(self.top_table)
        self.top_table.setMaximumHeight(220)
        self.content_layout.addWidget(self.top_table)

        # ---------- Low Stock ----------
        self.content_layout.addWidget(
            make_section_header("⚠️", L("low_stock_alerts"))
        )
        self.low_table = QTableWidget()
        self.low_table.setColumnCount(4)
        self.low_table.setHorizontalHeaderLabels([
            L("product"), L("brand"), L("qty"), L("alert_level")
        ])
        self._style_table(self.low_table)
        self.low_table.setMaximumHeight(220)
        self.content_layout.addWidget(self.low_table)

        self.content_layout.addStretch()

        scroll.setWidget(self.content)
        outer.addWidget(scroll)

        self.refresh()

    def _style_table(self, table):
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(False)
        table.setShowGrid(False)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                font-size: 13px;
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #475569;
                padding: 10px 8px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-weight: bold;
                font-size: 12px;
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
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.setColumnWidth(0, 300)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def refresh(self):
        L = lambda key: t(key, self.lang)
        C = currency(self.lang)

        # ---------- Today ----------
        today = get_today_sales_summary()
        self._clear_layout(self.today_grid)
        self.today_grid.addWidget(StatCard(
            "💰", L("todays_sales"),
            f"{today['total']:.2f} {C}",
            "#0ea5e9",
            f"{today['count']} {L('sale_s')}"
        ), 0, 0)
        self.today_grid.addWidget(StatCard(
            "📈", L("todays_profit"),
            f"{today['profit']:.2f} {C}",
            "#16a34a"
        ), 0, 1)

        # ---------- Month ----------
        month = get_month_sales_summary()
        self._clear_layout(self.month_grid)
        self.month_grid.addWidget(StatCard(
            "💵", L("month_sales"),
            f"{month['total']:.2f} {C}",
            "#0ea5e9",
            f"{month['count']} {L('sale_s')}"
        ), 0, 0)
        self.month_grid.addWidget(StatCard(
            "📊", L("month_profit"),
            f"{month['profit']:.2f} {C}",
            "#16a34a"
        ), 0, 1)

        # ---------- Inventory ----------
        counts = get_counts()
        total_debts = get_total_debts()
        self._clear_layout(self.inv_grid)

        self.inv_grid.addWidget(StatCard(
            "📦", L("products_count"),
            str(counts["products"]), "#6366f1",
            L("total_registered")
        ), 0, 0)
        self.inv_grid.addWidget(StatCard(
            "📱", L("phones_in_stock"),
            str(counts["phones_in_stock"]), "#8b5cf6",
            L("available_units")
        ), 0, 1)
        self.inv_grid.addWidget(StatCard(
            "👥", L("customers_count"),
            str(counts["customers"]), "#f59e0b"
        ), 0, 2)
        self.inv_grid.addWidget(StatCard(
            "🏭", L("suppliers_count"),
            str(counts["suppliers"]), "#ec4899"
        ), 0, 3)
        self.inv_grid.addWidget(StatCard(
            "⚠️", L("low_stock_count"),
            str(counts["low_stock"]), "#ef4444",
            L("need_restocking")
        ), 0, 4)

        # Debts card
        debts_color = "#dc2626" if total_debts > 0.01 else "#16a34a"
        self.inv_grid.addWidget(StatCard(
            "💰", L("total_debts"),
            f"{total_debts:.2f} {C}", debts_color,
            L("no_debts") if total_debts <= 0.01 else L("customer_debts")
        ), 1, 0)

        # ---------- Top Selling ----------
        top = get_top_selling_products(5)
        self.top_table.setRowCount(len(top))
        for row, p in enumerate(top):
            name = p["name"] + (f" ({p['brand']})" if p["brand"] else "")
            self.top_table.setItem(row, 0, QTableWidgetItem(name))

            qty_item = QTableWidgetItem(str(p["qty_sold"]))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top_table.setItem(row, 1, qty_item)

            rev_item = QTableWidgetItem(f"{p['revenue']:.2f} {C}")
            rev_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.top_table.setItem(row, 2, rev_item)

        # ---------- Low Stock ----------
        low = get_low_stock_products(10)
        self.low_table.setRowCount(len(low))
        for row, p in enumerate(low):
            name_item = QTableWidgetItem(p["name"])
            brand_item = QTableWidgetItem(p["brand"] or "")

            qty_item = QTableWidgetItem(str(p["quantity"]))
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            qty_item.setForeground(QColor("#991b1b"))

            alert_item = QTableWidgetItem(str(p["low_stock_alert"]))
            alert_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.low_table.setItem(row, 0, name_item)
            self.low_table.setItem(row, 1, brand_item)
            self.low_table.setItem(row, 2, qty_item)
            self.low_table.setItem(row, 3, alert_item)