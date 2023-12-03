import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from sqlalchemy import asc, desc
from app import models, db
import os

bp = Blueprint('entries', __name__, url_prefix='/entries')


@bp.route('', methods=('GET', 'POST'))
def index():
    entries = models.Entry.query.order_by(desc(models.Entry.created)).all()
  
    return render_template('entries.html', entries=entries)



