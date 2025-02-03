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
from sync_worker import SyncWorker  # Importa el worker de sincronización

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
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        host = read_file(HOST_FILE)

        if not host:
            QMessageBox.critical(self, "Error", "El Host no está configurado.")
            return

        if not email or not password:
            QMessageBox.critical(self, "Error", "Completa los campos de email y password.")
            return

        url = f"{API_BASE_URL}/auth/login"
        data = {
            "email": email,
            "password": password
        }
        headers = {
            "Accept": "application/json",
            "Host": host
        }

        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                resp_json = response.json()
                access_token = resp_json.get("access_token")
                refresh_token = resp_json.get("refresh_token")

                if access_token and refresh_token:
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
        """
        Abre la ventana del POS y, en segundo plano, sincroniza los productos sin bloquear la UI.
        """
        # 1) Abrir la ventana del POS de inmediato
        self.pos_window = POSWindow()
        self.pos_window.show()
        self.close()

        # 2) Iniciar la sincronización en segundo plano usando un QThread
        self.sync_worker = SyncWorker()
        self.sync_worker.finished.connect(self.handle_sync_finished)
        self.sync_worker.start()

    def handle_sync_finished(self, result):
        """
        Maneja el resultado de la sincronización.
        En este ejemplo se imprime el resultado en la consola; puedes adaptarlo según necesites.
        """
        if isinstance(result, Exception):
            print("Error en sincronización:", result)
        else:
            print(result)
