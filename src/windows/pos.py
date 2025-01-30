from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox
import requests
from constants import API_BASE_URL, TOKEN_FILE, HOST_FILE
from utils import read_file

class POSWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("POS con PyQt6")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.label = QLabel("Lista de Productos")
        layout.addWidget(self.label)

        self.listWidget = QListWidget()
        layout.addWidget(self.listWidget)

        self.btnActualizar = QPushButton("Actualizar Productos")
        self.btnActualizar.clicked.connect(self.obtener_productos)
        layout.addWidget(self.btnActualizar)

        self.setLayout(layout)

    def obtener_productos(self):
        token = read_file(TOKEN_FILE)
        host = read_file(HOST_FILE)

        if not token or not host:
            QMessageBox.critical(self, "Error", "Faltan configuraciones o autenticación.")
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Host": host,
        }

        try:
            response = requests.get(f"{API_BASE_URL}/products", headers=headers)
            if response.status_code == 200:
                productos = response.json().get("items", [])
                self.listWidget.clear()
                for producto in productos:
                    self.listWidget.addItem(f"{producto['name']} - ${producto['unit_price']}")
            else:
                QMessageBox.critical(self, "Error", f"Error al obtener productos: {response.status_code}")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error de conexión", str(e))
