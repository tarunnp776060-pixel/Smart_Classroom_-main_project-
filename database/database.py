from database.models import db, User, Student, FaceEncoding, ClassSession, AttendanceRecord, AttentionRecord, SystemLog
from datetime import datetime, date, timedelta
import numpy as np
import json
import os

def init_db(app):
    """Initialize database and seed demo data if empty."""
    db.init_app(app)
    
    # Ensure instance folder exists
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
    os.makedirs(app.config['DATASET_DIR'], exist_ok=True)
    
    with app.app_context():
        db.create_all()
        seed_demo_data()

def seed_demo_data():
    """Seed default teacher account and initial demo students if not present."""
    # 1. Seed Teacher / Admin User
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@college.edu',
            full_name='Dr. Sarah Jenkins (Professor)',
            role='Teacher'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("[DB] Created default admin user: admin / admin123")
    
    # 2. Seed Demo Students if database is fresh
    if Student.query.count() == 0:
        demo_students = [
            {'student_id': 'STU101', 'name': 'Alex Johnson', 'roll_number': '21AD001', 'dept': 'AI & DS', 'sem': '6th Sem', 'email': 'alex.j@college.edu'},
            {'student_id': 'STU102', 'name': 'Priya Sharma', 'roll_number': '21AD002', 'dept': 'AI & DS', 'sem': '6th Sem', 'email': 'priya.s@college.edu'},
            {'student_id': 'STU103', 'name': 'Rahul Verma', 'roll_number': '21AD003', 'dept': 'AI & DS', 'sem': '6th Sem', 'email': 'rahul.v@college.edu'},
            {'student_id': 'STU104', 'name': 'Emily Davis', 'roll_number': '21AD004', 'dept': 'AI & DS', 'sem': '6th Sem', 'email': 'emily.d@college.edu'},
            {'student_id': 'STU105', 'name': 'Mohammed Ali', 'roll_number': '21AD005', 'dept': 'AI & DS', 'sem': '6th Sem', 'email': 'm.ali@college.edu'}
        ]
        
        for s_data in demo_students:
            student = Student(
                student_id=s_data['student_id'],
                name=s_data['name'],
                roll_number=s_data['roll_number'],
                department=s_data['dept'],
                semester=s_data['sem'],
                email=s_data['email']
            )
            db.session.add(student)
            db.session.flush() # Get student.id
            
            # Create a synthetic normalized 128-d face embedding vector for demo student recognition
            # Use deterministic seed based on student_id for reproducibility
            seed_val = int(s_data['student_id'].replace('STU', ''))
            rng = np.random.RandomState(seed_val)
            synthetic_vector = rng.randn(128)
            synthetic_vector /= np.linalg.norm(synthetic_vector)
            
            face_enc = FaceEncoding(
                student_id=student.id,
                encoding_json=json.dumps(synthetic_vector.tolist())
            )
            db.session.add(face_enc)

        print(f"[DB] Seeded {len(demo_students)} demo students with face embeddings.")

    # 3. Seed active class session if none exist
    active_session = ClassSession.query.filter_by(is_active=True).first()
    if not active_session:
        session = ClassSession(
            subject_name='Artificial Intelligence & Neural Networks',
            class_section='6th Sem AI&DS - Sec A',
            session_date=date.today(),
            start_time=datetime.utcnow() - timedelta(minutes=25),
            is_active=True
        )
        db.session.add(session)
        db.session.flush()
        
        # Add historical attendance & attentiveness demo logs for visualization charts
        students = Student.query.all()
        for idx, student in enumerate(students):
            # Mark attendance
            att = AttendanceRecord(
                session_id=session.id,
                student_id=student.id,
                record_date=date.today(),
                timestamp=datetime.utcnow() - timedelta(minutes=20 - idx),
                status='Present' if idx != 3 else 'Absent',
                confidence=0.92 + (idx * 0.01)
            )
            db.session.add(att)
            
            # Add historical attention entries
            if idx != 3: # Present students
                base_score = 88.0 - (idx * 9.5)
                att_record = AttentionRecord(
                    session_id=session.id,
                    student_id=student.id,
                    timestamp=datetime.utcnow() - timedelta(minutes=5),
                    attention_score=max(35.0, base_score),
                    category='Attentive' if base_score >= 80 else ('Partially Attentive' if base_score >= 50 else 'Inattentive'),
                    ear_value=0.28 - (idx * 0.02),
                    pitch=2.0 * idx,
                    yaw=4.0 * idx,
                    roll=1.0,
                    eye_status='Eyes Open' if base_score > 50 else 'Drowsy',
                    head_pose_status='Facing Forward' if idx < 2 else 'Looking Away'
                )
                db.session.add(att_record)
                
        print("[DB] Created initial active class session and sample data.")

    # Log startup event
    sys_log = SystemLog(
        level='INFO',
        event_type='SYSTEM_STARTUP',
        message='Classroom Attentiveness & Attendance System initialized successfully.'
    )
    db.session.add(sys_log)
    db.session.commit()
