# populate_db.py
import os
import sys
# Añade la ruta de la aplicación al path para poder importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app import create_app, db
from app.models.comisaria import Comisaria
from app.models.user_model import User # Necesario si quieres crear un admin inicial desde aquí también
from app.data.comisarias_data import COMISARIAS_PERU
from werkzeug.security import generate_password_hash

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Asegúrate de que las tablas existan
        db.create_all()

        # --- Crear Usuario Administrador (redundante si ya está en __init__.py, pero útil para testing) ---
        admin_email = "antezanaangelica517@gmail.com"
        admin_password = "sos102Am?"

        admin_user = User.query.filter_by(email=admin_email).first()
        if not admin_user:
            print(f"Creando usuario administrador desde populate_db.py: {admin_email}")
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
            print("Usuario administrador creado.")
        else:
            if not admin_user.is_admin:
                admin_user.is_admin = True
                db.session.commit()
                print(f"El usuario {admin_email} ahora es administrador.")
            print("El usuario administrador ya existe.")

        # --- Poblar la base de datos con comisarías de ejemplo ---
        print("\nPoblando la base de datos con comisarías de ejemplo...")
        for comisaria_data in COMISARIAS_PERU:
            existing_comisaria = Comisaria.query.filter_by(nombre=comisaria_data['nombre']).first()
            if not existing_comisaria:
                new_comisaria = Comisaria(
                    nombre=comisaria_data['nombre'],
                    telefono_celular=comisaria_data.get('telefono_celular'),
                    telefono_fijo=comisaria_data.get('telefono_fijo'),
                    latitud=comisaria_data['latitud'],
                    longitud=comisaria_data['longitud'],
                    departamento=comisaria_data['departamento'],
                    provincia=comisaria_data['provincia'],
                    distrito=comisaria_data['distrito'],
                    direccion=comisaria_data.get('direccion')
                )
                db.session.add(new_comisaria)
                print(f"Añadida: {comisaria_data['nombre']}")
            else:
                print(f"Saltada: {comisaria_data['nombre']} (ya existe)")
        db.session.commit()
        print("Población de comisarías completada.")