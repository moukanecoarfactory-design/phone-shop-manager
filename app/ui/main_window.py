from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame,
    QMessageBox
)
from PySide6.QtCore import Qt, Signal

from app.ui.products_page import ProductsPage
from app.ui.customers_page import CustomersPage
from app.ui.suppliers_page import SuppliersPage
from app.ui.phone_units_page import PhoneUnitsPage
from app.ui.sales_page import SalesPage
from app.ui.dashboard_page import DashboardPage
from app.ui.reports_page import ReportsPage
from app.ui.settings_page import SettingsPage
from app.ui.change_password_dialog import ChangePasswordDialog
from app.ui.users_page import UsersPage
from app.locales.translations import t, get_current_language, get_setting


class NavButton(QPushButton):
    """Custom sidebar navigation button with icon."""

    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self.icon_text = icon
        self.label_text = text
        self.setText(f"   {icon}    {text}")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                color: #cbd5e1;
                background: transparent;
                text-align: left;
                padding: 12px 18px;
                font-size: 14px;
                border: none;
                border-radius: 0px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.06);
                color: white;
            }
            QPushButton:checked {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0ea5e9, stop:1 #6366f1
                );
                color: white;
                font-weight: bold;
            }
        """)


class MainWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(self, user: dict = None):
        super().__init__()
        self.user = user or {"username": "admin", "full_name": "Administrator", "role": "admin"}
        self.role = self.user.get("role", "admin")
        self.is_admin = (self.role == "admin")

        self.setWindowTitle("Phone Shop Manager")
        self.resize(1280, 780)

        # Load settings
        self.lang = get_current_language()
        shop_name = get_setting("shop_name", "My Phone Shop")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ================= SIDEBAR =================
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a, stop:1 #1e293b
                );
                border-right: 1px solid #334155;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # ---------- Logo / Shop name ----------
        logo_frame = QFrame()
        logo_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0ea5e9, stop:1 #6366f1
                );
                border: none;
            }
        """)
        logo_frame.setFixedHeight(90)
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(20, 14, 20, 14)
        logo_layout.setSpacing(2)

        shop_label = QLabel(f"📱 {shop_name}")
        shop_label.setStyleSheet("""
            color: white;
            font-size: 15px;
            font-weight: bold;
            background: transparent;
        """)
        shop_label.setWordWrap(True)
        logo_layout.addWidget(shop_label)

        role_label = QLabel("Management System")
        role_label.setStyleSheet("""
            color: #e0f2fe;
            font-size: 10px;
            background: transparent;
        """)
        logo_layout.addWidget(role_label)

        sidebar_layout.addWidget(logo_frame)

        # ---------- Navigation ----------
        self.nav_buttons = []
                # Each item: (icon, label, page_index, admin_only)
        all_pages = [
            ("🏠", t("dashboard", self.lang),   0, False),
            ("📦", t("products", self.lang),    1, False),
            ("📱", t("phone_units", self.lang), 2, False),
            ("👥", t("customers", self.lang),   3, False),
            ("🏭", t("suppliers", self.lang),   4, True),    # admin only
            ("💰", t("sales", self.lang),       5, False),
            ("📊", t("reports", self.lang),     6, True),    # admin only
            ("⚙️", t("settings", self.lang),    7, True),    # admin only
            ("👤", t("users", self.lang),       8, True),    # admin only — new page
        ]

        pages = [(icon, label, idx) for icon, label, idx, admin_only in all_pages
                 if self.is_admin or not admin_only]

        nav_container = QVBoxLayout()
        nav_container.setContentsMargins(8, 12, 8, 12)
        nav_container.setSpacing(2)

        for icon, label, idx in pages:
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda checked=False, i=idx: self.switch_page(i))
            nav_container.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addLayout(nav_container)
        sidebar_layout.addStretch()

        # ---------- User section ----------
        user_frame = QFrame()
        user_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.25);
                border-top: 1px solid #334155;
            }
        """)
        user_layout = QVBoxLayout(user_frame)
        user_layout.setContentsMargins(18, 14, 18, 14)
        user_layout.setSpacing(4)

        user_icon = QLabel("👤")
        user_icon.setStyleSheet("font-size: 20px; background: transparent;")
        user_layout.addWidget(user_icon)

        self.user_name_label = QLabel(self.user.get("full_name") or self.user.get("username", "User"))
        self.user_name_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-weight: bold;
            background: transparent;
        """)
        user_layout.addWidget(self.user_name_label)

        role_text = "👑 Admin" if self.is_admin else "👤 Cashier"
        self.user_role_label = QLabel(f"@{self.user.get('username', 'user')}  ·  {role_text}")
        self.user_role_label.setStyleSheet("""
            color: #94a3b8;
            font-size: 11px;
            background: transparent;
        """)
        user_layout.addWidget(self.user_role_label)

        user_layout.addSpacing(4)

                # --- Change Password button ---
        change_pw_btn = QPushButton("🔐  Change Password")
        change_pw_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_pw_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(99, 102, 241, 0.15);
                color: #a5b4fc;
                border: 1px solid rgba(99, 102, 241, 0.3);
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(99, 102, 241, 0.3);
                color: white;
            }
        """)
        change_pw_btn.clicked.connect(self.on_change_password)
        user_layout.addWidget(change_pw_btn)

        # --- Logout button ---
        logout_btn = QPushButton("🚪  Logout")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 68, 68, 0.15);
                color: #fca5a5;
                border: 1px solid rgba(239, 68, 68, 0.3);
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.3);
                color: white;
            }
        """)
        logout_btn.clicked.connect(self.on_logout)
        user_layout.addWidget(logout_btn)

        sidebar_layout.addWidget(user_frame)

        # ================= CONTENT =================
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #f1f5f9;")

        self.stack.addWidget(DashboardPage(lang=self.lang))
        self.stack.addWidget(ProductsPage(lang=self.lang, is_admin=self.is_admin))
        self.stack.addWidget(PhoneUnitsPage(lang=self.lang, is_admin=self.is_admin))
        self.stack.addWidget(CustomersPage(lang=self.lang, is_admin=self.is_admin))
        self.stack.addWidget(SuppliersPage(lang=self.lang, is_admin=self.is_admin))
        self.stack.addWidget(SalesPage(lang=self.lang, is_admin=self.is_admin))
        self.stack.addWidget(ReportsPage(lang=self.lang))
        self.stack.addWidget(SettingsPage(lang=self.lang))
        self.stack.addWidget(UsersPage(lang=self.lang, current_user=self.user))

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, 1)

        self.nav_buttons[0].setChecked(True)
        self.stack.setCurrentIndex(0)

    def switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def on_change_password(self):
        dlg = ChangePasswordDialog(self, user=self.user)
        dlg.exec()

    def on_logout(self):
        confirm = QMessageBox.question(
            self, "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
            self.close()
