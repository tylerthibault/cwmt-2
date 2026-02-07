"""
Instructor controller for instructor-specific operations.

NOTE: Instructor privilege management (add/remove instructor status) has been moved to admin.py
This controller focuses on instructor dashboard and instructor-specific views.
"""
from flask import Blueprint, render_template, redirect, url_for, session, jsonify
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required
from src.services import instructor_service
import json

instructor_bp = Blueprint('instructor', __name__, url_prefix='/instructor')


def _get_current_user():
    """Helper to get current user from session."""
    return Doorman.get_by_token(session['doorman_token']).user

@instructor_bp.route('/dashboard')
@login_required
@role_required('instructor')
def dashboard():
    """Instructor dashboard with course calendar and overview."""
    current_user = _get_current_user()
    dashboard_data = instructor_service.get_instructor_dashboard_data(current_user)
    
    context = {
        'current_user': current_user,
        'current_instructor_id': dashboard_data['current_instructor_id'],
        'course_instances': dashboard_data['course_instances'],
        'instructors': dashboard_data['instructors'],
        'role': 'instructor'
    }
    return render_template('private/instructors/dashboard/index.html', **context)

# =============== PROFILE ROUTES ===============

@instructor_bp.route('/profile')
@login_required
@role_required('instructor')
def profile():
    """Instructor profile page."""
    from src.models.user_folder import instructors
    
    user = _get_current_user()
    instructor = instructors.Instructor.query.filter_by(user_id=user.id).first()
    
    context = {
        'current_user': user,
        'instructor': instructor
    }
    return render_template('private/instructors/profile/index.html', **context)


@instructor_bp.route('/profile/update-profile', methods=['POST'])
@login_required
@role_required('instructor')
def update_profile():
    """Update instructor profile information."""
    from flask import request, flash
    from src.models.user_folder import users
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
            return redirect(url_for('instructor.profile'))
        
        # Check if email is already taken by another user
        existing_user = users.User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user.id:
            flash('Email address is already in use.', 'danger')
            return redirect(url_for('instructor.profile'))
        
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
    
    return redirect(url_for('instructor.profile'))


@instructor_bp.route('/profile/update-password', methods=['POST'])
@login_required
@role_required('instructor')
def update_password():
    """Update instructor password."""
    from flask import request, flash
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
            return redirect(url_for('instructor.profile'))
        
        # Verify current password
        if not verify_hash(user.password_hash, current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('instructor.profile'))
        
        # Validate new password
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'danger')
            return redirect(url_for('instructor.profile'))
        
        # Check if passwords match
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('instructor.profile'))
        
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
    
    return redirect(url_for('instructor.profile'))


@instructor_bp.route('/profile/delete-account', methods=['POST'])
@login_required
@role_required('instructor')
def delete_account():
    """Delete instructor account."""
    from flask import request, flash
    from src.models.user_folder import instructors
    from src.models.logs import Log
    from src.utils.password_management import verify_hash
    
    user = _get_current_user()
    
    try:
        # Get password confirmation
        password = request.form.get('password')
        
        if not password:
            flash('Password is required to delete account.', 'danger')
            return redirect(url_for('instructor.profile'))
        
        # Verify password
        if not verify_hash(user.password_hash, password):
            flash('Incorrect password.', 'danger')
            return redirect(url_for('instructor.profile'))
        
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
        
        # Delete instructor role and user
        instructor = instructors.Instructor.query.filter_by(user_id=user.id).first()
        if instructor:
            instructor.delete()
        
        # Logout and delete session
        Doorman.query.filter_by(user_id=user.id).delete()
        session.clear()
        
        flash('Your account has been deleted.', 'success')
        return redirect(url_for('auth.loginReg'))
        
    except Exception as e:
        flash(f'Error deleting account: {str(e)}', 'danger')
    
    return redirect(url_for('instructor.profile'))