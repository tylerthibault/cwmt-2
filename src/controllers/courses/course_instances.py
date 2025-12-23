from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from datetime import datetime, time, date
from src.models.user_folder import users, instructors
from src.models.course_folder import course_templates, payable_templates
from src.utils.custom_decorators import login_required, role_required
from src.models.doorman import Doorman

# Create blueprint
courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

@courses_bp.route('/admin/show')
@login_required
@role_required('admin')
def admin_course_instances():
    """List all course instances for admin."""
    from src.models.course_folder import course_instances
    from datetime import timedelta
    import json
    instances = course_instances.CourseInstance.get_all()
    
    # Format instances for calendar
    events = []
    for instance in instances:
        # Calculate end date from start date + duration
        end_date = instance.start_date + timedelta(days=instance.duration_days - 1) if instance.start_date and instance.duration_days else None
        
        # Get instructor names
        instructors_list = []
        if instance.c1_instructor and instance.c1_instructor.user:
            instructors_list.append(instance.c1_instructor.user.full_name)
        if instance.c2_instructor and instance.c2_instructor.user:
            instructors_list.append(instance.c2_instructor.user.full_name)
        instructor_text = ', '.join(instructors_list) if instructors_list else 'Unassigned'
        
        events.append({
            'id': instance.id,
            'title': instance.course_template.name if instance.course_template else 'Unknown Course',
            'start': instance.start_date.isoformat() if instance.start_date else None,
            'end': end_date.isoformat() if end_date else None,
            'location': instance.location,
            'instructor': instructor_text,
            'status': instance.status,
            'enrollment': f"0/{instance.max_students}"  # No current_enrollment tracking yet
        })
    
    context = {
        'course_instances': instances,
        'all_course_templates': course_templates.CourseTemplate.get_all(),
        'events_json': json.dumps(events),
        'current_user': Doorman.get_by_token(session['doorman_token']).user
    }
    return render_template('private/admins/courses/index.html', **context)

@courses_bp.route('/admin/calendar')
@login_required
@role_required('admin')
def admin_course_calendar():
    """Calendar view of all course instances for admin."""
    from src.models.course_folder import course_instances
    import json
    instances = course_instances.CourseInstance.get_all()
    
    # Format instances for calendar
    events = []
    for instance in instances:
        # Calculate end date from start date + duration
        from datetime import timedelta
        end_date = instance.start_date + timedelta(days=instance.duration_days - 1) if instance.start_date and instance.duration_days else None
        
        # Get instructor names
        instructors_list = []
        if instance.c1_instructor and instance.c1_instructor.user:
            instructors_list.append(instance.c1_instructor.user.full_name)
        if instance.c2_instructor and instance.c2_instructor.user:
            instructors_list.append(instance.c2_instructor.user.full_name)
        instructor_text = ', '.join(instructors_list) if instructors_list else 'Unassigned'
        
        events.append({
            'id': instance.id,
            'title': instance.course_template.name if instance.course_template else 'Unknown Course',
            'start': instance.start_date.isoformat() if instance.start_date else None,
            'end': end_date.isoformat() if end_date else None,
            'location': instance.location,
            'instructor': instructor_text,
            'status': instance.status,
            'enrollment': f"0/{instance.max_students}"  # No current_enrollment tracking yet
        })
    
    # Get course templates and instructors for the wizard
    templates = course_templates.CourseTemplate.get_all()
    instructor_list = instructors.Instructor.get_all()
    
    context = {
        'course_instances': instances,
        'events_json': json.dumps(events),
        'course_templates': templates,
        'instructors': instructor_list,
        'current_user': Doorman.get_by_token(session['doorman_token']).user
    }
    return render_template('private/admins/courses/index.html', **context)

@courses_bp.route('/admin/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_course_instance():
    """Create a new course instance."""
    from src.models.course_folder import course_instances
    
    try:
        data = request.get_json()
        
        # Parse date and time
        start_date_str = data.get('start_date')
        start_time_str = data.get('start_time')
        
        start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
        
        # Create course instance
        instance = course_instances.CourseInstance(
            course_template_id=int(data.get('course_template_id')),
            start_date=start_date_obj,
            start_time=start_time_obj,
            duration_days=int(data.get('duration_days')),
            location=data.get('location'),
            max_students=int(data.get('max_students')),
            c1_instructor_id=int(data.get('c1_instructor_id')) if data.get('c1_instructor_id') else None,
            c2_instructor_id=int(data.get('c2_instructor_id')) if data.get('c2_instructor_id') else None,
            notes=data.get('notes')
        )
        
        instance.save()
        
        return jsonify({'success': True, 'message': 'Course instance created successfully'}), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    
@courses_bp.route('/admin/view/<int:instance_id>')
@login_required
@role_required('admin')
def admin_view_course_instance(instance_id):
    """View details of a specific course instance."""
    from src.models.course_folder import course_instances
    instance = course_instances.CourseInstance.query.get(instance_id)
    if not instance:
        flash('Course instance not found.', 'error')
        return redirect(url_for('courses.admin_course_instances'))
    
    context = {
        'course_instance': instance,
        'current_user': Doorman.get_by_token(session['doorman_token']).user
    }
    return render_template('private/admins/courses/view_instance.html', **context)