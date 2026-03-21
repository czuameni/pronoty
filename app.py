import sys
from PySide6.QtWidgets import QApplication
from core.database import Database
from core.crypto_manager import CryptoManager
from core.auth_manager import AuthManager
from core.notes_manager import NotesManager
from ui.main_window import MainWindow
from ui.login_window import LoginWindow

app = QApplication(sys.argv)
app.setApplicationName("Pronoty")

from PySide6.QtGui import QIcon
app.setWindowIcon(QIcon("assets/pronoty.ico"))

auth = AuthManager()
db = Database()

window = None

def handle_login(password):
    global window

    if not auth.verify_or_set_password(password):
        return False

    crypto = CryptoManager(password)
    notes_manager = NotesManager(db, crypto)

    window = MainWindow(notes_manager)
    window.show()

    login.close()
    return True

login = LoginWindow(handle_login)

with open("ui/styles.qss") as f:
    app.setStyleSheet(f.read())

login.show()
sys.exit(app.exec())