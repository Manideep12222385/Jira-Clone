from models import db
from models.user import User
from models.team import Team

class TeamMember(db.Model):
    __tablename__ = 'team_members'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    skills = db.Column(db.String(255))
    is_approved = db.Column(db.Boolean, default=False)

    user = db.relationship('User', foreign_keys=[user_id])
    team = db.relationship('Team', foreign_keys=[team_id])
