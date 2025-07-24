import sqlite3
from models import DB_NAME

def add_sample_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Clear existing data and reset sequences
    tables = ['tasks', 'projects', 'team_members', 'teams', 'users', 'admin', 'client', 'stakeholder', 'manager']
    for table in tables:
        c.execute(f"DELETE FROM {table}")
        c.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")  # Reset auto-increment
    conn.commit()

    # Admins
    admins = [
        ('Vaibhav', 'VaibhavAdmin', 'Admin123'),
    ]
    c.executemany("INSERT INTO admin (name, username, password) VALUES (?, ?, ?)", admins)

    # Managers
    managers = [
        ('Abdul Khan', 'AbdulManager', 'Manager123', 'abdul@manager.com'),
        ('Priya Sharma', 'PriyaManager', 'Manager123', 'priya@manager.com'),
        ('Rahul Verma', 'RahulManager', 'Manager123', 'rahul@manager.com'),
    ]
    c.executemany("INSERT INTO manager (name, username, password, mail) VALUES (?, ?, ?, ?)", managers)

    # Stakeholders
    stakeholders = [
        ('Suresh Kumar', 'SureshStake', 'Stake123', 'suresh@stake.com'),
        ('Meena Patel', 'MeenaStake', 'Stake123', 'meena@stake.com'),
        ('Vikram Singh', 'VikramStake', 'Stake123', 'vikram@stake.com'),
    ]
    c.executemany("INSERT INTO stakeholder (name, username, password, mail) VALUES (?, ?, ?, ?)", stakeholders)

    # Clients
    clients = [
        ('Amit Technologies', 'AmitClient', 'Client123', 'amit@client.com'),
        ('Neha Healthcare', 'NehaClient', 'Client123', 'neha@client.com'),
        ('Rajesh Banking', 'RajeshClient', 'Client123', 'rajesh@client.com'),
        ('Anu SmartSystems', 'AnuClient', 'Client123', 'anu@client.com'),
    ]
    c.executemany("INSERT INTO client (name, username, password, mail) VALUES (?, ?, ?, ?)", clients)

    # Users (team members)
    users = [
        ('Kartik', 'KartikTeam', 'Team123', 'kartik@team.com'),
        ('Divya', 'DivyaTeam', 'Team123', 'divya@team.com'),
        ('Arjun', 'ArjunTeam', 'Team123', 'arjun@team.com'),
        ('Sanjana', 'SanjanaTeam', 'Team123', 'sanjana@team.com'),
        ('Rohan', 'RohanTeam', 'Team123', 'rohan@team.com'),
    ]
    c.executemany("INSERT INTO users (name, username, password, mail) VALUES (?, ?, ?, ?)", users)
    conn.commit()

    # Teams
    c.execute("SELECT id, username FROM users")
    leader_ids = {row[1]: row[0] for row in c.fetchall()}
    teams = [
        ('KartikTeam', leader_ids['KartikTeam'], 'Python/React', 1),
        ('DivyaTeam', leader_ids['DivyaTeam'], 'Java/Angular', 1),
        ('ArjunTeam', leader_ids['ArjunTeam'], 'Node.js/Vue', 1),
        ('SanjanaTeam', leader_ids['SanjanaTeam'], 'PHP/Laravel', 1),
        ('RohanTeam', leader_ids['RohanTeam'], 'Flutter/Firebase', 1),
    ]
    c.executemany("INSERT INTO teams (name, leader_id, skills, is_approved) VALUES (?, ?, ?, ?)", teams)
    conn.commit()

    # Team members (add 2 per team for demo)
    team_members = []
    for team_name in leader_ids:
        team_id = None
        c.execute("SELECT id FROM teams WHERE name = ?", (team_name,))
        result = c.fetchone()
        if result:
            team_id = result[0]
        if team_id:
            for i in range(2):
                member_name = f"{team_name}_Member{i+1}"
                member_username = f"{team_name.lower()}_member{i+1}"
                member_password = "Team123"
                member_mail = f"{member_username}@team.com"
                c.execute("INSERT INTO users (name, username, password, mail) VALUES (?, ?, ?, ?)", (member_name, member_username, member_password, member_mail))
                c.execute("SELECT id FROM users WHERE username = ?", (member_username,))
                member_id = c.fetchone()[0]
                team_members.append((member_id, team_id, 'General', 1))
    c.executemany("INSERT INTO team_members (user_id, team_id, skills, is_approved) VALUES (?, ?, ?, ?)", team_members)
    conn.commit()

    # Projects
    # Reset projects
    c.execute("DELETE FROM projects")
    c.execute("DELETE FROM sqlite_sequence WHERE name='projects'")
    conn.commit()

    # Get clients and teams, ensure we have data
    c.execute("SELECT id, name FROM client ORDER BY id")
    clients_data = c.fetchall()
    client_ids = [row[0] for row in clients_data]
    if not client_ids:
        raise Exception("No clients found in database")

    c.execute("SELECT id, name FROM teams ORDER BY id")
    teams_data = c.fetchall()
    team_ids = [row[0] for row in teams_data]
    if not team_ids:
        raise Exception("No teams found in database")
    
    # Current date: July 18, 2025
    projects = [
        ('E-commerce Platform Revamp', 'Complete modernization of the existing e-commerce platform with microservices architecture, AI-powered recommendations, and enhanced security features', 
         client_ids[0], team_ids[0], '2025-06-01', '2025-12-31', 75, 1),
        
        ('Mobile Banking App', 'Next-generation mobile banking application with biometric authentication, real-time transactions, and AI-powered fraud detection', 
         client_ids[1], team_ids[1], '2025-05-15', '2025-11-30', 45, 1),
        
        ('Healthcare Management System', 'Integrated healthcare platform with electronic health records, telemedicine capabilities, and AI-assisted diagnostics', 
         client_ids[2], team_ids[2], '2025-07-01', '2026-01-31', 15, 1),
        
        ('Supply Chain Analytics', 'Advanced supply chain analytics platform with real-time tracking, predictive analytics, and blockchain integration', 
         client_ids[3], team_ids[3], '2025-06-15', '2025-09-30', 90, 1),
        
        ('Smart Home IoT Platform', 'Comprehensive IoT platform for smart home automation with AI-powered energy optimization and predictive maintenance', 
         client_ids[0], team_ids[4], '2025-07-15', '2026-02-28', 0, 1)
    ]
    
    # Insert projects (only once)
    c.executemany("""
        INSERT INTO projects (name, description, client_id, team_id, start_date, end_date, progress, is_approved)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, projects)
    conn.commit()

    # Tasks
    c.execute("DELETE FROM tasks")
    c.execute("DELETE FROM sqlite_sequence WHERE name='tasks'")
    conn.commit()

    # Get project IDs for tasks
    c.execute("SELECT id, name FROM projects")
    project_ids = {name: id for id, name in c.fetchall()}
    
    # Get all team members including leads
    team_members = {}
    for team_name in ['KartikTeam', 'DivyaTeam', 'ArjunTeam', 'SanjanaTeam', 'RohanTeam']:
        c.execute("""
            SELECT u.id, u.username, t.name 
            FROM users u 
            JOIN team_members tm ON u.id = tm.user_id 
            JOIN teams t ON tm.team_id = t.id 
            WHERE t.name = ?
            UNION 
            SELECT u.id, u.username, t.name 
            FROM users u 
            JOIN teams t ON u.id = t.leader_id 
            WHERE t.name = ?
        """, (team_name, team_name))
        team_members[team_name] = c.fetchall()
    
    tasks = []
    
    # E-commerce tasks
    proj_id = project_ids['E-commerce Platform Revamp']
    team = team_members['KartikTeam']
    tasks.extend([
        ('User Authentication System', 'Implement secure user authentication system with OAuth2 and MFA', 
         proj_id, team[0][0], 'DONE', 'story', 'Security', '2025-06-01', '2025-06-15', 'Python/React', 1),
        ('Product Catalog Management', 'Create dynamic product catalog with real-time updates and caching', 
         proj_id, team[1][0], 'DONE', 'story', 'Core Features', '2025-06-16', '2025-07-15', 'Python/React', 1),
        ('Shopping Cart Implementation', 'Build advanced shopping cart with payment gateway integration', 
         proj_id, team[2][0], 'IN PROGRESS', 'story', 'Core Features', '2025-07-16', '2025-08-15', 'Python/React', 1)
    ])
    
    # Mobile Banking tasks
    proj_id = project_ids['Mobile Banking App']
    team = team_members['DivyaTeam']
    tasks.extend([
        ('Secure User Registration', 'Implement biometric-enabled mobile registration system', 
         proj_id, team[0][0], 'DONE', 'story', 'Security', '2025-05-15', '2025-06-15', 'Java/Angular', 1),
        ('Account Dashboard', 'Design responsive account dashboard with real-time updates', 
         proj_id, team[1][0], 'IN PROGRESS', 'story', 'UI/UX', '2025-06-16', '2025-07-15', 'Java/Angular', 1),
        ('Transaction History', 'Build comprehensive transaction tracking with analytics', 
         proj_id, team[2][0], 'TO DO', 'story', 'Core Features', '2025-07-16', '2025-08-15', 'Java/Angular', 1)
    ])
    
    # Healthcare tasks
    proj_id = project_ids['Healthcare Management System']
    team = team_members['ArjunTeam']
    tasks.extend([
        ('Patient Registration Module', 'Develop HIPAA-compliant patient registration system', 
         proj_id, team[0][0], 'IN PROGRESS', 'story', 'Core Features', '2025-07-01', '2025-08-15', 'Node.js/Vue', 1),
        ('Appointment Scheduling', 'Create intelligent appointment management system', 
         proj_id, team[1][0], 'TO DO', 'story', 'Core Features', '2025-08-16', '2025-09-30', 'Node.js/Vue', 1),
        ('Medical Records System', 'Implement secure electronic health records system', 
         proj_id, team[2][0], 'TO DO', 'story', 'Core Features', '2025-10-01', '2025-11-15', 'Node.js/Vue', 1)
    ])

    # Supply Chain tasks
    proj_id = project_ids['Supply Chain Analytics']
    team = team_members['SanjanaTeam']
    tasks.extend([
        ('Data Integration Framework', 'Build scalable data integration pipeline', 
         proj_id, team[0][0], 'DONE', 'story', 'Integration', '2025-06-15', '2025-07-15', 'PHP/Laravel', 1),
        ('Analytics Dashboard', 'Create interactive analytics dashboard with ML insights', 
         proj_id, team[1][0], 'DONE', 'story', 'UI/UX', '2025-07-16', '2025-08-15', 'PHP/Laravel', 1),
        ('Predictive Analytics', 'Implement AI-powered forecasting system', 
         proj_id, team[2][0], 'IN PROGRESS', 'story', 'Analytics', '2025-08-16', '2025-09-15', 'PHP/Laravel', 1)
    ])

    # Smart Home IoT tasks
    proj_id = project_ids['Smart Home IoT Platform']
    team = team_members['RohanTeam']
    tasks.extend([
        ('Device Integration API', 'Develop secure IoT device integration API', 
         proj_id, team[0][0], 'TO DO', 'story', 'Integration', '2025-07-15', '2025-08-30', 'Flutter/Firebase', 1),
        ('Mobile App Interface', 'Create intuitive mobile app interface with real-time controls', 
         proj_id, team[1][0], 'TO DO', 'story', 'UI/UX', '2025-09-01', '2025-10-15', 'Flutter/Firebase', 1),
        ('Automation Rules Engine', 'Build AI-powered automation rules engine', 
         proj_id, team[2][0], 'TO DO', 'story', 'Core Features', '2025-10-16', '2025-11-30', 'Flutter/Firebase', 1)
    ])

    c.executemany("INSERT INTO tasks (title, description, project_id, assignee_id, status, type, epic, start_date, end_date, skills, is_approved) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", tasks)
    conn.commit()

    print("Sample data created with realistic project scenarios and tasks.")

if __name__ == "__main__":
    add_sample_data()
