import os
import sqlite3
from flask import Flask, redirect, url_for, render_template #type: ignore
from models import init_db
from routes import register_blueprints

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
init_db()
register_blueprints(app)

@app.route('/')
def index():
    return render_template('welcome.html')

if __name__ == '__main__':
    # Get port from environment variable or default to 5007
    port = int(os.environ.get('PORT', 5007))
    app.run(host='0.0.0.0', port=port)