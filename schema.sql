-- schema.sql (ACTUALIZADO PARA PostgreSQL)

-- Primero, eliminar las tablas en orden de dependencia inversa
-- Esto es crucial porque 'task_assignments' depende de 'tasks' y 'users',
-- y 'tasks' depende de 'users'.
DROP TABLE IF EXISTS task_assignments;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id SERIAL PRIMARY KEY, -- SERIAL para autoincremento en PostgreSQL
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL -- Se mantiene para compatibilidad con Flask-Login, aunque no se use para validar
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY, -- SERIAL para autoincremento en PostgreSQL
    task_description TEXT NOT NULL,
    status TEXT DEFAULT 'pending' NOT NULL,
    due_date TEXT,
    priority TEXT DEFAULT 'Baja' NOT NULL,
    created_by INTEGER NOT NULL, -- ID del usuario que creó la tarea
    is_public INTEGER DEFAULT 0 NOT NULL, -- 0 para privado, 1 para público
    completed_photo_url TEXT, 
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. NUEVA TABLA: task_assignments (para asignaciones de muchos a muchos)
CREATE TABLE task_assignments (
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (task_id, user_id), -- Clave primaria compuesta para asegurar que una tarea solo se asigne una vez por usuario
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE, -- Si se borra la tarea, se borra la asignación
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE -- Si se borra el usuario, se borran sus asignaciones
);
