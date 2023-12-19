import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlalchemy import asc, desc, delete, func
from app import db
from app.models import Entry
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
    ).order_by(Entry.created.desc()).all()

    violations = db.session.query(Entry).filter(
        Entry.user_id.in_([3, 4])
    ).all()

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
        Entry.user_id.in_([3, 4])
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

    row = 2
    for entry in entries:
        sheet['A' + str(row)] = entry.user.student_id
        sheet['B' + str(row)] = entry.user.first_name
        sheet['C' + str(row)] = entry.user.last_name
        sheet['D' + str(row)] = entry.user.course
        sheet['E' + str(row)] = entry.user.year_level
        sheet['F' + str(row)] = entry.created
        row += 1
        
    violation_sheet = workbook.create_sheet('Student Violations')
    violation_sheet['A1'] = 'Violation Type'
    violation_sheet['B1'] = 'Time Detected'
    
    row = 2
    for violation in violations:
        violation_sheet['A' + str(row)] = violation.user.username
        violation_sheet['B' + str(row)] = violation.created
        row += 1
    
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
