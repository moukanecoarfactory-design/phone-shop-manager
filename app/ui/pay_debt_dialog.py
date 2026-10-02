"""
Pay Debt Dialog — record a payment from a customer.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.db.payment_repo import (
    add_payment, get_customer_payments, get_customer_debt
)
from app.locales.translations import t, currency


class PayDebtDialog(QDialog):
    """Dialog to record a debt payment."""

    def __init__(self, parent=None, customer: dict = None, lang: str = "en"):
        super().__init__(parent)
        self.lang = lang
        self.customer = customer or {}

        L = lambda key: t(key, self.lang)
        C = currency(self.lang)

        self.customer_id = self.customer.get("id")
        self.customer_name = self.customer.get("name", "?")
        self.current_debt = get_customer_debt(self.customer_id)

        self.setWindowTitle(f"Pay Debt - {self.customer_name}")
        self.setMinimumWidth(520)
        self.setMinimumHeight(600)

        self.setStyleSheet("QDialog { background-color: #f1f5f9; }")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)

        # ---------- Card ----------
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

        icon_badge = QLabel("💰")
        icon_badge.setFixedSize(46, 46)
        icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_badge.setStyleSheet("""
            background-color: #fef3c7;
            border-radius: 12px;
            font-size: 24px;
        """)
        title_row.addWidget(icon_badge)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel(L("pay_debt_title"))
        title.setStyleSheet("""
            color: #0f172a;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        """)
        title_col.addWidget(title)

        subtitle = QLabel(f"@ {self.customer_name}")
        subtitle.setStyleSheet("""
            color: #64748b;
            font-size: 12px;
            background: transparent;
        """)
        title_col.addWidget(subtitle)

        title_row.addLayout(title_col)
        title_row.addStretch()
        card_layout.addLayout(title_row)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #e2e8f0; border: none;")
        card_layout.addWidget(divider)

        # ---------- Current debt ----------
        debt_frame = QFrame()
        debt_frame.setStyleSheet("""
            QFrame {
                background-color: #fef3c7;
                border: 1px solid #fcd34d;
                border-radius: 10px;
                padding: 12px;
            }
        """)
        debt_layout = QVBoxLayout(debt_frame)
        debt_layout.setContentsMargins(12, 8, 12, 8)

        debt_lbl = QLabel(L("current_debt"))
        debt_lbl.setStyleSheet("""
            color: #92400e;
            font-size: 12px;
            font-weight: bold;
            background: transparent;
        """)
        debt_layout.addWidget(debt_lbl)

        self.debt_value = QLabel(f"{self.current_debt:.2f} {C}")
        self.debt_value.setStyleSheet("""
            color: #b45309;
            font-size: 22px;
            font-weight: bold;
            background: transparent;
        """)
        debt_layout.addWidget(self.debt_value)

        card_layout.addWidget(debt_frame)

        # ---------- Payment amount input ----------
        amount_lbl = QLabel(L("payment_amount"))
        amount_lbl.setStyleSheet("""
            color: #334155;
            font-size: 13px;
            font-weight: bold;
            background: transparent;
        """)
        card_layout.addWidget(amount_lbl)

        amount_row = QHBoxLayout()
        amount_row.setSpacing(8)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(9999999)
        self.amount_input.setDecimals(2)
        self.amount_input.setSuffix(" " + C)
        self.amount_input.setMinimumHeight(42)
        self.amount_input.setValue(self.current_debt)  # Default = full debt
        self.amount_input.setStyleSheet(self._input_style())
        amount_row.addWidget(self.amount_input, 1)

        pay_all_btn = QPushButton(L("pay_full"))
        pay_all_btn.setMinimumHeight(42)
        pay_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pay_all_btn.setStyleSheet(self._secondary_btn_style())
        pay_all_btn.clicked.connect(self.on_pay_full)
        amount_row.addWidget(pay_all_btn)

        card_layout.addLayout(amount_row)

        # ---------- Notes ----------
        notes_lbl = QLabel(L("notes"))
        notes_lbl.setStyleSheet("""
            color: #334155;
            font-size: 13px;
            font-weight: bold;
            background: transparent;
        """)
        card_layout.addWidget(notes_lbl)

        self.notes_input = QLineEdit()
        self.notes_input.setMinimumHeight(38)
        self.notes_input.setPlaceholderText(L("enter_notes_optional"))
        self.notes_input.setStyleSheet(self._input_style())
        card_layout.addWidget(self.notes_input)

        # ---------- Previous payments ----------
        history_lbl = QLabel(L("payment_history"))
        history_lbl.setStyleSheet("""
            color: #334155;
            font-size: 13px;
            font-weight: bold;
            background: transparent;
        """)
        card_layout.addWidget(history_lbl)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels([
            L("date"), L("amount"), L("notes")
        ])
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setShowGrid(False)
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.setMaximumHeight(180)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 12px;
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                color: #475569;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-weight: bold;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #f1f5f9;
            }
        """)
        hh = self.history_table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        card_layout.addWidget(self.history_table)

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

        save_btn = QPushButton("✓  " + L("save_payment"))
        save_btn.setMinimumHeight(42)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(self._primary_btn_style())
        save_btn.clicked.connect(self.on_save)
        btn_row.addWidget(save_btn)

        card_layout.addLayout(btn_row)

        outer.addWidget(card)

        # Load history
        self.refresh_history()

    # ---------- Styles ----------

    def _input_style(self) -> str:
        return """
            QLineEdit, QDoubleSpinBox {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 14px;
            }
            QLineEdit:focus, QDoubleSpinBox:focus { border: 1px solid #0ea5e9; }
        """

    def _primary_btn_style(self) -> str:
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

    # ---------- Actions ----------

    def on_pay_full(self):
        """Set the amount to the full debt."""
        self.amount_input.setValue(self.current_debt)

    def refresh_history(self):
        """Reload payment history."""
        C = currency(self.lang)
        payments = get_customer_payments(self.customer_id)

        self.history_table.setRowCount(len(payments))
        for row, p in enumerate(payments):
            date_item = QTableWidgetItem(str(p["payment_date"])[:16])
            amount_item = QTableWidgetItem(f"{p['amount']:.2f} {C}")
            amount_item.setForeground(QColor("#16a34a"))
            notes_item = QTableWidgetItem(p["notes"] or "")

            self.history_table.setItem(row, 0, date_item)
            self.history_table.setItem(row, 1, amount_item)
            self.history_table.setItem(row, 2, notes_item)

    def on_save(self):
        L = lambda key: t(key, self.lang)
        amount = self.amount_input.value()

        if amount <= 0:
            QMessageBox.warning(self, L("error_title"), L("amount_must_be_positive"))
            return

        if amount > self.current_debt + 0.01:
            QMessageBox.warning(self, L("error_title"),
                                L("amount_exceeds_debt").replace(
                                    "{max}", f"{self.current_debt:.2f}"))
            return

        # Save the payment
        add_payment(
            customer_id=self.customer_id,
            amount=amount,
            sale_id=None,
            notes=self.notes_input.text().strip() or "Debt payment"
        )

        QMessageBox.information(
            self, L("payment_saved_title"),
            L("payment_saved_msg").replace("{amount}", f"{amount:.2f}")
        )
        self.accept()