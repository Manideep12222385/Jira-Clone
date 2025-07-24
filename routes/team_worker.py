from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from models import Project, Task

team_worker_bp = Blueprint('team_worker', __name__, url_prefix='/team_worker')

@team_worker_bp.route('/')
def team_worker_dashboard():
    if 'role' not in session or session['role'] != 'team_worker':
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    projects = Project.get_worker_projects(user_id)
    tasks = Task.get_worker_tasks(user_id)
    return render_template('teamworker_dashboard.html', projects=projects, tasks=tasks)

@team_worker_bp.route('/update_task_status', methods=['POST'])
def update_task_status():
    if 'role' not in session or session['role'] != 'team_worker':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    data = request.get_json()
    if not data or not all(key in data for key in ['task_id', 'status']):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    try:
        success = Task.update_status(data['task_id'], data['status'])
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@team_worker_bp.route('/edit_task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    if 'role' not in session or session['role'] != 'team_worker':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    task = Task.get_task(task_id)
    if not task:
        return jsonify({'success': False, 'message': 'Task not found'}), 404
        
    return jsonify({
        'success': True,
        'task': {
            'id': task[0],
            'title': task[1],
            'description': task[2],
            'type': task[6],
            'project_name': task[9]
        }
    })

@team_worker_bp.route('/edit_task/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    if 'role' not in session or session['role'] != 'team_worker':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    data = request.get_json()
    if not data or not all(key in data for key in ['title', 'description', 'type']):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    try:
        success = Task.update_task(task_id, data['title'], data['description'], data['type'])
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@team_worker_bp.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if 'role' not in session or session['role'] != 'team_worker':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        success = Task.delete_task(task_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@team_worker_bp.route('/create_task', methods=['POST'])
def create_task():
    if 'role' not in session or session['role'] != 'team_worker':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    data = request.get_json()
    if not data or not all(key in data for key in ['title', 'description', 'project_id', 'type']):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
    # Verify the project belongs to the worker's team
    user_id = session['user_id']
    projects = Project.get_worker_projects(user_id)
    project_ids = [p[0] for p in projects]
    
    if int(data['project_id']) not in project_ids:
        return jsonify({'success': False, 'message': 'Project not found or not assigned to your team'}), 404
    
    try:
        Task.create_task(
            title=data['title'],
            description=data['description'],
            project_id=data['project_id'],
            assignee_id=user_id,  # Assign to self
            status='TO DO',
            type=data['type'],
            epic=None  # Optional
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500 