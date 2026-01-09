from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from src.models.user_folder import superusers, users
from src.models.doorman import Doorman
from src.models.logs import Log
from src.utils.custom_decorators import login_required, role_required

# Create blueprint
superuser_bp = Blueprint('superuser', __name__, url_prefix='/superuser')

@superuser_bp.route('/dashboard')
@login_required
@role_required('superuser')
def dashboard():
    """superuser dashboard route."""
    context = {
        'current_user': Doorman.get_by_token(session['doorman_token']).user
    }
    return render_template('private/superusers/dashboard/index.html', **context)


@superuser_bp.route('/set-superuser/<int:user_id>/<status>', methods=['GET', 'POST'])
@login_required
@role_required('superuser')
def superuser_status(user_id, status='add'):
    """
        Route to set a user as a superuser.
    """
    user = users.User.query.get(user_id)
    if not user:
        return "User not found", 404

    if status == 'add':
        # Check if the user is already a superuser
        existing_superuser = superusers.Superuser.query.filter_by(user_id=user.id).first()
        if existing_superuser:
            return "User is already a superuser", 400

        # Create a new Superuser entry
        new_superuser = superusers.Superuser.create(user_id=user.id)

        # Log the action
        current_user = Doorman.get_by_token(session['doorman_token']).user
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='grant_superuser',
            description=f'Superuser privileges granted to {user.email}',
            user_id=current_user.id,
            target_type='user',
            target_id=user.id,
            status='success',
            extra_data={
                'target_email': user.email,
                'target_user_id': user.id,
                'superuser_id': new_superuser.id
            }
        )

        return redirect(url_for('superuser.dashboard'))

    if status == 'remove':
        # Find the superuser entry
        existing_superuser = superusers.Superuser.query.filter_by(user_id=user.id).first()
        if not existing_superuser:
            return "User is not a superuser", 400

        # Delete the superuser entry
        existing_superuser.delete()

        # Log the action
        current_user = Doorman.get_by_token(session['doorman_token']).user
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='revoke_superuser',
            description=f'Superuser privileges revoked from {user.email}',
            user_id=current_user.id,
            target_type='user',
            target_id=user.id,
            status='success',
            extra_data={
                'target_email': user.email,
                'target_user_id': user.id
            }
        )

        return redirect(url_for('auth.dashboard'))

@superuser_bp.route('/manage-users')
@login_required
@role_required('superuser')
def manage_users():
    """Route to manage users."""
    focus = request.args.get('focus', 'all')
    all_users = users.User.query.all()
    
    # Count users by role
    role_counts = {
        'all': len(all_users),
        'student': sum(1 for u in all_users if u.is_student),
        'instructor': sum(1 for u in all_users if u.is_instructor),
        'admin': sum(1 for u in all_users if u.is_admin),
        'superuser': sum(1 for u in all_users if u.is_superuser)
    }
    
    context = {
        'users': all_users,
        'current_user': Doorman.get_by_token(session['doorman_token']).user,
        'focus': focus,
        'role_counts': role_counts
    }
    return render_template('private/superusers/users/index.html', **context)

@superuser_bp.route('/manage-user-roles/<int:user_id>')
@login_required
@role_required('superuser')
def manage_user_roles(user_id):
    """Route to view and manage roles for a specific user."""
    user = users.User.query.get_or_404(user_id)
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    # Get current roles
    current_roles = user.get_roles()
    
    # Define available roles
    available_roles = ['student', 'instructor', 'admin', 'superuser']
    
    context = {
        'user': user,
        'current_user': current_user,
        'current_roles': current_roles,
        'available_roles': available_roles
    }
    return render_template('private/superusers/users/manage_roles.html', **context)

