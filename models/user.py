import sqlite3
from . import DB_NAME

def populate_sample_data(c):
    # Insert users first
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
    
    # Get team leader IDs
    c.execute("SELECT id, username FROM users WHERE username IN ('KartikTeam', 'DivyaTeam', 'ArjunTeam', 'SanjanaTeam', 'RohanTeam')")
    leader_ids = {row[1]: row[0] for row in c.fetchall()}
    
    # Create teams with leader_id
    teams = [
        ('Development Team A', leader_ids['KartikTeam'], 'Main development team for web applications', 1),
        ('Development Team B', leader_ids['DivyaTeam'], 'Mobile development team', 1),
        ('Development Team C', leader_ids['ArjunTeam'], 'Backend services team', 1),
        ('Development Team D', leader_ids['SanjanaTeam'], 'Frontend development team', 1),
        ('Development Team E', leader_ids['RohanTeam'], 'QA and testing team', 1)
    ]
    
    c.executemany("INSERT INTO teams (name, leader_id, description, is_approved) VALUES (?, ?, ?, ?)", teams)
    
    # Update team leaders with their team_id
    for team_name, leader_id, _, _ in teams:
        c.execute("UPDATE users SET team_id = (SELECT id FROM teams WHERE name = ?) WHERE id = ?", 
                 (team_name, leader_id))

class User:
    @staticmethod
    def get_user(username, password):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'name': user[3],
                'role': user[4],
                'approved': bool(user[6]),
                'team_id': user[7]
            }
        return None

    @staticmethod
    def create_user(username, email, password, role, name, team_id=None):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        if role is None:
            role = 'pending'
        try:
            c.execute("""INSERT INTO users (username, email, name, role, password, team_id, approved) 
                         VALUES (?, ?, ?, ?, ?, ?, 0)""", 
                     (username, email, name, role, password, team_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    @staticmethod
    def get_all_users():
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM users")
        users = c.fetchall()
        conn.close()
        return users

    @staticmethod
    def approve_user(user_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE users SET approved=1 WHERE id=?", (user_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_users_by_role(role):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT u.*, t.name as team_name 
            FROM users u 
            LEFT JOIN teams t ON u.team_id = t.id 
            WHERE u.role = ? AND u.approved = 1
        """, (role,))
        users = c.fetchall()
        conn.close()
        return users

    @staticmethod
    def get_team_members(team_id, approved_only=True):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        if approved_only:
            c.execute("""
                SELECT id, username, email, name, role, team_id
                FROM users 
                WHERE team_id = ? AND role = 'team_worker' AND approved = 1
            """, (team_id,))
        else:
            c.execute("""
                SELECT id, username, email, name, role, team_id, approved
                FROM users 
                WHERE team_id = ? AND role = 'team_worker'
            """, (team_id,))
        members = c.fetchall()
        conn.close()
        return members

    @staticmethod
    def delete_user(user_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def approve_and_set_role(user_id, role):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            # First set team_id to NULL to avoid foreign key constraint
            c.execute("UPDATE users SET team_id = NULL WHERE id = ?", (user_id,))
            
            # Then update role and approved status
            c.execute("UPDATE users SET role = ?, approved = 1 WHERE id = ?", (role, user_id))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close() 