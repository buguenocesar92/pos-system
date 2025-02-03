from PyQt6.QtCore import QThread, pyqtSignal
import requests

from src.constants import API_BASE_URL, ACCESS_TOKEN_FILE, REFRESH_TOKEN_FILE, HOST_FILE
from src.utils import read_file, write_file

class LoginWorker(QThread):
    # Emite el resultado: un diccionario con la respuesta en caso de éxito, o una excepción en caso de error.
    finished = pyqtSignal(object)

    def __init__(self, email: str, password: str):
        super().__init__()
        self.email = email
        self.password = password

    def run(self):
        try:
            host = read_file(HOST_FILE)
            if not host:
                raise Exception("El Host no está configurado.")
            url = f"{API_BASE_URL}/auth/login"
            data = {"email": self.email, "password": self.password}
            headers = {"Accept": "application/json", "Host": host}
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                resp_json = response.json()
                access_token = resp_json.get("access_token")
                refresh_token = resp_json.get("refresh_token")
                if access_token and refresh_token:
                    write_file(ACCESS_TOKEN_FILE, access_token)
                    write_file(REFRESH_TOKEN_FILE, refresh_token)
                    self.finished.emit(resp_json)
                else:
                    raise Exception("No se obtuvieron los tokens en la respuesta.")
            else:
                raise Exception(f"Error al iniciar sesión. Código: {response.status_code}")
        except Exception as e:
            self.finished.emit(e)
