import os
from dotenv import load_dotenv
from app import create_app

# Carga las variables de entorno desde .env al inicio
load_dotenv()

# Crea la instancia de la aplicación Flask
app = create_app()

if __name__ == '__main__':
    # Obtén el puerto de las variables de entorno o usa 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    # Ejecuta la aplicación en modo depuración (útil durante el desarrollo)
    # host='0.0.0.0' permite que sea accesible desde otras máquinas/emuladores en la red local
    app.run(debug=True, host='0.0.0.0', port=port)