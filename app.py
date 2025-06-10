import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g, flash
from datetime import datetime
import os # Importar os para obtener la clave secreta del entorno

app = Flask(__name__)
# Usar una variable de entorno para la clave secreta en producción
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_dev_secret_key')
app.config['DATABASE'] = 'database.db'

# --- Funciones de Base de Datos ---

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        # Asegurarse de que la ruta de la base de datos sea absoluta
        db_path = os.path.join(app.root_path, app.config['DATABASE'])
        db = g._database = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# --- Rutas de la Aplicación (Vistas) ---

@app.route('/')
def index():
    db = get_db()
    status_filter = request.args.get('status_filter', 'all')
    sort_by = request.args.get('sort_by', 'id_desc')

    query = 'SELECT id, task_description, status, due_date, priority FROM tasks'
    params = []

    if status_filter == 'pending':
        query += ' WHERE status = ?'
        params.append('pending')
    elif status_filter == 'completed':
        query += ' WHERE status = ?'
        params.append('completed')

    if sort_by == 'id_desc':
        query += ' ORDER BY id DESC'
    elif sort_by == 'due_date_asc':
        query += ' ORDER BY due_date ASC, id DESC'
    elif sort_by == 'due_date_desc':
        query += ' ORDER BY due_date DESC, id DESC'
    elif sort_by == 'priority_desc':
        query += ' ORDER BY CASE priority WHEN "Alta" THEN 1 WHEN "Media" THEN 2 WHEN "Baja" THEN 3 ELSE 4 END ASC, id DESC'
    elif sort_by == 'priority_asc':
        query += ' ORDER BY CASE priority WHEN "Baja" THEN 1 WHEN "Media" THEN 2 WHEN "Alta" THEN 3 ELSE 4 END ASC, id DESC'

    cursor = db.execute(query, params)
    tasks = cursor.fetchall()
    return render_template('index.html', tasks=tasks, status_filter=status_filter, sort_by=sort_by)

@app.route('/add', methods=['POST'])
def add_task():
    if request.method == 'POST':
        task_description = request.form['task_description'].strip()
        due_date = request.form['due_date']
        priority = request.form['priority']

        if not task_description:
            flash('La descripción de la tarea no puede estar vacía.', 'error')
            return redirect(url_for('index'))

        if due_date:
            try:
                datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                flash('Formato de fecha de vencimiento inválido. Use YYYY-MM-DD.', 'error')
                return redirect(url_for('index'))
        else:
            due_date = None

        db = get_db()
        db.execute('INSERT INTO tasks (task_description, due_date, priority) VALUES (?, ?, ?)',
                   (task_description, due_date, priority))
        db.commit()
        flash('Tarea añadida correctamente.', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>')
def edit_task(task_id):
    db = get_db()
    cursor = db.execute('SELECT id, task_description, status, due_date, priority FROM tasks WHERE id = ?', (task_id,))
    task = cursor.fetchone()
    if task is None:
        flash('Tarea no encontrada.', 'error')
        return redirect(url_for('index'))
    return render_template('edit.html', task=task)

@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    if request.method == 'POST':
        task_description = request.form['task_description'].strip()
        due_date = request.form['due_date']
        priority = request.form['priority']
        status = request.form['status']

        if not task_description:
            flash('La descripción de la tarea no puede estar vacía.', 'error')
            return redirect(url_for('edit_task', task_id=task_id))

        if due_date:
            try:
                datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                flash('Formato de fecha de vencimiento inválido. Use YYYY-MM-DD.', 'error')
                return redirect(url_for('edit_task', task_id=task_id))
        else:
            due_date = None

        db = get_db()
        db.execute('UPDATE tasks SET task_description = ?, due_date = ?, priority = ?, status = ? WHERE id = ?',
                   (task_description, due_date, priority, status, task_id))
        db.commit()
        flash('Tarea actualizada correctamente.', 'success')
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    db = get_db()
    db.execute('UPDATE tasks SET status = ? WHERE id = ?', ('completed', task_id))
    db.commit()
    flash('Tarea marcada como completada.', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    db.commit()
    flash('Tarea eliminada correctamente.', 'success')
    return redirect(url_for('index'))

# Esto se ejecutará solo cuando el script se ejecute directamente, no cuando sea importado por Gunicorn
if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000) # Mantén esto para tu desarrollo local