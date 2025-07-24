import sqlite3
from tabulate import tabulate
from datetime import datetime

class DBManager:
    def __init__(self, db_name='jiraclone.db'):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
    
    def show_users_by_role(self):
        print("\n=== Users by Role ===")
        # Admins
        self.c.execute("SELECT name, username, password FROM admin")
        print("\nAdmins:")
        print(tabulate(self.c.fetchall(), headers=['Name', 'Username', 'Password']))
        
        # Managers
        self.c.execute("SELECT name, username, mail FROM manager")
        print("\nManagers:")
        print(tabulate(self.c.fetchall(), headers=['Name', 'Username', 'Email']))
        
        # Team Leaders
        self.c.execute("""
            SELECT u.name, u.username, t.name as team, t.skills
            FROM users u
            JOIN teams t ON u.id = t.leader_id
        """)
        print("\nTeam Leaders:")
        print(tabulate(self.c.fetchall(), headers=['Name', 'Username', 'Team', 'Skills']))

    def show_project_status(self):
        print("\n=== Project Status ===")
        self.c.execute("""
            SELECT 
                p.name as project,
                c.name as client,
                t.name as team,
                p.start_date,
                p.end_date,
                p.progress,
                (SELECT COUNT(*) FROM tasks WHERE project_id = p.id AND status = 'DONE') as done_tasks,
                (SELECT COUNT(*) FROM tasks WHERE project_id = p.id) as total_tasks
            FROM projects p
            JOIN client c ON p.client_id = c.id
            JOIN teams t ON p.team_id = t.id
            ORDER BY p.progress DESC
        """)
        print(tabulate(self.c.fetchall(), 
                      headers=['Project', 'Client', 'Team', 'Start', 'End', 'Progress%', 'Done/Total Tasks']))

    def show_tasks_by_status(self):
        print("\n=== Tasks by Status ===")
        self.c.execute("""
            SELECT 
                t.title,
                t.status,
                p.name as project,
                u.name as assignee,
                t.start_date,
                t.end_date,
                t.skills
            FROM tasks t
            JOIN projects p ON t.project_id = p.id
            JOIN users u ON t.assignee_id = u.id
            ORDER BY 
                CASE t.status 
                    WHEN 'IN PROGRESS' THEN 1 
                    WHEN 'TO DO' THEN 2
                    WHEN 'DONE' THEN 3 
                END,
                t.start_date
        """)
        print(tabulate(self.c.fetchall(), 
                      headers=['Task', 'Status', 'Project', 'Assignee', 'Start', 'End', 'Skills']))

    def show_team_members(self):
        print("\n=== Team Members ===")
        self.c.execute("""
            SELECT 
                t.name as team,
                u.name as member,
                tm.skills,
                CASE WHEN t.leader_id = u.id THEN 'Leader' ELSE 'Member' END as role
            FROM teams t
            LEFT JOIN team_members tm ON t.id = tm.team_id
            LEFT JOIN users u ON tm.user_id = u.id OR t.leader_id = u.id
            ORDER BY t.name, role DESC
        """)
        print(tabulate(self.c.fetchall(), headers=['Team', 'Member', 'Skills', 'Role']))

if __name__ == '__main__':
    db = DBManager()
    while True:
        print("\n=== Jira Clone Database Manager ===")
        print("1. Show Users by Role")
        print("2. Show Project Status")
        print("3. Show Tasks by Status")
        print("4. Show Team Members")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            db.show_users_by_role()
        elif choice == '2':
            db.show_project_status()
        elif choice == '3':
            db.show_tasks_by_status()
        elif choice == '4':
            db.show_team_members()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")
