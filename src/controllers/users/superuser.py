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
    focus = request.args.get('focus', 'superuser')
    all_users = users.User.query.all()
    context = {
        'users': all_users,
        'current_user': Doorman.get_by_token(session['doorman_token']).user,
        'focus': focus
    }
    return render_template('private/superusers/users/index.html', **context)

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
                
                # Log the settings change
                Log.create_log(
                    log_type=Log.TYPE_USER_ACTION,
                    action='update_email_settings',
                    description='Email settings updated',
                    user_id=current_user.id,
                    status='success',
                    extra_data={'updated_fields': ['email_configuration']}
                )
                
                flash('Email settings updated successfully!', 'success')
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