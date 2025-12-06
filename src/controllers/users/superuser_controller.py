from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from functools import wraps
from src.models.logbook import Logbook
from src.logic.user_logic import UserLogic
from src.models.user import User
from src.models.roles import Role, UserHasRoles
from src.models.courses_model import Course, CourseTemplate
from src.logic.setting_logic import SettingsLogic

superuser_bp = Blueprint('superuser', __name__, url_prefix='/super')


def superuser_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash('Authentication required', 'error')
            return redirect(url_for('auth.login'))
        # find token in logbook
        
        token = session.get('token')
        logbook_page = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        if not logbook_page or logbook_page.is_timed_out():
            session.pop('token', None)
            flash('Session expired. Please log in again.', 'error')
            return redirect(url_for('auth.login'))
        
        user = logbook_page.user
        if not user or 'superuser' not in [role.name for role in user.role_list]:
            flash('Superuser access required', 'error')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)
    return decorated_function


@superuser_bp.route('/')
@superuser_bp.route('/dashboard')
@superuser_required
def dashboard():
    """
    Super User dashboard - main landing page for super users.
    Shows system overview and quick access to management tools.
    """
    user_context = UserLogic.get_context(view_as='superuser')

    print("*"*80)
    
    # Get system stats
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_roles = Role.query.count()
    total_course_templates = CourseTemplate.query.count()
    total_courses = Course.query.count()
    
    # Get recent users
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_users = User.query.filter(
        User.created_at >= week_ago
    ).order_by(User.created_at.desc()).limit(5).all()
    
    context = {
        **user_context,
        'total_users': total_users,
        'active_users': active_users,
        'total_roles': total_roles,
        'total_course_templates': total_course_templates,
        'total_courses': total_courses,
        'recent_users': recent_users,
        'page_title': 'Super User Dashboard'
    }
    
    return render_template('private/superuser/dashboard/index.html', **context)


@superuser_bp.route('/user-management', methods=['GET', 'POST'])
@superuser_required
def user_management():
    """Manage users in the system"""
    if request.method == 'POST':
        # Handle user management actions
        pass
    
    # Get filters from query parameters
    role_filter = request.args.get('role', None)
    status_filter = request.args.get('status', 'active')  # Default to active users
    
    # Get all users for display
    if role_filter:
        # Filter users by role
        role = Role.get_by_name(role_filter)
        if role:
            all_users = role.users_list
            # Get users NOT in this role
            users_not_in_role = [u for u in User.get_all() if role not in u.role_list]
        else:
            all_users = User.get_all()
            users_not_in_role = []
    else:
        all_users = User.get_all()
        users_not_in_role = []
    
    # Apply status filter
    if status_filter == 'active':
        all_users = [u for u in all_users if u.is_active]
        users_not_in_role = [u for u in users_not_in_role if u.is_active]
    elif status_filter == 'inactive':
        all_users = [u for u in all_users if not u.is_active]
        users_not_in_role = [u for u in users_not_in_role if not u.is_active]
    # 'all' status filter shows both active and inactive
    
    # Get all available roles for filter buttons
    all_roles = Role.get_all_roles()
    
    user_context = UserLogic.get_context(view_as='superuser')
    context = {
        **user_context,
        'all_users': all_users,
        'all_roles': all_roles,
        'current_role_filter': role_filter,
        'current_status_filter': status_filter,
        'users_not_in_role': users_not_in_role
    }
    return render_template('private/superuser/user_management/index.html', **context)


@superuser_bp.route('/user-management/add-to-role', methods=['POST'])
@superuser_required
def add_user_to_role():
    """Add a user to a specific role"""
    # Get form data instead of JSON
    user_id = request.form.get('user_id')
    role_name = request.form.get('role_name')
    
    if not user_id or not role_name:
        flash('Missing user or role information', 'error')
        return redirect(url_for('superuser.user_management', role=role_name))
    
    # Get the role
    role = Role.get_by_name(role_name)
    if not role:
        flash('Role not found', 'error')
        return redirect(url_for('superuser.user_management'))
    
    # Get the user
    user = User.get_by_id(int(user_id))
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('superuser.user_management', role=role_name))
    
    # Check if user already has this role
    if role in user.role_list:
        flash(f'User {user.username} already has the {role_name} role', 'warning')
        return redirect(url_for('superuser.user_management', role=role_name))
    
    # Assign the role
    try:
        UserHasRoles.assign_role(int(user_id), role.id)
        
        # If role is student, create student profile if it doesn't exist
        if role_name == 'student':
            from src.logic.student_logic import StudentLogic
            if not StudentLogic.get_student_profile(int(user_id)):
                try:
                    StudentLogic.create_student_profile(int(user_id))
                except Exception as e:
                    flash(f'Warning: Student profile creation failed: {str(e)}', 'warning')
        
        flash(f'Successfully added {user.username} to {role_name} role', 'success')
    except Exception as e:
        flash(f'Error adding user to role: {str(e)}', 'error')
    
    return redirect(url_for('superuser.user_management', role=role_name))


