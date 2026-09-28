from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox,
    QMessageBox, QHeaderView, QAbstractItemView, QDialog,
    QFormLayout, QDialogButtonBox, QFrame,
    QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.db.user_repo import get_all_users, create_user
from app.db.database import get_connection
from app.locales.translations import t


# ============================================================
# Modern Add User Dialog
# ============================================================
class UserDialog(QDialog):
    """Modern dialog to add a new user."""

    def __init__(self, parent=None, lang: str = "en"):
        super().__init__(parent)
        self.lang = lang
        L = lambda key: t(key, self.lang)

        self.setWindowTitle(L("add_user_title"))
        self.setMinimumWidth(440)

        self.setStyleSheet("""
            QDialog {
                background-color: #f1f5f9;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(0)

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
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 22)
        card_layout.setSpacing(12)

        # Icon + title
        icon_row = QHBoxLayout()
        icon_row.setSpacing(10)

        icon_badge = QLabel("👤")
        icon_badge.setFixedSize(42, 42)
        icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_badge.setStyleSheet("""
            background-color: #eef2ff;
            border-radius: 10px;
            font-size: 20px;
        """)
        icon_row.addWidget(icon_badge)

        title = QLabel(L("add_user_title"))
        title.setStyleSheet("""
            color: #0f172a;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        """)
        icon_row.addWidget(title)
        icon_row.addStretch()

        card_layout.addLayout(icon_row)

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

        self.username_input = QLineEdit()
        self.username_input.setMinimumHeight(40)
        self.username_input.setStyleSheet(self._input_style())
        form.addRow(self._label(L("username") + " *"), self.username_input)

        self.full_name_input = QLineEdit()
        self.full_name_input.setMinimumHeight(40)
        self.full_name_input.setStyleSheet(self._input_style())
        form.addRow(self._label(L("full_name")), self.full_name_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.setStyleSheet(self._input_style())
        form.addRow(self._label(L("password") + " *"), self.password_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setMinimumHeight(40)
        self.confirm_input.setStyleSheet(self._input_style())
        form.addRow(self._label(L("confirm_password") + " *"), self.confirm_input)

        self.role_combo = QComboBox()
        self.role_combo.setMinimumHeight(40)
        self.role_combo.setStyleSheet(self._input_style())
        self.role_combo.addItem("👑  " + L("admin_role"), "admin")
        self.role_combo.addItem("👤  " + L("cashier_role"), "cashier")
        form.addRow(self._label(L("role")), self.role_combo)

        card_layout.addLayout(form)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel_btn = QPushButton(L("cancel"))
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(self._secondary_btn_style())
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("✓  " + L("save"))
        save_btn.setMinimumHeight(40)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(self._primary_btn_style())
        save_btn.clicked.connect(self._on_accept)
        btn_row.addWidget(save_btn)

        card_layout.addLayout(btn_row)

        outer.addWidget(card)

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
            QLineEdit, QComboBox {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 14px;
                font-size: 13px;
            }
            QLineEdit:hover, QComboBox:hover { border: 1px solid #cbd5e1; }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #0ea5e9; }
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

    def _on_accept(self):
        L = lambda key: t(key, self.lang)
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Missing Fields",
                                "Username and password are required.")
            return

        if len(password) < 4:
            QMessageBox.warning(self, "Too Short", L("password_too_short"))
            return

        if password != confirm:
            QMessageBox.warning(self, "Mismatch", L("password_mismatch"))
            return

        conn = get_connection()
        row = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()
        if row:
            QMessageBox.warning(self, "Exists", L("username_taken"))
            return

        self.accept()

    def get_user(self) -> dict:
        return {
            "username": self.username_input.text().strip(),
            "password": self.password_input.text(),
            "full_name": self.full_name_input.text().strip(),
            "role": self.role_combo.currentData(),
        }


# ============================================================
# Users Management Page
# ============================================================
class UsersPage(QWidget):
    def __init__(self, lang: str = "en", current_user: dict = None):
        super().__init__()
        self.lang = lang
        self.current_user = current_user or {}

        L = lambda key: t(key, self.lang)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()
        title = QLabel(L("users"))
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #0f172a;
            background: transparent;
        """)
        header.addWidget(title)
        header.addStretch()

        self.add_btn = QPushButton("＋  " + L("add_user").lstrip("+ "))
        self.add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_btn.setMinimumHeight(42)
        self.add_btn.setStyleSheet(self._primary_btn_style())
        self.add_btn.clicked.connect(self.on_add)
        header.addWidget(self.add_btn)

        layout.addLayout(header)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  " + L("search_users"))
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet(self._input_style())
        self.search_input.textChanged.connect(self.refresh)
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
        self.table.setColumnCount(5)
        self.table.setColumnHidden(0, True)
        self.table.setHorizontalHeaderLabels([
            "ID", L("username"), L("full_name"), L("role"), "Created"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
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
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(46)

        table_layout.addWidget(self.table)
        layout.addWidget(table_card, 1)

        # Bottom
        bottom = QHBoxLayout()
        bottom.addStretch()

        self.delete_btn = QPushButton("🗑  " + L("delete_user").lstrip("🗑 "))
        self.delete_btn.setMinimumHeight(42)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet(self._danger_btn_style())
        self.delete_btn.clicked.connect(self.on_delete)
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
        search = self.search_input.text().strip().lower()
        users = get_all_users()

        if search:
            users = [u for u in users
                     if search in (u["username"] or "").lower()
                     or search in (u["full_name"] or "").lower()]

        role_labels = {
            "admin": "👑  " + L("admin_role"),
            "cashier": "👤  " + L("cashier_role"),
        }

        self.table.setRowCount(len(users))
        for row, u in enumerate(users):
            id_item = QTableWidgetItem(str(u["id"]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, id_item)

            # Username
            username_item = QTableWidgetItem("@" + u["username"])
            username_item.setForeground(QColor("#0ea5e9"))
            self.table.setItem(row, 1, username_item)

            # Full name + (you)
            full_name = u["full_name"] or "—"
            name_item = QTableWidgetItem(full_name)
            if u["id"] == self.current_user.get("id"):
                name_item.setText(full_name + "   (you)")
                name_item.setForeground(QColor("#16a34a"))
            self.table.setItem(row, 2, name_item)

            # Role
            role_text = role_labels.get(u["role"], u["role"])
            role_item = QTableWidgetItem(role_text)
            if u["role"] == "admin":
                role_item.setForeground(QColor("#7c3aed"))
            else:
                role_item.setForeground(QColor("#0891b2"))
            self.table.setItem(row, 3, role_item)

            # Created
            created_item = QTableWidgetItem(str(u.get("created_at", "")))
            created_item.setForeground(QColor("#94a3b8"))
            self.table.setItem(row, 4, created_item)

            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, u["id"])

    def _selected_id(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return None
        return self.table.item(rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)

    def on_add(self):
        dlg = UserDialog(self, lang=self.lang)
        if dlg.exec():
            data = dlg.get_user()
            create_user(
                data["username"],
                data["password"],
                data["full_name"],
                data["role"]
            )
            self.refresh()

    def on_delete(self):
        L = lambda key: t(key, self.lang)
        uid = self._selected_id()
        if uid is None:
            QMessageBox.information(self, "No Selection",
                                    "Please select a user first.")
            return

        if uid == self.current_user.get("id"):
            QMessageBox.warning(self, "Not Allowed", L("cannot_delete_self"))
            return

        conn = get_connection()
        admins = conn.execute(
            "SELECT COUNT(*) FROM users WHERE role = 'admin'"
        ).fetchone()[0]
        target = conn.execute(
            "SELECT username, role FROM users WHERE id = ?", (uid,)
        ).fetchone()
        conn.close()

        if target and target["role"] == "admin" and admins <= 1:
            QMessageBox.warning(self, "Not Allowed",
                                "Cannot delete the last admin.")
            return

        username = target["username"] if target else "?"
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete user '{username}'?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            conn.execute("DELETE FROM users WHERE id = ?", (uid,))
            conn.commit()
            conn.close()
            self.refresh()