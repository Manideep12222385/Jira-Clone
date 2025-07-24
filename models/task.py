import sqlite3
from . import DB_NAME
from .project import Project

class Task:
    @staticmethod
    def get_all_tasks():
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT 
                t.id,
                t.title,
                t.description,
                t.project_id,
                t.assignee_id,
                t.status,
                t.type,
                t.epic,
                t.created_at,
                p.name as project_name,
                u.username as assignee_name
            FROM tasks t
            LEFT JOIN projects p ON t.project_id = p.id
            LEFT JOIN users u ON t.assignee_id = u.id
            ORDER BY p.name, t.title
        """)
        tasks = c.fetchall()
        conn.close()
        return tasks

    @staticmethod
    def get_worker_tasks(user_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        c.execute("SELECT team_id FROM users WHERE id = ?", (user_id,))
        result = c.fetchone()
        if not result or not result[0]:
            conn.close()
            return []
            
        team_id = result[0]
        c.execute("""
            SELECT t.*, p.name as project_name 
            FROM tasks t 
            JOIN projects p ON t.project_id = p.id 
            WHERE p.team_id = ? AND p.is_approved = 1
        """, (team_id,))
        tasks = c.fetchall()
        conn.close()
        return tasks

    @staticmethod
    def update_status(task_id, status):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("SELECT project_id FROM tasks WHERE id = ?", (task_id,))
            project_id = c.fetchone()[0]
            
            c.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
            conn.commit()
            if project_id:
                Project.update_project_progress(project_id)
            
            return True
        except Exception as e:
            print(f"Error updating task status: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_project_tasks_filtered(project_id, epic=None, type_filter=None):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        query = """SELECT t.*, u.username as assignee_name 
                   FROM tasks t 
                   LEFT JOIN users u ON t.assignee_id = u.id 
                   WHERE t.project_id = ?"""
        params = [project_id]
        if epic:
            query += " AND t.epic = ?"
            params.append(epic)
        if type_filter:
            query += " AND t.type = ?"
            params.append(type_filter)
        c.execute(query, params)
        tasks = c.fetchall()
        conn.close()
        return tasks 

    @staticmethod
    def create_task(title, description, project_id, assignee_id, status, type, epic=None):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("""
                INSERT INTO tasks (title, description, project_id, assignee_id, status, type, epic, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (title, description, project_id, assignee_id, status, type, epic))
            task_id = c.lastrowid
            conn.commit()
            
            # Update project progress
            Project.update_project_progress(project_id)
            
            return task_id
        except Exception as e:
            print(f"Error creating task: {e}")
            conn.rollback()
            raise e
        finally:
            conn.close() 

    @staticmethod
    def update_task(task_id, title, description, type):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("""
                UPDATE tasks 
                SET title = ?, description = ?, type = ?
                WHERE id = ?
            """, (title, description, type, task_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating task: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def delete_task(task_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            # Get project_id before deleting
            c.execute("SELECT project_id FROM tasks WHERE id = ?", (task_id,))
            result = c.fetchone()
            project_id = result[0] if result else None

            # Delete the task
            c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()

            # Update project progress if project exists
            if project_id:
                Project.update_project_progress(project_id)
            return True
        except Exception as e:
            print(f"Error deleting task: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_task(task_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT t.*, p.name as project_name 
            FROM tasks t 
            JOIN projects p ON t.project_id = p.id 
            WHERE t.id = ?
        """, (task_id,))
        task = c.fetchone()
        conn.close()
        return task 