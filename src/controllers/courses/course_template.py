from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from datetime import datetime
from src.models.user_folder import users
from src.models.course_folder import course_templates, payable_templates
from src.models.logs import Log
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
    """Create a new course template or update an existing one."""
    if request.method == 'POST':
        template_id = request.form.get('template_id')
        name = request.form.get('name')
        experience_level = request.form.get('experience_level')
        duration_days = request.form.get('duration_days')
        max_students = request.form.get('max_students')
        tuition = request.form.get('tuition')
        color = request.form.get('color', '#0d6efd')
        
        # Validate inputs
        if not name or not experience_level or not duration_days or not max_students or not tuition:
            flash('All fields are required!', 'error')
            return redirect(url_for('course_temp.create_course_temp'))
        
        # Check if we're updating an existing template
        if template_id:
            # UPDATE existing template
            template = course_templates.CourseTemplate.query.get(template_id)
            if not template:
                flash('Course template not found!', 'error')
                return redirect(url_for('course_temp.list_course_temps'))
            
            # Update template fields
            old_name = template.name  # Store old name before updating
            template.name = name
            template.experience_level = experience_level
            template.duration_days = int(duration_days)
            template.max_students = int(max_students)
            template.color = color
            template.save()
            
            # Find the tuition payable template using the OLD name
            tuition_payable = None
            for payable in template.payable_templates:
                if payable.name == f"{old_name} Tuition" or "Tuition" in payable.name:
                    tuition_payable = payable
                    break
            
            if tuition_payable:
                # Update existing tuition payable with new values
                tuition_payable.name = f"{name} Tuition"
                tuition_payable.amount = float(tuition)
                tuition_payable.description = f"Tuition for {name}"
                tuition_payable.save()
            else:
                # Create new tuition payable if it doesn't exist
                tuition_payable = payable_templates.PayableTemplate(
                    name=f"{name} Tuition",
                    amount=float(tuition),
                    description=f"Tuition for {name}",
                    is_required=True
                )
                tuition_payable.save()
                template.payable_templates.append(tuition_payable)
                template.save()
            
            # Log the course template update
            current_user = Doorman.get_by_token(session['doorman_token']).user
            Log.create_log(
                log_type=Log.TYPE_USER_ACTION,
                action='update_course_template',
                description=f'Course template updated: {template.name}',
                user_id=current_user.id,
                target_type='course_template',
                target_id=template.id,
                status='success',
                extra_data={
                    'template_name': template.name,
                    'old_name': old_name,
                    'experience_level': template.experience_level,
                    'duration_days': template.duration_days,
                    'max_students': template.max_students,
                    'tuition': float(tuition),
                    'color': template.color
                }
            )
            
            flash('Course template updated successfully!', 'success')
        else:
            # CREATE new template
            new_template = course_templates.CourseTemplate(
                name=name,
                experience_level=experience_level,
                duration_days=int(duration_days),
                max_students=int(max_students),
                color=color
            )
            new_template.save()
            
            # Create tuition payable template
            tuition_payable = payable_templates.PayableTemplate(
                name=f"{name} Tuition",
                amount=float(tuition),
                description=f"Tuition for {name}",
                is_required=True
            )
            tuition_payable.save()
            
            # Attach the tuition payable to the course template
            new_template.payable_templates.append(tuition_payable)
            new_template.save()
            
            # Log the course template creation
            current_user = Doorman.get_by_token(session['doorman_token']).user
            Log.create_log(
                log_type=Log.TYPE_USER_ACTION,
                action='create_course_template',
                description=f'Course template created: {new_template.name}',
                user_id=current_user.id,
                target_type='course_template',
                target_id=new_template.id,
                status='success',
                extra_data={
                    'template_name': new_template.name,
                    'experience_level': new_template.experience_level,
                    'duration_days': new_template.duration_days,
                    'max_students': new_template.max_students,
                    'tuition': float(tuition),
                    'color': new_template.color,
                    'tuition_payable_id': tuition_payable.id
                }
            )
            
            flash('Course template created successfully with tuition!', 'success')
        
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
            
            # Log the payable addition
            current_user = Doorman.get_by_token(session['doorman_token']).user
            Log.create_log(
                log_type=Log.TYPE_USER_ACTION,
                action='add_payable_to_course',
                description=f'Payable "{payable_template.name}" added to course template "{course_template.name}"',
                user_id=current_user.id,
                target_type='course_template',
                target_id=course_template.id,
                status='success',
                extra_data={
                    'course_template_name': course_template.name,
                    'payable_template_name': payable_template.name,
                    'payable_template_id': payable_template.id,
                    'payable_amount': payable_template.amount,
                    'is_required': payable_template.is_required
                }
            )
            
            flash('Payable template added to course template.', 'success')
        else:
            flash('Payable template already associated with this course template.', 'info')
    elif action == 'remove':
        if course_template.payable_templates.filter_by(id=payable_template.id).first():
            course_template.payable_templates.remove(payable_template)
            course_template.save()
            
            # Log the payable removal
            current_user = Doorman.get_by_token(session['doorman_token']).user
            Log.create_log(
                log_type=Log.TYPE_USER_ACTION,
                action='remove_payable_from_course',
                description=f'Payable "{payable_template.name}" removed from course template "{course_template.name}"',
                user_id=current_user.id,
                target_type='course_template',
                target_id=course_template.id,
                status='success',
                extra_data={
                    'course_template_name': course_template.name,
                    'payable_template_name': payable_template.name,
                    'payable_template_id': payable_template.id
                }
            )
            
            flash('Payable template removed from course template.', 'success')
        else:
            flash('Payable template not associated with this course template.', 'info')
    else:
        flash('Invalid action.', 'error')

    return redirect(url_for('course_temp.list_course_temps'))


# ------------------------------------------------------
# --------------------- API ROUTES ---------------------
# ------------------------------------------------------
