import os
from flask import (Flask, render_template)
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SQLALCHEMY_DATABASE_URI='sqlite:///' +
    os.path.join(app.instance_path, 'flaskr.sqlite'),
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
)
app.config['UPLOAD_FOLDER'] = '/profiles'
socketio = SocketIO(app, cors_allowed_origins="*")
db = SQLAlchemy(app)

from app import landing, entries, auth, users

app.register_blueprint(landing.bp)
app.register_blueprint(entries.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(users.bp)

with app.app_context():
    db.create_all()

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')
        