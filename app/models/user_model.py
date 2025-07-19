import uuid

# Simulación de una base de datos en memoria para los usuarios.
# Los datos se perderán al reiniciar el servidor.
_users_db = {} # {email: User_object}

class User:
    def __init__(self, id, email, password_hash, first_name, last_name, gender, profile_photo_url):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.profile_photo_url = profile_photo_url

    @staticmethod
    def create(email, password_hash, first_name, last_name, gender, profile_photo_url):
        # Genera un ID único para el usuario
        new_id = str(uuid.uuid4())
        new_user = User(new_id, email, password_hash, first_name, last_name, gender, profile_photo_url)
        _users_db[email] = new_user # Almacena el usuario usando el email como clave
        return new_user

    @staticmethod
    def find_by_email(email):
        # Busca un usuario por su correo electrónico
        return _users_db.get(email)

    @staticmethod
    def find_by_id(user_id):
        # Busca un usuario por su ID
        for user in _users_db.values():
            if user.id == user_id:
                return user
        return None

    def to_dict(self):
        # Convierte el objeto User a un diccionario para respuestas JSON
        return {
            'id': self.id,
            'email': self.email,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'gender': self.gender,
            'profilePhotoUrl': self.profile_photo_url
        }