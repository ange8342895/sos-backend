# app/routes/comisarias_routes.py
from flask import Blueprint, request, jsonify
from app import db # Importa la instancia de SQLAlchemy
from app.models.comisaria import Comisaria
from app.models.user_model import User # Importa el modelo de usuario para verificar el rol
from flask_jwt_extended import jwt_required, get_jwt_identity
from math import radians, sin, cos, sqrt, atan2

comisarias_bp = Blueprint('comisarias', __name__)

# --- Decorador personalizado para requerir rol de administrador ---
def admin_required():
    def wrapper(fn):
        @jwt_required() # Primero verifica que el usuario esté autenticado
        def decorator(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.find_by_id(current_user_id) # Busca el usuario en la BD (SQLAlchemy)
            if not user or not user.is_admin:
                return jsonify({"message": "Acceso denegado: Se requiere rol de administrador."}), 403 # 403 Forbidden
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# --- Rutas de Gestión de Comisarías (SÓLO PARA ADMINISTRADORES) ---

@comisarias_bp.route('/comisarias', methods=['POST'])
@admin_required() # Protegida por el decorador admin_required
def add_comisaria():
    data = request.get_json()
    required_fields = ['nombre', 'latitud', 'longitud', 'departamento', 'provincia', 'distrito']
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Faltan campos obligatorios (nombre, latitud, longitud, departamento, provincia, distrito)."}), 400

    try:
        new_comisaria = Comisaria(
            nombre=data['nombre'],
            telefono_celular=data.get('telefonoCelular'),
            telefono_fijo=data.get('telefonoFijo'),
            latitud=data['latitud'],
            longitud=data['longitud'],
            departamento=data['departamento'],
            provincia=data['provincia'],
            distrito=data['distrito'],
            direccion=data.get('direccion')
        )
        db.session.add(new_comisaria)
        db.session.commit()
        return jsonify({"message": "Comisaría añadida exitosamente", "comisaria": new_comisaria.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error al añadir comisaría: {e}")
        return jsonify({"message": f"Error interno del servidor al añadir comisaría: {str(e)}"}), 500

@comisarias_bp.route('/comisarias', methods=['GET'])
@admin_required() # Protegida por el decorador admin_required
def get_all_comisarias():
    comisarias = Comisaria.query.all()
    return jsonify({"comisarias": [c.to_dict() for c in comisarias]}), 200

@comisarias_bp.route('/comisarias/<int:comisaria_id>', methods=['GET'])
@admin_required() # Protegida por el decorador admin_required
def get_comisaria(comisaria_id):
    comisaria = Comisaria.query.get(comisaria_id)
    if not comisaria:
        return jsonify({"message": "Comisaría no encontrada."}), 404
    return jsonify({"comisaria": comisaria.to_dict()}), 200


@comisarias_bp.route('/comisarias/<int:comisaria_id>', methods=['PUT'])
@admin_required() # Protegida por el decorador admin_required
def update_comisaria(comisaria_id):
    comisaria = Comisaria.query.get(comisaria_id)
    if not comisaria:
        return jsonify({"message": "Comisaría no encontrada."}), 404

    data = request.get_json()
    comisaria.nombre = data.get('nombre', comisaria.nombre)
    comisaria.telefono_celular = data.get('telefonoCelular', comisaria.telefono_celular)
    comisaria.telefono_fijo = data.get('telefonoFijo', comisaria.telefono_fijo)
    comisaria.latitud = data.get('latitud', comisaria.latitud)
    comisaria.longitud = data.get('longitud', comisaria.longitud)
    comisaria.departamento = data.get('departamento', comisaria.departamento)
    comisaria.provincia = data.get('provincia', comisaria.provincia)
    comisaria.distrito = data.get('distrito', comisaria.distrito)
    comisaria.direccion = data.get('direccion', comisaria.direccion)

    try:
        db.session.commit()
        return jsonify({"message": "Comisaría actualizada exitosamente", "comisaria": comisaria.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar comisaría: {e}")
        return jsonify({"message": f"Error interno del servidor al actualizar comisaría: {str(e)}"}), 500

@comisarias_bp.route('/comisarias/<int:comisaria_id>', methods=['DELETE'])
@admin_required() # Protegida por el decorador admin_required
def delete_comisaria(comisaria_id):
    comisaria = Comisaria.query.get(comisaria_id)
    if not comisaria:
        return jsonify({"message": "Comisaría no encontrada."}), 404

    try:
        db.session.delete(comisaria)
        db.session.commit()
        return jsonify({"message": "Comisaría eliminada exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar comisaría: {e}")
        return jsonify({"message": f"Error interno del servidor al eliminar comisaría: {str(e)}"}), 500

# --- Ruta de Búsqueda de Comisaría Más Cercana (ACCESIBLE PARA TODOS LOS USUARIOS AUTENTICADOS) ---
@comisarias_bp.route('/comisarias/nearest', methods=['GET'])
@jwt_required() # Accesible para cualquier usuario autenticado (normal o admin)
def get_nearest_comisaria():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    if lat is None or lon is None:
        return jsonify({"message": "Latitud y longitud son obligatorias (parámetros 'lat' y 'lon')."}), 400

    R = 6371 # Radio de la Tierra en kilómetros

    nearest_comisaria = None
    min_distance = float('inf')

    all_comisarias = Comisaria.query.all() # Consulta la base de datos

    for comisaria in all_comisarias:
        lat1 = radians(lat)
        lon1 = radians(lon)
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
        return jsonify({"comisaria": nearest_comisaria.to_dict(), "distanceKm": round(min_distance, 2)}), 200
    else:
        return jsonify({"message": "No se encontró ninguna comisaría cerca de la ubicación proporcionada."}), 404