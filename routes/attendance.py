from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from database.models import db, AttendanceRecord, Student, ClassSession
from datetime import datetime, date

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance')
@login_required
def list_attendance():
    date_str = request.args.get('date', '').strip()
    session_id = request.args.get('session_id', '').strip()
    search = request.args.get('search', '').strip()

    query = AttendanceRecord.query.join(Student)

    if date_str:
        try:
            filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(AttendanceRecord.record_date == filter_date)
        except ValueError:
            pass

    if session_id and session_id.isdigit():
        query = query.filter(AttendanceRecord.session_id == int(session_id))

    if search:
        query = query.filter(
            (Student.name.ilike(f'%{search}%')) |
            (Student.student_id.ilike(f'%{search}%'))
        )

    records = query.order_by(AttendanceRecord.timestamp.desc()).all()
    sessions = ClassSession.query.order_by(ClassSession.start_time.desc()).all()

    return render_template(
        'attendance.html',
        records=records,
        sessions=sessions,
        selected_date=date_str,
        selected_session=session_id,
        search=search
    )


@attendance_bp.route('/sessions', methods=['GET', 'POST'])
@login_required
def manage_sessions():
    if request.method == 'POST':
        subject_name = request.form.get('subject_name', '').strip()
        class_section = request.form.get('class_section', '').strip()

        if not subject_name or not class_section:
            flash('Subject Name and Class/Section are required!', 'warning')
            return redirect(url_for('attendance.manage_sessions'))

        # Deactivate any currently active sessions
        active_sessions = ClassSession.query.filter_by(is_active=True).all()
        for s in active_sessions:
            s.is_active = False
            s.end_time = datetime.utcnow()

        # Create new session
        new_session = ClassSession(
            subject_name=subject_name,
            class_section=class_section,
            session_date=date.today(),
            start_time=datetime.utcnow(),
            is_active=True,
            created_by_id=current_user.id
        )
        db.session.add(new_session)
        db.session.commit()

        flash(f'Class session "{subject_name}" started successfully!', 'success')
        return redirect(url_for('monitoring.live_monitoring'))

    sessions = ClassSession.query.order_by(ClassSession.start_time.desc()).all()
    active_session = ClassSession.query.filter_by(is_active=True).first()

    return render_template('sessions.html', sessions=sessions, active_session=active_session)


@attendance_bp.route('/sessions/stop/<int:session_id>', methods=['POST'])
@login_required
def stop_session(session_id):
    session = ClassSession.query.get_or_404(session_id)
    session.is_active = False
    session.end_time = datetime.utcnow()
    db.session.commit()
    flash(f'Class session "{session.subject_name}" ended.', 'info')
    return redirect(url_for('attendance.manage_sessions'))
