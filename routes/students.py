from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required
from database.models import db, Student, FaceEncoding, AttendanceRecord, AttentionRecord
from ai.face_recognition import FaceRecognizerEngine
import os
import cv2
import base64
import numpy as np

students_bp = Blueprint('students', __name__)
recognizer = FaceRecognizerEngine()

@students_bp.route('/students')
@login_required
def list_students():
    search_query = request.args.get('search', '').strip()
    if search_query:
        students = Student.query.filter(
            (Student.name.ilike(f'%{search_query}%')) |
            (Student.student_id.ilike(f'%{search_query}%')) |
            (Student.roll_number.ilike(f'%{search_query}%'))
        ).all()
    else:
        students = Student.query.order_by(Student.student_id).all()
        
    return render_template('students.html', students=students, search_query=search_query)

@students_bp.route('/students/add', methods=['POST'])
@login_required
def add_student():
    student_id = request.form.get('student_id', '').strip()
    name = request.form.get('name', '').strip()
    roll_number = request.form.get('roll_number', '').strip()
    department = request.form.get('department', 'AI & Data Science').strip()
    semester = request.form.get('semester', '6th Sem').strip()
    email = request.form.get('email', '').strip()

    if not student_id or not name or not roll_number:
        flash('Student ID, Name, and Roll Number are required!', 'warning')
        return redirect(url_for('students.list_students'))

    existing = Student.query.filter_by(student_id=student_id).first()
    if existing:
        flash(f'Student with ID {student_id} already exists!', 'danger')
        return redirect(url_for('students.list_students'))

    # Create new student
    student = Student(
        student_id=student_id,
        name=name,
        roll_number=roll_number,
        department=department,
        semester=semester,
        email=email
    )
    
    # Check if a profile photo was uploaded via file input
    if 'photo' in request.files and request.files['photo'].filename != '':
        photo = request.files['photo']
        filename = f"{student_id}_{int(os.urandom(4).hex(), 16)}.jpg"
        save_path = os.path.join(current_app.config['DATASET_DIR'], filename)
        photo.save(save_path)
        student.photo_path = f"dataset/students/{filename}"

        # Generate face embedding from uploaded photo
        img_bgr = cv2.imread(save_path)
        if img_bgr is not None:
            embedding = recognizer.extract_face_embedding(img_bgr)
            if embedding:
                db.session.add(student)
                db.session.flush()
                enc_model = FaceEncoding(student_id=student.id)
                enc_model.set_encoding(embedding)
                db.session.add(enc_model)
                db.session.commit()
                flash(f'Student {name} registered successfully with face encoding!', 'success')
                return redirect(url_for('students.list_students'))

    db.session.add(student)
    db.session.commit()
    flash(f'Student {name} registered! Please capture/upload face image for recognition.', 'info')
    return redirect(url_for('students.student_detail', student_id=student.id))


@students_bp.route('/api/students/register_webcam_face', methods=['POST'])
@login_required
def register_webcam_face():
    """Accept base64 webcam frame, compute face embedding, save image and DB record."""
    data = request.json or {}
    db_id = data.get('student_db_id')
    image_b64 = data.get('image_data')

    if not db_id or not image_b64:
        return jsonify({'success': False, 'message': 'Invalid student ID or image payload.'}), 400

    student = Student.query.get(db_id)
    if not student:
        return jsonify({'success': False, 'message': 'Student record not found.'}), 404

    try:
        # Decode base64 image
        header, encoded = image_b64.split(',', 1) if ',' in image_b64 else ('', image_b64)
        img_bytes = base64.b64decode(encoded)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame_bgr is None:
            return jsonify({'success': False, 'message': 'Could not decode image frame.'}), 400

        # Save face image file
        filename = f"{student.student_id}_webcam.jpg"
        save_path = os.path.join(current_app.config['DATASET_DIR'], filename)
        cv2.imwrite(save_path, frame_bgr)

        student.photo_path = f"dataset/students/{filename}"

        # Extract face embedding
        embedding = recognizer.extract_face_embedding(frame_bgr)
        if not embedding:
            return jsonify({'success': False, 'message': 'No face detected in webcam frame! Position face clearly.'}), 400

        # Save encoding
        enc_model = FaceEncoding(student_id=student.id)
        enc_model.set_encoding(embedding)
        db.session.add(enc_model)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Face profile successfully registered for {student.name}!'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@students_bp.route('/students/<int:student_id>')
@login_required
def student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Calculate Attendance stats
    total_records = AttendanceRecord.query.filter_by(student_id=student.id).count()
    present_records = AttendanceRecord.query.filter_by(student_id=student.id, status='Present').count()
    att_percentage = round((present_records / total_records * 100), 1) if total_records > 0 else 0.0

    # Calculate Average Attention Score
    attention_entries = AttentionRecord.query.filter_by(student_id=student.id).all()
    if attention_entries:
        avg_attention = round(np.mean([a.attention_score for a in attention_entries]), 1)
    else:
        avg_attention = 85.0 # Default benchmark if no session records yet

    recent_attendance = AttendanceRecord.query.filter_by(student_id=student.id).order_by(AttendanceRecord.timestamp.desc()).limit(10).all()
    recent_attention = AttentionRecord.query.filter_by(student_id=student.id).order_by(AttentionRecord.timestamp.desc()).limit(15).all()

    return render_template(
        'student_detail.html',
        student=student,
        attendance_percentage=att_percentage,
        present_records=present_records,
        total_records=total_records,
        avg_attention=avg_attention,
        recent_attendance=recent_attendance,
        recent_attention=recent_attention
    )


@students_bp.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    name = student.name
    db.session.delete(student)
    db.session.commit()
    flash(f'Student {name} deleted successfully.', 'info')
    return redirect(url_for('students.list_students'))
