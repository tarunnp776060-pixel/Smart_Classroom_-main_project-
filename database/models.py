from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='Teacher') # Teacher / Admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False, index=True) # e.g. STU202601
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(50), default='AI & Data Science')
    semester = db.Column(db.String(20), default='6th Sem')
    email = db.Column(db.String(120), nullable=True)
    photo_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    encodings = db.relationship('FaceEncoding', backref='student', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True, cascade='all, delete-orphan')
    attention_records = db.relationship('AttentionRecord', backref='student', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'roll_number': self.roll_number,
            'department': self.department,
            'semester': self.semester,
            'email': self.email or '',
            'photo_path': self.photo_path or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class FaceEncoding(db.Model):
    __tablename__ = 'face_encodings'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    encoding_json = db.Column(db.Text, nullable=False) # JSON array of 128-d vector or landmark features
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_encoding(self):
        return json.loads(self.encoding_json)

    def set_encoding(self, vector_list):
        self.encoding_json = json.dumps(vector_list)


class ClassSession(db.Model):
    __tablename__ = 'class_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    class_section = db.Column(db.String(50), nullable=False) # e.g. 6th Sem AI&DS - Sec A
    session_date = db.Column(db.Date, default=datetime.utcnow().date)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    attendance_records = db.relationship('AttendanceRecord', backref='session', lazy=True, cascade='all, delete-orphan')
    attention_records = db.relationship('AttentionRecord', backref='session', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'subject_name': self.subject_name,
            'class_section': self.class_section,
            'session_date': self.session_date.strftime('%Y-%m-%d') if self.session_date else '',
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else '',
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else 'Active',
            'is_active': self.is_active
        }


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('class_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    record_date = db.Column(db.Date, default=datetime.utcnow().date)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Present') # Present / Absent / Late
    confidence = db.Column(db.Float, default=0.95)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else 'Unknown',
            'student_code': self.student.student_id if self.student else 'N/A',
            'record_date': self.record_date.strftime('%Y-%m-%d') if self.record_date else '',
            'timestamp': self.timestamp.strftime('%H:%M:%S') if self.timestamp else '',
            'status': self.status,
            'confidence': round(self.confidence * 100, 1)
        }


class AttentionRecord(db.Model):
    __tablename__ = 'attention_records'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('class_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    attention_score = db.Column(db.Float, nullable=False) # 0.0 to 100.0
    category = db.Column(db.String(30), nullable=False) # Attentive, Partially Attentive, Inattentive
    ear_value = db.Column(db.Float, default=0.3)
    pitch = db.Column(db.Float, default=0.0)
    yaw = db.Column(db.Float, default=0.0)
    roll = db.Column(db.Float, default=0.0)
    eye_status = db.Column(db.String(30), default='Eyes Open')
    head_pose_status = db.Column(db.String(30), default='Facing Forward')

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else 'Unknown',
            'timestamp': self.timestamp.strftime('%H:%M:%S'),
            'attention_score': round(self.attention_score, 1),
            'category': self.category,
            'ear_value': round(self.ear_value, 3),
            'pitch': round(self.pitch, 1),
            'yaw': round(self.yaw, 1),
            'roll': round(self.roll, 1),
            'eye_status': self.eye_status,
            'head_pose_status': self.head_pose_status
        }


class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    level = db.Column(db.String(20), default='INFO') # INFO, WARNING, ERROR
    event_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
