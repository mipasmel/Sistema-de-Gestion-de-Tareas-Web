#!/usr/bin/env bash

# Inicializar la base de datos si no existe
# Render ejecuta esto cada vez que el servicio se inicia.
# SQLite solo creará la tabla si no existe, así que es seguro.
python -c "from app import app, init_db; with app.app_context(): init_db()"

# Iniciar Gunicorn
gunicorn app:app -w 4 --bind 0.0.0.0:$PORT