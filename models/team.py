import sqlite3
from . import DB_NAME

class Team:
    @staticmethod
    def get_all_teams():
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            SELECT t.*, u.username as leader_name, u.skills as leader_skills,
                   GROUP_CONCAT(m.username) as member_names
            FROM teams t
            LEFT JOIN users u ON t.leader_id = u.id
            LEFT JOIN users m ON m.team_id = t.id AND m.role = 'team_worker' AND m.id != t.leader_id
            GROUP BY t.id
        """)
        teams = c.fetchall()
        conn.close()
        return teams

    @staticmethod
    def get_team_by_id(team_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("""
                SELECT t.*, u.username as leader_name, u.skills as leader_skills,
                       GROUP_CONCAT(m.username) as member_names
                FROM teams t
                LEFT JOIN users u ON t.leader_id = u.id
                LEFT JOIN users m ON m.team_id = t.id AND m.role = 'team_worker' AND m.id != t.leader_id
                WHERE t.id = ?
                GROUP BY t.id
            """, (team_id,))
            team = c.fetchone()
            if team is None:
                return None
            return team
        except Exception as e:
            return None
        finally:
            conn.close()

    @staticmethod
    def update_team(team_id, name, leader_id, member_ids, skills=None):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            # Allow any user to be a team leader
            c.execute("SELECT username FROM users WHERE id = ?", (leader_id,))
            leader_result = c.fetchone()
            if not leader_result:
                conn.close()
                return {'success': False, 'error': 'Invalid team leader selected'}
            
            leader_username = leader_result[0]
            
            # Update team details
            c.execute("""
                UPDATE teams 
                SET name = ?,
                    leader_id = ?,
                    skills = ?
                WHERE id = ?
            """, (name, leader_id, skills, team_id))
            
            # Reset team members
            c.execute("""
                UPDATE users 
                SET team_id = NULL 
                WHERE team_id = ?
            """, (team_id,))
            
            # Add selected members
            for member_id in member_ids:
                c.execute("""
                    UPDATE users 
                    SET team_id = ? 
                    WHERE id = ?
                """, (team_id, member_id))
            
            # Make sure leader is part of the team
            c.execute("""
                UPDATE users 
                SET team_id = ? 
                WHERE id = ?
            """, (team_id, leader_id))
            
            conn.commit()
            return {'success': True}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            conn.close() 