# En sos/backend/app/__init__.py

from flask import Flask
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    load_dotenv()

    # ¡Asegúrate de que esta línea esté presente y usa la clave que generaste!
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '112797003c2d7b23df51f5ad3b4454a02ce1b9c71136876e')

    # Asegúrate de que DATABASE_URL exista en Render.
    # Esto reemplaza 'postgres://' por 'postgresql+pg8000://' si es necesario.
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith('postgres://'):
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace('postgres://', 'postgresql+pg8000://', 1)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url # Si ya es postgresql:// o no existe
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')

    with app.app_context():
        from app.models.user_model import User
        db.create_all()

    return app