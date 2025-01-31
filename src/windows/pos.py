# windows/pos.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox

# Importamos la función para hacer peticiones con refresh automático
from utils import request_with_refresh

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
        try:
            # Hacemos la petición GET a "/products"
            response = request_with_refresh("GET", "/products")
            if response.status_code == 200:
                # Si ok, cargamos productos
                productos = response.json().get("items", [])
                self.listWidget.clear()
                for producto in productos:
                    self.listWidget.addItem(f"{producto['name']} - ${producto['unit_price']}")
            elif response.status_code == 401:
                # Significa que ni refrescando se pudo (refresh_token inválido o expirado)
                QMessageBox.critical(
                    self, "Error",
                    "Tu token ha expirado y no se pudo refrescar. Por favor, inicia sesión de nuevo."
                )
            else:
                QMessageBox.critical(
                    self, "Error",
                    f"Error al obtener productos: {response.status_code}"
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
