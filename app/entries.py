import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlalchemy import asc, desc, delete, func, update
from app import db
from app.models import Entry, User
from app.auth import login_required
from datetime import datetime, date
from openpyxl import Workbook
import os

bp = Blueprint('entries', __name__, url_prefix='/entries')


@bp.route('', methods=['GET', 'POST'])
@login_required
def index():
    entries = db.session.query(Entry).filter(
        ~Entry.user_id.in_([3, 4])
    ).filter(
        Entry.violations == None
    ).order_by(Entry.created.desc()).all()

    violations = db.session.query(Entry).filter(
        ~Entry.user_id.in_([3, 4])
    ).filter(
        Entry.reported == 1
    ).order_by(Entry.created.desc()).all()

    return render_template('entries.html', entries=entries, violations=violations)


@bp.route('<id>/delete', methods=['POST'])
@login_required
def delete(id):
    entry = Entry.query.get_or_404(id)
    try:
        db.session.delete(entry)
        db.session.commit()
        return "success"
    except:
        flash("Something went wrong!")

    return redirect(url_for("entries.index"))


@bp.route('data/export', methods=['POST'])
@login_required
def export():
    entries = db.session.query(Entry).filter(func.DATE(Entry.created) == date.today()).filter(
        ~Entry.user_id.in_([3, 4])
    ).all()
    
    violations = db.session.query(Entry).filter(func.DATE(Entry.created) == date.today()).filter(
        ~Entry.user_id.in_([3, 4])
    ).filter(
        Entry.reported == 1
    ).all()

    workbook = Workbook()
    sheet = workbook.active

    sheet.title = 'Student Logs'

    sheet['A1'] = 'Student ID'
    sheet['B1'] = 'First name'
    sheet['C1'] = 'Last name'
    sheet['D1'] = 'Course'
    sheet['E1'] = 'Year Level'
    sheet['F1'] = 'Time In'

    rowIndex = 2
    for entry in entries:
        sheet['A' + str(rowIndex)] = entry.user.student_id
        sheet['B' + str(rowIndex)] = entry.user.first_name
        sheet['C' + str(rowIndex)] = entry.user.last_name
        sheet['D' + str(rowIndex)] = entry.user.course
        sheet['E' + str(rowIndex)] = entry.user.year_level
        sheet['F' + str(rowIndex)] = entry.created
        rowIndex += 1

    violation_sheet = workbook.create_sheet('Student Violations')
    violation_sheet['A1'] = 'Student ID'
    violation_sheet['B1'] = 'First name'
    violation_sheet['C1'] = 'Last name'
    violation_sheet['D1'] = 'Course'
    violation_sheet['E1'] = 'Year Level'
    violation_sheet['F1'] = 'Violation Type'
    violation_sheet['G1'] = 'Other'
    violation_sheet['H1'] = 'Time Detected'

    rowIndex = 2
    for violation in violations:
        violation_sheet['A' + str(rowIndex)] = violation.user.student_id
        violation_sheet['B' + str(rowIndex)] = violation.user.first_name
        violation_sheet['C' + str(rowIndex)] = violation.user.last_name
        violation_sheet['D' + str(rowIndex)] = violation.user.course
        violation_sheet['E' + str(rowIndex)] = violation.user.year_level
        violation_sheet['F' + str(rowIndex)] = violation.violations
        violation_sheet['G' + str(rowIndex)] = violation.other
        violation_sheet['H' + str(rowIndex)] = violation.created

        rowIndex += 1

    basedir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(basedir, 'static/reports',
                        datetime.now().strftime('%d-%b-%Y-%I-%M-%p-%S%f') + '.xlsx')
    workbook.save(filename=path)

    return redirect(url_for('reports.index'))


@bp.route('delete/batch', methods=['POST'])
@login_required
def batch():

    ids = request.form.getlist('ids[]')
    for id in ids:
        user = Entry.query.get_or_404(id)
        try:
            db.session.delete(user)
            db.session.commit()
        except:
            flash("Something went wrong!")
    return redirect(url_for("entries.index"))


@bp.route('submit-report', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        id = request.form['id']
        student_id = request.form['student_id']
        
        entry = Entry.query.filter(Entry.id == id).first()
        
        user_id = User.query.filter(
                        User.student_id == student_id).first().id
        if user_id == None:
            return redirect(url_for("entries.submit"))

        log = Entry(
            user_id=user_id,
            created= datetime.now(),
            reported=1,
            violations=entry.user.username
        )
       
        entry.reported = True
        db.session.add(log)
       
        db.session.commit()
    
        
        return redirect(url_for("entries.submit"))
        
    violations = db.session.query(Entry).filter(
        Entry.user_id.in_([3, 4])
    ).filter(
        Entry.reported == 0
    ).all()
    return render_template('submit-report.html', violations=violations)
