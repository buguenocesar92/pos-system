# windows/host_config.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from utils import write_file
from constants import HOST_FILE
from windows.login import LoginWindow

class HostConfigWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Configuración del Host")
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.label = QLabel("Configura el Host")
        layout.addWidget(self.label)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("Ejemplo: botilleriasok.api.localhost")
        layout.addWidget(self.host_input)

        self.save_button = QPushButton("Guardar y Continuar")
        self.save_button.clicked.connect(self.save_host)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

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
