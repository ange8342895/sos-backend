from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    app = Flask(__name__)

    # Carga las variables de entorno. Asegura que estén disponibles para toda la app.
    load_dotenv()

    # Configuración de la aplicación
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_if_not_set')
    app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')

    # Importa y registra los Blueprints (módulos de rutas)
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')

    return app