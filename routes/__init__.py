# routes/__init__.py

def register_blueprints(app):
    from .auth import auth_bp
    from .admin import admin_bp
    from .manager import manager_bp
    from .client import client_bp
    from .stakeholder import stakeholder_bp
    from .team_worker import team_worker_bp
    from .api import api_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(stakeholder_bp)
    app.register_blueprint(team_worker_bp)
    app.register_blueprint(api_bp) 