from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from src.controllers.auth_controller import login_required
from src.logic.user_logic import UserLogic

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_in_course(course_id):
    """Enroll the current user in a course"""
    from src.models.logbook import Logbook
    from src.logic.course_logic import CourseLogic, CourseBusinessError
    
    try:
        # Get user from token
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        
        if not logbook_entry or not logbook_entry.user_id:
            flash("You must be logged in to enroll in a course.", "error")
            return redirect(url_for('student.dashboard'))
        
        user_id = logbook_entry.user_id
        
        # Attempt to enroll the student
        course = CourseLogic.enroll_student(course_id, user_id, is_admin_override=False)
        flash(f"Successfully enrolled in {course.template.name}!", "success")
            
    except CourseBusinessError as e:
        current_app.logger.warning(f"Course business error enrolling user {user_id} in course {course_id}: {str(e)}")
        flash("Course business error", "error")
    except Exception as e:
        current_app.logger.error(f"Error enrolling user {user_id} in course {course_id}: {str(e)}", exc_info=True)
        flash("Unable to complete enrollment. Please try again.", "error")
    
    return redirect(url_for('student.dashboard'))


@user_bp.route('/settings')
@login_required
def settings():
    """User settings page"""
    # get the current user context
    context = UserLogic.get_context()
    return render_template('private/settings/index.html', **context)

@user_bp.route('/settings/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    from src.models.logbook import Logbook
    from flask import session
    
    # Get current user from session
    token = session.get('token')
    logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
    if not logbook_entry:
        flash('Session expired. Please log in again.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        user, email_changed = UserLogic.update_user_profile(
            logbook_entry.user_id,
            {
                'username': request.form.get('username'),
                'email': request.form.get('email'),
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name')
            }
        )
        
        if email_changed:
            flash('Profile updated successfully! Your email has been changed and needs to be verified.', 'success')
        else:
            flash('Profile updated successfully!', 'success')
            
    except ValueError as e:
        current_app.logger.warning(f"Validation error updating profile for user {logbook_entry.user_id}: {str(e)}")
        flash('Invalid profile information. Please check your input and try again.', 'error')
    except Exception as e:
        current_app.logger.error(f"Error updating profile for user {logbook_entry.user_id}: {str(e)}", exc_info=True)
        flash('Unable to update profile. Please try again.', 'error')
    
    return redirect(url_for('user.settings'))

@user_bp.route('/settings/update-password', methods=['POST'])
@login_required
def update_password():
    """Update user password"""
    from src.models.logbook import Logbook
    from flask import session
    
    # Get current user from session
    token = session.get('token')
    logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
    if not logbook_entry:
        flash('Session expired. Please log in again.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        UserLogic.update_user_password(
            logbook_entry.user_id,
            {
                'current_password': request.form.get('current_password'),
                'new_password': request.form.get('new_password'),
                'confirm_password': request.form.get('confirm_password')
            }
        )
        
        flash('Password changed successfully!', 'success')
            
    except ValueError as e:
        current_app.logger.warning(f"Validation error updating password for user {logbook_entry.user_id}: {str(e)}")
        flash('Invalid password information. Please check your input and try again.', 'error')
    except Exception as e:
        current_app.logger.error(f"Error updating password for user {logbook_entry.user_id}: {str(e)}", exc_info=True)
        flash('Unable to change password. Please try again.', 'error')
    
    return redirect(url_for('user.settings'))

@user_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    context = {}
    return render_template('user/profile.html', **context)
