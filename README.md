# Jira Clone Project Management System

A web-based project management system built with Python Flask, similar to Jira, allowing different user roles to manage projects, tasks, and teams.

## Features

- **Multi-Role Support**:
  - Admin: System administration and user approval
  - Manager: Project and team management
  - Client: Project tracking and oversight
  - Stakeholder: Project monitoring
  - Team Worker: Task management and updates

- **Project Management**:
  - Create and manage projects
  - Track project progress
  - Assign teams to projects
  - Real-time progress updates

- **Task Management**:
  - Create and assign tasks
  - Track task status (TO DO, IN PROGRESS, DONE)
  - Support for different task types and epics
  - Task progress tracking

- **Team Management**:
  - Create and manage teams
  - Assign team leaders
  - Team member management
  - Skill tracking

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Session-based authentication

## Project Structure

```
├── app.py                 # Main application file
├── models/               # Database models
│   ├── project.py        # Project model
│   ├── task.py          # Task model
│   ├── team.py          # Team model
│   └── user.py          # User model
├── routes/              # Route handlers
│   ├── admin.py         # Admin routes
│   ├── client.py        # Client routes
│   ├── manager.py       # Manager routes
│   └── team_worker.py   # Team worker routes
├── static/             # Static files
│   ├── css/            # Stylesheets
│   └── js/             # JavaScript files
└── templates/          # HTML templates
    ├── base.html       # Base template
    └── dashboard/      # Dashboard templates
```

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd jira-clone
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python setup_db.py
```

4. Run the application:
```bash
python app.py
```

5. Access the application at `http://localhost:5007`

## Default Users

The system comes with pre-configured users for testing:

- Admin: username: VaibhavAdmin, password: Admin123
- Manager: username: AbdulManager, password: Manager123
- Client: username: AmitClient, password: Client123
- Stakeholder: username: SureshStake, password: Stake123
- Team Worker: username: KartikTeam, password: Team123

## Features by User Role

### Admin
- User approval
- System management
- User management

### Manager
- Project creation and management
- Team assignment
- Progress tracking

### Client
- Project viewing
- Progress monitoring
- Task status tracking

### Team Worker
- Task management
- Status updates
- Project collaboration

## Security Features

- Password validation with requirements:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character
- Session-based authentication
- Role-based access control

## Contributing

Feel free to fork this repository and submit pull requests for any improvements.

# Jira-Clone
A web-based project management system built with Python Flask, similar to Jira, allowing different user roles to manage projects, tasks, and teams.
