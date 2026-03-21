from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
)

class LoginWindow(QWidget):
    def __init__(self, on_login):
        super().__init__()
        self.on_login = on_login
        self.setWindowTitle("Pronoty - Login")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Enter master password")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.handle_login)

        self.button = QPushButton("Unlock")
        self.button.clicked.connect(self.handle_login)

        self.error = QLabel("")
        self.error.setStyleSheet("color: red;")

        layout.addWidget(self.label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.button)
        layout.addWidget(self.error)

        self.setLayout(layout)

    def handle_login(self):
        password = self.password_input.text()
        if not password:
            self.error.setText("Password required")
            return

        success = self.on_login(password)

        if not success:
            self.error.setText("Wrong password")