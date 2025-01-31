# main.py

import sys
import os
from PyQt6.QtWidgets import QApplication
from constants import HOST_FILE
from windows.host_config import HostConfigWindow
from windows.login import LoginWindow

def main():
    app = QApplication(sys.argv)

    # Verificar si existe host_config.txt
    if os.path.exists(HOST_FILE):
        # Ir directo al login
        login_window = LoginWindow()
        login_window.show()
    else:
        # Pedir que configuren el host
        from windows.host_config import HostConfigWindow
        host_window = HostConfigWindow()
        host_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
