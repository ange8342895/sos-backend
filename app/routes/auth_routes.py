from flask import Blueprint, request, jsonify
from app.services.auth_service import register_user, authenticate_user
from twilio.rest import Client  # Importa la librería de Twilio
import os  # Importa os para acceder a las variables de entorno

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



### **Nueva Ruta para Envío de Alerta SOS**


@auth_bp.route('/send_sos', methods=['POST'])
def send_sos():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    user_name = data.get('userName')
    location_info = data.get('location') # Esto será tu "Lat: X, Lon: Y" desde Flutter

    if not user_name or not location_info:
        return jsonify({"message": "Missing user name or location"}), 400

    # Obtener credenciales de Twilio y el número de contacto de emergencia de las variables de entorno
    # IMPORTANTE: Asegúrate de configurar estas variables en Render.com
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER') # El número de Twilio
    emergency_contact_number = os.environ.get('EMERGENCY_CONTACT_NUMBER') # ¡Tu número: +51982962559!

    if not all([account_sid, auth_token, twilio_phone_number, emergency_contact_number]):
        print("ERROR: Credenciales de Twilio o número de contacto de emergencia no configurados en el backend.")
        return jsonify({"message": "Server configuration error for SOS service"}), 500

    try:
        client = Client(account_sid, auth_token)

        message_body = f"¡ALERTA SOS! Nombre: {user_name}. Ubicación: {location_info}. "

        # Intentar añadir enlace de Google Maps si la ubicación es válida
        if "Lat:" in location_info and "Lon:" in location_info:
            try:
                lat = location_info.split('Lat: ')[1].split(',')[0].strip()
                lon = location_info.split('Lon: ')[1].strip()
                maps_link = f"[https://www.google.com/maps/search/?api=1&query=](https://www.google.com/maps/search/?api=1&query=){lat},{lon}"
                message_body += f" Ver en mapa: {maps_link}"
            except Exception as e:
                print(f"Error al parsear ubicación para mapa: {e}")
                # Si falla el parseo, el mensaje sigue sin el enlace al mapa

        message = client.messages.create(
            to=emergency_contact_number, # ¡Aquí se envía el SMS a TU número!
            from_=twilio_phone_number,   # Desde el número de Twilio
            body=message_body
        )
        print(f"Mensaje SOS enviado: {message.sid}")
        return jsonify({"message": "SOS alert sent successfully via SMS Gateway", "sid": message.sid}), 200

    except Exception as e:
        print(f"Error al enviar SMS SOS: {e}")
        return jsonify({"message": f"Failed to send SOS alert: {str(e)}"}), 500