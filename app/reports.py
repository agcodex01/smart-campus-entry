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
    reports = []
    basedir = os.path.abspath(os.path.dirname(__file__))
    dir = os.path.join(basedir, 'static/reports')

    for file in os.listdir(dir):
        reports.append(file)
        
    return render_template('reports.html', reports=sorted(reports, reverse=True))
