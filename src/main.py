import sys
from PyQt6.QtWidgets import QApplication
from windows.host_config import HostConfigWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    host_config_window = HostConfigWindow()
    host_config_window.show()
    sys.exit(app.exec())
