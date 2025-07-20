# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
import os
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Configuración de JWT ---
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'tu_secreto_jwt_super_seguro_cambialo')
    # NEW LINE HERE: Tell Flask-JWT-Extended where to look for tokens
    app.config["JWT_TOKEN_LOCATION"] = ["headers"] # <--- ADD THIS LINE

    db.init_app(app)
    jwt.init_app(app)

    from app.routes.auth_routes import auth_bp
    from app.routes.comisarias_routes import comisarias_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(comisarias_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

        from app.models.user_model import User

        admin_email = "antezanaangelica517@gmail.com"
        admin_password = "sos102Am?"

        admin_user = User.query.filter_by(email=admin_email).first()

        if not admin_user:
            print(f"Creando usuario administrador: {admin_email}")
            new_admin = User(
                first_name="Admin",
                last_name="SOS",
                email=admin_email,
                password_hash=generate_password_hash(admin_password),
                gender="No especificado",
                profile_photo_url=None,
                is_admin=True
            )
            db.session.add(new_admin)
            db.session.commit()
            print("Usuario administrador creado exitosamente.")
        else:
            if not admin_user.is_admin:
                admin_user.is_admin = True
                db.session.commit()
                print(f"El usuario '{admin_email}' ha sido actualizado a administrador.")
            else:
                print(f"El usuario administrador '{admin_email}' ya existe.")

    return app