@superuser_bp.route('/add-user-role/<int:user_id>/<role_name>', methods=['POST'])
@login_required
@role_required('superuser')
def add_user_role(user_id, role_name):
    """Add a role to a user."""
    from src.models.user_folder.students import Student
    from src.models.user_folder.instructors import Instructor
    from src.models.user_folder.admins import Admin
    from src.models.user_folder.superusers import Superuser
    
    user = users.User.query.get_or_404(user_id)
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    # Validate role name
    valid_roles = ['student', 'instructor', 'admin', 'superuser']
    if role_name not in valid_roles:
        flash(f'Invalid role: {role_name}', 'danger')
        return redirect(url_for('superuser.manage_user_roles', user_id=user_id))
    
    # Check if user already has this role
    if user.has_role_by_name(role_name):
        flash(f'User already has {role_name} role', 'warning')
        return redirect(url_for('superuser.manage_user_roles', user_id=user_id))
    
    try:
        # Add the role based on role_name
        if role_name == 'student':
            Student.create(
                user_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                phone_number=user.phone_number
            )
        elif role_name == 'instructor':
            Instructor.create(user_id=user.id)
        elif role_name == 'admin':
            Admin.create(user_id=user.id)
        elif role_name == 'superuser':
            Superuser.create(user_id=user.id)
        
        # Log the action
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action=f'add_{role_name}_role',
            description=f'{role_name.capitalize()} role added to {user.email}',
            user_id=current_user.id,
            target_type='user',
            target_id=user.id,
            status='success',
            extra_data={
                'target_email': user.email,
                'role_added': role_name
            }
        )
        
        flash(f'{role_name.capitalize()} role added successfully', 'success')
    except Exception as e:
        flash(f'Error adding role: {str(e)}', 'danger')
    
    return redirect(url_for('superuser.manage_user_roles', user_id=user_id))

@superuser_bp.route('/remove-user-role/<int:user_id>/<role_name>', methods=['POST'])
@login_required
@role_required('superuser')
def remove_user_role(user_id, role_name):
    """Remove a role from a user."""
    from src.models.user_folder.students import Student
    from src.models.user_folder.instructors import Instructor
    from src.models.user_folder.admins import Admin
    from src.models.user_folder.superusers import Superuser
    
    user = users.User.query.get_or_404(user_id)
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    # Validate role name
    valid_roles = ['student', 'instructor', 'admin', 'superuser']
    if role_name not in valid_roles:
        flash(f'Invalid role: {role_name}', 'danger')
        return redirect(url_for('superuser.manage_user_roles', user_id=user_id))
    
    # Check if user has this role
    if not user.has_role_by_name(role_name):
        flash(f'User does not have {role_name} role', 'warning')
        return redirect(url_for('superuser.manage_user_roles', user_id=user_id))
    
    # Prevent removing last role
    if len(user.get_roles()) == 1:
        flash('Cannot remove the last role from a user', 'danger')
        return redirect(url_for('superuser.manage_user_roles', user_id=user_id))
    
    try:
        # Remove the role based on role_name
        if role_name == 'student':
            role_record = Student.query.filter_by(user_id=user.id).first()
        elif role_name == 'instructor':
            role_record = Instructor.query.filter_by(user_id=user.id).first()
        elif role_name == 'admin':
            role_record = Admin.query.filter_by(user_id=user.id).first()
        elif role_name == 'superuser':
            role_record = Superuser.query.filter_by(user_id=user.id).first()
        
        if role_record:
            role_record.delete()
            
            # Log the action
            Log.create_log(
                log_type=Log.TYPE_USER_ACTION,
                action=f'remove_{role_name}_role',
                description=f'{role_name.capitalize()} role removed from {user.email}',
                user_id=current_user.id,
                target_type='user',
                target_id=user.id,
                status='success',
                extra_data={
                    'target_email': user.email,
                    'role_removed': role_name
                }
            )
            
            flash(f'{role_name.capitalize()} role removed successfully', 'success')
        else:
            flash(f'Role record not found', 'danger')
    except Exception as e:
        flash(f'Error removing role: {str(e)}', 'danger')
    
    return redirect(url_for('superuser.manage_user_roles', user_id=user_id))

