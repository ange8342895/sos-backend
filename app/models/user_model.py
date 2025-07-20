# app/models/user_model.py
from app import db # Importa la instancia de SQLAlchemy desde app/__init__.py
from werkzeug.security import generate_password_hash, check_password_hash
# Ya no necesitamos 'uuid' si usamos un id autoincremental de la BD.

class User(db.Model):
    __tablename__ = 'users' # Nombre de la tabla en la base de datos

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(50), nullable=True) # Hacer nullable por si algunos no lo tienen
    profile_photo_url = db.Column(db.String(255), nullable=True) # Hacer nullable
    # --- Nuevo campo para el rol de administrador ---
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Métodos estáticos adaptados para SQLAlchemy
    @staticmethod
    def create(email, password_hash, first_name, last_name, gender, profile_photo_url):
        new_user = User(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            profile_photo_url=profile_photo_url
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def find_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def find_by_id(user_id):
        return User.query.get(user_id) # .get() es para buscar por primary key

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'gender': self.gender,
            'profilePhotoUrl': self.profile_photo_url,
            'isAdmin': self.is_admin # Incluir en el dict para el frontend
        }