from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from functools import wraps
from src.models.logbook import Logbook
from src.logic.user_logic import UserLogic
from src.models.user import User
from src.models.roles import Role, UserHasRoles
from src.models.courses_model import Course, CourseTemplate
from src.logic.setting_logic import SettingsLogic

super_user_bp = Blueprint('super_user', __name__, url_prefix='/super')


def super_user_required(f):
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
        if not user or 'super-user' not in [role.name for role in user.role_list]:
            flash('Super-user access required', 'error')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)
    return decorated_function


@super_user_bp.route('/user-management', methods=['GET', 'POST'])
@super_user_required
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
    
    user_context = UserLogic.get_context(view_as='super-user')
    context = {
        **user_context,
        'all_users': all_users,
        'all_roles': all_roles,
        'current_role_filter': role_filter,
        'current_status_filter': status_filter,
        'users_not_in_role': users_not_in_role
    }
    return render_template('private/super_user/user_management/index.html', **context)


@super_user_bp.route('/user-management/add-to-role', methods=['POST'])
@super_user_required
def add_user_to_role():
    """Add a user to a specific role"""
    # Get form data instead of JSON
    user_id = request.form.get('user_id')
    role_name = request.form.get('role_name')
    
    if not user_id or not role_name:
        flash('Missing user or role information', 'error')
        return redirect(url_for('super_user.user_management', role=role_name))
    
    # Get the role
    role = Role.get_by_name(role_name)
    if not role:
        flash('Role not found', 'error')
        return redirect(url_for('super_user.user_management'))
    
    # Get the user
    user = User.get_by_id(int(user_id))
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('super_user.user_management', role=role_name))
    
    # Check if user already has this role
    if role in user.role_list:
        flash(f'User {user.username} already has the {role_name} role', 'warning')
        return redirect(url_for('super_user.user_management', role=role_name))
    
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
    
    return redirect(url_for('super_user.user_management', role=role_name))


@super_user_bp.route('/user-management/create-user', methods=['POST'])
@super_user_required
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
    return redirect(url_for('super_user.user_management', role=role_filter, status=status_filter))


@super_user_bp.route('/user-management/remove-from-role', methods=['POST'])
@super_user_required
def remove_user_from_role():
    """Remove a user from a specific role"""
    user_id = request.form.get('user_id')
    role_name = request.form.get('role_name')
    
    if not user_id or not role_name:
        flash('Missing user or role information', 'error')
        return redirect(url_for('super_user.user_management', role=role_name))
    
    # Get the role
    role = Role.get_by_name(role_name)
    if not role:
        flash('Role not found', 'error')
        return redirect(url_for('super_user.user_management'))
    
    # Get the user
    user = User.get_by_id(int(user_id))
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('super_user.user_management', role=role_name))
    
    # Check if user has this role
    if role not in user.role_list:
        flash(f'User {user.username} does not have the {role_name} role', 'warning')
        return redirect(url_for('super_user.user_management', role=role_name))
    
    # Remove the role
    try:
        UserHasRoles.remove_role(int(user_id), role.id)
        flash(f'Successfully removed {user.username} from {role_name} role', 'success')
    except Exception as e:
        flash(f'Error removing user from role: {str(e)}', 'error')
    
    return redirect(url_for('super_user.user_management', role=role_name))

@super_user_bp.route('/user-management/deactivate-user', methods=['POST'])
@super_user_required
def deactivate_user():
    """Deactivate a user account"""
    user_id = request.form.get('user_id')
    
    if not user_id:
        flash('Missing user information', 'error')
        return redirect(url_for('super_user.user_management'))
    
    # Get the user
    user = User.get_by_id(int(user_id))
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('super_user.user_management'))
    
    # Deactivate the user
    try:
        User.deactivate(user.id)
        flash(f'Successfully deactivated user {user.username}', 'success')
    except Exception as e:
        flash(f'Error deactivating user: {str(e)}', 'error')
    
    return redirect(url_for('super_user.user_management'))


