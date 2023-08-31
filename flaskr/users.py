import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db

bp = Blueprint('users', __name__, url_prefix='/users')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('', methods=('GET', 'POST'))
@login_required
def index():

    db = get_db()

    users = db.execute("SELECT * FROM users WHERE type='user'").fetchall()
  
    return render_template('users/users-index.html', users=users)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():

    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        course = request.form['course']
        db = get_db()
        error = None

        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (username, first_name, last_name, course) VALUES (?, ?, ?, ?)",
                    (username, first_name, last_name, course),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("users.index"))

        flash(error)
  
    return render_template('users/user-create.html')

