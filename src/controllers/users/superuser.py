"""
Superuser controller for superuser-specific operations.

NOTE: Superuser privilege management (add/remove superuser status) has been moved to admin.py
This controller focuses on user management, role assignments, and system settings.
"""
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify, current_app
from src.models.doorman import Doorman
from src.models.app_settings import AppSettings
from src.utils.custom_decorators import login_required, role_required
from src.services import superuser_service

superuser_bp = Blueprint('superuser', __name__, url_prefix='/superuser')


def _get_current_user():
    """Get current user from session."""
    return Doorman.get_by_token(session['doorman_token']).user


@superuser_bp.route('/dashboard')
@login_required
@role_required('superuser')
def dashboard():
    """Superuser dashboard."""
    return render_template('private/superusers/dashboard/index.html',
                         current_user=_get_current_user())


@superuser_bp.route('/manage-users')
@login_required
@role_required('superuser')
def manage_users():
    """Manage all users with role filtering."""
    focus = request.args.get('focus', 'all')
    data = superuser_service.get_all_users_with_counts(focus)
    
    return render_template('private/superusers/users/index.html',
                         current_user=_get_current_user(),
                         **data)


@superuser_bp.route('/manage-user-roles/<int:user_id>')
@login_required
@role_required('superuser')
def manage_user_roles(user_id):
    """View and manage roles for a specific user."""
    try:
        data = superuser_service.get_user_roles_data(user_id)
        return render_template('private/superusers/users/manage_roles.html',
                             current_user=_get_current_user(),
                             **data)
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('superuser.manage_users'))


@superuser_bp.route('/add-user-role/<int:user_id>/<role_name>', methods=['POST'])
@login_required
@role_required('superuser')
def add_user_role(user_id, role_name):
    """Add a role to a user."""
    try:
        superuser_service.add_role_to_user(user_id, role_name, _get_current_user().id)
        flash(f'{role_name.capitalize()} role added successfully', 'success')
    except ValueError as e:
        flash(str(e), 'warning' if 'already has' in str(e) else 'danger')
    except Exception as e:
        flash(f'Error adding role: {str(e)}', 'danger')
    
    return redirect(url_for('superuser.manage_user_roles', user_id=user_id))


@superuser_bp.route('/remove-user-role/<int:user_id>/<role_name>', methods=['POST'])
@login_required
@role_required('superuser')
def remove_user_role(user_id, role_name):
    """Remove a role from a user."""
    try:
        superuser_service.remove_role_from_user(user_id, role_name, _get_current_user().id)
        flash(f'{role_name.capitalize()} role removed successfully', 'success')
    except ValueError as e:
        flash(str(e), 'warning' if 'does not have' in str(e) or 'Cannot remove' in str(e) else 'danger')
    except Exception as e:
        flash(f'Error removing role: {str(e)}', 'danger')
    
    return redirect(url_for('superuser.manage_user_roles', user_id=user_id))


