# app/__init__.py

from flask import Flask
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager # <-- NEW: Import JWTManager
from werkzeug.security import generate_password_hash # <-- NEW: Import for password hashing

db = SQLAlchemy()
jwt = JWTManager() # <-- NEW: Initialize JWTManager

def create_app():
    app = Flask(__name__)

    load_dotenv() # Load .env for local development

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '112797003c2d7b23df51f5ad3b4454a02ce1b9c71136876e')

    # --- NEW: JWT Configuration ---
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your_jwt_secret_key_change_me')
    app.config["JWT_TOKEN_LOCATION"] = ["headers"] # Required for Flask-JWT-Extended
    # --- END NEW JWT Configuration ---

    # --- DATABASE CONFIGURATION (Simplified for psycopg2) ---
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # SQLAlchemy will automatically use psycopg2 if psycopg2-binary is installed
        # No need to replace 'postgres://' or 'postgresql://' with specific driver.
        # Just use the URL directly, as psycopg2 is the default for 'postgresql' scheme.
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        print("WARNING: DATABASE_URL environment variable is not set! Using SQLite for local development.")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # Fallback for local dev
    # --- END DATABASE CONFIGURATION ---

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    jwt.init_app(app) # <-- NEW: Initialize JWTManager with the app

    # --- Import Blueprints ---
    from app.routes.auth_routes import auth_bp
    from app.routes.comisarias_routes import comisarias_bp # <-- NEW: Import comisarias blueprint

    # --- Register Blueprints ---
    app.register_blueprint(auth_bp, url_prefix='/api/auth') # <-- CHANGED URL PREFIX to make sense with /api/auth/register, /api/auth/login
    app.register_blueprint(comisarias_bp, url_prefix='/api') # <-- NEW: Register comisarias blueprint


    with app.app_context():
        db.create_all() # This creates all tables (User, Comisaria)

        from app.models.user_model import User # <-- Ensure this import is correct

        # --- NEW: Create Default Admin User ---
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
                is_admin=True # Set this user as admin
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
        # --- END NEW Admin User Logic ---

    return app