@superuser_bp.route('/user-management/create-user', methods=['POST'])
@superuser_required
def create_user():
    """Create a new user"""
    # Get form data
    data = {
        'username': request.form.get('username'),
        'email': request.form.get('email'),
        'first_name': request.form.get('first_name'),
        'last_name': request.form.get('last_name'),
        'password': request.form.get('password'),
        'confirm_password': request.form.get('confirm_password'),
        'role_name': request.form.get('role_name')
    }
    
    try:
        # Use UserLogic to create the user with full validation
        user = UserLogic.create_user(data)
        flash(f'Successfully created user: {user.username}', 'success')
    except ValueError as e:
        flash(f'Error creating user: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error creating user: {str(e)}', 'error')
    
    # Preserve filters when redirecting
    role_filter = request.args.get('role')
    status_filter = request.args.get('status', 'active')
    return redirect(url_for('superuser.user_management', role=role_filter, status=status_filter))


@superuser_bp.route('/user-management/remove-from-role', methods=['POST'])
@superuser_required
def remove_user_from_role():
    """Remove a user from a specific role"""
    user_id = request.form.get('user_id')
    role_name = request.form.get('role_name')
    
    if not user_id or not role_name:
        flash('Missing user or role information', 'error')
        return redirect(url_for('superuser.user_management', role=role_name))
    
    # Get the role
    role = Role.get_by_name(role_name)
    if not role:
        flash('Role not found', 'error')
        return redirect(url_for('superuser.user_management'))
    
    # Get the user
    user = User.get_by_id(int(user_id))
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('superuser.user_management', role=role_name))
    
    # Check if user has this role
    if role not in user.role_list:
        flash(f'User {user.username} does not have the {role_name} role', 'warning')
        return redirect(url_for('superuser.user_management', role=role_name))
    
    # Remove the role
    try:
        UserHasRoles.remove_role(int(user_id), role.id)
        flash(f'Successfully removed {user.username} from {role_name} role', 'success')
    except Exception as e:
        flash(f'Error removing user from role: {str(e)}', 'error')
    
    return redirect(url_for('superuser.user_management', role=role_name))

@superuser_bp.route('/user-management/deactivate-user', methods=['POST'])
@superuser_required
def deactivate_user():
    """Deactivate a user account"""
    user_id = request.form.get('user_id')
    
    if not user_id:
        flash('Missing user information', 'error')
        return redirect(url_for('superuser.user_management'))
    
    # Get the user
    user = User.get_by_id(int(user_id))
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('superuser.user_management'))
    
    # Deactivate the user
    try:
        User.deactivate(user.id)
        flash(f'Successfully deactivated user {user.username}', 'success')
    except Exception as e:
        flash(f'Error deactivating user: {str(e)}', 'error')
    
    return redirect(url_for('superuser.user_management'))


@superuser_bp.route('/user-management/reactivate-user', methods=['POST'])
@superuser_required
def reactivate_user():
    """Reactivate a user account"""
    user_id = request.form.get('user_id')
    
    if not user_id:
        flash('Missing user information', 'error')
        return redirect(url_for('superuser.user_management'))
    
    # Get the user
    user = User.get_by_id(int(user_id))
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('superuser.user_management'))
    
    # Reactivate the user
    try:
        User.activate(user.id)
        flash(f'Successfully reactivated user {user.username}', 'success')
    except Exception as e:
        flash(f'Error reactivating user: {str(e)}', 'error')
    
    return redirect(url_for('superuser.user_management'))


@superuser_bp.route('/system-settings', methods=['GET', 'POST'])
@superuser_required
def system_settings():
    """Configure system-wide settings"""
    if request.method == 'POST':
        # Handle settings update
        pass
    
    # Get current settings
    email_settings = SettingsLogic.get_settings_by_category('email')
    
    context = UserLogic.get_context(view_as='superuser')
    context.update({
        'page_title': 'System Settings',
        'settings': email_settings  # Pass email settings to the template
    })
    return render_template('private/superuser/system_settings/index.html', **context)


# ============================================================================
# STUDENT MANAGEMENT ROUTES (Super User has full access)
# ============================================================================