@super_user_bp.route('/user-management/reactivate-user', methods=['POST'])
@super_user_required
def reactivate_user():
    """Reactivate a user account"""
    user_id = request.form.get('user_id')
    
    if not user_id:
        flash('Missing user information', 'error')
        return redirect(url_for('super_user.user_management'))
    
    # Get the user
    user = User.get_by_id(int(user_id))
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('super_user.user_management'))
    
    # Reactivate the user
    try:
        User.activate(user.id)
        flash(f'Successfully reactivated user {user.username}', 'success')
    except Exception as e:
        flash(f'Error reactivating user: {str(e)}', 'error')
    
    return redirect(url_for('super_user.user_management'))


@super_user_bp.route('/course-management', methods=['GET', 'POST'])
@super_user_required
def course_management():
    """Manage courses in the system"""
    # Get all course templates for display
    user_context = UserLogic.get_context(view_as='super-user')
    
    # Get all course templates using the model method
    from src.models.courses_model import CourseTemplate
    all_templates = CourseTemplate.query.all()
    
    context = {
        **user_context,
        'all_courses': all_templates  
    }
    return render_template('private/super_user/course_management/index.html', **context)


@super_user_bp.route('/course-management/create-template', methods=['POST'])
@super_user_required
def create_course_template():
    """Create a new course template"""
    from src.logic.course_logic import CourseTemplateLogic, CourseValidationError, CourseBusinessError
    
    # Get form data
    data = {
        'name': request.form.get('name'),
        'description': request.form.get('description', ''),
        'duration_days': int(request.form.get('duration_days', 1)),
        'experience_level': request.form.get('experience_level'),
        'is_active': True
    }
    
    try:
        template = CourseTemplateLogic.create_template(data)
        flash(f'Successfully created course template: {template.name}', 'success')
    except (CourseValidationError, CourseBusinessError) as e:
        flash(f'Error creating template: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    return redirect(url_for('super_user.course_management'))


@super_user_bp.route('/course-management/update-template', methods=['POST'])
@super_user_required
def update_course_template():
    """Update an existing course template"""
    from src.logic.course_logic import CourseTemplateLogic, CourseValidationError, CourseBusinessError
    
    template_id = request.form.get('template_id')
    
    if not template_id:
        flash('Missing template ID', 'error')
        return redirect(url_for('super_user.course_management'))
    
    # Get form data
    data = {
        'name': request.form.get('name'),
        'description': request.form.get('description', ''),
        'duration_days': int(request.form.get('duration_days', 1)),
        'experience_level': request.form.get('experience_level')
    }
    
    try:
        template = CourseTemplateLogic.update_template(int(template_id), data)
        flash(f'Successfully updated course template: {template.name}', 'success')
    except (CourseValidationError, CourseBusinessError) as e:
        flash(f'Error updating template: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    return redirect(url_for('super_user.course_management'))


@super_user_bp.route('/course-management/deactivate-template', methods=['POST'])
@super_user_required
def deactivate_course_template():
    """Deactivate a course template"""
    from src.logic.course_logic import CourseTemplateLogic, CourseBusinessError
    
    template_id = request.form.get('template_id')
    
    if not template_id:
        flash('Missing template ID', 'error')
        return redirect(url_for('super_user.course_management'))
    
    try:
        template = CourseTemplateLogic.deactivate_template(int(template_id))
        flash(f'Successfully deactivated course template: {template.name}', 'success')
    except CourseBusinessError as e:
        flash(f'Error deactivating template: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    return redirect(url_for('super_user.course_management'))


@super_user_bp.route('/course-management/activate-template', methods=['POST'])
@super_user_required
def activate_course_template():
    """Activate a course template"""
    from src.logic.course_logic import CourseTemplateLogic, CourseBusinessError
    
    template_id = request.form.get('template_id')
    
    if not template_id:
        flash('Missing template ID', 'error')
        return redirect(url_for('super_user.course_management'))
    
    try:
        template = CourseTemplateLogic.get_template(int(template_id))
        template.is_active = True
        from src.models import db
        db.session.commit()
        flash(f'Successfully activated course template: {template.name}', 'success')
    except CourseBusinessError as e:
        flash(f'Error activating template: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    return redirect(url_for('super_user.course_management'))


@super_user_bp.route('/system-settings', methods=['GET', 'POST'])
@super_user_required
def system_settings():
    """Configure system-wide settings"""
    if request.method == 'POST':
        # Handle settings update
        pass
    
    # Get current settings
    context = UserLogic.get_context(view_as='super-user')
    context.update({
        'page_title': 'System Settings',
        'main_container': SettingsLogic.get_settings_by_category('email')
    })
    return render_template('private/super_user/system_settings/index.html', **context)


# ============================================================================
# STUDENT MANAGEMENT ROUTES (Super User has full access)
# ============================================================================

@super_user_bp.route('/students')
@super_user_required
def students_list():
    """
    Display list of all students (super user has full access).
    """
    from src.models.student_profile import StudentProfile
    from src.models.user import User
    
    context = UserLogic.get_context(view_as='super-user')
    
    # Get all student profiles with user information
    students = StudentProfile.query.join(User).order_by(User.last_name, User.first_name).all()
    
    context.update({
        'students': students,
        'page_title': 'Student Management'
    })
    
    return render_template('private/super_user/students/list.html', **context)


@super_user_bp.route('/students/<int:student_id>')
@super_user_required
def student_detail(student_id):
    """
    Display detailed information about a student.
    Super user has full access to all student information.
    
    Args:
        student_id: StudentProfile ID (not User ID)
    """
    from src.logic.student_logic import StudentLogic
    from src.models.student_profile import StudentProfile
    
    context = UserLogic.get_context(view_as='super-user')
    
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
    
    return render_template('private/super_user/students/detail.html', **context)


@super_user_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@super_user_required
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
            return redirect(url_for('super_user.student_detail', student_id=student_id))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Failed to update student profile: {str(e)}', 'error')
    
    # GET request - display form
    context = UserLogic.get_context(view_as='super-user')
    
    context.update({
        'student': student,
        'page_title': f'Edit Student: {student.user.first_name} {student.user.last_name}'
    })
    
    return render_template('private/super_user/students/edit.html', **context)


# ============================================================================
# Flask Mail Integration
# ============================================================================

from flask import jsonify


@super_user_bp.route('/settings/email', methods=['GET'])
@super_user_required
def email_settings():
    """Display email settings page."""
    settings = SettingsLogic.get_settings_by_category('email')
    context = UserLogic.get_context(view_as='super-user')
    context.update({
        'settings': settings,
        'page_title': 'Email Settings'
    })
    return render_template('private/super_user/email_settings.html', **context)

@super_user_bp.route('/settings/email', methods=['POST'])
@super_user_required
def update_email_settings():
    """Update email settings."""
    data = request.get_json()
    
    for key, value in data.items():
        if key.startswith('mail_'):
            is_encrypted = key == 'mail_password'
            SettingsLogic.set_setting(key, value, category='email', is_encrypted=is_encrypted)
    
    # Reload mail config
    mail_config = SettingsLogic.get_flask_mail_config()
    current_app.config.update(mail_config)
    
    return jsonify({'message': 'Settings updated successfully'})

@super_user_bp.route('/settings/email/test', methods=['POST'])
@super_user_required
def test_email_settings():
    """Test email configuration."""
    try:
        from flask_mail import Message
        from run import mail  # Import mail from main app
        
        msg = Message(
            subject='Test Email',
            recipients=[SettingsLogic.get_setting('mail_default_sender')],
            body='This is a test email.'
        )
        mail.send(msg)
        return jsonify({'message': 'Test email sent successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500