"""
Admin controller for administrative operations.

All payment and enrollment routes have been moved to dedicated controllers:
- Payment routes: src/controllers/payments.py
- Enrollment routes: src/controllers/enrollments.py

Responsibilities: dashboard, admin privileges, student management, activity logs
"""

from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify, make_response
from src.models.user_folder import admins, users
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required
from src.services import admin_service

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _get_current_user():
    """Get current user from session."""
    return Doorman.get_by_token(session['doorman_token']).user


# =============== CORE ADMIN ROUTES ===============

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    """Admin dashboard route."""
    stats = admin_service.get_dashboard_stats()
    
    return render_template('private/admins/dashboard/index.html',
                         current_user=_get_current_user(),
                         **stats)


@admin_bp.route('/set-admin/<int:user_id>/<status>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'superuser')
def admin_status(user_id, status='add'):
    """Route to set a user as an admin."""
    user = users.User.query.get(user_id)
    if not user:
        return "User not found", 404

    try:
        current_user_id = _get_current_user().id
        
        if status == 'add':
            admin_service.grant_admin_privileges(user, current_user_id)
            return redirect(url_for('admin.dashboard'))
        elif status == 'remove':
            admin_service.revoke_admin_privileges(user, current_user_id)
            return redirect(url_for('auth.login'))
        else:
            return "Invalid status", 400
            
    except ValueError as e:
        return str(e), 400


@admin_bp.route('/set-instructor/<int:user_id>/<status>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'superuser')
def instructor_status(user_id, status='add'):
    """Route to grant or revoke instructor privileges."""
    from src.services import instructor_service
    
    try:
        if status == 'add':
            instructor_service.create_instructor(user_id)
            return redirect(url_for('admin.dashboard'))
        elif status == 'remove':
            instructor_service.deactivate_instructor(user_id)
            return redirect(url_for('auth.login'))
        else:
            return "Invalid status", 400
            
    except ValueError as e:
        return str(e), 404 if "not found" in str(e).lower() else 400
    

@admin_bp.route('/set-superuser/<int:user_id>/<status>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'superuser')
def superuser_status(user_id, status='add'):
    """Route to grant or revoke superuser privileges."""
    from src.services import superuser_service
    
    try:
        if status == 'add':
            superuser_service.create_superuser(user_id, _get_current_user().id)
            return redirect(url_for('admin.dashboard'))
        elif status == 'remove':
            superuser_service.revoke_superuser(user_id, _get_current_user().id)
            return redirect(url_for('auth.login'))
        else:
            return "Invalid status", 400
            
    except ValueError as e:
        return str(e), 404 if "not found" in str(e).lower() else 400
    

@admin_bp.route('/students')
@login_required
@role_required('admin')
def students():
    """Route to view all students with filtering."""
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')
    enrollments = request.args.get('enrollments', '')
    limit = request.args.get('limit', '50')
    export = request.args.get('export', '')
    
    filtered_students = admin_service.get_filtered_students(search, status, enrollments, limit)
    
    if export == 'csv':
        csv_data = admin_service.export_students_to_csv(filtered_students)
        response = make_response(csv_data)
        response.headers['Content-Disposition'] = f'attachment; filename=students_{datetime.now().strftime("%Y%m%d")}.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response
    
    counts = admin_service.get_student_counts()
    
    return render_template('private/admins/students/index.html',
                         current_user=_get_current_user(),
                         students=filtered_students,
                         **counts)

@admin_bp.route('/students/<int:student_id>')
@login_required
@role_required('admin')
def view_student(student_id):
    """Route to view a specific student's details."""
    from src.models.user_folder.students import Student
    from src.models.stripe.payments import Payment
    
    student = Student.query.get(student_id)
    if not student:
        return "Student not found", 404
    
    payments = Payment.query.filter_by(student_id=student_id).order_by(Payment.created_at.desc()).all()
    
    return render_template('private/admins/students/details.html',
                         current_user=_get_current_user(),
                         student=student,
                         payments=payments)

@admin_bp.route('/students/<int:student_id>/toggle-status', methods=['POST'])
@login_required
@role_required('admin')
def toggle_student_status(student_id):
    """Route to activate or deactivate a student account."""
    from src.models.user_folder.students import Student
    
    student = Student.query.get(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('admin.students'))
    
    try:
        status_text = admin_service.toggle_student_active_status(student, _get_current_user().id)
        flash(f'Student account has been {status_text} successfully.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash(f'Error updating student status: {str(e)}', 'danger')
    
    return redirect(url_for('admin.view_student', student_id=student_id))


@admin_bp.route('/logs')
@login_required
@role_required('admin')
def activity_logs():
    """Route to view activity logs including email logs."""
    page = request.args.get('page', 1, type=int)
    log_type_filter = request.args.get('log_type', '')
    status_filter = request.args.get('status', '')
    purpose_filter = request.args.get('purpose', '')
    action_filter = request.args.get('action', '')
    user_filter = request.args.get('user_id', '')
    
    pagination = admin_service.get_filtered_logs(
        page, 50, log_type_filter, status_filter, purpose_filter, action_filter, user_filter
    )
    filter_options = admin_service.get_log_filter_options()
    
    return render_template('private/admins/logs/index.html',
                         current_user=_get_current_user(),
                         logs=pagination.items,
                         pagination=pagination,
                         current_log_type=log_type_filter,
                         current_status=status_filter,
                         current_purpose=purpose_filter,
                         current_action=action_filter,
                         current_user_id=user_filter,
                         **filter_options)
    return redirect(url_for('admin.view_student', student_id=student_id))