@superuser_bp.route('/students')
@superuser_required
def students_list():
    """
    Display list of all students (super user has full access).
    """
    from src.models.student_profile import StudentProfile
    from src.models.user import User
    
    context = UserLogic.get_context(view_as='superuser')
    
    # Get all student profiles with user information
    students = StudentProfile.query.join(User).order_by(User.last_name, User.first_name).all()
    
    context.update({
        'students': students,
        'page_title': 'Student Management'
    })
    
    return render_template('private/superuser/students/list.html', **context)


@superuser_bp.route('/students/<int:student_id>')
@superuser_required
def student_detail(student_id):
    """
    Display detailed information about a student.
    Super user has full access to all student information.
    
    Args:
        student_id: StudentProfile ID (not User ID)
    """
    from src.logic.student_logic import StudentLogic
    from src.models.student_profile import StudentProfile
    
    context = UserLogic.get_context(view_as='superuser')
    
    # Get student profile
    student = StudentProfile.query.get_or_404(student_id)
    
    # Get all enrollments for this student
    enrollments = StudentLogic.get_student_courses(student_id)
    
    # Calculate GPA
    gpa = StudentLogic.calculate_student_gpa(student_id)
    
    context.update({
        'student': student,
        'enrollments': enrollments,
        'gpa': gpa,
        'page_title': f'Student: {student.user.first_name} {student.user.last_name}'
    })
    
    return render_template('private/superuser/students/detail.html', **context)


