# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os
from werkzeug.security import generate_password_hash

# Inicializa SQLAlchemy y JWTManager aquí, para que otros módulos los importen.
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # --- Configuración de la Base de Datos ---
    # Usará la variable de entorno DATABASE_URL (para Render.com PostgreSQL)
    # o una base de datos SQLite local para desarrollo si no está definida.
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desactiva el seguimiento de modificaciones

    # --- Configuración de JWT ---
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'tu_secreto_jwt_super_seguro_cambialo')

    # Inicializa las extensiones con la aplicación Flask
    db.init_app(app)
    jwt.init_app(app)

    # --- Importar Blueprints ---
    # Importa tus Blueprints aquí para evitar problemas de importación circular
    from app.routes.auth_routes import auth_bp
    from app.routes.comisarias_routes import comisarias_bp # Nuevo Blueprint para comisarías

    # --- Registrar Blueprints ---
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(comisarias_bp, url_prefix='/api') # Prefijo para rutas de comisarías

    # --- Creación de tablas y usuario administrador al iniciar la app ---
    with app.app_context():
        db.create_all() # Crea todas las tablas definidas en tus modelos (User y Comisaria)

        # Importa el modelo de usuario aquí para evitar circular imports
        from app.models.user_model import User

        # Datos del usuario administrador predefinido
        admin_email = "antezanaangelica517@gmail.com"
        admin_password = "sos102Am?"

        # Busca si el usuario administrador ya existe
        admin_user = User.query.filter_by(email=admin_email).first()

        if not admin_user:
            # Si el usuario administrador no existe, lo crea
            print(f"Creando usuario administrador: {admin_email}")
            new_admin = User(
                first_name="Admin",
                last_name="SOS",
                email=admin_email,
                password_hash=generate_password_hash(admin_password), # ¡Importante hashear la contraseña!
                gender="No especificado", # Puedes ajustar si lo necesitas
                profile_photo_url=None, # Puedes poner una URL predeterminada si quieres
                is_admin=True # ¡Este es el campo clave para el rol de administrador!
            )
            db.session.add(new_admin)
            db.session.commit()
            print("Usuario administrador creado exitosamente.")
        else:
            # Si el usuario existe, asegúrate de que tenga el rol de administrador
            if not admin_user.is_admin:
                admin_user.is_admin = True
                db.session.commit()
                print(f"El usuario '{admin_email}' ha sido actualizado a administrador.")
            else:
                print(f"El usuario administrador '{admin_email}' ya existe.")
            # Opcional: Si quieres que siempre tenga la misma contraseña si ya existe:
            # if not admin_user.check_password(admin_password):
            #     admin_user.set_password(admin_password)
            #     db.session.commit()
            #     print(f"Contraseña del administrador '{admin_email}' restablecida.")


    return app