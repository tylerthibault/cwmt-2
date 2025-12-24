from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from datetime import datetime, time, date, timedelta
from src.models.user_folder import users, instructors
from src.models.course_folder import course_templates, payable_templates
from src.utils.custom_decorators import login_required, role_required
from src.models.doorman import Doorman
from src.services.calendar import format_course_instances_for_calendar

# Create blueprint
courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

@courses_bp.route('/admin/show')
@login_required
@role_required('admin')
def admin_course_instances():
    """List all course instances for admin."""
    from src.models.course_folder import course_instances
    import json
    
    instances = course_instances.CourseInstance.get_all()
    events = format_course_instances_for_calendar(instances)
    
    context = {
        'course_instances': instances,
        'all_course_templates': course_templates.CourseTemplate.get_all(),
        'course_templates': course_templates.CourseTemplate.get_all(),
        'instructors': instructors.Instructor.get_all(),
        'events_json': json.dumps(events),
        'current_user': Doorman.get_by_token(session['doorman_token']).user,
        'role': 'admin'
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
    events = format_course_instances_for_calendar(instances)
    
    # Get course templates and instructors for the wizard
    templates = course_templates.CourseTemplate.get_all()
    instructor_list = instructors.Instructor.get_all()
    
    context = {
        'course_instances': instances,
        'events_json': json.dumps(events),
        'course_templates': templates,
        'instructors': instructor_list,
        'current_user': Doorman.get_by_token(session['doorman_token']).user,
        'role': 'admin'
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

# =============== INSTRUCTOR ROUTES ===============

@courses_bp.route('/instructor/calendar')
@login_required
@role_required('instructor')
def instructor_course_calendar():
    """Calendar view of all course instances for instructor."""
    from src.models.course_folder import course_instances
    import json
    
    instances = course_instances.CourseInstance.get_all()
    events = format_course_instances_for_calendar(instances)
    
    # Get current user's instructor record
    current_user = Doorman.get_by_token(session['doorman_token']).user
    current_instructor = instructors.Instructor.query.filter_by(user_id=current_user.id).first()
    
    # Get all instructors for displaying names
    instructor_list = instructors.Instructor.get_all()
    
    context = {
        'course_instances': instances,
        'events_json': json.dumps(events),
        'instructors': instructor_list,
        'current_user': current_user,
        'current_instructor_id': current_instructor.id if current_instructor else None,
        'role': 'instructor'
    }
    return render_template('private/instructors/courses/index.html', **context)

@courses_bp.route('/instructor/signup', methods=['POST'])
@login_required
@role_required('instructor')
def instructor_signup_for_course():
    """Instructor signs up for a course as C1 or C2."""
    from src.models.course_folder import course_instances
    
    try:
        data = request.get_json()
        course_instance_id = data.get('course_instance_id')
        role = data.get('role')  # 'c1' or 'c2'
        
        if not course_instance_id or not role:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        if role not in ['c1', 'c2']:
            return jsonify({'success': False, 'message': 'Invalid role. Must be c1 or c2.'}), 400
        
        # Get the course instance
        instance = course_instances.CourseInstance.query.get(course_instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Course instance not found'}), 404
        
        # Get current user's instructor record
        current_user = Doorman.get_by_token(session['doorman_token']).user
        instructor = instructors.Instructor.query.filter_by(user_id=current_user.id).first()
        
        if not instructor:
            return jsonify({'success': False, 'message': 'Instructor record not found'}), 404
        
        # Check if slot is available
        if role == 'c1':
            if instance.c1_instructor_id:
                return jsonify({'success': False, 'message': 'C1 instructor slot is already taken'}), 400
            instance.c1_instructor_id = instructor.id
        else:  # c2
            if instance.c2_instructor_id:
                return jsonify({'success': False, 'message': 'C2 instructor slot is already taken'}), 400
            instance.c2_instructor_id = instructor.id
        
        instance.save()
        
        return jsonify({'success': True, 'message': f'Successfully signed up as {role.upper()} instructor'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@courses_bp.route('/instructor/withdraw', methods=['POST'])
@login_required
@role_required('instructor')
def instructor_withdraw_from_course():
    """Instructor withdraws from a course."""
    from src.models.course_folder import course_instances
    
    try:
        data = request.get_json()
        course_instance_id = data.get('course_instance_id')
        
        if not course_instance_id:
            return jsonify({'success': False, 'message': 'Missing course_instance_id'}), 400
        
        # Get the course instance
        instance = course_instances.CourseInstance.query.get(course_instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Course instance not found'}), 404
        
        # Get current user's instructor record
        current_user = Doorman.get_by_token(session['doorman_token']).user
        instructor = instructors.Instructor.query.filter_by(user_id=current_user.id).first()
        
        if not instructor:
            return jsonify({'success': False, 'message': 'Instructor record not found'}), 404
        
        # Remove instructor from course
        if instance.c1_instructor_id == instructor.id:
            instance.c1_instructor_id = None
        elif instance.c2_instructor_id == instructor.id:
            instance.c2_instructor_id = None
        else:
            return jsonify({'success': False, 'message': 'You are not signed up for this course'}), 400
        
        instance.save()
        
        return jsonify({'success': True, 'message': 'Successfully withdrawn from course'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400