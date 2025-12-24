from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, session
from src.models.user_folder import instructors, users
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required
from src.models.course_folder import course_instances
from src.services.calendar import format_course_instances_for_calendar
import json

# Create blueprint
instructor_bp = Blueprint('instructor', __name__, url_prefix='/instructor')

@instructor_bp.route('/dashboard')
@login_required
@role_required('instructor')
def dashboard():
    """instructor dashboard route."""

    instances = course_instances.CourseInstance.get_all()
    events = format_course_instances_for_calendar(instances)
    
    # Get current user's instructor record
    current_user = Doorman.get_by_token(session['doorman_token']).user
    current_instructor = instructors.Instructor.query.filter_by(user_id=current_user.id).first()

    context = {
        'current_user': current_user,
        'current_instructor_id': current_instructor.id if current_instructor else None,
        'course_instances': instances,
        'instructors': instructors.Instructor.get_all(),
        'events_json': json.dumps(events),
        'role': 'instructor'
    }
    return render_template('private/instructors/dashboard/index.html', **context)


@instructor_bp.route('/set-instructor/<int:user_id>/<status>', methods=['GET', 'POST'])
@login_required
@role_required('instructor', 'admin', 'superuser')
def instructor_status(user_id, status='add'):
    """
        Route to set a user as an instructor.
    """
    user = users.User.query.get(user_id)
    if not user:
        return "User not found", 404

    if status == 'add':
        # Check if the user is already an instructor
        existing_instructor = instructors.Instructor.query.filter_by(user_id=user.id).first()
        if existing_instructor:
            return "User is already an instructor", 400

        # Create a new Instructor entry
        new_instructor = instructors.Instructor.create(
            user_id=user.id,
            is_active=True,
            status_change_date=datetime.utcnow()
        )

        return redirect(url_for('instructor.dashboard'))

    if status == 'remove':
        # Find the instructor entry
        existing_instructor = instructors.Instructor.query.filter_by(user_id=user.id).first()
        if not existing_instructor:
            return "User is not an instructor", 400

        # soft delete by setting is_active to False
        existing_instructor.is_active = False
        existing_instructor.status_change_date = datetime.utcnow()
        existing_instructor.save()
        return redirect(url_for('auth.login'))



# ------------------------------------------------------
# --------------------- API ROUTES ---------------------
# ------------------------------------------------------