@superuser_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@superuser_required
def edit_student(student_id):
    """
    Edit student profile information (super user access).
    
    Args:
        student_id: StudentProfile ID (not User ID)
    """
    from src.logic.student_logic import StudentLogic
    from src.models.student_profile import StudentProfile
    
    student = StudentProfile.query.get_or_404(student_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            update_data = {
                'student_number': request.form.get('student_number'),
                'grade_level': request.form.get('grade_level'),
                'emergency_contact_name': request.form.get('emergency_contact_name'),
                'emergency_contact_phone': request.form.get('emergency_contact_phone')
            }
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            # Update student profile
            StudentLogic.update_student_profile(student_id, update_data)
            
            flash('Student profile updated successfully', 'success')
            return redirect(url_for('superuser.student_detail', student_id=student_id))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Failed to update student profile: {str(e)}', 'error')
    
    # GET request - display form
    context = UserLogic.get_context(view_as='superuser')
    
    context.update({
        'student': student,
        'page_title': f'Edit Student: {student.user.first_name} {student.user.last_name}'
    })
    
    return render_template('private/superuser/students/edit.html', **context)


# ============================================================================
# Flask Mail Integration
# ============================================================================

from flask import jsonify


@superuser_bp.route('/settings/email', methods=['GET'])
@superuser_required
def email_settings():
    """Display email settings page."""
    settings = SettingsLogic.get_settings_by_category('email')
    context = UserLogic.get_context(view_as='superuser')
    context.update({
        'settings': settings,
        'page_title': 'Email Settings'
    })
    return render_template('private/superuser/email_settings.html', **context)

@superuser_bp.route('/settings/email', methods=['POST'])
@superuser_required
def update_email_settings():
    """Update email settings."""
    # Get form data
    data = request.form.to_dict()
    
    for key, value in data.items():
        if key.startswith('mail_'):
            is_encrypted = key == 'mail_password'
            # Skip empty password fields (don't update if blank)
            if key == 'mail_password' and not value:
                continue
            SettingsLogic.set_setting(key, value, category='email', is_encrypted=is_encrypted)
    
    # Reload mail config
    mail_config = SettingsLogic.get_flask_mail_config()
    current_app.config.update(mail_config)
    
    flash('Email settings updated successfully', 'success')
    # super/system-settings#email
    return redirect(url_for('superuser.system_settings', ))

@superuser_bp.route('/settings/email/test', methods=['POST'])
@superuser_required
def test_email_settings():
    """Test email configuration by sending a test email using EmailLogic."""
    try:
        from src.logic.email_logic import EmailLogic
        
        current_app.logger.info('Starting test email process...')
        
        # Get current user from session
        token = session.get('token')
        logbook_page = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        user = logbook_page.user if logbook_page else None
        
        if not user or not user.email:
            current_app.logger.error('User validation failed - no valid email found')
            return jsonify({'error': 'No valid email address found for current user'}), 400
        
        # Get the configured default sender for the test recipient
        mail_config = SettingsLogic.get_flask_mail_config()
        test_recipient = mail_config.get('MAIL_DEFAULT_SENDER')
        
        if not test_recipient:
            return jsonify({'error': 'MAIL_DEFAULT_SENDER is not configured. Please set it in email settings.'}), 400
        
        # Use EmailLogic to send test email
        current_app.logger.info(f'Sending test email to: {test_recipient}')
        
        EmailLogic.send_test_email(
            recipient_email=test_recipient,
            test_message='If you received this message, your email settings are properly configured!'
        )
        
        current_app.logger.info('Test email sent successfully!')
        return jsonify({'message': f'Test email sent successfully to {test_recipient}'})
        
    except ValueError as e:
        # Handle validation errors (missing template, etc.)
        current_app.logger.error(f'Validation error: {str(e)}')
        return jsonify({'error': str(e)}), 400
        
    except ConnectionRefusedError as e:
        current_app.logger.error(f'SMTP connection refused: {str(e)}', exc_info=True)
        return jsonify({'error': 'Cannot connect to email server. Please verify your MAIL_SERVER and MAIL_PORT settings are correct and the server is accessible.'}), 500
        
    except Exception as e:
        current_app.logger.error(f'Error sending test email: {str(e)}', exc_info=True)
        
        # Provide more helpful error messages for common issues
        error_msg = str(e)
        if 'authentication' in error_msg.lower():
            error_msg = 'Email authentication failed. Please check your MAIL_USERNAME and MAIL_PASSWORD.'
        elif 'timeout' in error_msg.lower():
            error_msg = 'Connection to email server timed out. Please check your MAIL_SERVER and network settings.'
        else:
            error_msg = f'Failed to send test email: {error_msg}'
            
        return jsonify({'error': error_msg}), 500


# ============================================================================
# REFUND MANAGEMENT ROUTES
# ============================================================================

@superuser_bp.route('/refund-requests')
@superuser_required
def refund_requests():
    """
    Display all refund requests for superuser review.
    Shows pending, approved, denied, and processed refunds.
    """
    from src.logic.payment_logic import PaymentLogic
    from src.models.payment_models import Refund
    
    user_context = UserLogic.get_context(view_as='superuser')
    
    # Get all refund requests, grouped by status
    pending_refunds = Refund.query.filter_by(status='requested').order_by(Refund.request_date.desc()).all()
    processed_refunds = Refund.query.filter(Refund.status.in_(['approved', 'denied', 'processed'])).order_by(Refund.refund_date.desc()).limit(50).all()
    
    context = {
        **user_context,
        'pending_refunds': pending_refunds,
        'processed_refunds': processed_refunds,
        'page_title': 'Refund Requests Management'
    }
    
    return render_template('private/superuser/refund_requests.html', **context)


@superuser_bp.route('/refund-requests/<int:refund_id>/approve', methods=['POST'])
@superuser_required
def approve_refund(refund_id):
    """
    Approve a refund request.
    """
    from src.logic.payment_logic import PaymentLogic, PaymentValidationError
    
    try:
        # Get current superuser
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        
        if not logbook_entry or not logbook_entry.user_id:
            return jsonify({'success': False, 'message': 'Session expired'}), 401
        
        # Get form data
        data = request.get_json()
        refund_method = data.get('refund_method', 'stripe')
        admin_notes = data.get('admin_notes', '').strip()
        
        # Approve refund
        refund = PaymentLogic.approve_refund_request(
            refund_id=refund_id,
            superuser_id=logbook_entry.user_id,
            refund_method=refund_method,
            admin_notes=admin_notes
        )
        
        return jsonify({
            'success': True,
            'message': 'Refund approved and processed successfully',
            'refund_id': refund.id
        })
        
    except PaymentValidationError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error approving refund: {str(e)}'}), 500


@superuser_bp.route('/refund-requests/<int:refund_id>/deny', methods=['POST'])
@superuser_required
def deny_refund(refund_id):
    """
    Deny a refund request.
    """
    from src.logic.payment_logic import PaymentLogic, PaymentValidationError
    
    try:
        # Get current superuser
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        
        if not logbook_entry or not logbook_entry.user_id:
            return jsonify({'success': False, 'message': 'Session expired'}), 401
        
        # Get form data
        data = request.get_json()
        admin_notes = data.get('admin_notes', '').strip()
        
        if not admin_notes:
            return jsonify({'success': False, 'message': 'Admin notes are required when denying a refund'}), 400
        
        # Deny refund
        refund = PaymentLogic.deny_refund_request(
            refund_id=refund_id,
            superuser_id=logbook_entry.user_id,
            admin_notes=admin_notes
        )
        
        return jsonify({
            'success': True,
            'message': 'Refund request denied',
            'refund_id': refund.id
        })
        
    except PaymentValidationError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error denying refund: {str(e)}'}), 500
