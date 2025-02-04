import sys
import os

# Ajuste para que funcione tanto en desarrollo como en el exe de PyInstaller
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS  # PyInstaller usa esta ruta cuando se empaqueta el exe
else:
    base_path = os.path.abspath(os.path.dirname(__file__))  # Desarrollo usa la ubicación real del script

sys.path.insert(0, base_path)  # Asegurar que `src` esté en sys.path

# Importaciones con rutas absolutas
from src.constants import HOST_FILE
from src.views.login import LoginWindow

from PyQt6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)

    # Verificar si existe el archivo de configuración
    if os.path.exists(HOST_FILE):
        login_window = LoginWindow()
        login_window.show()
    else:
        from src.views.host_config import HostConfigWindow
        host_window = HostConfigWindow()
        host_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
