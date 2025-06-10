-- schema.sql
DROP TABLE IF EXISTS tasks;
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_description TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    due_date TEXT, -- Nueva columna para la fecha de vencimiento (formato YYYY-MM-DD)
    priority TEXT DEFAULT 'Media' -- Nueva columna para la prioridad (ej. 'Baja', 'Media', 'Alta')
);