@superuser_bp.route('/toggle-user-status/<int:user_id>', methods=['POST'])
@login_required
@role_required('superuser')
def toggle_user_status(user_id):
    """Toggle a user's active status (activate/deactivate)."""
    try:
        status_text = superuser_service.toggle_user_active_status(user_id, _get_current_user().id)
        flash(f'User account has been {status_text} successfully.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash(f'Error updating user status: {str(e)}', 'danger')
    
    focus = request.args.get('focus', 'all')
    return redirect(url_for('superuser.manage_users', focus=focus))


@superuser_bp.route('/add-user-to-role/<role_name>', methods=['GET', 'POST'])
@login_required
@role_required('superuser')
def add_user_to_role(role_name):
    """Add a user to a specific role."""
    try:
        superuser_service.get_users_without_role(role_name)  # Validate role name
    except ValueError as e:
        flash(str(e), 'danger')
        return redirect(url_for('superuser.manage_users'))
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if not user_id:
            flash('Please select a user', 'warning')
            return redirect(url_for('superuser.add_user_to_role', role_name=role_name))
        
        try:
            result = superuser_service.add_role_to_user(user_id, role_name, _get_current_user().id)
            flash(f'{role_name.capitalize()} role added to {result["user"].full_name} successfully', 'success')
            return redirect(url_for('superuser.manage_users', focus=role_name))
        except ValueError as e:
            flash(str(e), 'warning' if 'already has' in str(e) else 'danger')
            return redirect(url_for('superuser.add_user_to_role', role_name=role_name))
        except Exception as e:
            flash(f'Error adding role: {str(e)}', 'danger')
            return redirect(url_for('superuser.add_user_to_role', role_name=role_name))
    
    # GET - show form
    available_users = superuser_service.get_users_without_role(role_name)
    return render_template('private/superusers/users/add_to_role.html',
                         current_user=_get_current_user(),
                         role_name=role_name,
                         available_users=available_users)


@superuser_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@role_required('superuser')
def settings():
    """Superuser settings page with multiple tabs."""
    settings_obj = AppSettings.get_settings()
    
    if request.method == 'POST':
        tab = request.form.get('tab', 'email')
        
        if tab == 'email':
            try:
                update_data = {
                    'mail_server': request.form.get('mail_server'),
                    'mail_port': int(request.form.get('mail_port', 587)),
                    'mail_use_tls': request.form.get('mail_use_tls') == '1',
                    'mail_use_ssl': request.form.get('mail_use_ssl') == '1',
                    'mail_username': request.form.get('mail_username'),
                    'mail_default_sender': request.form.get('mail_default_sender'),
                }
                
                mail_password = request.form.get('mail_password')
                if mail_password:
                    update_data['mail_password'] = mail_password
                
                superuser_service.update_email_settings(update_data, _get_current_user().id)
                
                # Reload mail configuration
                from src import reload_mail_config
                success, message = reload_mail_config(current_app._get_current_object())
                
                if success:
                    flash('Email settings updated and reloaded successfully!', 'success')
                else:
                    flash(f'Settings saved but reload failed: {message}', 'warning')
            except Exception as e:
                flash(f'Error updating settings: {str(e)}', 'danger')
            
            return redirect(url_for('superuser.settings', tab='email'))
        
        elif tab == 'payment':
            try:
                # Parse tax rate from percentage to decimal
                tax_rate_percent = request.form.get('tax_rate', '0')
                tax_rate = float(tax_rate_percent) / 100.0 if tax_rate_percent else 0.0
                
                update_data = {
                    'currency': request.form.get('currency', 'USD'),
                    'tax_rate': tax_rate,
                    'stripe_enabled': request.form.get('stripe_enabled') == '1',
                    'stripe_publishable_key': request.form.get('stripe_publishable_key'),
                }
                
                # Only update secrets if provided (not empty)
                stripe_secret_key = request.form.get('stripe_secret_key')
                if stripe_secret_key:
                    update_data['stripe_secret_key'] = stripe_secret_key
                
                stripe_webhook_secret = request.form.get('stripe_webhook_secret')
                if stripe_webhook_secret:
                    update_data['stripe_webhook_secret'] = stripe_webhook_secret
                
                superuser_service.update_payment_settings(update_data, _get_current_user().id)
                
                flash('Payment settings updated successfully!', 'success')
            except Exception as e:
                flash(f'Error updating payment settings: {str(e)}', 'danger')
            
            return redirect(url_for('superuser.settings', tab='payment'))
    
    active_tab = request.args.get('tab', 'email')
    return render_template('private/superusers/settings/index.html',
                         current_user=_get_current_user(),
                         settings=settings_obj,
                         active_tab=active_tab)


@superuser_bp.route('/check-email-config', methods=['GET'])
@login_required
@role_required('superuser')
def check_email_config():
    """Diagnostic endpoint to check email configuration status."""
    return jsonify(superuser_service.get_email_config_status())


@superuser_bp.route('/check-stripe-config', methods=['GET'])
@login_required
@role_required('superuser')
def check_stripe_config():
    """Diagnostic endpoint to check Stripe configuration status."""
    try:
        settings = AppSettings.get_settings()
        
        return jsonify({
            'stripe_enabled': settings.stripe_enabled,
            'stripe_publishable_key': settings.stripe_publishable_key[:20] + '...' if settings.stripe_publishable_key else None,
            'stripe_secret_key_configured': bool(settings.stripe_secret_key_encrypted),
            'stripe_secret_key_length': len(settings.stripe_secret_key_encrypted) if settings.stripe_secret_key_encrypted else 0,
            'stripe_webhook_secret_configured': bool(settings.stripe_webhook_secret_encrypted),
            'retrieved_secret_key': settings.get_stripe_secret_key()[:20] + '...' if settings.get_stripe_secret_key() else None,
            'retrieved_webhook_secret': settings.get_stripe_webhook_secret()[:20] + '...' if settings.get_stripe_webhook_secret() else None,
            'settings_id': settings.id,
            'settings_created_at': settings.created_at.isoformat() if settings.created_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============== PROFILE ROUTES ===============

@superuser_bp.route('/profile')
@login_required
@role_required('superuser')
def profile():
    """Superuser profile page."""
    user = _get_current_user()
    
    context = {
        'current_user': user
    }
    return render_template('private/superusers/profile/index.html', **context)


@superuser_bp.route('/profile/update-profile', methods=['POST'])
@login_required
@role_required('superuser')
def update_profile():
    """Update superuser profile information."""
    from src.models.logs import Log
    from src.models.user_folder.users import User
    
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
            return redirect(url_for('superuser.profile'))
        
        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user.id:
            flash('Email address is already in use.', 'danger')
            return redirect(url_for('superuser.profile'))
        
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
    
    return redirect(url_for('superuser.profile'))


@superuser_bp.route('/profile/update-password', methods=['POST'])
@login_required
@role_required('superuser')
def update_password():
    """Update superuser password."""
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
            return redirect(url_for('superuser.profile'))
        
        # Verify current password
        if not verify_hash(user.password_hash, current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('superuser.profile'))
        
        # Check if new passwords match
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('superuser.profile'))
        
        # Check password length
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('superuser.profile'))
        
        # Update password
        user.update_password(new_password)
        
        # Log password change
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
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
    
    return redirect(url_for('superuser.profile'))


@superuser_bp.route('/profile/delete-account', methods=['POST'])
@login_required
@role_required('superuser')
def delete_account():
    """Deactivate superuser account."""
    from src.models.logs import Log
    
    user = _get_current_user()
    
    try:
        # Log account deletion
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
        
        # Deactivate account
        user.is_active = False
        user.save()
        
        # Log out user
        session.clear()
        flash('Your account has been deactivated. Contact an administrator to reactivate.', 'info')
        return redirect(url_for('auth.loginReg'))
        
    except Exception as e:
        flash(f'Error deleting account: {str(e)}', 'danger')
        return redirect(url_for('superuser.profile'))
