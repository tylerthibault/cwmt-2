from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from datetime import datetime
from src.models.user_folder import users
from src.models.course_folder import course_templates
from src.utils.custom_decorators import login_required, role_required

# Create blueprint
course_template_bp = Blueprint('course_template', __name__)

@course_template_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'superuser'])
def create_course_template():
    """Create a new course template."""
    if request.method == 'POST':
        name = request.form.get('name')
        experience_level = request.form.get('experience_level')
        duration_days = request.form.get('duration_days')
        max_students = request.form.get('max_students')
        
        # Validate inputs
        if not name or not experience_level or not duration_days or not max_students:
            flash('All fields are required!', 'error')
            return redirect(url_for('course_template.create_course_template'))
        
        # Create and save the new course template
        new_template = course_templates.CourseTemplate(
            name=name,
            experience_level=experience_level,
            duration_days=int(duration_days),
            max_students=int(max_students)
        )
        new_template.save()
        
        flash('Course template created successfully!', 'success')
        return redirect(url_for('course_template.list_course_templates'))
    
    return render_template('create_course_template.html')




# ------------------------------------------------------
# --------------------- API ROUTES ---------------------
# ------------------------------------------------------
