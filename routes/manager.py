from flask import Blueprint, render_template, redirect, url_for, session
from models import User, Project, Task, Team

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')

@manager_bp.route('/')
def manager_dashboard():
    if 'role' not in session or session['role'] != 'manager':
        return redirect(url_for('auth.login'))
    projects = Project.get_all_projects()
    tasks = Task.get_all_tasks()
    teams = Team.get_all_teams()
    clients = User.get_users_by_role('client')
    users = User.get_all_users()
    user_count = len(users)
    stakeholder_count = len(User.get_users_by_role('stakeholder'))
    manager_count = len(User.get_users_by_role('manager'))
    admin_count = len(User.get_users_by_role('admin'))
    project_count = len(projects)
    task_count = len(tasks)
    teams_with_members = []
    for team in teams:
        members = list(User.get_team_members(team[0], approved_only=False))
        leader_id = team[2]
        leader_in_members = any(m[0] == leader_id for m in members)
        if not leader_in_members:
            from models import DB_NAME
            import sqlite3
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id, username, email, role, skills, team_id FROM users WHERE id = ?", (leader_id,))
            leader = c.fetchone()
            conn.close()
            if leader:
                members.insert(0, leader)
        teams_with_members.append({'team': team, 'members': members})
    return render_template('manager_dashboard.html',
                         projects=projects,
                         tasks=tasks,
                         teams_with_members=teams_with_members,
                         clients=clients,
                         users=users,
                         user_count=user_count,
                         stakeholder_count=stakeholder_count,
                         manager_count=manager_count,
                         admin_count=admin_count,
                         project_count=project_count,
                         task_count=task_count,
                         teams=teams) 