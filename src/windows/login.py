# windows/login.py
import requests
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

from utils import write_file, read_file
from constants import (
    API_BASE_URL,
    ACCESS_TOKEN_FILE,
    REFRESH_TOKEN_FILE,
    HOST_FILE
)
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
        if not email or not password:
            QMessageBox.critical(self, "Error", "Por favor completa los campos de email y password.")
            return

        url = f"{API_BASE_URL}/auth/login"

        # Tu backend: un POST a /auth/login
        # Ej. si requiere JSON => json={"email": ..., "password": ...}
        # Si requiere form-data => data={...}
        # Ajusta según corresponda:
        data = {
            "email": email,
            "password": password
        }
        headers = {
            "Accept": "application/json",
            "Host": host
        }

        try:
            # Usamos data= en vez de json= si tu login espera form-data;
            # Cambia a `json=data` si espera JSON.
            response = requests.post(url, headers=headers, data=data)

            if response.status_code == 200:
                resp_json = response.json()
                access_token = resp_json.get("access_token")
                refresh_token = resp_json.get("refresh_token")

                if access_token and refresh_token:
                    # Guardamos ambos tokens
                    write_file(ACCESS_TOKEN_FILE, access_token)
                    write_file(REFRESH_TOKEN_FILE, refresh_token)

                    QMessageBox.information(self, "Éxito", "Inicio de sesión exitoso.")
                    self.open_pos()
                else:
                    QMessageBox.critical(self, "Error", "No se obtuvieron los tokens en la respuesta.")
            else:
                QMessageBox.critical(self, "Error", f"Error al iniciar sesión. Código: {response.status_code}")

        except requests.RequestException as e:
            QMessageBox.critical(self, "Error de conexión", str(e))

    def open_pos(self):
        self.close()
        self.pos_window = POSWindow()
        self.pos_window.show()
