import os
from flask import Flask, render_template, request, redirect, url_for, g, flash, session
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# Nuevas importaciones para PostgreSQL
import psycopg2
import psycopg2.extras # Para DictCursor

app = Flask(__name__)
# CRÍTICO: Usar una variable de entorno para la clave secreta en producción.
# Esta clave debe ser fuerte y secreta para proteger las sesiones de usuario.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu_clave_super_secreta_aqui_cambiala_en_produccion')

# --- Configuración de Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    """Clase de usuario para Flask-Login."""
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    """
    Carga un usuario de la base de datos por su ID para Flask-Login.
    Esta función es utilizada por Flask-Login para recargar al usuario de la sesión.
    """
    db = get_db()
    # Usar el cursor explícitamente y %s como placeholder para PostgreSQL
    cursor = db.cursor()
    cursor.execute('SELECT id, username, password_hash FROM users WHERE id = %s', (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['password_hash'])
    return None

# --- Funciones de Base de Datos (ACTUALIZADAS PARA PostgreSQL) ---

def get_db():
    """
    Establece una conexión con la base de datos PostgreSQL.
    La conexión se almacena en el objeto 'g' de Flask para reutilización por solicitud.
    """
    db = getattr(g, '_database', None)
    if db is None:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            # PARA DESARROLLO LOCAL SIN DBaaS:
            # Si DATABASE_URL no está establecida (ej. en tu entorno local),
            # puedes proporcionar una URL de conexión local de PostgreSQL.
            # Asegúrate de cambiar 'user', 'password', 'localhost:5432' y 'mydatabase'
            # para que coincidan con tu configuración local de PostgreSQL.
            print("ADVERTENCIA: La variable de entorno DATABASE_URL no está configurada. "
                  "Intentando conectar a PostgreSQL local por defecto. ¡Esto no funcionará en producción!")
            # Esto es un placeholder, cámbialo para tu configuración local
            database_url = "postgresql://your_user:your_password@localhost:5432/your_database" 
        
        # Conectar a PostgreSQL
        conn = psycopg2.connect(database_url)
        # Configurar DictCursor para que las filas se devuelvan como diccionarios (ej. fila['columna'])
        conn.cursor_factory = psycopg2.extras.DictCursor
        db = g._database = conn
    return db

@app.teardown_appcontext
def close_connection(exception):
    """
    Cierra la conexión a la base de datos al finalizar el contexto de la aplicación.
    Asegura que la conexión a la base de datos se cierre limpiamente y se confirmen los cambios.
    """
    db = getattr(g, '_database', None)
    if db is not None:
        if not db.autocommit: # Solo confirmar si no está en modo autocommit
            db.commit()
        db.close()

def init_db():
    """
    Inicializa la base de datos creando las tablas según el esquema definido en 'schema.sql'.
    Maneja múltiples sentencias SQL para PostgreSQL.
    """
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        with app.open_resource('schema.sql', mode='r') as f:
            sql_script = f.read()
            # Dividir el script por punto y coma y ejecutar cada sentencia individualmente
            # Esto es necesario porque cursor.execute() en psycopg2 típicamente espera una sola sentencia.
            for statement in sql_script.split(';'):
                stripped_statement = statement.strip()
                if stripped_statement:
                    try:
                        cursor.execute(stripped_statement)
                    except psycopg2.Error as e:
                        # Ignorar errores como "table does not exist" para DROP TABLE IF EXISTS
                        if "does not exist" not in str(e):
                            raise e
        db.commit() # Confirmar los cambios de DDL (CREATE TABLE)
        cursor.close()

# --- Rutas de Autenticación ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Ya has iniciado sesión.', 'info')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        if not username or not password:
            flash('El nombre de usuario y la contraseña no pueden estar vacíos.', 'error')
            return render_template('register.html')

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
        existing_user = cursor.fetchone()
        cursor.close()

        if existing_user:
            flash('El nombre de usuario ya existe. Por favor, elige otro.', 'error')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)',
                       (username, hashed_password))
        db.commit()
        cursor.close()
        flash('Registro exitoso. ¡Ahora puedes iniciar sesión!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Ya has iniciado sesión.', 'info')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = %s', (username,))
        user_data = cursor.fetchone()
        cursor.close()

        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['username'], user_data['password_hash'])
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('index'))

