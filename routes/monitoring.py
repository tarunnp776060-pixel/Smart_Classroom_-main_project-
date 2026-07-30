from flask import Blueprint, render_template, Response, jsonify, request, current_app
from flask_login import login_required
from database.models import db, Student, FaceEncoding, ClassSession, AttendanceRecord, AttentionRecord
from ai.pipeline import MonitoringPipeline
from datetime import datetime, date
import cv2
import numpy as np
import json
import time

monitoring_bp = Blueprint('monitoring', __name__)

pipeline = MonitoringPipeline()

# Global state for monitoring server thread
camera_state = {
    'is_monitoring': True,
    'source_type': 'webcam', # 'webcam' or 'demo'
    'cap': None,
    'last_stats': {
        'total_detected': 0,
        'recognized_count': 0,
        'unknown_count': 0,
        'attentive_count': 0,
        'partially_attentive_count': 0,
        'inattentive_count': 0,
        'students_data': []
    }
}


def db_logging_callback(student_db_id, active_session_id, attention_data, eye_data, head_data, should_log_attention):
    """
    Thread-safe callback to log attendance & attention metrics into SQLite.
    """
    try:
        from app import app
        with app.app_context():
            # Get active session ID
            if not active_session_id:
                active_s = ClassSession.query.filter_by(is_active=True).first()
                if not active_s:
                    return
                active_session_id = active_s.id

            student = Student.query.get(student_db_id)
            if not student:
                return

            today_date = date.today()
            
            # 1. Prevent duplicate attendance record for same student in same session
            existing_att = AttendanceRecord.query.filter_by(
                session_id=active_session_id,
                student_id=student_db_id,
                record_date=today_date
            ).first()

            if not existing_att:
                att_record = AttendanceRecord(
                    session_id=active_session_id,
                    student_id=student_db_id,
                    record_date=today_date,
                    timestamp=datetime.utcnow(),
                    status='Present',
                    confidence=0.95
                )
                db.session.add(att_record)

            # 2. Log attention entry if interval elapsed
            if should_log_attention:
                att_entry = AttentionRecord(
                    session_id=active_session_id,
                    student_id=student_db_id,
                    timestamp=datetime.utcnow(),
                    attention_score=attention_data['score'],
                    category=attention_data['category'],
                    ear_value=eye_data.get('avg_ear', 0.3),
                    pitch=head_data.get('pitch', 0.0),
                    yaw=head_data.get('yaw', 0.0),
                    roll=head_data.get('roll', 0.0),
                    eye_status=eye_data.get('eye_status', 'Eyes Open'),
                    head_pose_status=head_data.get('status', 'Facing Forward')
                )
                db.session.add(att_entry)

            db.session.commit()
    except Exception as e:
        print(f"[DB Callback Error] {e}")


def generate_demo_classroom_frame(counter):
    """
    Generates a high-quality simulated classroom video frame for demo mode
    when physical webcam is not present or when demo video mode is selected.
    """
    width, height = 800, 500
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Gradient background simulating a classroom board & desks
    for y in range(height):
        ratio = y / height
        b = int(25 + ratio * 20)
        g = int(35 + ratio * 25)
        r = int(45 + ratio * 30)
        frame[y, :] = [b, g, r]

    # Draw simulated classroom header text
    cv2.putText(frame, "CLASSROOM MONITORED STREAM (DEMO MODE)", (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 225, 255), 2, cv2.LINE_AA)

    # Simulate 3 student faces positioned in classroom seats
    students_positions = [
        {'x': 180, 'y': 220, 'radius': 55, 'name': 'Alex Johnson', 'id': 'STU101'},
        {'x': 400, 'y': 210, 'radius': 55, 'name': 'Priya Sharma', 'id': 'STU102'},
        {'x': 620, 'y': 230, 'radius': 55, 'name': 'Rahul Verma', 'id': 'STU103'}
    ]

    for idx, s in enumerate(students_positions):
        cx, cy, r = s['x'], s['y'], s['radius']
        
        # Face oval
        cv2.ellipse(frame, (cx, cy), (r-10, r+10), 0, 0, 360, (190, 210, 225), -1)
        
        # Hair top
        cv2.ellipse(frame, (cx, cy - 20), (r-5, 25), 0, 180, 360, (30, 35, 45), -1)

        # Dynamic Eye blinking / head turning simulation based on counter
        eye_open = (counter + idx * 15) % 40 > 5
        head_yaw = np.sin((counter + idx * 20) * 0.1) * 25.0

        # Draw eyes
        eye_y = cy - 8
        dx = int(head_yaw * 0.3)
        if eye_open:
            cv2.circle(frame, (cx - 18 + dx, eye_y), 6, (255, 255, 255), -1)
            cv2.circle(frame, (cx + 18 + dx, eye_y), 6, (255, 255, 255), -1)
            cv2.circle(frame, (cx - 18 + dx, eye_y), 3, (40, 20, 10), -1)
            cv2.circle(frame, (cx + 18 + dx, eye_y), 3, (40, 20, 10), -1)
        else:
            cv2.line(frame, (cx - 24 + dx, eye_y), (cx - 12 + dx, eye_y), (40, 20, 10), 2)
            cv2.line(frame, (cx + 12 + dx, eye_y), (cx + 24 + dx, eye_y), (40, 20, 10), 2)

        # Nose & Mouth
        cv2.line(frame, (cx + dx, cy - 2), (cx + dx, cy + 12), (120, 140, 160), 2)
        cv2.line(frame, (cx - 10 + dx, cy + 24), (cx + 10 + dx, cy + 24), (80, 70, 120), 2)

    return frame


