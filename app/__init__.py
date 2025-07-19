from flask import Flask
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy # Asegúrate de que esta importación esté

db = SQLAlchemy() # Asegúrate de que esta línea esté

def create_app():
    app = Flask(__name__)

    # Puedes dejar load_dotenv() para que funcione en tu entorno local si lo deseas,
    # pero Render no lo usa ya que maneja las variables de entorno directamente.
    load_dotenv()

    # Configuración de la aplicación
    # Render proporcionará SECRET_KEY y DATABASE_URL directamente
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') # Ya no necesitamos un default aquí
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') # ¡Importante! Sin default local aquí
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Esto también debe estar aquí

    db.init_app(app) # Inicializa SQLAlchemy con la aplicación Flask

    # Importa y registra los Blueprints (módulos de rutas)
    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')

    # Importa los modelos y crea las tablas si no existen
    with app.app_context():
        from app.models.user_model import User # Asegúrate de que este import esté
        db.create_all() # ¡Esto creará las tablas en tu DB de Render la primera vez!

    return app