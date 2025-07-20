# En sos/backend/app/__init__.py

from flask import Flask
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    load_dotenv()

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '112797003c2d7b23df51f5ad3b4454a02ce1b9c71136876e')

    # --- CAMBIO CLAVE AQUÍ ---
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Reemplaza 'postgres://' por 'postgresql+pg8000://' para que SQLAlchemy use pg8000
        if database_url.startswith('postgres://'):
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace('postgres://', 'postgresql+pg8000://', 1)
        elif database_url.startswith('postgresql://') and not 'pg8000' in database_url:
            # Si ya es postgresql:// pero no especifica un driver, asegúrate de que use pg8000
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace('postgresql://', 'postgresql+pg8000://', 1)
        else:
            # Si ya está bien (ej. 'postgresql+pg8000://' o un dialecto diferente)
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Esto es importante si DATABASE_URL no se encuentra. Maneja el caso.
        print("WARNING: DATABASE_URL environment variable is not set!")
        # Puedes establecer una URL de fallback para desarrollo local o levantar un error
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # Ejemplo para desarrollo local
        pass # O levanta un error si la DB es obligatoria para el despliegue
    # --- FIN DEL CAMBIO CLAVE ---


    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from app.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api')

    with app.app_context():
        from app.models.user_model import User
        # Solo crea tablas si la DB_URL está configurada y no en un entorno de solo lectura
        if app.config['SQLALCHEMY_DATABASE_URI']:
            db.create_all()

    return app