import sqlite3

DB_NAME = 'jiraclone.db'

from .user import User, populate_sample_data
from .project import Project
from .task import Task
from .team import Team

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Enable foreign key support
    c.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT NOT NULL,
                  password TEXT NOT NULL,
                  role TEXT NOT NULL,
                  skills TEXT,
                  approved BOOLEAN DEFAULT 0,
                  team_id INTEGER,
                  FOREIGN KEY (team_id) REFERENCES teams(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS teams
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  leader_id INTEGER NOT NULL,
                  skills TEXT,
                  FOREIGN KEY (leader_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  description TEXT,
                  client_id INTEGER,
                  team_id INTEGER,
                  start_date DATE,
                  end_date DATE,
                  progress INTEGER DEFAULT 0,
                  FOREIGN KEY (client_id) REFERENCES users(id),
                  FOREIGN KEY (team_id) REFERENCES teams(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  description TEXT,
                  project_id INTEGER,
                  assignee_id INTEGER,
                  status TEXT DEFAULT 'TO DO',
                  type TEXT DEFAULT 'story',
                  epic TEXT,
                  created_at DATE DEFAULT CURRENT_DATE,
                  FOREIGN KEY (project_id) REFERENCES projects(id),
                  FOREIGN KEY (assignee_id) REFERENCES users(id))''')
    # Check if data exists
    c.execute("SELECT COUNT(*) FROM users WHERE username = 'VaibhavAdmin'")
    if c.fetchone()[0] == 0:
        from .user import populate_sample_data
        populate_sample_data(c)
    conn.commit()
    conn.close() 