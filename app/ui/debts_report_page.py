"""
Customer Debts Report — shows all customers who owe money.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QFrame, QGraphicsDropShadowEffect, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.db.payment_repo import get_all_debts, get_total_debts
from app.ui.pay_debt_dialog import PayDebtDialog
from app.locales.translations import t, currency


class DebtsReportPage(QWidget):
    def __init__(self, lang: str = "en"):
        super().__init__()
        self.lang = lang
        L = lambda key: t(key, self.lang)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title = QLabel(L("customer_debts"))
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
        self.refresh_btn.setMinimumHeight(40)
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

        layout.addLayout(header)

        # Summary card (compact)
        summary_card = QFrame()
        summary_card.setStyleSheet("""
            QFrame {
                background-color: #fef3c7;
                border: 2px solid #fcd34d;
                border-radius: 12px;
            }
        """)
        summary_card.setFixedHeight(110)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 25))
        summary_card.setGraphicsEffect(shadow)

        summary_layout = QHBoxLayout(summary_card)
        summary_layout.setContentsMargins(24, 14, 24, 14)
        summary_layout.setSpacing(14)

        icon_badge = QLabel("💰")
        icon_badge.setFixedSize(50, 50)
        icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_badge.setStyleSheet("""
            background-color: #fde68a;
            border-radius: 14px;
            font-size: 26px;
        """)
        summary_layout.addWidget(icon_badge)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        lbl_title = QLabel(L("total_debts"))
        lbl_title.setStyleSheet("""
            color: #92400e;
            font-size: 13px;
            font-weight: bold;
            background: transparent;
        """)
        text_col.addWidget(lbl_title)

        self.total_debts_lbl = QLabel("0.00 MAD")
        self.total_debts_lbl.setStyleSheet("""
            color: #b45309;
            font-size: 26px;
            font-weight: bold;
            background: transparent;
        """)
        text_col.addWidget(self.total_debts_lbl)

        summary_layout.addLayout(text_col)
        summary_layout.addStretch()

        self.count_lbl = QLabel("")
        self.count_lbl.setStyleSheet("""
            color: #92400e;
            font-size: 14px;
            font-weight: bold;
            background: transparent;
        """)
        summary_layout.addWidget(self.count_lbl)

        layout.addWidget(summary_card)

        # Empty state label
        self.empty_label = QLabel(L("no_debts"))
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("""
            color: #94a3b8;
            font-size: 16px;
            font-weight: bold;
            padding: 60px 20px;
            background: transparent;
        """)
        layout.addWidget(self.empty_label)

        # Table card
        self.table_card = QFrame()
        self.table_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        table_layout = QVBoxLayout(self.table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            L("name"), L("phone"), L("total_sales_col"),
            L("paid_label"), L("debt_col")
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.doubleClicked.connect(self.on_pay_debt)
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
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in [1, 2, 3, 4]:
            hh.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(46)

        table_layout.addWidget(self.table)
        layout.addWidget(self.table_card, 1)

        # Bottom
        bottom = QHBoxLayout()
        bottom.addStretch()

        self.pay_btn = QPushButton(L("pay_debt"))
        self.pay_btn.setMinimumHeight(42)
        self.pay_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pay_btn.setStyleSheet("""
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
        """)
        self.pay_btn.clicked.connect(self.on_pay_debt)
        bottom.addWidget(self.pay_btn)

        layout.addLayout(bottom)

        self.refresh()

    def refresh(self):
        L = lambda key: t(key, self.lang)
        C = currency(self.lang)

        debts = get_all_debts()
        total = get_total_debts()

        self.total_debts_lbl.setText(f"{total:.2f} {C}")
        self.count_lbl.setText(f"{len(debts)} {L('customers_label')}")

        # Show table or empty state
        if len(debts) == 0:
            self.table_card.setVisible(False)
            self.empty_label.setVisible(True)
        else:
            self.table_card.setVisible(True)
            self.empty_label.setVisible(False)

            self.table.setRowCount(len(debts))
            for row, d in enumerate(debts):
                name_item = QTableWidgetItem(d["name"])
                name_item.setData(Qt.ItemDataRole.UserRole, d["customer_id"])
                self.table.setItem(row, 0, name_item)

                self.table.setItem(row, 1, QTableWidgetItem(d["phone"]))

                sales_item = QTableWidgetItem(f"{d['total_sales']:.2f} {C}")
                sales_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 2, sales_item)

                paid_item = QTableWidgetItem(f"{d['total_paid']:.2f} {C}")
                paid_item.setForeground(QColor("#16a34a"))
                paid_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 3, paid_item)

                debt_item = QTableWidgetItem(f"{d['debt']:.2f} {C}")
                debt_item.setForeground(QColor("#dc2626"))
                debt_item.setBackground(QColor("#fef2f2"))
                debt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 4, debt_item)

    def _selected_customer_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return self.table.item(rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)

    def on_pay_debt(self):
        L = lambda key: t(key, self.lang)
        cid = self._selected_customer_id()
        if cid is None:
            QMessageBox.information(self, L("no_selection"),
                                    L("select_customer_first_debt"))
            return

        rows = self.table.selectionModel().selectedRows()
        row = rows[0].row()
        name = self.table.item(row, 0).text()
        phone = self.table.item(row, 1).text()

        customer_dict = {
            "id": cid,
            "name": name,
            "phone": phone,
        }

        dlg = PayDebtDialog(self, customer=customer_dict, lang=self.lang)
        if dlg.exec():
            self.refresh()