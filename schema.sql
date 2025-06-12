-- schema.sql (ACTUALIZADO PARA PostgreSQL)
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;

-- Tabla de Usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY, -- SERIAL para autoincremento en PostgreSQL
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- Tabla de Tareas
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY, -- SERIAL para autoincremento en PostgreSQL
    task_description TEXT NOT NULL,
    status TEXT DEFAULT 'pending' NOT NULL,
    due_date TEXT, -- Mantener como TEXT si la fecha no necesita operaciones SQL
    priority TEXT DEFAULT 'Baja' NOT NULL,
    createdBy INTEGER NOT NULL, -- ID del usuario que creó la tarea
    isPublic INTEGER DEFAULT 0 NOT NULL, -- 0 para privado, 1 para público
    FOREIGN KEY (createdBy) REFERENCES users(id) ON DELETE CASCADE -- ON DELETE CASCADE para eliminar tareas si el usuario es eliminado
);
