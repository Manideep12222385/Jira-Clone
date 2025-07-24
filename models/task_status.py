from models import db

class TaskStatus(db.Model):
    __tablename__ = 'task_statuses'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False)
