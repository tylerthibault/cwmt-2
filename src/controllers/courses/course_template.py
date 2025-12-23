from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from datetime import datetime
from src.models.user_folder import users
from src.models.course_folder import course_templates
from src.utils.custom_decorators import login_required, role_required
from src.models.doorman import Doorman

# Create blueprint
course_temp_bp = Blueprint('course_temp', __name__)

@course_temp_bp.route('/show')
@login_required
@role_required('superuser')
def list_course_temps():
    """List all course templates."""
    templates = course_templates.CourseTemplate.get_all()
    context = {
        'course_templates': templates,
        'current_user': Doorman.get_by_token(session['doorman_token']).user
    }
    return render_template('private/superusers/course_templates/index.html', **context)

@course_temp_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('superuser')
def create_course_temp():
    """Create a new course template."""
    if request.method == 'POST':
        name = request.form.get('name')
        experience_level = request.form.get('experience_level')
        duration_days = request.form.get('duration_days')
        max_students = request.form.get('max_students')
        
        # Validate inputs
        if not name or not experience_level or not duration_days or not max_students:
            flash('All fields are required!', 'error')
            return redirect(url_for('course_temp.create_course_temp'))
        
        # Create and save the new course template
        new_template = course_templates.CourseTemplate(
            name=name,
            experience_level=experience_level,
            duration_days=int(duration_days),
            max_students=int(max_students)
        )
        new_template.save()
        
        flash('Course template created successfully!', 'success')
        return redirect(url_for('course_temp.list_course_temps'))
    
    return render_template('create_course_temp.html')




# ------------------------------------------------------
# --------------------- API ROUTES ---------------------
# ------------------------------------------------------
