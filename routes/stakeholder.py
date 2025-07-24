from flask import Blueprint, render_template, redirect, url_for, session
from models import Project

stakeholder_bp = Blueprint('stakeholder', __name__, url_prefix='/stakeholder')

@stakeholder_bp.route('/')
def stakeholder_dashboard():
    if 'role' not in session or session['role'] != 'stakeholder':
        return redirect(url_for('auth.login'))
    projects = Project.get_all_projects()
    return render_template('stakeholder_dashboard.html', projects=projects) 