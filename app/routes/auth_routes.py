from flask import Blueprint, request, jsonify
from app.services.auth_service import register_user, authenticate_user

# Crea un Blueprint para las rutas de autenticación
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() # Obtiene los datos JSON de la solicitud
    # Extrae los campos del JSON
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    gender = data.get('gender')
    photo_base64 = data.get('photoBase64') # Recibe la imagen en base64

    # Validación básica de campos obligatorios
    if not all([email, password, first_name, last_name]):
        return jsonify({'success': False, 'message': 'Todos los campos obligatorios deben ser proporcionados.'}), 400

    try:
        # Llama al servicio de registro
        user_data = register_user(email, password, first_name, last_name, gender, photo_base64)
        return jsonify({'success': True, 'message': 'Registro exitoso', 'user': user_data}), 201 # 201 Created
    except ValueError as e:
        # Manejo de errores de validación o lógica de negocio
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        # Manejo de otros errores inesperados
        print(f"Error durante el registro: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor durante el registro.'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Validación básica de campos obligatorios
    if not email or not password:
        return jsonify({'success': False, 'message': 'Correo y contraseña son obligatorios'}), 400

    try:
        # Llama al servicio de autenticación
        token, user_data = authenticate_user(email, password)
        return jsonify({'success': True, 'message': 'Inicio de sesión exitoso', 'token': token, 'user': user_data}), 200
    except ValueError as e:
        # Manejo de errores de credenciales inválidas
        return jsonify({'success': False, 'message': str(e)}), 401 # 401 Unauthorized
    except Exception as e:
        # Manejo de otros errores inesperados
        print(f"Error durante el inicio de sesión: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor durante el inicio de sesión.'}), 500