def fetch_registered_encodings():
    """Fetch all registered student encodings from database."""
    enc_records = []
    try:
        from app import app
        with app.app_context():
            students = Student.query.all()
            for s in students:
                for enc in s.encodings:
                    enc_records.append({
                        'student_db_id': s.id,
                        'student_id': s.student_id,
                        'name': s.name,
                        'roll_number': s.roll_number,
                        'encoding': enc.get_encoding()
                    })
    except Exception as e:
        print(f"[Fetch Encodings Error] {e}")
    return enc_records


def generate_video_stream():
    """Video streaming generator function."""
    cap = None
    frame_counter = 0

    while True:
        if not camera_state['is_monitoring']:
            time.sleep(0.2)
            continue

        frame = None

        if camera_state['source_type'] == 'webcam':
            if cap is None or not cap.isOpened():
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW if cv2.os.name == 'nt' else cv2.CAP_ANY)
                # Lower resolution for fast CPU processing
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            ret, read_frame = cap.read()
            if ret and read_frame is not None:
                frame = read_frame
            else:
                # If webcam unavailable or failed, fallback gracefully to demo video stream
                frame_counter += 1
                frame = generate_demo_classroom_frame(frame_counter)
        else:
            frame_counter += 1
            frame = generate_demo_classroom_frame(frame_counter)

        if frame is None:
            time.sleep(0.05)
            continue

        # Get active session ID
        active_session_id = None
        try:
            from app import app
            with app.app_context():
                active_s = ClassSession.query.filter_by(is_active=True).first()
                if active_s:
                    active_session_id = active_s.id
        except Exception:
            pass

        registered_encodings = fetch_registered_encodings()

        # Run AI Pipeline
        annotated_frame, stats = pipeline.process_frame(
            frame,
            registered_students=registered_encodings,
            app_context_db_callback=db_logging_callback,
            active_session_id=active_session_id
        )

        camera_state['last_stats'] = stats

        # Encode frame as JPEG
        ret_enc, buffer = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret_enc:
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        time.sleep(0.03) # ~30 fps cap for smooth video


@monitoring_bp.route('/monitoring')
@login_required
def live_monitoring():
    active_session = ClassSession.query.filter_by(is_active=True).first()
    students_count = Student.query.count()
    return render_template(
        'monitoring.html',
        active_session=active_session,
        students_count=students_count,
        is_monitoring=camera_state['is_monitoring'],
        source_type=camera_state['source_type']
    )


@monitoring_bp.route('/video_feed')
@login_required
def video_feed():
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@monitoring_bp.route('/api/monitoring_stats')
@login_required
def get_monitoring_stats():
    return jsonify({
        'status': 'success',
        'is_monitoring': camera_state['is_monitoring'],
        'source_type': camera_state['source_type'],
        'stats': camera_state['last_stats']
    })


@monitoring_bp.route('/api/monitoring/toggle', methods=['POST'])
@login_required
def toggle_monitoring():
    data = request.json or {}
    action = data.get('action')
    if action == 'start':
        camera_state['is_monitoring'] = True
    elif action == 'stop':
        camera_state['is_monitoring'] = False
    else:
        camera_state['is_monitoring'] = not camera_state['is_monitoring']

    return jsonify({'success': True, 'is_monitoring': camera_state['is_monitoring']})


@monitoring_bp.route('/api/monitoring/set_source', methods=['POST'])
@login_required
def set_source():
    data = request.json or {}
    source = data.get('source', 'webcam')
    if source in ['webcam', 'demo']:
        camera_state['source_type'] = source
        return jsonify({'success': True, 'source_type': source})
    return jsonify({'success': False, 'message': 'Invalid source'}), 400
