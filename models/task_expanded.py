import sqlite3
from . import DB_NAME

class Task:
    @staticmethod
    def create_task(name, project_id, assignee_id, start_date, end_date, status, skills, is_approved):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""INSERT INTO tasks (name, project_id, assignee_id, start_date, end_date, status, skills, is_approved) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (name, project_id, assignee_id, start_date, end_date, status, skills, is_approved))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_tasks():
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""SELECT t.*, p.name as project_name, u.username as assignee_name FROM tasks t JOIN projects p ON t.project_id = p.id JOIN users u ON t.assignee_id = u.id""")
        tasks = c.fetchall()
        conn.close()
        return tasks

    @staticmethod
    def get_task_by_id(task_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = c.fetchone()
        conn.close()
        return task
