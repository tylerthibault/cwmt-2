from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from datetime import datetime, time, date, timedelta
from src.models.user_folder import users, instructors
from src.models.course_folder import course_templates, payable_templates
from src.models.logs import Log
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
        
        # Log the course instance creation
        current_user = Doorman.get_by_token(session['doorman_token']).user
        course_template = course_templates.CourseTemplate.query.get(instance.course_template_id)
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='create_course_instance',
            description=f'Course instance created: {course_template.name if course_template else "Unknown Course"} on {start_date_obj.strftime("%Y-%m-%d")}',
            user_id=current_user.id,
            target_type='course_instance',
            target_id=instance.id,
            status='success',
            extra_data={
                'course_template_id': instance.course_template_id,
                'course_name': course_template.name if course_template else None,
                'start_date': start_date_obj.isoformat(),
                'start_time': start_time_obj.isoformat(),
                'duration_days': instance.duration_days,
                'location': instance.location,
                'max_students': instance.max_students,
                'c1_instructor_id': instance.c1_instructor_id,
                'c2_instructor_id': instance.c2_instructor_id
            }
        )
        
        return jsonify({'success': True, 'message': 'Course instance created successfully'}), 201
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    
@courses_bp.route('/admin/view/<int:instance_id>')
@login_required
@role_required('admin')
def admin_view_course_instance(instance_id):
    """View details of a specific course instance."""
    from src.models.course_folder import course_instances
    from src.models.user_folder.students import Student
    from src.models.user_folder.users import User
    
    instance = course_instances.CourseInstance.query.get(instance_id)
    if not instance:
        flash('Course instance not found.', 'error')
        return redirect(url_for('courses.admin_course_instances'))
    
    # Get all students for enrollment modal
    students = Student.query.join(User).order_by(User.email).all()
    
    context = {
        'course_instance': instance,
        'students': students,
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
            return jsonify({'success - 67f50d19': False, 'message': 'Missing required fields'}), 400
        
        if role not in ['c1', 'c2']:
            return jsonify({'success - 00a9cf40': False, 'message': 'Invalid role. Must be c1 or c2.'}), 400
        
        # Get the course instance
        instance = course_instances.CourseInstance.query.get(course_instance_id)
        if not instance:
            return jsonify({'success - 776423dc': False, 'message': 'Course instance not found'}), 404
        
        # Get current user's instructor record
        current_user = Doorman.get_by_token(session['doorman_token']).user
        instructor = instructors.Instructor.query.filter_by(user_id=current_user.id).first()
        
        if not instructor:
            return jsonify({'success - e352da0d': False, 'message': 'Instructor record not found'}), 404
        
        # Check if slot is available
        if role == 'c1':
            if instance.c1_instructor_id:
                return jsonify({'success - a75c5cbe': False, 'message': 'C1 instructor slot is already taken'}), 400
            instance.c1_instructor_id = instructor.id
        else:  # c2
            if instance.c2_instructor_id:
                return jsonify({'success - 272babe8': False, 'message': 'C2 instructor slot is already taken'}), 400
            instance.c2_instructor_id = instructor.id
        
        instance.save()
        
        # Log the instructor course signup
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='course_signup',
            description=f'{instructor.user.first_name} {instructor.user.last_name} signed up as {role.upper()} instructor for {instance.course_template.name}',
            user_id=current_user.id,
            target_type='course_instance',
            target_id=instance.id,
            status='success',
            extra_data={
                'role': role.upper(),
                'course_name': instance.course_template.name,
                'start_date': instance.start_date.isoformat() if instance.start_date else None
            }
        )
        
        return jsonify({'success - b82d6859': True, 'message': f'Successfully signed up as {role.upper()} instructor'}), 200
        
    except Exception as e:
        return jsonify({'success - f607efb0': False, 'message': str(e)}), 400

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
            return jsonify({'success - d104c389': False, 'message': 'Missing course_instance_id'}), 400
        
        # Get the course instance
        instance = course_instances.CourseInstance.query.get(course_instance_id)
        if not instance:
            return jsonify({'success - ea977684': False, 'message': 'Course instance not found'}), 404
        
        # Get current user's instructor record
        current_user = Doorman.get_by_token(session['doorman_token']).user
        instructor = instructors.Instructor.query.filter_by(user_id=current_user.id).first()
        
        if not instructor:
            return jsonify({'success': False, 'message': 'Instructor record not found'}), 404
        
        # Remove instructor from course
        role_dropped = None
        if instance.c1_instructor_id == instructor.id:
            instance.c1_instructor_id = None
            role_dropped = 'C1'
        elif instance.c2_instructor_id == instructor.id:
            instance.c2_instructor_id = None
            role_dropped = 'C2'
        else:
            return jsonify({'success': False, 'message': 'You are not signed up for this course'}), 400
        
        instance.save()
        
        # Log the instructor course withdrawal
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='course_withdrawal',
            description=f'{instructor.user.first_name} {instructor.user.last_name} withdrew from {role_dropped} instructor position for {instance.course_template.name}',
            user_id=current_user.id,
            target_type='course_instance',
            target_id=instance.id,
            status='success',
            extra_data={
                'role': role_dropped,
                'course_name': instance.course_template.name,
                'start_date': instance.start_date.isoformat() if instance.start_date else None
            }
        )
        
        return jsonify({'success': True, 'message': 'Successfully withdrawn from course'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@courses_bp.route('/student/checkout/<int:course_id>')
@login_required
@role_required('student')
def student_checkout(course_id):
    """Display checkout page for course enrollment."""
    from src.models.course_folder import course_instances
    from src.models.user_folder import students
    
    # Get the course instance
    instance = course_instances.CourseInstance.query.get(course_id)
    if not instance:
        flash('Course not found', 'error')
        return redirect(url_for('student.dashboard'))
    
    # Get current user's student record
    current_user = Doorman.get_by_token(session['doorman_token']).user
    student = students.Student.query.filter_by(user_id=current_user.id).first()
    
    if not student:
        flash('Student record not found', 'error')
        return redirect(url_for('student.dashboard'))
    
    context = {
        'current_user': current_user,
        'student': student,
        'course': instance,
        'course_name': instance.course_template.name if instance.course_template else 'Unknown Course',
        'course_price': instance.get_total_tuition() if instance.course_template else 0.0
    }
    
    return render_template('private/students/checkout/index.html', **context)

@courses_bp.route('/student/process-payment', methods=['POST'])
@login_required
@role_required('student')
def student_process_payment():
    """Process mock payment and create enrollment."""
    from src.models.course_folder import course_instances
    from src.models.user_folder import students
    
    try:
        data = request.get_json()
        course_instance_id = data.get('course_instance_id')
        
        if not course_instance_id:
            return jsonify({'success': False, 'message': 'Missing course_instance_id'}), 400
        
        # Get the course instance
        instance = course_instances.CourseInstance.query.get(course_instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Course instance not found'}), 404
        
        # Get current user's student record
        current_user = Doorman.get_by_token(session['doorman_token']).user
        student = students.Student.query.filter_by(user_id=current_user.id).first()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student record not found'}), 404
        
        # TODO: Check if course is full
        # TODO: Check if student is already enrolled
        # TODO: Create enrollment record
        # TODO: In future, integrate with Stripe here
        
        # Mock payment success
        return jsonify({
            'success': True, 
            'message': 'Payment processed successfully',
            'redirect_url': url_for('student.dashboard')
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400