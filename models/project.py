import sqlite3
from . import DB_NAME

class Project:
    @staticmethod
    def get_all_projects():
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT p.*, u.username as client_name, t.name as team_name,
                   (SELECT COUNT(*) FROM tasks WHERE project_id = p.id AND status = 'DONE') as done_tasks,
                   (SELECT COUNT(*) FROM tasks WHERE project_id = p.id) as total_tasks
            FROM projects p
            LEFT JOIN users u ON p.client_id = u.id
            LEFT JOIN teams t ON p.team_id = t.id
        """)
        projects = c.fetchall()
        
        # Calculate progress for each project
        result = []
        for project in projects:
            done_tasks = project[-2]  # Second to last column
            total_tasks = project[-1]  # Last column
            progress = round((done_tasks / total_tasks * 100) if total_tasks > 0 else 0)
            
            # Update progress in database
            c.execute("UPDATE projects SET progress = ? WHERE id = ?", (progress, project[0]))
            
            # Create modified project tuple with updated progress
            project_list = list(project[:-2])  # Remove the last two columns (done_tasks, total_tasks)
            project_list[7] = progress  # Update progress value
            result.append(tuple(project_list))
        
        conn.commit()
        conn.close()
        return result

    @staticmethod
    def create_project(name, description, client_id, team_id, start_date, end_date):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("""
                INSERT INTO projects (name, description, client_id, team_id, start_date, end_date, progress, is_approved)
                VALUES (?, ?, ?, ?, ?, ?, 0, 1)
            """, (name, description, client_id, team_id, start_date, end_date))
            project_id = c.lastrowid
            conn.commit()
            conn.close()
            return project_id
        except sqlite3.IntegrityError:
            conn.close()
            return None

    @staticmethod
    def update_project(project_id, name, description, client_id, team_id, start_date, end_date):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("""
                UPDATE projects 
                SET name = ?, description = ?, client_id = ?, team_id = ?, 
                    start_date = ?, end_date = ?
                WHERE id = ?
            """, (name, description, client_id, team_id, start_date, end_date, project_id))
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False

    @staticmethod
    def delete_project(project_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            # First delete all tasks associated with this project
            c.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
            # Then delete the project
            c.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False

    @staticmethod
    def get_client_projects(client_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT p.*, u.username as client_name, t.name as team_name,
                   (SELECT COUNT(*) FROM tasks WHERE project_id = p.id AND status = 'DONE') as done_tasks,
                   (SELECT COUNT(*) FROM tasks WHERE project_id = p.id) as total_tasks
            FROM projects p
            LEFT JOIN users u ON p.client_id = u.id
            LEFT JOIN teams t ON p.team_id = t.id
            WHERE p.client_id = ?
        """, (client_id,))
        projects = c.fetchall()
        
        result = []
        for project in projects:
            done_tasks = project[-2]
            total_tasks = project[-1]
            progress = round((done_tasks / total_tasks * 100) if total_tasks > 0 else 0)
            
            project_list = list(project[:-2])
            project_list[7] = progress
            result.append(tuple(project_list))
        
        conn.close()
        return result

    @staticmethod
    def get_project_details(project_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT p.*, u.username as client_name, t.name as team_name
            FROM projects p
            LEFT JOIN users u ON p.client_id = u.id
            LEFT JOIN teams t ON p.team_id = t.id
            WHERE p.id = ?
        """, (project_id,))
        project = c.fetchone()
        conn.close()
        return project

    @staticmethod
    def update_progress(project_id, progress):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("UPDATE projects SET progress = ? WHERE id = ?", (progress, project_id))
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False 

    @staticmethod
    def get_worker_projects(user_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # First get the worker's team_id
        c.execute("SELECT team_id FROM users WHERE id = ?", (user_id,))
        result = c.fetchone()
        if not result or not result[0]:
            conn.close()
            return []
            
        team_id = result[0]
        
        # Get all projects assigned to the worker's team
        c.execute("""
            SELECT p.*, u.username as client_name, t.name as team_name,
                   (SELECT COUNT(*) FROM tasks WHERE project_id = p.id AND status = 'DONE') as done_tasks,
                   (SELECT COUNT(*) FROM tasks WHERE project_id = p.id) as total_tasks
            FROM projects p
            LEFT JOIN users u ON p.client_id = u.id
            LEFT JOIN teams t ON p.team_id = t.id
            WHERE p.team_id = ? AND p.is_approved = 1
        """, (team_id,))
        
        projects = c.fetchall()
        
        # Calculate progress for each project
        result = []
        for project in projects:
            done_tasks = project[-2]  # Second to last column
            total_tasks = project[-1]  # Last column
            progress = round((done_tasks / total_tasks * 100) if total_tasks > 0 else 0)
            
            # Create modified project tuple with updated progress
            project_list = list(project[:-2])  # Remove the last two columns (done_tasks, total_tasks)
            project_list[7] = progress  # Update progress value
            result.append(tuple(project_list))
        
        conn.close()
        return result

    @staticmethod
    def update_project_progress(project_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Calculate progress based on tasks
        c.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'DONE' THEN 1 END) as done_tasks,
                COUNT(*) as total_tasks
            FROM tasks 
            WHERE project_id = ?
        """, (project_id,))
        
        done_tasks, total_tasks = c.fetchone()
        progress = round((done_tasks / total_tasks * 100) if total_tasks > 0 else 0)
        
        # Update project progress
        c.execute("UPDATE projects SET progress = ? WHERE id = ?", (progress, project_id))
        
        conn.commit()
        conn.close()
        return progress 