# --- Rutas de la Aplicación (Gestión de Tareas) ---

@app.route('/')
@login_required
def index():
    db = get_db()
    
    status_filter = request.args.get('status_filter', 'all')
    sort_by = request.args.get('sort_by', 'id_desc')
    view_shared_user_id = request.args.get('view_shared_user_id', '').strip()

    query_parts = []
    params = []
    display_user_id_for_title = ""
    is_viewing_others_tasks = False

    # Unir la tabla de tareas con la tabla de usuarios para obtener el nombre de usuario
    query_base = 'SELECT t.id, t.task_description, t.status, t.due_date, t.priority, t.createdBy, t.isPublic, u.username as createdByUsername FROM tasks t JOIN users u ON t.createdBy = u.id'

    if view_shared_user_id and view_shared_user_id != str(current_user.id):
        # Si se proporciona un ID de otro usuario, filtrar por ese ID y que sean públicas
        query_parts.append(' WHERE t.createdBy = %s AND t.isPublic = 1')
        params.append(view_shared_user_id)
        
        # Obtener el nombre de usuario del ID compartido para mostrar en el título
        cursor = db.cursor()
        cursor.execute('SELECT username FROM users WHERE id = %s', (view_shared_user_id,))
        other_user = cursor.fetchone()
        cursor.close()
        other_username = other_user['username'] if other_user else view_shared_user_id
        display_user_id_for_title = f"Tareas de {other_username}"
        is_viewing_others_tasks = True
    else:
        # Mostrar las tareas del usuario actualmente logeado
        query_parts.append(' WHERE t.createdBy = %s')
        params.append(current_user.id)
        display_user_id_for_title = f"Mis Tareas ({current_user.username})"
        is_viewing_others_tasks = False

    # Aplicar filtro de estado adicional si existe
    if status_filter != 'all':
        query_parts.append(' AND t.status = %s')
        params.append(status_filter)

    # Añadir cláusula ORDER BY
    if sort_by == 'id_desc':
        query_parts.append(' ORDER BY t.id DESC')
    elif sort_by == 'due_date_asc':
        query_parts.append(' ORDER BY t.due_date ASC, t.id DESC')
    elif sort_by == 'due_date_desc':
        query_parts.append(' ORDER BY t.due_date DESC, t.id DESC')
    elif sort_by == 'priority_desc':
        # Ordenación por prioridad para PostgreSQL
        query_parts.append(' ORDER BY CASE t.priority WHEN \'Alta\' THEN 1 WHEN \'Media\' THEN 2 WHEN \'Baja\' THEN 3 ELSE 4 END ASC, t.id DESC')
    elif sort_by == 'priority_asc':
        # Ordenación por prioridad para PostgreSQL
        query_parts.append(' ORDER BY CASE t.priority WHEN \'Baja\' THEN 1 WHEN \'Media\' THEN 2 WHEN \'Alta\' THEN 3 ELSE 4 END ASC, t.id DESC')

    final_query = query_base + "".join(query_parts)
    
    cursor = db.cursor()
    cursor.execute(final_query, tuple(params)) # Los parámetros deben ser una tupla
    tasks = cursor.fetchall()
    cursor.close()
    
    return render_template('index.html', 
                           tasks=tasks, 
                           status_filter=status_filter, 
                           sort_by=sort_by,
                           current_user=current_user,
                           view_shared_user_id=view_shared_user_id,
                           display_user_id_for_title=display_user_id_for_title,
                           is_viewing_others_tasks=is_viewing_others_tasks
                           )

