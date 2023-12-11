import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlalchemy import asc, desc, delete, func
from app import db
from app.models import Entry
from app.auth import login_required

bp = Blueprint('entries', __name__, url_prefix='/entries')


@bp.route('', methods=['GET', 'POST'])
@login_required
def index():
    entries = Entry.query.order_by(Entry.created.desc()).all()
  
    return render_template('entries.html', entries=entries)

@bp.route('<id>', methods=['DELETE'])
@login_required
def delete(id):
    entry = Entry.query.get_or_404(id)
    try:
        db.session.delete(entry)
        db.session.commit()
        return "success"
    except:
        flash("Something went wrong!")
    return "success"



