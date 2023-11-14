import os
import time

from flask import (Flask, render_template, Response, request, redirect, url_for)
from flask_socketio import SocketIO, emit
from sqlalchemy import asc, desc
from . import auth
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import threading
from ultralytics import YOLO
import cv2
import math
from gtts import gTTS
from playsound import playsound
from werkzeug.utils import secure_filename

socketio = SocketIO()
db = SQLAlchemy()

last_play = datetime.now()



def create_app(test_config=None):
    UPLOAD_FOLDER = '/profiles'
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI='sqlite:///' +
        os.path.join(app.instance_path, 'flaskr.sqlite'),
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    socketio.init_app(app)

    def do_tts(class_id=""):
        global last_play
        now = datetime.now()
        if class_id in ['blonde', 'blondes']:
            diff = now - last_play
            if diff.total_seconds() > 5:
                last_play = now
                tts = gTTS(class_id + " detected", lang="en")
                filename = 'detect-' + datetime.now().strftime('%H-%M-%S-%f') + "-class.mp3"
                tts.save(filename)
                playsound(filename)
                os.remove(filename)
        else:
            with app.app_context():
                global socketio
                user_id = User.query.filter(
                    User.student_id == '19104882').first().id
                user_entry = Entry.query.filter(
                    Entry.user_id == user_id).order_by(desc(Entry.created)).first()
                if user_entry:
                    diff = now - user_entry.created
                    if diff.total_seconds() > 5:
                        entry = Entry(
                            user_id=user_id,
                            created=now
                        )
                        db.session.add(entry)
                        db.session.commit()
                        socketio.emit('detected', entry.to_dict())
                else:
                    entry = Entry(
                        user_id=user_id,
                        created=now
                    )
                    db.session.add(entry)
                    db.session.commit()

    def generate_video_detection():

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            exit()
        model = YOLO("best.pt")
        names = model.names
        while True:
            success, img = cap.read()
            if not success:
                break
            if img is None:
                continue
            results = model(img, stream=True)
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    conf = math.ceil((box.conf[0] * 100)) / 100
                    class_index = int(box.cls[0])
                    print(class_index)
                    if conf < 0.5:
                        continue
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                    name = names[class_index]
                    label = f"{name}: conf {conf}"
                    threading.Thread(target=do_tts, args=(name,)).start()
                    t_size = cv2.getTextSize(
                        label, 0, fontScale=1, thickness=2)[0]
                    c2 = x1 + t_size[0], y1 - t_size[1] - 3
                    cv2.rectangle(
                        img, (x1, y1), c2, [255, 0, 255], -1, cv2.LINE_AA
                    )  # filled
                    cv2.putText(
                        img,
                        label,
                        (x1, y1 - 2),
                        0,
                        1,
                        [255, 255, 255],
                        thickness=1,
                        lineType=cv2.LINE_AA,
                    )
            ref, buffer = cv2.imencode(".jpg", img)
            if ref:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" +
                    bytearray(buffer) + b"\r\n"
                )
        cap.release()
        cv2.destroyAllWindows()

    @app.route("/", methods=("GET", "POST"))
    def index():
        entries = Entry.query.order_by(desc(Entry.created)).limit(6).all()
        users = User.query.all()

        return render_template("index.html", entries=entries, users=users)

    @app.route("/video_detection", methods=["GET"])
    def video_detection():
        return Response(
            generate_video_detection(), mimetype="multipart/x-mixed-replace; boundary=frame"
        )
    
    @app.route('/users')
    def users_index():
        users = User.query.all()
        return render_template('users/users-index.html', users=users)
    
    @app.route('/users/create', methods=['GET', 'POST'])
    def users_create():
        if request.method == 'POST':
            student_id = request.form['student_id']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            course = request.form['course']
            year_level = request.form['year_level']
            
            file = request.files['file']
            basedir = os.path.abspath(os.path.dirname(__file__))
            file.save(os.path.join(basedir,'static/profiles', student_id + '.png') )
            
            user = User(
                student_id = student_id,
                first_name = first_name,
                last_name = last_name,
                course = course,
                year_level = year_level,
                username = 'user'
            )
            
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("users_index"))
        
        return render_template('users/user-create.html')
    @app.route('/entries')
    def entries_index():
        entries = Entry.query.all()
        return render_template('entries.html', entries=entries)

    # app.register_blueprint(entries.bp)
    app.register_blueprint(auth.bp)
    # app.register_blueprint(users.bp)

    return app


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
            'created': self.created.strftime('%m/%d/%Y, %H:%M:%S')
        }