from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, session
from src.models.user_folder import students, users
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required

# Create blueprint
student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@login_required
@role_required('student')
def dashboard():
    """Student dashboard route."""
    context = {
        'current_user': Doorman.get_by_token(session['doorman_token']).user
    }
    return render_template('private/students/dashboard/index.html', **context)


@student_bp.route('/set-student/<int:user_id>/<status>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def student_status(user_id, status='add'):
    """
        Route to set a user as a student.
    """
    user = users.User.query.get(user_id)
    if not user:
        return "User not found", 404

    if status == 'add':
        # Check if the user already has a student profile
        existing_student = students.Student.query.filter_by(user_id=user.id).first()
        if existing_student:
            return "User already has a student profile", 400

        # Create a new Student entry
        new_student = students.Student.create(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name
        )

        return redirect(url_for('student.dashboard'))

    if status == 'remove':
        # Find the student entry
        existing_student = students.Student.query.filter_by(user_id=user.id).first()
        if not existing_student:
            return "User does not have a student profile", 400

        # Delete the student entry
        existing_student.delete()

        return redirect(url_for('student.dashboard'))


# ------------------------------------------------------
# --------------------- API ROUTES ---------------------
# ------------------------------------------------------