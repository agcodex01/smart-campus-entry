import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db

from . import auth

bp = Blueprint('users', __name__, url_prefix='/users')


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
@auth.login_required
def index():

    db = get_db()

    users = db.execute("SELECT * FROM users WHERE type='user'").fetchall()
  
    return render_template('users/users-index.html', users=users)

@bp.route('/create', methods=('GET', 'POST'))
@auth.login_required
def create():

    if request.method == 'POST':
        student_id = request.form['student_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        course = request.form['course']
        year_level = request.form['year_level']
        db = get_db()
        error = None

        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (student_id, first_name, last_name, course,year_level) VALUES (?, ?, ?, ?, ?)",
                    (student_id, first_name, last_name, course, year_level),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User withs {student_id} is already registered."
            else:
                return redirect(url_for("users.index"))

        flash(error)
  
    return render_template('users/user-create.html')