@app.route('/add', methods=['POST'])
@login_required
def add_task():
    if request.method == 'POST':
        task_description = request.form['task_description'].strip()
        due_date = request.form['due_date']
        priority = request.form['priority']
        is_public = 1 if request.form.get('is_public') == 'on' else 0

        if not task_description:
            flash('La descripción de la tarea no puede estar vacía.', 'error')
            return redirect(url_for('index'))

        if due_date:
            try:
                datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                flash('Formato de fecha de vencimiento inválido. Use AAAA-MM-DD.', 'error')
                return redirect(url_for('index'))
        else:
            due_date = None

        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO tasks (task_description, due_date, priority, createdBy, isPublic) VALUES (%s, %s, %s, %s, %s)',
                       (task_description, due_date, priority, current_user.id, is_public))
        db.commit()
        cursor.close()
        flash('Tarea añadida correctamente.', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>')
@login_required
def edit_task(task_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, task_description, status, due_date, priority, createdBy, isPublic FROM tasks WHERE id = %s AND createdBy = %s', (task_id, current_user.id))
    task = cursor.fetchone()
    cursor.close()
    if task is None:
        flash('Tarea no encontrada o no tienes permiso para editarla.', 'error')
        return redirect(url_for('index'))
    return render_template('edit.html', task=task)

@app.route('/update/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    if request.method == 'POST':
        task_description = request.form['task_description'].strip()
        due_date = request.form['due_date']
        priority = request.form['priority']
        status = request.form['status']
        is_public = 1 if request.form.get('is_public') == 'on' else 0

        if not task_description:
            flash('La descripción de la tarea no puede estar vacía.', 'error')
            return redirect(url_for('edit_task', task_id=task_id))

        if due_date:
            try:
                datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                flash('Formato de fecha de vencimiento inválido. Use AAAA-MM-DD.', 'error')
                return redirect(url_for('edit_task', task_id=task_id))
        else:
            due_date = None

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT createdBy FROM tasks WHERE id = %s', (task_id,))
        task = cursor.fetchone()
        
        if task and task['createdBy'] == current_user.id:
            cursor.execute('UPDATE tasks SET task_description = %s, due_date = %s, priority = %s, status = %s, isPublic = %s WHERE id = %s',
                           (task_description, due_date, priority, status, is_public, task_id))
            db.commit()
            flash('Tarea actualizada correctamente.', 'success')
        else:
            flash('No tienes permiso para actualizar esta tarea.', 'error')
        cursor.close()
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>')
@login_required
def complete_task(task_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT createdBy FROM tasks WHERE id = %s', (task_id,))
    task = cursor.fetchone()

    if task and task['createdBy'] == current_user.id:
        cursor.execute('UPDATE tasks SET status = %s WHERE id = %s', ('completed', task_id))
        db.commit()
        flash('Tarea marcada como completada.', 'success')
    else:
        flash('No tienes permiso para completar esta tarea.', 'error')
    cursor.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT createdBy FROM tasks WHERE id = %s', (task_id,))
    task = cursor.fetchone()

    if task and task['createdBy'] == current_user.id:
        cursor.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
        db.commit()
        flash('Tarea eliminada correctamente.', 'success')
    else:
        flash('No tienes permiso para eliminar esta tarea.', 'error')
    cursor.close()
    return redirect(url_for('index'))

@app.route('/toggle_public/<int:task_id>')
@login_required
def toggle_public_status(task_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT createdBy, isPublic FROM tasks WHERE id = %s', (task_id,))
    task = cursor.fetchone()

    if task and task['createdBy'] == current_user.id:
        new_public_status = 1 if task['isPublic'] == 0 else 0 # Alternar el estado
        cursor.execute('UPDATE tasks SET isPublic = %s WHERE id = %s', (new_public_status, task_id))
        db.commit()
        flash(f'Tarea marcada como {"pública" if new_public_status == 1 else "privada"}.', 'success')
    else:
        flash('No tienes permiso para cambiar el estado de privacidad de esta tarea.', 'error')
    cursor.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Para desarrollo local, si tienes PostgreSQL instalado y configurado
    # Puedes crear una base de datos y un usuario, y luego ejecutar init_db()
    # Una vez que la DB está inicializada, puedes comentar esta línea
    # with app.app_context():
    #     init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
