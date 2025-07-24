from flask import Blueprint, render_template, redirect, url_for, session
from models import Project

client_bp = Blueprint('client', __name__, url_prefix='/client')

@client_bp.route('/')
def client_dashboard():
    if 'role' not in session or session['role'] != 'client':
        return redirect(url_for('auth.login'))
    projects = Project.get_client_projects(session['user_id'])
    return render_template('client_dashboard.html', projects=projects) 