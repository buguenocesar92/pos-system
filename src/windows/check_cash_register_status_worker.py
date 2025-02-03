# check_cash_register_status_worker.py

from PyQt6.QtCore import QThread, pyqtSignal
import requests
from constants import API_BASE_URL, ACCESS_TOKEN_FILE, HOST_FILE
from utils import read_file

class CheckCashRegisterStatusWorker(QThread):
    """
    Worker que consulta el estado de la caja mediante una petición GET al endpoint /cash-register/status.
    Emite la señal 'finished' con el resultado (un diccionario con la clave 'is_open') o con una excepción.
    """
    finished = pyqtSignal(object)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            # Leer el host configurado
            host = read_file(HOST_FILE)
            if not host:
                raise Exception("El Host no está configurado.")

            # Leer el token de acceso
            token = read_file(ACCESS_TOKEN_FILE)
            if not token:
                raise Exception("El token de acceso no está disponible.")

            url = f"{API_BASE_URL}/cash-register/status"
            headers = {
                "Accept": "application/json",
                "Host": host,
                "Authorization": f"Bearer {token}"
            }

            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                self.finished.emit(response.json())
            else:
                raise Exception(f"Error al consultar el estado de la caja. Código: {response.status_code} - {response.text}")

        except Exception as e:
            self.finished.emit(e)
