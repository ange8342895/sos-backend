# app/routes/auth_routes.py
from flask import Blueprint, request, jsonify
from app.services.auth_service import register_user, authenticate_user
from twilio.rest import Client
import os
from flask_jwt_extended import jwt_required, get_jwt_identity # Importa estos para JWT
from app.models.user_model import User # ¡Asegúrate que esto apunte a tu modelo de usuario!
from app.models.comisaria import Comisaria # Necesitamos importar el modelo Comisaria
from math import radians, sin, cos, sqrt, atan2 # Para cálculo de distancia

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    gender = data.get('gender')
    photo_base64 = data.get('photoBase64')

    if not all([email, password, first_name, last_name]):
        return jsonify({'success': False, 'message': 'Todos los campos obligatorios deben ser proporcionados.'}), 400

    try:
        user_data = register_user(email, password, first_name, last_name, gender, photo_base64)
        return jsonify({'success': True, 'message': 'Registro exitoso', 'user': user_data}), 201
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        print(f"Error durante el registro: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor durante el registro.'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Correo y contraseña son obligatorios'}), 400

    try:
        token, user_data = authenticate_user(email, password)
        return jsonify({'success': True, 'message': 'Inicio de sesión exitoso', 'token': token, 'user': user_data}), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 401
    except Exception as e:
        print(f"Error durante el inicio de sesión: {e}")
        return jsonify({'success': False, 'message': 'Error interno del servidor durante el inicio de sesión.'}), 500

# --- Ruta para Envío de Alerta SOS (protegida por JWT) ---
@auth_bp.route('/send_sos', methods=['POST'])
@jwt_required() # Protege esta ruta, requiere autenticación
def send_sos():
    current_user_id = get_jwt_identity() # Obtiene el ID del usuario del token JWT
    user = User.find_by_id(current_user_id) # Busca el usuario en la BD (SQLAlchemy)
    if not user:
        return jsonify({"message": "Usuario no encontrado."}), 404

    data = request.get_json()
    location_info = data.get('location')

    if not location_info:
        return jsonify({"message": "Información de ubicación es obligatoria."}), 400

    user_name = f"{user.first_name} {user.last_name}"

    target_numbers = []
    comisaria_encontrada_nombre = "No encontrada"
    comisaria_distancia_km = "N/A"

    lat_usuario = None
    lon_usuario = None
    if "Lat:" in location_info and "Lon:" in location_info:
        try:
            lat_usuario = float(location_info.split('Lat: ')[1].split(',')[0].strip())
            lon_usuario = float(location_info.split('Lon: ')[1].strip())
        except ValueError:
            print(f"Advertencia: No se pudo parsear lat/lon de '{location_info}'.")
            lat_usuario = None
            lon_usuario = None

    if lat_usuario is not None and lon_usuario is not None:
        R = 6371 # Radio de la Tierra en kilómetros (para Haversine)

        nearest_comisaria = None
        min_distance = float('inf')

        # Consulta todas las comisarías de la base de datos (SQLAlchemy)
        all_comisarias = Comisaria.query.all()

        for comisaria in all_comisarias:
            lat1 = radians(lat_usuario)
            lon1 = radians(lon_usuario)
            lat2 = radians(comisaria.latitud)
            lon2 = radians(comisaria.longitud)

            dlon = lon2 - lon1
            dlat = lat2 - lat1

            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance = R * c

            if distance < min_distance:
                min_distance = distance
                nearest_comisaria = comisaria

        if nearest_comisaria:
            comisaria_encontrada_nombre = nearest_comisaria.nombre
            comisaria_distancia_km = round(min_distance, 2)
            if nearest_comisaria.telefono_celular:
                target_numbers.append(nearest_comisaria.telefono_celular)
                print(f"Comisaría cercana encontrada: {comisaria_encontrada_nombre} (Celular: {nearest_comisaria.telefono_celular})")
            elif nearest_comisaria.telefono_fijo:
                 target_numbers.append(nearest_comisaria.telefono_fijo)
                 print(f"Comisaría cercana encontrada: {comisaria_encontrada_nombre} (Fijo: {nearest_comisaria.telefono_fijo})")
            else:
                print(f"Comisaría {comisaria_encontrada_nombre} encontrada, pero sin número de contacto válido.")
        else:
            print("No se encontró comisaría en la base de datos cerca de la ubicación proporcionada.")
    else:
        print("Latitud/Longitud no válidas para buscar comisaría.")

    personal_test_number = os.environ.get('EMERGENCY_CONTACT_NUMBER')
    if personal_test_number and personal_test_number not in target_numbers:
        target_numbers.append(personal_test_number)
        print(f"Añadiendo número de prueba personal: {personal_test_number}")

    if not target_numbers:
        return jsonify({"success": False, "message": "No se encontró ningún número de contacto de emergencia válido."}), 400

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')

    if not all([account_sid, auth_token, twilio_phone_number]):
        return jsonify({"success": False, "message": "Error de configuración de Twilio."}), 500

    try:
        client = Client(account_sid, auth_token)
        message_body = f"¡ALERTA SOS de {user_name}! COMISARÍA: {comisaria_encontrada_nombre}. "

        maps_link = ""
        if lat_usuario is not None and lon_usuario is not None:
            maps_link = f"https://www.google.com/maps/search/?api=1&query={lat_usuario},{lon_usuario}"
            message_body += f"Ubicación: Lat: {lat_usuario}, Lon: {lon_usuario}. Distancia a comisaría: {comisaria_distancia_km}km. Ver en mapa: {maps_link}"
        else:
            message_body += f"Ubicación: {location_info}. "

        sent_to = []
        for number in target_numbers:
            try:
                message = client.messages.create(
                    to=number,
                    from_=twilio_phone_number,
                    body=message_body
                )
                sent_to.append(number)
                print(f"Mensaje SOS enviado a {number} (SID: {message.sid})")
            except Exception as sms_e:
                print(f"ERROR: Falló el envío de SMS a {number}: {sms_e}")

        if sent_to:
            return jsonify({"success": True, "message": f"Alerta SOS enviada exitosamente a: {', '.join(sent_to)}", "sent_numbers": sent_to}), 200
        else:
            return jsonify({"success": False, "message": "Fallo al enviar la alerta SOS a cualquier destinatario."}), 500

    except Exception as e:
        print(f"Error general durante el envío de SOS: {e}")
        return jsonify({"success": False, "message": f"Error interno del servidor: {str(e)}"}), 500