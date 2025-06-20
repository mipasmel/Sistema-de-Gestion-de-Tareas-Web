# ✅ Sistema de Gestión de Tareas Web (Flask & PostgreSQL) 🚀

Un robusto sistema de gestión de tareas basado en la web, desarrollado con Python y el microframework Flask, utilizando PostgreSQL como base de datos. Permite a los usuarios añadir, ver, actualizar, asignar y eliminar tareas de manera eficiente a través de una interfaz de navegador, incluyendo la posibilidad de asociar una URL a una foto de la tarea completada.

# 📝 Tabla de Contenidos
## ✅ Sistema de Gestión de Tareas Web (Flask & PostgreSQL) 🚀
## ✨ Descripción
## 🌟 Características
## 🛠️ Tecnologías Utilizadas
## 🚀 Instalación y Ejecución
- Prerrequisitos
- Configuración de PostgreSQL
- Pasos de Instalación del Proyecto
  
## 🌐 Uso
## 🤝 Contribuciones

# ✨ Descripción
Esta aplicación web es un completo sistema de gestión de tareas que aprovecha la potencia de PostgreSQL para el almacenamiento de datos. Ofrece una solución sencilla pero efectiva para organizar tus tareas pendientes, permitiendo operaciones CRUD (Crear, Leer, Actualizar, Eliminar) sobre las tareas. Además, incorpora funcionalidades para asignar tareas a múltiples usuarios y adjuntar una URL de foto cuando una tarea ha sido completada. Es ideal para aprender sobre el desarrollo web con Flask, la interacción con bases de datos relacionales avanzadas como PostgreSQL, y la construcción de interfaces de usuario robustas.

# 🌟 Características
- Creación de Tareas: Añade nuevas tareas con descripciones, fecha de vencimiento y prioridad.
- Visualización de Tareas: Muestra una lista de todas las tareas existentes, incluyendo su estado y si son públicas o privadas.
- Actualización de Tareas: Edita las descripciones, estado, fecha de vencimiento y prioridad de las tareas.
- Eliminación de Tareas: Borra tareas que ya no son necesarias.
- Asignación de Tareas: Asigna tareas a uno o varios usuarios, permitiendo una gestión colaborativa.
- URL de Foto de Tarea Completada: Permite adjuntar una URL a una imagen que demuestra la finalización de una tarea.
- Gestión de Usuarios: Creación y autenticación de usuarios (aunque la validación por contraseña en app.py podría ser opcional/no requerida para simplificar el login en esta versión).
- Base de Datos PostgreSQL: Almacenamiento persistente y escalable de los datos.
- Interfaz Web Intuitiva: Acceso a la funcionalidad a través de un navegador web.

# 🛠️ Tecnologías Utilizadas
- Python 3.12.10: Lenguaje de programación principal.
- Flask: Microframework web para Python.
- PostgreSQL: Sistema de gestión de bases de datos relacionales.
- psycopg2 (o psycopg2-binary): Adaptador de PostgreSQL para Python.
- HTML/CSS: Para la estructura y el estilo de la interfaz web.

# 🚀 Instalación y Ejecución
Sigue estos pasos para poner en marcha la aplicación en tu entorno local.

Prerrequisitos
Asegúrate de tener instalado:

- Python 3.12.10 (Descargar Python)
- pip (el gestor de paquetes de Python, suele venir con Python)
- Un servidor PostgreSQL instalado y en funcionamiento en tu máquina local o en un servidor accesible.
    - Puedes descargarlo desde postgresql.org/download/.
    
   ### Configuración de PostgreSQL
   #### 1) Crea un usuario y una base de datos en PostgreSQL para tu aplicación. Puedes hacerlo a través de la consola psql o una herramienta como pgAdmin.

    SQL

    -- Conéctate a tu base de datos por defecto (ej. 'postgres')
    CREATE USER task_user WITH PASSWORD 'tu_contraseña_segura';
    CREATE DATABASE task_manager_db WITH OWNER task_user;
    GRANT ALL PRIVILEGES ON DATABASE task_manager_db TO task_user;
    
    - Importante: Reemplaza 'tu_contraseña_segura' con una contraseña fuerte y segura.
    
   #### 2) Configura las credenciales de la base de datos en tu aplicación Flask. Esto se hará usualmente en tu archivo app.py o en un archivo de configuración separado, usando una cadena de conexión como:

    Python
    
    DATABASE_URL = "postgresql://task_user:tu_contraseña_segura@localhost:5432/task_manager_db"
    Asegúrate de que tu aplicación lea esta variable para conectar a la DB

    #### 3) Ejecuta el script schema.sql para crear las tablas en tu nueva base de datos. Puedes hacerlo usando psql desde tu terminal:
```Bash

    psql -U task_user -d task_manager_db -f schema.sql
```
    

Nota: Asegúrate de que schema.sql esté en el directorio correcto o proporciona la ruta completa.

   ## Pasos de Instalación del Proyecto
   ### 1) Clona el repositorio:

    Bash

    git clone https://github.com/mipasmel/Sistema-de-Gesti-n-de-Tareas-Web-Python-Flask-SQLite-2.0.git
    cd Sistema-de-Gesti-n-de-Tareas-Web-Python-Flask-SQLite-2.0
    
    
   ### 2) Crea y activa un entorno virtual (recomendado):

    Bash

    python -m venv venv
    
#### En Windows:
    .\venv\Scripts\activate
    
#### En macOS/Linux:
    source venv/bin/activate

   ### 3) Instala las dependencias:
Asegúrate de que tu requirements.txt incluya Flask y psycopg2 (o psycopg2-binary).

    Bash

    pip install -r requirements.txt
(Si aún no tienes un requirements.txt, puedes crearlo después de instalar las dependencias con pip freeze > requirements.txt)

   ### 4) Ejecuta la aplicación:

    Bash

    export FLASK_APP=app.py # O el nombre de tu archivo principal de Flask, ej. main.py
    flask run
 (En Windows, usa set FLASK_APP=app.py en lugar de export).

# 🌐 Uso

Una vez que la aplicación esté ejecutándose, abre tu navegador web y navega a la dirección que te proporcione Flask (normalmente http://127.0.0.1:5000/).

Desde allí, podrás:

- Registrar nuevos usuarios (si aplica).
- Iniciar sesión.
- Añadir nuevas tareas con detalles como descripción, fecha de vencimiento y prioridad.
- Asignar tareas a otros usuarios.
- Editar tareas existentes y actualizar su estado, incluyendo la URL de una foto de finalización.
- Eliminar tareas.
- Ver las tareas asignadas a ti o creadas por ti.

# 🤝 Contribuciones

¡Las contribuciones son bienvenidas y muy apreciadas! Si deseas mejorar este proyecto, corregir un error o añadir nuevas características, por favor:

Abre un "issue" para discutir tu propuesta o reportar un error.

Haz un "fork" de este repositorio.

Crea una nueva rama para tu característica (git checkout -b feature/nombre-de-la-caracteristica).

Realiza tus cambios y haz "commit" de ellos (git commit -m 'feat: añade funcionalidad X').

Empuja la rama a tu "fork" (git push origin feature/nombre-de-la-caracteristica).

Abre un "Pull Request" a la rama main de este repositorio.


