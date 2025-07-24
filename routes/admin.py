from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from models import User, Project, Task, Team, DB_NAME
import sqlite3

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/get_team_details/<int:team_id>')
def get_team_details(team_id):
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get team details
    c.execute("""
        SELECT t.id, t.name, t.leader_id, t.description, u.username as leader_name
        FROM teams t
        LEFT JOIN users u ON t.leader_id = u.id
        WHERE t.id = ?
    """, (team_id,))
    team = c.fetchone()
    
    if not team:
        conn.close()
        return jsonify({'error': 'Team not found'}), 404
    
    # Get team members
    c.execute("""
        SELECT u.id
        FROM users u
        WHERE u.team_id = ? AND u.role = 'team_worker'
    """, (team_id,))
    members = [row[0] for row in c.fetchall()]
    
    conn.close()
    
    return jsonify({
        'id': team[0],
        'name': team[1],
        'leader_id': team[2],
        'description': team[3],
        'leader_name': team[4],
        'members': members
    })

@admin_bp.route('/update_team', methods=['POST'])
def update_team():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    team_id = data.get('team_id')
    name = data.get('name')
    description = data.get('description')
    leader_id = data.get('leader_id')
    members = data.get('members', [])
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Update team details
        c.execute("""
            UPDATE teams 
            SET name = ?, leader_id = ?, description = ?
            WHERE id = ?
        """, (name, leader_id, description, team_id))
        
        # Update team members
        # First, remove all current team members
        c.execute("UPDATE users SET team_id = NULL WHERE team_id = ?", (team_id,))
        
        # Then add selected members
        for member_id in members:
            c.execute("UPDATE users SET team_id = ? WHERE id = ?", (team_id, member_id))
        
        # Set team leader's team_id
        c.execute("UPDATE users SET team_id = ? WHERE id = ?", (team_id, leader_id))
        
        conn.commit()
        flash('Team updated successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        flash('Error updating team.', 'error')
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@admin_bp.route('/create_team', methods=['POST'])
def create_team():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    name = data.get('name')
    description = data.get('description')
    leader_id = data.get('leader_id')
    members = data.get('members', [])
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Create new team
        c.execute("""
            INSERT INTO teams (name, description, leader_id, is_approved)
            VALUES (?, ?, ?, 1)
        """, (name, description, leader_id))
        
        team_id = c.lastrowid
        
        # Add team members
        for member_id in members:
            c.execute("UPDATE users SET team_id = ? WHERE id = ?", (team_id, member_id))
        
        # Set team leader's team_id
        c.execute("UPDATE users SET team_id = ? WHERE id = ?", (team_id, leader_id))
        
        conn.commit()
        flash('Team created successfully!', 'success')
        return jsonify({'success': True, 'team_id': team_id})
    except Exception as e:
        conn.rollback()
        flash('Error creating team.', 'error')
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@admin_bp.route('/delete_team/<int:team_id>', methods=['POST'])
def delete_team(team_id):
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # First update all users in this team to have no team
        c.execute("UPDATE users SET team_id = NULL WHERE team_id = ?", (team_id,))
        
        # Then delete the team
        c.execute("DELETE FROM teams WHERE id = ?", (team_id,))
        
        conn.commit()
        flash('Team deleted successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        flash('Error deleting team.', 'error')
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@admin_bp.route('/approve_user/<int:user_id>', methods=['GET', 'POST'])
def approve_user_route(user_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        role = request.form.get('role')
        if role not in ['admin', 'manager', 'client', 'stakeholder', 'team_worker']:
            return redirect(url_for('admin.admin_dashboard'))
        User.approve_and_set_role(user_id, role)
        flash('User has been approved successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    else:
        User.approve_user(user_id)
        flash('User has been approved successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/decline_user/<int:user_id>')
def decline_user_route(user_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))
    User.delete_user(user_id)
    flash('User has been declined and removed.', 'success')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/change_user_role/<int:user_id>', methods=['POST'])
def change_user_role(user_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))
    
    if user_id == session['user_id']:
        flash('You cannot change your own role.', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    role = request.form.get('role')
    if role not in ['admin', 'manager', 'client', 'stakeholder', 'team_worker']:
        flash('Invalid role selected.', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
    conn.commit()
    conn.close()
    
    flash(f'User role has been updated to {role}.', 'success')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('auth.login'))
    
    if user_id == session['user_id']:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    User.delete_user(user_id)
    flash('User has been deleted successfully.', 'success')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
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
    
    # Separate pending and approved users
    pending_users = []
    approved_users = []
    for user in users:
        if not user[6]:  # not approved
            pending_users.append(user)
        else:
            approved_users.append(user)
    
    # Get teams with leader and member details
    teams_with_members = []
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    for team in teams:
        # Get team leader details
        c.execute("""
            SELECT username 
            FROM users 
            WHERE id = ?
        """, (team[2],))  # team[2] is leader_id
        leader_result = c.fetchone()
        leader_name = leader_result[0] if leader_result else 'Not Assigned'
        
        # Get team members
        c.execute("""
            SELECT username
            FROM users 
            WHERE team_id = ? AND role = 'team_worker' AND id != ?
        """, (team[0], team[2]))  # Exclude leader from members list
        members = c.fetchall()
        
        teams_with_members.append({
            'team': (
                team[0],  # id
                team[1],  # name
                team[2],  # leader_id
                team[3],  # description
                leader_name,  # leader name instead of id
                [member[0] for member in members]  # list of member usernames
            ),
            'members': [member[0] for member in members]  # list of member usernames
        })
    
    conn.close()
    
    return render_template('admin_dashboard.html',
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
                         pending_users=pending_users,
                         approved_users=approved_users,
                         teams=teams) 

@admin_bp.route('/update_task_status', methods=['POST'])
def update_task_status():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    task_id = data.get('task_id')
    new_status = data.get('status')
    
    if not task_id or not new_status:
        return jsonify({'error': 'Missing task_id or status'}), 400
    
    if new_status not in ['TO DO', 'IN PROGRESS', 'DONE']:
        return jsonify({'error': 'Invalid status'}), 400
    
    success = Task.update_status(task_id, new_status)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to update task status'}), 500

@admin_bp.route('/get_project_details/<int:project_id>')
def get_project_details(project_id):
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Get project details
        c.execute("""
            SELECT p.*, u.username as client_name, t.name as team_name
            FROM projects p
            LEFT JOIN users u ON p.client_id = u.id
            LEFT JOIN teams t ON p.team_id = t.id
            WHERE p.id = ?
        """, (project_id,))
        project = c.fetchone()
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get team members assigned to this project
        c.execute("""
            SELECT DISTINCT u.id
            FROM users u
            JOIN teams t ON u.team_id = t.id
            WHERE t.id = ?
        """, (project[4],))  # project[4] is team_id
        team_members = [row[0] for row in c.fetchall()]
        
        return jsonify({
            'id': project[0],
            'name': project[1],
            'description': project[2],
            'client_id': project[3],
            'team_id': project[4],
            'start_date': project[5],
            'end_date': project[6],
            'progress': project[7],
            'is_approved': bool(project[8]),
            'client_name': project[9],
            'team_name': project[10],
            'team_members': team_members
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@admin_bp.route('/update_project', methods=['POST'])
def update_project():
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    project_id = data.get('project_id')
    name = data.get('name')
    description = data.get('description')
    client_id = data.get('client_id')
    team_id = data.get('team_id')
    end_date = data.get('end_date')
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Update project details
        c.execute("""
            UPDATE projects 
            SET name = ?, description = ?, client_id = ?, team_id = ?, end_date = ?
            WHERE id = ?
        """, (name, description, client_id, team_id, end_date, project_id))
        
        conn.commit()
        flash('Project updated successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        flash('Error updating project.', 'error')
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@admin_bp.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    if 'role' not in session or session['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Delete all tasks associated with this project
        c.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
        
        # Delete the project
        c.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        
        conn.commit()
        flash('Project deleted successfully!', 'success')
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        flash('Error deleting project.', 'error')
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close() 