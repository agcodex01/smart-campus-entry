from flask import (
    Blueprint, redirect, g, render_template, request, session, url_for, flash
)

import os

from app import db
from app.models import User
from app.auth import login_required
from sqlalchemy import any_

bp = Blueprint('users', __name__, url_prefix='/users')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

courses = [
    'Bachelor of Science in Information Technology(BSIT)',
    'Bachelor of Science in Entrepreneurship(BSEntrep)',
    'Bachelor of Science in Fisheries (BSFi)',
    'The Bachelor in Technical-Vocational Teacher Education (BTVTEd)'
]


@bp.route('', methods=('GET', 'POST'))
@login_required
def index():
    
    users = User.query.filter(
        User.student_id != '00000-001'
    ).filter(
        User.student_id != '00000-002'

    ).filter(
        User.student_id != '00000-003'
    ).all()

    return render_template('users/users-index.html', users=users)


@bp.route('create', methods=['GET', 'POST'])
@login_required
def users_create():
    if request.method == 'POST':
        student_id = request.form['student_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        course = request.form['course']
        year_level = request.form['year_level']

        file = request.files['file']
        basedir = os.path.abspath(os.path.dirname(__file__))
        file.save(os.path.join(basedir, 'static/profiles', student_id + '.png'))

        user = User(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            course=course,
            year_level=year_level,
            username='user'
        )

        db.session.add(user)
        db.session.commit()
        return redirect(url_for("users.index"))

    return render_template('users/user-create.html', courses=courses)


@bp.route('<id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    user = User.query.filter(User.id == id).first()
    if request.method == 'POST':
        student_id = request.form['student_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        course = request.form['course']
        year_level = request.form['year_level']

        file = request.files['file']
        if file:
            basedir = os.path.abspath(os.path.dirname(__file__))
            path = os.path.join(basedir, 'static/profiles',
                                student_id + '.png')
            if os.path.exists(path):
                os.remove(path)
            file.save(path)

        user.first_name = first_name
        user.last_name = last_name
        user.student_id = student_id
        user.course = course
        user.year_level = year_level
        db.session.commit()

        return redirect(url_for("users.index"))

    return render_template('users/user-edit.html', user=user, courses=courses)


@bp.route('<id>', methods=['POST'])
def delete(id):
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("users.index"))
    except:
        flash("Something went wrong!")
    return redirect(url_for("users.index"))


@bp.route('delete/batch', methods=['POST'])
@login_required
def batch():
  
    ids = request.form.getlist('ids[]')
    print(ids)
    for id in ids:
        user = User.query.get_or_404(id)
        try:
            db.session.delete(user)
            db.session.commit()
        except:
            flash("Something went wrong!")
    return redirect(url_for("users.index"))
    