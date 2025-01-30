def read_file(file_path):
    try:
        with open(file_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def write_file(file_path, content):
    try:
        with open(file_path, "w") as f:
            f.write(content)
    except IOError as e:
        raise IOError(f"Error al escribir en el archivo: {file_path}. Detalle: {str(e)}")
