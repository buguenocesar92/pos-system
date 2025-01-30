import sys
import os
from PyQt6.QtWidgets import QApplication
from windows.host_config import HostConfigWindow
from windows.login import LoginWindow
from constants import HOST_FILE

def main():
    app = QApplication(sys.argv)

    # Verificar si el archivo de configuración del host existe
    if os.path.exists(HOST_FILE):
        # Si existe, abrir la ventana de inicio de sesión directamente
        login_window = LoginWindow()
        login_window.show()
    else:
        # Si no existe, abrir la ventana de configuración del host
        host_config_window = HostConfigWindow()
        host_config_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
