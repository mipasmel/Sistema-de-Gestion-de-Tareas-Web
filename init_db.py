# init_db.py
from app import app, init_db

# Ejecutar la función init_db() dentro del contexto de la aplicación
with app.app_context():
    init_db()
print("Base de datos inicializada o ya existente.")