# app/services/auth_service.py
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user_model import User # Asegúrate que esto apunte a tu modelo de usuario
from flask_jwt_extended import create_access_token
import datetime

# Función para registrar un nuevo usuario
def register_user(email, password, first_name, last_name, gender, photo_base64):
    # Verificar si el usuario ya existe
    if User.find_by_email(email):
        raise ValueError('El correo electrónico ya está registrado.')

    # Hashear la contraseña antes de guardar
    password_hash = generate_password_hash(password)

    # Crear el nuevo usuario en la base de datos
    new_user = User.create(
        email=email,
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        profile_photo_url=photo_base64 # Asumiendo que photo_base64 es la URL final o el dato en sí
    )
    return new_user.to_dict()

# Función para autenticar un usuario
def authenticate_user(email, password):
    user = User.find_by_email(email)
    if not user or not user.check_password(password):
        raise ValueError('Credenciales inválidas')

    # Si las credenciales son válidas, crear un token JWT
    expires = datetime.timedelta(days=1) # El token expira en 1 día
    access_token = create_access_token(identity=user.id, expires_delta=expires)
    
    return access_token, user.to_dict()