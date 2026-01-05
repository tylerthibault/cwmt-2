from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, session
from src.models.user_folder import superusers, users
from src.models.doorman import Doorman
from src.models.flask_mail.email_logs import Log
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

# ------------------------------------------------------
# --------------------- API ROUTES ---------------------
# ------------------------------------------------------