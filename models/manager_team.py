from models import db
from models.user import User
from models.team import Team

class ManagerTeam(db.Model):
    __tablename__ = 'manager_teams'
    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_approved = db.Column(db.Boolean, default=False)

    manager = db.relationship('User', foreign_keys=[manager_id])
    team = db.relationship('Team', foreign_keys=[team_id])
