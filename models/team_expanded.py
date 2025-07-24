import sqlite3
from . import DB_NAME

class Team:
    @staticmethod
    def create_team(name, leader_id, skills, is_approved):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""INSERT INTO teams (name, leader_id, skills, is_approved) VALUES (?, ?, ?, ?)""", (name, leader_id, skills, is_approved))
        conn.commit()
        conn.close()

    @staticmethod
    def get_all_teams():
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""SELECT t.*, u.username as leader_name, u.skills as leader_skills FROM teams t LEFT JOIN users u ON t.leader_id = u.id""")
        teams = c.fetchall()
        conn.close()
        return teams

    @staticmethod
    def get_team_by_id(team_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
        team = c.fetchone()
        conn.close()
        return team
