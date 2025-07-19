import bcrypt
import jwt
from datetime import datetime, timedelta
import os

# Obtén la clave secreta del entorno. Es crucial para JWT.
SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    raise EnvironmentError("SECRET_KEY no está configurada en las variables de entorno. Asegúrate de tener un archivo .env válido.")

def hash_password(password):
    # Genera un salt y hashea la contraseña. bcrypt es seguro para contraseñas.
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    # Verifica si la contraseña proporcionada coincide con el hash almacenado.
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_jwt(user_id):
    # Payload del token: user_id, fecha de expiración y fecha de emisión.
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1), # El token expira en 1 día
        'iat': datetime.utcnow() # Fecha de emisión del token
    }
    # Codifica el token usando la clave secreta y el algoritmo HS256.
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_jwt(token):
    try:
        # Intenta decodificar el token.
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expirado.")
    except jwt.InvalidTokenError:
        raise ValueError("Token inválido.")