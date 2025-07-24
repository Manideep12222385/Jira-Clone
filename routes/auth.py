from flask import Blueprint, render_template, request, redirect, url_for, session, flash  # type: ignore
from models import User
import re

auth_bp = Blueprint('auth', __name__)

def validate_password(password):
    """
    Validate password meets all requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    - Contains at least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*]', password):
        return False, "Password must contain at least one special character (!@#$%^&*)"
    
    return True, "Password is valid"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_user(username, password)
        if user:
            if not user['approved'] and user['role'] != 'admin':
                flash('Your account is pending approval from admin.')
                return redirect(url_for('auth.login'))
            
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif user['role'] == 'manager':
                return redirect(url_for('manager.manager_dashboard'))
            elif user['role'] == 'client':
                return redirect(url_for('client.client_dashboard'))
            elif user['role'] == 'stakeholder':
                return redirect(url_for('stakeholder.stakeholder_dashboard'))
            elif user['role'] == 'team_worker':
                return redirect(url_for('team_worker.team_worker_dashboard'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        role = request.form.get('role')
        
        if not all([username, email, password, confirm_password, name, role]):
            flash('All fields are required.')
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('auth.register'))
        
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message)
            return redirect(url_for('auth.register'))
        
        if role not in ['manager', 'client', 'stakeholder', 'team_worker']:
            flash('Invalid role selected.')
            return redirect(url_for('auth.register'))
        if User.create_user(username, email, password, role, name):
            flash('Registration successful! Please wait for admin approval.')
            return redirect(url_for('auth.login'))
        else:
            flash('Username or email already exists.')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login')) 