@superuser_bp.route('/add-user-to-role/<role_name>', methods=['GET', 'POST'])
@login_required
@role_required('superuser')
def add_user_to_role(role_name):
    """Add a user to a specific role."""
    from src.models.user_folder.students import Student
    from src.models.user_folder.instructors import Instructor
    from src.models.user_folder.admins import Admin
    from src.models.user_folder.superusers import Superuser
    
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    # Validate role name
    valid_roles = ['student', 'instructor', 'admin', 'superuser']
    if role_name not in valid_roles:
        flash(f'Invalid role: {role_name}', 'danger')
        return redirect(url_for('superuser.manage_users'))
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        
        if not user_id:
            flash('Please select a user', 'warning')
            return redirect(url_for('superuser.add_user_to_role', role_name=role_name))
        
        user = users.User.query.get_or_404(user_id)
        
        # Check if user already has this role
        if user.has_role_by_name(role_name):
            flash(f'{user.full_name} already has {role_name} role', 'warning')
            return redirect(url_for('superuser.add_user_to_role', role_name=role_name))
        
        try:
            # Add the role based on role_name
            if role_name == 'student':
                Student.create(
                    user_id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    phone_number=user.phone_number
                )
            elif role_name == 'instructor':
                Instructor.create(user_id=user.id)
            elif role_name == 'admin':
                Admin.create(user_id=user.id)
            elif role_name == 'superuser':
                Superuser.create(user_id=user.id)
            
            # Log the action
            Log.create_log(
                log_type=Log.TYPE_USER_ACTION,
                action=f'add_{role_name}_role',
                description=f'{role_name.capitalize()} role added to {user.email}',
                user_id=current_user.id,
                target_type='user',
                target_id=user.id,
                status='success',
                extra_data={
                    'target_email': user.email,
                    'role_added': role_name
                }
            )
            
            flash(f'{role_name.capitalize()} role added to {user.full_name} successfully', 'success')
            return redirect(url_for('superuser.manage_users', focus=role_name))
        except Exception as e:
            flash(f'Error adding role: {str(e)}', 'danger')
            return redirect(url_for('superuser.add_user_to_role', role_name=role_name))
    
    # GET request - show form
    # Get users who don't have this role
    all_users = users.User.query.all()
    available_users = [u for u in all_users if not u.has_role_by_name(role_name)]
    
    context = {
        'current_user': current_user,
        'role_name': role_name,
        'available_users': available_users
    }
    return render_template('private/superusers/users/add_to_role.html', **context)

@superuser_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@role_required('superuser')
def settings():
    """Superuser settings page with multiple tabs."""
    from src.models.app_settings import AppSettings
    
    settings_obj = AppSettings.get_settings()
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    if request.method == 'POST':
        tab = request.form.get('tab', 'email')
        
        if tab == 'email':
            # Update email settings
            try:
                update_data = {
                    'mail_server': request.form.get('mail_server'),
                    'mail_port': int(request.form.get('mail_port', 587)),
                    'mail_use_tls': request.form.get('mail_use_tls') == '1',
                    'mail_use_ssl': request.form.get('mail_use_ssl') == '1',
                    'mail_username': request.form.get('mail_username'),
                    'mail_default_sender': request.form.get('mail_default_sender'),
                }
                
                # Only update password if a new one was provided
                mail_password = request.form.get('mail_password')
                if mail_password:  # If not empty
                    update_data['mail_password'] = mail_password
                
                AppSettings.update_settings(
                    updated_by_user_id=current_user.id,
                    **update_data
                )
                
                # Reload mail configuration without server restart
                from flask import current_app
                from src import reload_mail_config
                success, message = reload_mail_config(current_app._get_current_object())
                
                if success:
                    # Log the settings change
                    Log.create_log(
                        log_type=Log.TYPE_USER_ACTION,
                        action='update_email_settings',
                        description='Email settings updated and reloaded',
                        user_id=current_user.id,
                        status='success',
                        extra_data={'updated_fields': ['email_configuration']}
                    )
                    flash('Email settings updated and reloaded successfully!', 'success')
                else:
                    flash(f'Settings saved but reload failed: {message}', 'warning')
            except Exception as e:
                flash(f'Error updating settings: {str(e)}', 'danger')
            
            return redirect(url_for('superuser.settings', tab='email'))
    
    # Determine active tab from query param
    active_tab = request.args.get('tab', 'email')
    
    context = {
        'current_user': current_user,
        'settings': settings_obj,
        'active_tab': active_tab
    }
    return render_template('private/superusers/settings/index.html', **context)

# ------------------------------------------------------
# --------------------- API ROUTES ---------------------
# ------------------------------------------------------