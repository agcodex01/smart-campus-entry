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

bp = Blueprint('reports', __name__, url_prefix='/reports')


@bp.route('', methods=['GET', 'POST'])
@login_required
def index():
    basedir = os.path.abspath(os.path.dirname(__file__))
    dir = os.path.join(basedir, 'static/reports')
    
    if request.method == 'POST':
        names = request.form.getlist('names[]')
        for name in names:
            os.remove(dir + "/" + name)
        return redirect(url_for('reports.index'))
    
    reports = []
    for file in os.listdir(dir):
        reports.append(file)
        
    return render_template('reports.html', reports=sorted(reports, reverse=True))

@bp.route('<name>/delete', methods=['POST'])
def delete(name):
    basedir = os.path.abspath(os.path.dirname(__file__))
    dir = os.path.join(basedir, 'static/reports')
    
    os.remove(dir + "/" + name)

    return redirect(url_for('reports.index'))