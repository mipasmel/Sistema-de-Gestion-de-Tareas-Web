#!/usr/bin/env bash

# Inicializar la base de datos
python init_db.py # Llama al nuevo script Python

# Iniciar Gunicorn
gunicorn app:app -w 4 --bind 0.0.0.0:$PORT