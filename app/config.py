import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu_super_clave_secreta_default'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    # Puedes añadir más configuraciones aquí, si las necesitas