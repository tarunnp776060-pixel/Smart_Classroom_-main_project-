from flask import Blueprint, render_template, request, Response, flash
from flask_login import login_required
from database.models import db, Student, ClassSession, AttendanceRecord, AttentionRecord
from datetime import datetime, date
import csv
import io

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def report_view():
    students = Student.query.all()
    sessions = ClassSession.query.order_by(ClassSession.start_time.desc()).all()

    selected_student = request.args.get('student_id', '')
    selected_session = request.args.get('session_id', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    query_att = AttendanceRecord.query.join(Student)
    query_attention = AttentionRecord.query.join(Student)

    if selected_student and selected_student.isdigit():
        query_att = query_att.filter(AttendanceRecord.student_id == int(selected_student))
        query_attention = query_attention.filter(AttentionRecord.student_id == int(selected_student))

    if selected_session and selected_session.isdigit():
        query_att = query_att.filter(AttendanceRecord.session_id == int(selected_session))
        query_attention = query_attention.filter(AttentionRecord.session_id == int(selected_session))

    if start_date:
        try:
            d_start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query_att = query_att.filter(AttendanceRecord.record_date >= d_start)
        except ValueError:
            pass

    if end_date:
        try:
            d_end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query_att = query_att.filter(AttendanceRecord.record_date <= d_end)
        except ValueError:
            pass

    attendance_records = query_att.order_by(AttendanceRecord.timestamp.desc()).all()
    attention_records = query_attention.order_by(AttentionRecord.timestamp.desc()).limit(50).all()

    return render_template(
        'reports.html',
        students=students,
        sessions=sessions,
        attendance_records=attendance_records,
        attention_records=attention_records,
        selected_student=selected_student,
        selected_session=selected_session,
        start_date=start_date,
        end_date=end_date
    )


@reports_bp.route('/reports/export/csv')
@login_required
def export_csv():
    report_type = request.args.get('type', 'attendance')
    
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == 'attendance':
        writer.writerow(['Record ID', 'Date', 'Time', 'Student ID', 'Student Name', 'Roll Number', 'Department', 'Status', 'Confidence'])
        records = AttendanceRecord.query.join(Student).order_by(AttendanceRecord.timestamp.desc()).all()
        for r in records:
            writer.writerow([
                r.id,
                r.record_date.strftime('%Y-%m-%d'),
                r.timestamp.strftime('%H:%M:%S'),
                r.student.student_id if r.student else '',
                r.student.name if r.student else '',
                r.student.roll_number if r.student else '',
                r.student.department if r.student else '',
                r.status,
                f"{round(r.confidence * 100, 1)}%"
            ])
        filename = f"attendance_report_{date.today().strftime('%Y%m%d')}.csv"
    else:
        writer.writerow(['Record ID', 'Timestamp', 'Student ID', 'Student Name', 'Attention Score', 'Category', 'Eye Status', 'Head Pose', 'EAR', 'Yaw', 'Pitch'])
        records = AttentionRecord.query.join(Student).order_by(AttentionRecord.timestamp.desc()).all()
        for r in records:
            writer.writerow([
                r.id,
                r.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                r.student.student_id if r.student else '',
                r.student.name if r.student else '',
                round(r.attention_score, 1),
                r.category,
                r.eye_status,
                r.head_pose_status,
                round(r.ear_value, 3),
                round(r.yaw, 1),
                round(r.pitch, 1)
            ])
        filename = f"attentiveness_report_{date.today().strftime('%Y%m%d')}.csv"

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )


@reports_bp.route('/architecture')
@login_required
def project_architecture():
    """Viva / Demo Project Architecture & Methodology Explanation Page."""
    return render_template('architecture.html')
