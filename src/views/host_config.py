from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QFont, QGuiApplication
from PyQt6.QtCore import Qt

from src.utils import write_file
from src.constants import HOST_FILE
from src.views.login import LoginWindow


class HostConfigWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Configuración del Host")
        self.setFixedSize(400, 200)  # Tamaño fijo para mantener consistencia
        self.setStyleSheet("background-color: #FFFFFF; border-radius: 10px;")

        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Etiqueta de título
        self.label = QLabel("Configura el Host")
        self.label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Input de Host
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Ejemplo: botilleriasok.api.localhost")
        self.host_input.setStyleSheet("""
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
        layout.addWidget(self.host_input)

        # Botón de guardar
        self.save_button = QPushButton("Guardar y Continuar")
        self.save_button.setStyleSheet("""
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
        self.save_button.clicked.connect(self.save_host)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        # Centrar la ventana
        self.center_window()

    def center_window(self):
        """ Centra la ventana en la pantalla. """
        screen_geometry = QGuiApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()

        center_x = (screen_geometry.width() - self.width()) // 2
        center_y = (screen_geometry.height() - self.height()) // 2

        self.move(center_x, center_y)

    def save_host(self):
        host = self.host_input.text().strip()
        if not host:
            QMessageBox.critical(self, "Error", "El campo Host no puede estar vacío.")
            return

        try:
            write_file(HOST_FILE, host)
            QMessageBox.information(self, "Éxito", "Host configurado correctamente.")
            self.open_login()
        except IOError as e:
            QMessageBox.critical(self, "Error", str(e))

    def open_login(self):
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()
