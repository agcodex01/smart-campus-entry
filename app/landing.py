import os
import time

from flask import (Blueprint, render_template, g, Response)
from flask_socketio import emit
from sqlalchemy import cast, Date, desc, func

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import threading
from ultralytics import YOLO
import cv2
import math
from gtts import gTTS
from playsound import playsound
from werkzeug.utils import secure_filename
import random

from app import db, app, socketio
from app.models import User, Entry

bp = Blueprint('landing', __name__, url_prefix="/")
last_play = datetime.now()

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
            stud_id = random.choice(['19104882', '1000293', '1022299344'])
            user_id = User.query.filter(
                User.student_id == stud_id).first().id
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


@bp.route("", methods=("GET", "POST"))
def index():
    entries = Entry.query.filter(func.DATE(Entry.created)  == date.today()).order_by(desc(Entry.created)).limit(6).all()
    users = User.query.all()

    return render_template("index.html", entries=entries, users=users)


@bp.route("video_detection", methods=["GET"])
def video_detection():
    return Response(
        generate_video_detection(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@bp.route("dashboard", methods=["GET"])
def dashboard():
    data = {
        'students': User.query.count(),
        'scan' : Entry.query.filter(func.DATE(Entry.created)  == date.today()).count()
    }
    return render_template('dashboard.html', data=data)
