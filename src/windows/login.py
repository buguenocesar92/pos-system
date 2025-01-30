from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import requests
from constants import API_BASE_URL, TOKEN_FILE, HOST_FILE
from utils import write_file, read_file
from windows.pos import POSWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Inicio de Sesión")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Inicia Sesión")
        layout.addWidget(self.label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico")
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        host = read_file(HOST_FILE)

        if not host:
            QMessageBox.critical(self, "Error", "El Host no está configurado.")
            return

        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                headers={
                    "Accept": "*/*",
                    "User-Agent": "PyQt POS",
                    "Host": host,
                },
                data={"email": email, "password": password}
            )

            if response.status_code == 200:
                token = response.json().get("access_token")
                if token:
                    write_file(TOKEN_FILE, token)
                    QMessageBox.information(self, "Éxito", "Inicio de sesión exitoso.")
                    self.open_pos()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo obtener el token.")
            else:
                QMessageBox.critical(self, "Error", f"Error al iniciar sesión. Código: {response.status_code}")

        except requests.RequestException as e:
            QMessageBox.critical(self, "Error de conexión", str(e))

    def open_pos(self):
        self.close()
        self.pos_window = POSWindow()
        self.pos_window.show()
