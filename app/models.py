
from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    year_level = db.Column(db.String(50), nullable=False)
    course = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=True)
    entries = db.relationship('Entry', backref='user')

    def __repr__(self):
        return '<User %r>' % self.id

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'student_id': self.student_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'year_level': self.year_level,
            'course': self.course,
        }


class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<Entry %r>' % self.id

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.to_dict(),
            'created': self.created.strftime('%m/%d/%Y, %H:%M:%S'),
            'time': self.created.strftime('%I:%M %p'),
            'time_hour': self.created.strftime('%I %p'),
        }