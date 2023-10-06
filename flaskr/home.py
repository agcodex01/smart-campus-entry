import functools
from ultralytics import YOLO
import cv2;
import math

from gtts import gTTS
from playsound import playsound
import tempfile

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, Response
)

from flaskr.db import get_db

bp = Blueprint('home', __name__,)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

def do_tts(text="Hi"):
    tts = gTTS(text)
    temp_file = tempfile.NamedTemporaryFile(suffix= ".mp3", delete= False)
    tts.save(temp_file.name)
    # file_path = os.path.abspath(temp_file.)
    playsound(temp_file.name)
    
def generate_video_detection():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    model=YOLO('yolov8n.pt')
    names = model.names
    print(names)
    while True:
        success, img = cap.read()
        if not success: break
        if img is None:
            continue
        results=model(img,stream=True)
        for r in results:
            boxes=r.boxes
            for box in boxes:
                conf=math.ceil((box.conf[0]*100))/100
                class_index = int(box.cls[0])
                print(class_index)
                if conf < 0.2:
                    continue
                x1,y1,x2,y2=box.xyxy[0]
                x1,y1,x2,y2=int(x1), int(y1), int(x2), int(y2)
                # print(x1,y1,x2,y2)
                cv2.rectangle(img, (x1,y1), (x2,y2), (255,0,255),3)
                name = names[class_index]
                label=f'{name}: conf {conf}'          
                t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
                # print(t_size)
                c2 = x1 + t_size[0], y1 - t_size[1] - 3
                cv2.rectangle(img, (x1,y1), c2, [255,0,255], -1, cv2.LINE_AA)  # filled
                cv2.putText(img, label, (x1,y1-2),0, 1,[255,255,255], thickness=1,lineType=cv2.LINE_AA)
        ref,buffer=cv2.imencode('.jpg',img)
        if ref:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(buffer) +b'\r\n')    
           
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/', methods=('GET', 'POST'))
def index():
    db = get_db()
    users = db.execute("SELECT * FROM users WHERE type='user'").fetchall()
    entries = db.execute('SELECT e.id, created, u.first_name, u.last_name, u.course  FROM entries e JOIN users u ON e.user_id = u.id  ORDER BY created DESC LIMIT 4').fetchall()
  
    return render_template('index.html', entries=entries, users=users)

@bp.route('/video_detection', methods=['GET'])
def video_detection():
    return Response(generate_video_detection(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
    
cv2.destroyAllWindows()
