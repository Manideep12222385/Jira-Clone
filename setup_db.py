import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'jiraclone.db'

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("PRAGMA foreign_keys = ON")
    
    tables = [
        'tasks',
        'team_members',
        'projects',
        'teams',
        'users'
    ]
    
    for table in tables:
        c.execute(f"DROP TABLE IF EXISTS {table}")
        try:
            c.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        except sqlite3.OperationalError:
            pass
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        password TEXT NOT NULL,
        approved BOOLEAN DEFAULT 0,
        team_id INTEGER NULL,
        skills TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        leader_id INTEGER NOT NULL,
        description TEXT,
        is_approved BOOLEAN DEFAULT 0,
        FOREIGN KEY (leader_id) REFERENCES users(id)
    )''')

    c.execute('''CREATE TRIGGER fk_users_team_id
        BEFORE UPDATE ON users
        FOR EACH ROW
        WHEN NEW.team_id IS NOT NULL
        BEGIN
            SELECT RAISE(ROLLBACK, 'Foreign key violation: team_id not found')
            WHERE NOT EXISTS (SELECT 1 FROM teams WHERE id = NEW.team_id);
        END;
    ''')

    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        client_id INTEGER,
        team_id INTEGER,
        start_date DATE,
        end_date DATE,
        progress INTEGER DEFAULT 0,
        is_approved BOOLEAN DEFAULT 0,
        FOREIGN KEY (client_id) REFERENCES users(id),
        FOREIGN KEY (team_id) REFERENCES teams(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        project_id INTEGER,
        assignee_id INTEGER,
        status TEXT DEFAULT 'TO DO',
        type TEXT DEFAULT 'story',
        epic TEXT,
        created_at DATE DEFAULT CURRENT_DATE,
        start_date DATE,
        end_date DATE,
        skills TEXT,
        is_approved BOOLEAN DEFAULT 0,
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (assignee_id) REFERENCES users(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS team_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        team_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (team_id) REFERENCES teams(id)
    )''')

    users = [
        ('VaibhavAdmin', 'vaibhav@admin.com', 'Vaibhav Admin', 'admin', 'Admin123', 1, None),
        ('AbdulManager', 'abdul@manager.com', 'Abdul Manager', 'manager', 'Manager123', 1, None),
        ('PriyaManager', 'priya@manager.com', 'Priya Manager', 'manager', 'Manager123', 1, None),
        ('RahulManager', 'rahul@manager.com', 'Rahul Manager', 'manager', 'Manager123', 1, None),
        ('AmitClient', 'amit@client.com', 'Amit Singh', 'client', 'Client123', 1, None),
        ('NehaClient', 'neha@client.com', 'Neha Patel', 'client', 'Client123', 1, None),
        ('RajeshClient', 'rajesh@client.com', 'Rajesh Kumar', 'client', 'Client123', 1, None),
        ('AnuClient', 'anu@client.com', 'Anu Sharma', 'client', 'Client123', 1, None),
        ('SureshStake', 'suresh@stake.com', 'Suresh Kumar', 'stakeholder', 'Stake123', 1, None),
        ('MeenaStake', 'meena@stake.com', 'Meena Sharma', 'stakeholder', 'Stake123', 1, None),
        ('KartikTeam', 'kartik@team.com', 'Kartik Kumar', 'team_worker', 'Team123', 1, None),
        ('DivyaTeam', 'divya@team.com', 'Divya Sharma', 'team_worker', 'Team123', 1, None),
        ('ArjunTeam', 'arjun@team.com', 'Arjun Singh', 'team_worker', 'Team123', 1, None),
        ('SanjanaTeam', 'sanjana@team.com', 'Sanjana Patel', 'team_worker', 'Team123', 1, None),
        ('RohanTeam', 'rohan@team.com', 'Rohan Kumar', 'team_worker', 'Team123', 1, None)
    ]
    
    for user in users:
        c.execute("""INSERT INTO users (username, email, name, role, password, approved, team_id) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)""", user)
    
    c.execute("SELECT id, username FROM users WHERE username IN ('KartikTeam', 'DivyaTeam', 'ArjunTeam', 'SanjanaTeam', 'RohanTeam')")
    leader_ids = {row[1]: row[0] for row in c.fetchall()}
    teams = [
        ('Development Team A', leader_ids['KartikTeam'], 'Main development team for web applications', 1),
        ('Development Team B', leader_ids['DivyaTeam'], 'Mobile development team', 1),
        ('Development Team C', leader_ids['ArjunTeam'], 'Backend services team', 1),
        ('Development Team D', leader_ids['SanjanaTeam'], 'Frontend development team', 1),
        ('Development Team E', leader_ids['RohanTeam'], 'QA and testing team', 1)
    ]
    
    c.executemany("INSERT INTO teams (name, leader_id, description, is_approved) VALUES (?, ?, ?, ?)", teams)
    
    for team_name, leader_id, _, _ in teams:
        c.execute("UPDATE users SET team_id = (SELECT id FROM teams WHERE name = ?) WHERE id = ?", 
                 (team_name, leader_id))

    c.execute("SELECT id, username FROM users WHERE role = 'client'")
    client_ids = {row[1]: row[0] for row in c.fetchall()}
    c.execute("SELECT id, name FROM teams")
    team_ids = {row[1]: row[0] for row in c.fetchall()}

    # Insert sample projects
    today = datetime.now()
    projects = [
        ('E-commerce Website', 'Build a modern e-commerce platform', client_ids['AmitClient'], team_ids['Development Team A'], 
         today.strftime('%Y-%m-%d'), (today + timedelta(days=90)).strftime('%Y-%m-%d'), 0, 1),
        ('Mobile Banking App', 'Develop a secure mobile banking application', client_ids['NehaClient'], team_ids['Development Team B'],
         today.strftime('%Y-%m-%d'), (today + timedelta(days=120)).strftime('%Y-%m-%d'), 0, 1),
        ('CRM System', 'Create a customer relationship management system', client_ids['RajeshClient'], team_ids['Development Team C'],
         today.strftime('%Y-%m-%d'), (today + timedelta(days=60)).strftime('%Y-%m-%d'), 0, 1),
        ('Analytics Dashboard', 'Build a real-time analytics dashboard', client_ids['AnuClient'], team_ids['Development Team D'],
         today.strftime('%Y-%m-%d'), (today + timedelta(days=45)).strftime('%Y-%m-%d'), 0, 1)
    ]

    c.executemany("""
        INSERT INTO projects (name, description, client_id, team_id, start_date, end_date, progress, is_approved)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, projects)

    # Get project IDs
    c.execute("SELECT id, name FROM projects")
    project_ids = {row[1]: row[0] for row in c.fetchall()}

    # Get team worker IDs
    c.execute("SELECT id, username FROM users WHERE role = 'team_worker'")
    worker_ids = {row[1]: row[0] for row in c.fetchall()}

    # Insert sample tasks
    tasks = [
        # E-commerce Website Tasks
        ('Setup Database Schema', 'Design and implement database structure', project_ids['E-commerce Website'], 
         worker_ids['KartikTeam'], 'TO DO', 'story', 'Database', today.strftime('%Y-%m-%d'), 
         today.strftime('%Y-%m-%d'), (today + timedelta(days=5)).strftime('%Y-%m-%d'), 'SQL, Database Design', 1),
        
        ('User Authentication', 'Implement user login and registration', project_ids['E-commerce Website'], 
         worker_ids['DivyaTeam'], 'IN PROGRESS', 'story', 'Backend', today.strftime('%Y-%m-%d'), 
         today.strftime('%Y-%m-%d'), (today + timedelta(days=7)).strftime('%Y-%m-%d'), 'Authentication, Security', 1),
        
        ('Product Catalog', 'Create product listing and details pages', project_ids['E-commerce Website'], 
         worker_ids['ArjunTeam'], 'DONE', 'story', 'Frontend', today.strftime('%Y-%m-%d'), 
         today.strftime('%Y-%m-%d'), (today + timedelta(days=10)).strftime('%Y-%m-%d'), 'React, UI Design', 1),

        # Mobile Banking App Tasks
        ('API Integration', 'Integrate banking APIs', project_ids['Mobile Banking App'], 
         worker_ids['SanjanaTeam'], 'TO DO', 'story', 'Backend', today.strftime('%Y-%m-%d'), 
         today.strftime('%Y-%m-%d'), (today + timedelta(days=15)).strftime('%Y-%m-%d'), 'API, Integration', 1),
        
        ('Mobile UI Design', 'Design user interface for mobile app', project_ids['Mobile Banking App'], 
         worker_ids['RohanTeam'], 'IN PROGRESS', 'story', 'Design', today.strftime('%Y-%m-%d'), 
         today.strftime('%Y-%m-%d'), (today + timedelta(days=8)).strftime('%Y-%m-%d'), 'UI/UX, Mobile Design', 1),

        # CRM System Tasks
        ('Contact Management', 'Implement contact CRUD operations', project_ids['CRM System'], 
         worker_ids['KartikTeam'], 'TO DO', 'story', 'Backend', today.strftime('%Y-%m-%d'), 
         today.strftime('%Y-%m-%d'), (today + timedelta(days=12)).strftime('%Y-%m-%d'), 'CRUD, Database', 1),
        
        ('Dashboard Analytics', 'Create analytics dashboard', project_ids['CRM System'], 
         worker_ids['DivyaTeam'], 'IN PROGRESS', 'story', 'Frontend', today.strftime('%Y-%m-%d'), 
         today.strftime('%Y-%m-%d'), (today + timedelta(days=9)).strftime('%Y-%m-%d'), 'Analytics, Charts', 1),

        # Analytics Dashboard Tasks
        ('Data Visualization', 'Implement charts and graphs', project_ids['Analytics Dashboard'], 
         worker_ids['ArjunTeam'], 'TO DO', 'story', 'Frontend', today.strftime('%Y-%m-%d'), 
         today.strftime('%Y-%m-%d'), (today + timedelta(days=6)).strftime('%Y-%m-%d'), 'D3.js, Charts', 1),
        
        ('Real-time Updates', 'Add WebSocket support for live updates', project_ids['Analytics Dashboard'], 
         worker_ids['SanjanaTeam'], 'IN PROGRESS', 'story', 'Backend', today.strftime('%Y-%m-%d'), 
         today.strftime('%Y-%m-%d'), (today + timedelta(days=11)).strftime('%Y-%m-%d'), 'WebSocket, Real-time', 1)
    ]

    c.executemany("""
        INSERT INTO tasks (title, description, project_id, assignee_id, status, type, epic, 
                         created_at, start_date, end_date, skills, is_approved)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tasks)

    conn.commit()
    conn.close()
    print("Database setup completed successfully!")

if __name__ == '__main__':
    setup_database()
