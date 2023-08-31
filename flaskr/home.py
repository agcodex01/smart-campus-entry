import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db

bp = Blueprint('home', __name__,)

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


@bp.route('/', methods=('GET', 'POST'))
def index():
    db = get_db()
    users = db.execute("SELECT * FROM users WHERE type='user'").fetchall()
    entries = db.execute('SELECT e.id, created, u.first_name, u.last_name, u.course  FROM entries e JOIN users u ON e.user_id = u.id  ORDER BY created DESC LIMIT 4').fetchall()
  
    return render_template('index.html', entries=entries, users=users)



