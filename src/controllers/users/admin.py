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
from src.models.faq import FAQ
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


# =============== FAQ ROUTES ===============

@admin_bp.route('/faq')
@login_required
@role_required('admin')
def faq():
    """Admin FAQ management page."""
    faqs = FAQ.query.order_by(FAQ.display_order, FAQ.id).all()
    return render_template('private/admins/FAQ/index.html',
                         current_user=_get_current_user(),
                         faqs=faqs)


@admin_bp.route('/faq/create', methods=['POST'])
@login_required
@role_required('admin')
def faq_create():
    """Create a new FAQ."""
    try:
        question = request.form.get('question')
        answer = request.form.get('answer')
        category = request.form.get('category') or None
        display_order = int(request.form.get('display_order', 0))
        is_active = 'is_active' in request.form
        
        faq = FAQ(
            question=question,
            answer=answer,
            category=category,
            display_order=display_order,
            is_active=is_active
        )
        faq.save()
        
        flash('FAQ created successfully!', 'success')
    except Exception as e:
        flash(f'Error creating FAQ: {str(e)}', 'error')
    
    return redirect(url_for('admin.faq'))


@admin_bp.route('/faq/update', methods=['POST'])
@login_required
@role_required('admin')
def faq_update():
    """Update an existing FAQ."""
    try:
        faq_id = request.form.get('faq_id')
        faq = FAQ.query.get(faq_id)
        
        if not faq:
            flash('FAQ not found.', 'error')
            return redirect(url_for('admin.faq'))
        
        faq.question = request.form.get('question')
        faq.answer = request.form.get('answer')
        faq.category = request.form.get('category') or None
        faq.display_order = int(request.form.get('display_order', 0))
        faq.is_active = 'is_active' in request.form
        
        faq.save()
        flash('FAQ updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating FAQ: {str(e)}', 'error')
    
    return redirect(url_for('admin.faq'))


@admin_bp.route('/faq/delete/<int:faq_id>', methods=['POST'])
@login_required
@role_required('admin')
def faq_delete(faq_id):
    """Delete an FAQ."""
    try:
        faq = FAQ.query.get(faq_id)
        
        if not faq:
            flash('FAQ not found.', 'error')
            return redirect(url_for('admin.faq'))
        
        faq.delete()
        flash('FAQ deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting FAQ: {str(e)}', 'error')
    
    return redirect(url_for('admin.faq'))


@admin_bp.route('/faq/get/<int:faq_id>')
@login_required
@role_required('admin')
def faq_get(faq_id):
    """Get FAQ data as JSON."""
    faq = FAQ.query.get(faq_id)
    
    if not faq:
        return jsonify({'error': 'FAQ not found'}), 404
    
    return jsonify({
        'id': faq.id,
        'question': faq.question,
        'answer': faq.answer,
        'category': faq.category,
        'display_order': faq.display_order,
        'is_active': faq.is_active
    })


# =============== PROFILE ROUTES ===============

@admin_bp.route('/profile')
@login_required
@role_required('admin')
def profile():
    """Admin profile page."""
    user = _get_current_user()
    admin = admins.Admin.query.filter_by(user_id=user.id).first()
    
    context = {
        'current_user': user,
        'admin': admin
    }
    return render_template('private/admins/profile/index.html', **context)


@admin_bp.route('/profile/update-profile', methods=['POST'])
@login_required
@role_required('admin')
def update_profile():
    """Update admin profile information."""
    from src.models.logs import Log
    
    user = _get_current_user()
    
    try:
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        
        # Validate required fields
        if not all([first_name, last_name, email]):
            flash('First name, last name, and email are required.', 'danger')
            return redirect(url_for('admin.profile'))
        
        # Check if email is already taken by another user
        existing_user = users.User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user.id:
            flash('Email address is already in use.', 'danger')
            return redirect(url_for('admin.profile'))
        
        # Update user information
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone_number
        user.save()
        
        # Log profile update
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='profile_update',
            description=f'{user.first_name} {user.last_name} updated their profile',
            user_id=user.id,
            target_type='user',
            target_id=user.id,
            status='success',
            extra_data={'ip_address': request.remote_addr}
        )
        
        flash('Profile updated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'danger')
    
    return redirect(url_for('admin.profile'))


@admin_bp.route('/profile/update-password', methods=['POST'])
@login_required
@role_required('admin')
def update_password():
    """Update admin password."""
    from src.models.logs import Log
    from src.utils.password_management import verify_hash
    
    user = _get_current_user()
    
    try:
        # Get form data
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate required fields
        if not all([current_password, new_password, confirm_password]):
            flash('All password fields are required.', 'danger')
            return redirect(url_for('admin.profile'))
        
        # Verify current password
        if not verify_hash(user.password_hash, current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('admin.profile'))
        
        # Validate new password
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'danger')
            return redirect(url_for('admin.profile'))
        
        # Check if passwords match
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('admin.profile'))
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Log password change
        Log.create_log(
            log_type=Log.TYPE_AUTH,
            action='password_change',
            description=f'{user.first_name} {user.last_name} changed their password',
            user_id=user.id,
            target_type='user',
            target_id=user.id,
            status='success',
            extra_data={'ip_address': request.remote_addr}
        )
        
        flash('Password updated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating password: {str(e)}', 'danger')
    
    return redirect(url_for('admin.profile'))


@admin_bp.route('/profile/delete-account', methods=['POST'])
@login_required
@role_required('admin')
def delete_account():
    """Delete admin account."""
    from src.models.logs import Log
    from src.utils.password_management import verify_hash
    
    user = _get_current_user()
    
    try:
        # Get password confirmation
        password = request.form.get('password')
        
        if not password:
            flash('Password is required to delete account.', 'danger')
            return redirect(url_for('admin.profile'))
        
        # Verify password
        if not verify_hash(user.password_hash, password):
            flash('Incorrect password.', 'danger')
            return redirect(url_for('admin.profile'))
        
        # Log account deletion before deleting
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='account_deletion',
            description=f'{user.first_name} {user.last_name} deleted their account',
            user_id=user.id,
            target_type='user',
            target_id=user.id,
            status='success',
            extra_data={'ip_address': request.remote_addr}
        )
        
        # Delete admin role and user
        admin = admins.Admin.query.filter_by(user_id=user.id).first()
        if admin:
            admin.delete()
        
        # Logout and delete session
        Doorman.query.filter_by(user_id=user.id).delete()
        session.clear()
        
        flash('Your account has been deleted.', 'success')
        return redirect(url_for('auth.loginReg'))
        
    except Exception as e:
        flash(f'Error deleting account: {str(e)}', 'danger')
    
    return redirect(url_for('admin.profile'))
