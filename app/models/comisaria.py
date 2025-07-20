# app/models/comisaria.py
from app import db # Importa la instancia de SQLAlchemy

class Comisaria(db.Model):
    __tablename__ = 'comisarias' # Nombre de la tabla en la base de datos

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    telefono_celular = db.Column(db.String(20), nullable=True)
    telefono_fijo = db.Column(db.String(20), nullable=True)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    departamento = db.Column(db.String(100), nullable=False)
    provincia = db.Column(db.String(100), nullable=False)
    distrito = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'telefonoCelular': self.telefono_celular,
            'telefonoFijo': self.telefono_fijo,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'departamento': self.departamento,
            'provincia': self.provincia,
            'distrito': self.distrito,
            'direccion': self.direccion
        }