import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlalchemy import asc, desc, delete
from app import db
from app.models import Entry
import os

bp = Blueprint('entries', __name__, url_prefix='/entries')


@bp.route('', methods=['GET', 'POST'])
def index():
    entries = Entry.query.order_by(desc(Entry.created)).all()
  
    return render_template('entries.html', entries=entries)

@bp.route('<id>', methods=['DELETE'])
def delete(id):
    entry = Entry.query.get_or_404(id)
    try:
        db.session.delete(entry)
        db.session.commit()
        return "success"
    except:
        flash("Something went wrong!")
    return "success"



