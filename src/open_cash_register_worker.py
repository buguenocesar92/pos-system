# open_cash_register_worker.py

from PyQt6.QtCore import QThread, pyqtSignal
import requests
from constants import API_BASE_URL, ACCESS_TOKEN_FILE, HOST_FILE
from utils import read_file

class OpenCashRegisterWorker(QThread):
    """
    Worker para abrir la caja mediante una petición POST al endpoint /cash-register/open.
    Emite la señal 'finished' con un diccionario con la respuesta en caso de éxito,
    o una excepción en caso de error.
    """
    finished = pyqtSignal(object)

    def __init__(self, opening_amount):
        """
        :param opening_amount: Valor de apertura (debe ser numérico, por ejemplo 1000.0)
        """
        super().__init__()
        self.opening_amount = opening_amount

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

            url = f"{API_BASE_URL}/cash-register/open"
            # Se arma el payload a enviar por form data
            data = {"opening_amount": self.opening_amount}

            headers = {
                "Accept": "application/json",
                "Host": host,
                "Authorization": f"Bearer {token}"
            }

            # Realizar la petición POST
            response = requests.post(url, headers=headers, data=data)

            # Si la respuesta es exitosa (por ejemplo, 200 o 201), se procesa la respuesta
            if response.status_code in (200, 201):
                self.finished.emit(response.json())
            else:
                raise Exception(f"Error al abrir caja. Código: {response.status_code} - {response.text}")

        except Exception as e:
            self.finished.emit(e)
