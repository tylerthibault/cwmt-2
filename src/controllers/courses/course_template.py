from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from datetime import datetime
from src.models.user_folder import users
from src.models.course_folder import course_templates, payable_templates
from src.utils.custom_decorators import login_required, role_required
from src.models.doorman import Doorman

# Create blueprint
course_temp_bp = Blueprint('course_temp', __name__)

@course_temp_bp.route('/show')
@login_required
@role_required('superuser')
def list_course_temps():
    """List all course templates."""
    from src.models.course_folder import payable_templates
    templates = course_templates.CourseTemplate.get_all()
    payables = payable_templates.PayableTemplate.get_all()
    context = {
        'course_templates': templates,
        'payable_templates': payables,
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

@course_temp_bp.route('/course/add-remove-payable', methods=['POST'])
@login_required
@role_required('superuser')
def add_payable_to_course():
    """Add or remove a payable template from a course template."""
    course_template_id = request.form.get('course_template_id')
    payable_template_id = request.form.get('payable_template_id')
    action = request.form.get('action')  # 'add' or 'remove'

    course_template = course_templates.CourseTemplate.query.get(course_template_id)
    payable_template = payable_templates.PayableTemplate.query.get(payable_template_id)

    if not course_template or not payable_template:
        flash('Invalid course or payable template.', 'error')
        return redirect(url_for('course_temp.list_course_temps'))

    if action == 'add':
        if not course_template.payable_templates.filter_by(id=payable_template.id).first():
            course_template.payable_templates.append(payable_template)
            course_template.save()
            flash('Payable template added to course template.', 'success')
        else:
            flash('Payable template already associated with this course template.', 'info')
    elif action == 'remove':
        if course_template.payable_templates.filter_by(id=payable_template.id).first():
            course_template.payable_templates.remove(payable_template)
            course_template.save()
            flash('Payable template removed from course template.', 'success')
        else:
            flash('Payable template not associated with this course template.', 'info')
    else:
        flash('Invalid action.', 'error')

    return redirect(url_for('course_temp.list_course_temps'))


# ------------------------------------------------------
# --------------------- API ROUTES ---------------------
# ------------------------------------------------------
