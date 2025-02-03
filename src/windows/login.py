from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QFont, QGuiApplication
from PyQt6.QtCore import Qt
from qt_material import apply_stylesheet

from constants import API_BASE_URL, ACCESS_TOKEN_FILE, REFRESH_TOKEN_FILE, HOST_FILE
from windows.pos import POSWindow
from sync_worker import SyncWorker
from loading_dialog import MaterialLoadingDialog
from login_worker import LoginWorker

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Inicio de Sesión")
        self.setFixedSize(400, 300)  # Tamaño fijo similar al ejemplo
        self.setStyleSheet("background-color: #FFFFFF; border-radius: 10px;")

        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Estilo de etiqueta del título
        self.label_email = QLabel("Correo Electrónico")
        self.label_email.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.label_email)

        # Input de correo
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("botilleriasok@gmail.com")
        self.email_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d9d9d9;
                border-radius: 5px;
                background: #F5F5F5;
                padding: 10px;
                font-size: 14px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
                background: #FFFFFF;
            }
        """)
        layout.addWidget(self.email_input)

        # Estilo de etiqueta de contraseña
        self.label_password = QLabel("Contraseña")
        self.label_password.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.label_password)

        # Input de contraseña
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d9d9d9;
                border-radius: 5px;
                background: #F5F5F5;
                padding: 10px;
                font-size: 14px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 1px solid #4A90E2;
                background: #FFFFFF;
            }
        """)
        layout.addWidget(self.password_input)

        # Botón de login con estilo Material
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2C5A94;
            }
        """)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

        # Centrar la ventana en la pantalla
        self.center_window()

    def center_window(self):
        """ Centra la ventana en la pantalla. """
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()

        center_x = (screen_geometry.width() - self.width()) // 2
        center_y = (screen_geometry.height() - self.height()) // 2

        self.move(center_x, center_y)

    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.critical(self, "Error", "Completa los campos de email y password.")
            return

        # Mostrar el loading inmediatamente con el mensaje de login
        self.loading_dialog = MaterialLoadingDialog(self, "Iniciando sesión, por favor espere...")
        self.loading_dialog.show()

        # Iniciar el LoginWorker en segundo plano
        self.login_worker = LoginWorker(email, password)
        self.login_worker.finished.connect(self.handle_login_finished)
        self.login_worker.start()

    def handle_login_finished(self, result):
        if isinstance(result, Exception):
            self.loading_dialog.close()
            QMessageBox.critical(self, "Error de login", str(result))
        else:
            # Login exitoso: actualizar el mensaje del loading y comenzar la sincronización
            self.loading_dialog.label.setText("Sincronizando productos, por favor espere...")
            self.start_sync()

    def start_sync(self):
        # Iniciar la sincronización en segundo plano
        self.sync_worker = SyncWorker()
        self.sync_worker.finished.connect(self.handle_sync_finished)
        self.sync_worker.start()

    def handle_sync_finished(self, result):
        self.loading_dialog.close()
        if isinstance(result, Exception):
            QMessageBox.warning(self, "Error de sincronización", f"Hubo un error al sincronizar: {result}")
        # Abrir la ventana del POS
        self.pos_window = POSWindow()
        self.pos_window.show()
        self.close()
