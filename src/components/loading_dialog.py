from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QMovie
import os
import sys

class MaterialLoadingDialog(QDialog):
    def __init__(self, parent=None, message="Cargando..."):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Etiqueta del mensaje
        self.label = QLabel(message)
        self.label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Etiqueta del GIF de carga
        self.loading_label = QLabel(self)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Ruta al GIF
        gif_path = self.get_gif_path()
        print(f"Ruta al GIF: {gif_path}")  # Para depuración
        if os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            self.movie.setScaledSize(QSize(100, 100))  # Ajusta el tamaño
            self.loading_label.setMovie(self.movie)
            self.movie.start()
        else:
            self.loading_label.setText("⚠️ GIF no encontrado")

        layout.addWidget(self.loading_label)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def get_gif_path(self):
        """Devuelve la ruta al archivo GIF, manejando entornos de desarrollo y empaquetado."""
        import sys
        if hasattr(sys, "_MEIPASS"):  # Entorno empaquetado
            return os.path.join(sys._MEIPASS, "loading.gif")
        else:  # Entorno de desarrollo
            return os.path.abspath(os.path.join(os.path.dirname(__file__), "loading.gif"))
