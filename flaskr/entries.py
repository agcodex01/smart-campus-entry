import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db

bp = Blueprint('entries', __name__, url_prefix='/entries')


@bp.route('', methods=('GET', 'POST'))
def index():
    
    db = get_db()
    if (request.method == 'POST'):
        user_id = request.form['user_id']
        try:
            db.execute(
                "INSERT INTO entries (user_id) VALUES (?)",
                (user_id),
            )
            db.commit()
        except db.IntegrityError:
            error = "Something went wrong"
        else:
            return redirect(url_for('home.index'))


    entries = db.execute('SELECT e.id, created,u.username, u.first_name, u.last_name, u.course  FROM entries e JOIN users u ON e.user_id = u.id  ORDER BY created DESC').fetchall()
  
    return render_template('entries.html', entries=entries)



