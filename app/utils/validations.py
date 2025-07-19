import re

def is_valid_email(email):
    # Expresión regular para validar formato de correo electrónico básico
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email) is not None

def is_strong_password(password):
    # La contraseña debe tener al menos 8 caracteres
    # Incluir al menos una mayúscula, una minúscula, un número y un carácter especial
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True