from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.db.customer_repo import (
    get_customers, count_customers, add_customer,
    update_customer, delete_customer, get_customer
)
from app.db.payment_repo import get_customer_debt
from app.ui.customer_dialog import CustomerDialog
from app.ui.pay_debt_dialog import PayDebtDialog
from app.locales.translations import t, currency


PAGE_SIZE = 50


class CustomersPage(QWidget):
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

        # Header
        header = QHBoxLayout()
        title = QLabel(L("customers_title"))
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #0f172a;
            background: transparent;
        """)
        header.addWidget(title)
        header.addStretch()

        self.add_btn = QPushButton("＋  " + L("add_customer").lstrip("+ "))
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setMinimumHeight(40)
        self.add_btn.setStyleSheet(self._primary_btn_style())
        self.add_btn.clicked.connect(self.on_add)
        self.add_btn.setVisible(self.is_admin)
        header.addWidget(self.add_btn)

        layout.addLayout(header)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  " + L("search_customers"))
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet(self._input_style())
        self.search_input.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search_input)

        # Table card
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
            L("id"), L("name"), L("phone"), L("address"), L("notes"), L("debt_col")
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
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
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        for col in [0, 2, 5]:
            hh.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(44)

        table_layout.addWidget(self.table)
        layout.addWidget(table_card, 1)

        # Bottom
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

        # Pay Debt button (always visible when a customer has debt)
        self.pay_debt_btn = QPushButton(L("pay_debt"))
        self.pay_debt_btn.setMinimumHeight(40)
        self.pay_debt_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pay_debt_btn.setStyleSheet(self._success_btn_style())
        self.pay_debt_btn.clicked.connect(self.on_pay_debt)
        bottom.addWidget(self.pay_debt_btn)

        self.edit_btn = QPushButton("✏  " + L("edit_customer").lstrip("✏ "))
        self.edit_btn.setMinimumHeight(40)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setStyleSheet(self._secondary_btn_style())
        self.edit_btn.clicked.connect(self.on_edit)
        self.edit_btn.setVisible(self.is_admin)
        bottom.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑  " + L("delete_customer").lstrip("🗑 "))
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
        """

    def _success_btn_style(self) -> str:
        return """
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #16a34a, stop:1 #22c55e
                );
                color: white;
                border: none;
                padding: 8px 18px;
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
        C = currency(self.lang)
        search = self.search_input.text().strip()
        self.total_count = count_customers(search)
        customers = get_customers(search, PAGE_SIZE, self.current_page * PAGE_SIZE)

        self.table.setRowCount(len(customers))
        for row, c in enumerate(customers):
            id_item = QTableWidgetItem(str(c.id))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, id_item)

            self.table.setItem(row, 1, QTableWidgetItem(c.name))
            self.table.setItem(row, 2, QTableWidgetItem(c.phone))
            self.table.setItem(row, 3, QTableWidgetItem(c.address))
            self.table.setItem(row, 4, QTableWidgetItem(c.notes))

            # Debt column
            debt = get_customer_debt(c.id)
            debt_item = QTableWidgetItem(f"{debt:.2f} {C}" if debt > 0.01 else "—")
            debt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            if debt > 0.01:
                debt_item.setForeground(QColor("#dc2626"))
                debt_item.setBackground(QColor("#fef2f2"))
            else:
                debt_item.setForeground(QColor("#16a34a"))

            self.table.setItem(row, 5, debt_item)

            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, c.id)

        self._update_pagination_ui()

    def _update_pagination_ui(self):
        L = lambda key: t(key, self.lang)
        total_pages = max(1, (self.total_count + PAGE_SIZE - 1) // PAGE_SIZE)
        self.page_label.setText(
            f"{L('page')} {self.current_page + 1} / {total_pages}"
            f"  ·  {self.total_count} {L('customers_label')}"
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

    def on_add(self):
        if not self.is_admin:
            return
        dlg = CustomerDialog(self, lang=self.lang)
        if dlg.exec():
            add_customer(dlg.get_customer())
            self.refresh()

    def on_edit(self):
        if not self.is_admin:
            return
        L = lambda key: t(key, self.lang)
        cid = self._selected_id()
        if cid is None:
            QMessageBox.information(self, L("no_selection"),
                                    L("select_customer_first"))
            return
        c = get_customer(cid)
        if not c:
            return
        dlg = CustomerDialog(self, customer=c, lang=self.lang)
        if dlg.exec():
            update_customer(dlg.get_customer())
            self.refresh()

    def on_delete(self):
        if not self.is_admin:
            return
        L = lambda key: t(key, self.lang)
        cid = self._selected_id()
        if cid is None:
            QMessageBox.information(self, L("no_selection"),
                                    L("select_customer_first"))
            return
        c = get_customer(cid)
        confirm = QMessageBox.question(
            self, L("confirm_delete"),
            L("delete_customer_confirm").format(name=c.name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            delete_customer(cid)
            self.refresh()

    def on_pay_debt(self):
        L = lambda key: t(key, self.lang)
        cid = self._selected_id()
        if cid is None:
            QMessageBox.information(self, L("no_selection"),
                                    L("select_customer_first_debt"))
            return

        c = get_customer(cid)
        if not c:
            return

        # Check if customer has debt
        debt = get_customer_debt(cid)
        if debt <= 0.01:
            QMessageBox.information(self, L("not_allowed"),
                                    L("no_debt_for_customer"))
            return

        # Build customer dict for the dialog
        customer_dict = {
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
        }

        dlg = PayDebtDialog(self, customer=customer_dict, lang=self.lang)
        if dlg.exec():
            self.refresh()