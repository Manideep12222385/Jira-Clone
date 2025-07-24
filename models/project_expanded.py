import sqlite3
from . import DB_NAME

class Project:
    @staticmethod
    def create_project(name, client_id, team_id, start_date, end_date, is_approved):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""INSERT INTO projects (name, client_id, team_id, start_date, end_date, is_approved) VALUES (?, ?, ?, ?, ?, ?)""", (name, client_id, team_id, start_date, end_date, is_approved))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_projects():
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""SELECT p.*, u.username as client_name, t.name as team_name FROM projects p JOIN users u ON p.client_id = u.id JOIN teams t ON p.team_id = t.id""")
        projects = c.fetchall()
        conn.close()
        return projects

    @staticmethod
    def get_project_by_id(project_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        project = c.fetchone()
        conn.close()
        return project
