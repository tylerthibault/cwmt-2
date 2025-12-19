from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, session
from src.models.user_folder import admins, users
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    """admin dashboard route."""
    context = {
        'current_user': Doorman.get_by_token(session['doorman_token']).user
    }
    return render_template('private/admins/dashboard/index.html', **context)


@admin_bp.route('/set-admin/<int:user_id>/<status>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_status(user_id, status='add'):
    """
        Route to set a user as an admin.
    """
    user = users.User.query.get(user_id)
    if not user:
        return "User not found", 404

    if status == 'add':
        # Check if the user is already an admin
        existing_admin = admins.Admin.query.filter_by(user_id=user.id).first()
        if existing_admin:
            return "User is already an admin", 400

        # Create a new Admin entry
        new_admin = admins.Admin.create(user_id=user.id)

        return redirect(url_for('admin.dashboard'))

    if status == 'remove':
        # Find the admin entry
        existing_admin = admins.Admin.query.filter_by(user_id=user.id).first()
        if not existing_admin:
            return "User is not an admin", 400

        # Delete the admin entry
        existing_admin.delete()

        return redirect(url_for('admin.dashboard'))


# ------------------------------------------------------
# --------------------- API ROUTES ---------------------
# ------------------------------------------------------