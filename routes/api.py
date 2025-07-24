from flask import Blueprint, jsonify, request, session  # type: ignore
from models import Project, Task, Team, User, DB_NAME
import sqlite3

api_bp = Blueprint('api', __name__)

@api_bp.route('/update_task_status', methods=['POST'])
def update_task_status_route():
    if 'role' not in session or session['role'] not in ['admin', 'manager']:
        return jsonify({'success': False})
    data = request.json or {}
    task_id = data.get('task_id')
    new_status = data.get('status')
    if not task_id or not new_status:
        return jsonify({'success': False, 'error': 'Missing task_id or status'})
    Task.update_status(task_id, new_status)
    return jsonify({'success': True})

@api_bp.route('/get_team_details/<int:team_id>')
def get_team_details(team_id):
    try:
        if 'role' not in session or session['role'] not in ['manager', 'admin']:
            return jsonify({'error': 'Unauthorized'}), 401
        team = Team.get_team_by_id(team_id)
        if not team:
            return jsonify({'error': 'Team not found'}), 404
        leader_id = team[2]
        leader_details = None
        if leader_id is not None:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("SELECT id, username, skills FROM users WHERE id = ?", (leader_id,))
            leader_details = c.fetchone()
            conn.close()
        if not leader_details:
            leader_details = (None, "Not Assigned", "")
        members = User.get_team_members(team_id) or []
        response_data = {
            'id': team[0],
            'name': team[1],
            'leader_id': leader_id,
            'leader_name': leader_details[1] if leader_details else "Not Assigned",
            'leader_skills': leader_details[2] if leader_details else "",
            'skills': team[3] if team[3] else "",
            'members': [
                {'id': m[0], 'username': m[1], 'skills': m[4] if len(m) > 4 else ""}
                for m in members if m[0] != leader_id
            ]
        }
        return jsonify(response_data)
    except Exception as e:
        import traceback
        return jsonify({'error': str(e)}), 500

@api_bp.route('/update_team/<int:team_id>', methods=['POST'])
def update_team(team_id):
    if 'role' not in session or session['role'] not in ['manager', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json or {}
    required_fields = ['name', 'leader_id', 'members', 'skills']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
    skills = data['skills'].strip()
    if not skills:
        return jsonify({'success': False, 'error': 'Team skills cannot be empty'}), 400
    members = [int(mid) for mid in data['members']]
    leader_id = int(data['leader_id'])
    result = Team.update_team(
        team_id,
        data['name'],
        leader_id,
        members,
        skills
    )
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@api_bp.route('/get_team_members_by_team/<int:team_id>')
def get_team_members_by_team(team_id):
    if 'role' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    members = User.get_team_members(team_id)
    return jsonify([
        {'id': m[0], 'username': m[1], 'skills': m[4] if len(m) > 4 else ""}
        for m in members
    ])

@api_bp.route('/get_team_members/<int:team_id>')
def get_team_members_for_project(team_id):
    members = User.get_team_members(team_id)
    return jsonify([
        {'id': m[0], 'username': m[1], 'skills': m[4] if len(m) > 4 else ""}
        for m in members
    ])

@api_bp.route('/api/projects/<int:project_id>/tasks')
def get_project_tasks(project_id):
    if 'role' not in session:
        return jsonify([])
    epic_filter = request.args.get('epic')
    type_filter = request.args.get('type')
    tasks = Task.get_project_tasks_filtered(project_id, epic_filter, type_filter)
    return jsonify(tasks)

@api_bp.route('/get_project_details/<int:project_id>/tasks')
def get_project_details_tasks(project_id):
    if 'role' not in session:
        return jsonify([])
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT title, description, status, type, epic 
        FROM tasks 
        WHERE project_id = ?
    """, (project_id,))
    tasks = [{'title': row[0], 'description': row[1], 'status': row[2], 'type': row[3], 'epic': row[4]} 
             for row in c.fetchall()]
    conn.close()
    return jsonify(tasks)

@api_bp.route('/get_team_members_by_project/<int:project_id>')
def get_team_members_by_project(project_id):
    if 'role' not in session:
        return jsonify([])
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT team_id FROM projects WHERE id = ?", (project_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify([])
    team_id = row[0]
    c.execute("SELECT leader_id FROM teams WHERE id = ?", (team_id,))
    leader_row = c.fetchone()
    leader = None
    if leader_row:
        c.execute("SELECT username, role, skills FROM users WHERE id = ?", (leader_row[0],))
        leader = c.fetchone()
    c.execute("SELECT username, role, skills FROM users WHERE team_id = ? AND role = 'team_worker'", (team_id,))
    members = c.fetchall()
    conn.close()
    result = []
    if leader:
        result.append({'username': leader[0], 'role': leader[1], 'skills': leader[2]})
    for m in members:
        if not leader or m[0] != leader[0]:
            result.append({'username': m[0], 'role': m[1], 'skills': m[2]})
    return jsonify(result)

@api_bp.route('/get_project_team_tasks/<int:project_id>')
def get_project_team_tasks(project_id):
    if 'role' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT team_id FROM projects WHERE id = ?", (project_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify([])
    team_id = row[0]
    c.execute("SELECT id, username, role, skills FROM users WHERE team_id = ?", (team_id,))
    members = c.fetchall()
    c.execute("SELECT id, title, description, status, assignee_id FROM tasks WHERE project_id = ?", (project_id,))
    tasks = c.fetchall()
    conn.close()
    member_dict = {}
    for m in members:
        member_dict[m[0]] = {
            'id': m[0],
            'username': m[1],
            'role': m[2],
            'skills': m[3],
            'tasks': []
        }
    for t in tasks:
        assignee_id = t[4]
        if assignee_id in member_dict:
            member_dict[assignee_id]['tasks'].append({
                'id': t[0],
                'title': t[1],
                'description': t[2],
                'status': t[3]
            })
    return jsonify(list(member_dict.values()))

@api_bp.route('/get_project_details/<int:project_id>')
def get_project_details(project_id):
    if 'role' not in session or session['role'] not in ['manager', 'admin', 'team_worker']:
        return jsonify({'error': 'Unauthorized'}), 401
    project = Project.get_project_by_id(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    return jsonify({
        'id': project[0],
        'name': project[1],
        'description': project[2],
        'client_id': project[3],
        'team_id': project[4],
        'start_date': project[5],
        'end_date': project[6],
        'progress': project[7],
        'client_name': project[8],
        'team_name': project[9]
    })

@api_bp.route('/update_project/<int:project_id>', methods=['POST'])
def update_project(project_id):
    if 'role' not in session or session['role'] not in ['manager', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json or {}
    required_fields = ['name', 'description', 'client_id', 'team_id', 'end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
    result = Project.update_project(
        project_id,
        data['name'],
        data['description'],
        int(data['client_id']),
        int(data['team_id']),
        data.get('end_date')
    )
    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400

@api_bp.route('/get_teams')
def get_teams():
    if 'role' not in session or session['role'] != 'manager':
        return jsonify({'error': 'Unauthorized'}), 401
    teams = Team.get_all_teams()
    return jsonify([
        {'id': t[0], 'name': t[1], 'skills': t[3]}
        for t in teams
    ]) 