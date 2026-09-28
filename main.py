import sys
from PySide6.QtWidgets import QApplication

from app.db.database import init_database
from app.locales.translations import get_current_language
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow


def main():
    init_database()

    app = QApplication(sys.argv)
    app.setApplicationName("Phone Shop Manager")

    while True:
        # ---------- Login ----------
        lang = get_current_language()
        login = LoginWindow(lang=lang)
        if not login.exec():
            sys.exit(0)

        # ---------- Main window ----------
        window = MainWindow(user=login.user)
        window.show()

        app.exec()

        # If logout was clicked → loop back to login
        # (If window closed normally → also loop; user must close login to exit)
        # Nothing to do here — while loop restarts


if __name__ == "__main__":
    main()