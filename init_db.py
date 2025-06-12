# init_db.py
from app import app, init_db

# Ejecuta la función init_db() dentro del contexto de la aplicación Flask
# Esto asegurará que get_db() funcione correctamente para conectar a la DB.
with app.app_context():
    print("Iniciando la inicialización de la base de datos...")
    try:
        init_db()
        print("Base de datos inicializada exitosamente.")
    except Exception as e:
        print(f"Error durante la inicialización de la base de datos: {e}")
        # En un entorno de producción, podrías querer levantar el error
        # para que el despliegue falle si la DB no se inicializa.
        # raise # Descomentar para hacer que el despliegue falle en caso de error de DB