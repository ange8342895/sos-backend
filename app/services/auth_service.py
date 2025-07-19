from app.models.user_model import User
from app.utils.security import hash_password, verify_password, generate_jwt
from app.utils.validations import is_valid_email, is_strong_password

def register_user(email, password, first_name, last_name, gender=None, photo_base64=None):
    # Validaciones de entrada
    if not is_valid_email(email):
        raise ValueError('Correo electrónico no válido.')
    if not is_strong_password(password):
        raise ValueError('La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y símbolos.')

    # Verifica si el correo ya está registrado
    if User.find_by_email(email):
        raise ValueError('El correo electrónico ya está registrado.')

    # Hashea la contraseña antes de guardarla
    hashed_pw = hash_password(password)

    # En un proyecto real, 'photo_base64' se subiría a un servicio de almacenamiento
    # (como AWS S3, Cloudinary) y la URL resultante se guardaría.
    # Aquí, la guardamos directamente como base64 o None si no se proporciona.
    profile_photo_url = photo_base64 if photo_base64 else None

    # Crea el nuevo usuario en la "base de datos" simulada
    new_user = User.create(email, hashed_pw, first_name, last_name, gender, profile_photo_url)
    return new_user.to_dict() # Devuelve el usuario como un diccionario

def authenticate_user(email, password):
    # Busca el usuario por email
    user = User.find_by_email(email)
    # Verifica si el usuario existe y si la contraseña es correcta
    if not user or not verify_password(password, user.password_hash):
        raise ValueError('Credenciales inválidas.')

    # Genera un token JWT para el usuario autenticado
    token = generate_jwt(user.id)
    return token, user.to_dict() # Devuelve el token y los datos del usuario