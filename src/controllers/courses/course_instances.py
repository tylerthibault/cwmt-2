"""
Course instance controller for managing course instances.
"""
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from src.models.doorman import Doorman
from src.models.course_folder.course_templates import CourseTemplate
from src.models.user_folder.instructors import Instructor
from src.models.user_folder.students import Student
from src.models.user_folder.users import User
from src.models.locations import Location
from src.utils.custom_decorators import login_required, role_required
from src.services import course_instance_service
import json

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')


def _get_current_user():
    """Get current user from session."""
    token = session.get('doorman_token')
    if token:
        doorman = Doorman.get_by_token(token)
        return doorman.user if doorman else None
    return None


def _format_events_for_calendar(instances):
    """Format course instances into calendar event objects."""
    events = []
    for instance in instances:
        template = instance.course_template
        if not template:
            continue
        
        c1_name = instance.c1_instructor.user.full_name if instance.c1_instructor else None
        c2_name = instance.c2_instructor.user.full_name if instance.c2_instructor else None
        instructor_text = None
        if c1_name and c2_name:
            instructor_text = f"{c1_name} & {c2_name}"
        elif c1_name:
            instructor_text = c1_name
        elif c2_name:
            instructor_text = c2_name
        
        enrollment_count = len([e for e in instance.enrollments if e.status == 'enrolled'])
        
        events.append({
            'id': instance.id,
            'title': template.name,
            'start': instance.start_date.isoformat(),
            'startTime': instance.start_time.strftime('%H:%M') if instance.start_time else None,
            'duration': instance.duration_days,
            'location': instance.location.name if instance.location else 'Unknown',
            'locationId': instance.location_id,
            'taxRate': float(instance.tax_rate) if instance.tax_rate else 0.0,
            'isTaxable': template.is_taxable if hasattr(template, 'is_taxable') else True,
            'color': template.color or '#0d6efd',
            'maxStudents': instance.max_students,
            'enrollmentCount': enrollment_count,
            'status': instance.status,
            'instructorText': instructor_text,
            'experienceLevel': template.experience_level,
            'description': template.description or '',
            'shortBlurb': template.short_blurb or '',
            'hasC1': instance.c1_instructor_id is not None,
            'hasC2': instance.c2_instructor_id is not None,
            'instructorC1Id': instance.c1_instructor_id,
            'instructorC2Id': instance.c2_instructor_id
        })
    return events


# =============== ADMIN ROUTES ===============

@courses_bp.route('/admin/show')
@login_required
@role_required('admin')
def admin_course_instances():
    """List all course instances for admin."""
    instances = course_instance_service.get_all_course_instances()
    events = _format_events_for_calendar(instances)
    
    # Convert course templates to dictionaries for JSON serialization
    templates = CourseTemplate.get_all()
    templates_dict = [{
        'id': t.id,
        'name': t.name,
        'duration_days': t.duration_days,
        'max_students': t.max_students,
        'experience_level': t.experience_level,
        'is_taxable': t.is_taxable if hasattr(t, 'is_taxable') else True
    } for t in templates]
    
    # Convert instructors to dictionaries
    instructors = Instructor.get_all()
    instructors_dict = [{
        'id': i.id,
        'user': {
            'first_name': i.user.first_name,
            'last_name': i.user.last_name
        }
    } for i in instructors]
    
    # Get active locations
    locations = Location.get_active_locations()
    locations_dict = [{
        'id': loc.id,
        'name': loc.name,
        'location': loc.location,
        'tax_rate': float(loc.tax_rate) if loc.tax_rate else 0.0
    } for loc in locations]
    
    return render_template('private/admins/courses/index.html',
                         course_instances=instances,
                         all_course_templates=templates,
                         course_templates=templates,
                         instructors=instructors,
                         locations=locations,
                         course_templates_json=json.dumps(templates_dict),
                         instructors_json=json.dumps(instructors_dict),
                         locations_json=json.dumps(locations_dict),
                         events_json=json.dumps(events),
                         current_user=_get_current_user(),
                         role='admin')


@courses_bp.route('/admin/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create_course_instance():
    """Create a new course instance."""
    try:
        data = request.get_json()
        
        course_instance_service.create_course_instance(
            course_template_id=data.get('course_template_id'),
            start_date=data.get('start_date'),
            start_time=data.get('start_time'),
            duration_days=data.get('duration_days'),
            location_id=data.get('location_id'),
            max_students=data.get('max_students'),
            c1_instructor_id=data.get('c1_instructor_id'),
            c2_instructor_id=data.get('c2_instructor_id'),
            notes=data.get('notes'),
            current_user_id=_get_current_user().id
        )
        
        return jsonify({'success': True, 'message': 'Course instance created successfully'}), 201
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@courses_bp.route('/admin/view/<int:instance_id>')
@login_required
@role_required('admin')
def admin_view_course_instance(instance_id):
    """View details of a specific course instance."""
    instance = course_instance_service.get_course_instance_by_id(instance_id)
    if not instance:
        flash('Course instance not found.', 'error')
        return redirect(url_for('courses.admin_course_instances'))
    
    students = Student.query.join(User).order_by(User.email).all()
    
    return render_template('private/admins/courses/view_instance.html',
                         course_instance=instance,
                         students=students,
                         current_user=_get_current_user())


@courses_bp.route('/admin/update/<int:instance_id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_update_course_instance(instance_id):
    """Update course instance details."""
    try:
        data = request.get_json()
        
        course_instance_service.update_course_instance(
            instance_id=instance_id,
            start_date=data.get('start_date'),
            start_time=data.get('start_time'),
            duration_days=data.get('duration_days'),
            max_students=data.get('max_students'),
            notes=data.get('notes'),
            current_user_id=_get_current_user().id
        )
        
        return jsonify({'success': True, 'message': 'Course instance updated successfully'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


# =============== INSTRUCTOR ROUTES ===============

@courses_bp.route('/instructor/signup', methods=['POST'])
@login_required
@role_required('instructor')
def instructor_signup_for_course():
    """Instructor signs up for a course as C1 or C2."""
    try:
        data = request.get_json()
        course_instance_id = data.get('course_instance_id')
        role = data.get('role')
        
        if not course_instance_id or not role:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        current_user = _get_current_user()
        instructor = Instructor.query.filter_by(user_id=current_user.id).first()
        
        if not instructor:
            return jsonify({'success': False, 'message': 'Instructor record not found'}), 404
        
        course_instance_service.instructor_signup_for_course(
            course_instance_id, 
            role, 
            instructor.id,
            current_user.id
        )
        
        return jsonify({'success': True, 'message': f'Successfully signed up as {role.upper()} instructor'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@courses_bp.route('/instructor/withdraw', methods=['POST'])
@login_required
@role_required('instructor')
def instructor_withdraw_from_course():
    """Instructor withdraws from a course."""
    try:
        data = request.get_json()
        course_instance_id = data.get('course_instance_id')
        
        if not course_instance_id:
            return jsonify({'success': False, 'message': 'Missing course_instance_id'}), 400
        
        current_user = _get_current_user()
        instructor = Instructor.query.filter_by(user_id=current_user.id).first()
        
        if not instructor:
            return jsonify({'success': False, 'message': 'Instructor record not found'}), 404
        
        course_instance_service.instructor_withdraw_from_course(
            course_instance_id,
            instructor.id,
            current_user.id
        )
        
        return jsonify({'success': True, 'message': 'Successfully withdrawn from course'}), 200
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    
@courses_bp.route('/instructor/courses')
@login_required
@role_required('instructor')
def instructor_course_list():
    """List of courses for instructors to view."""
    instances = course_instance_service.get_all_course_instances()
    events = _format_events_for_calendar(instances)
    
    current_user = _get_current_user()
    
    if not current_user:
        return redirect(url_for('auth.login'))
    
    instructor = Instructor.query.filter_by(user_id=current_user.id).first()
    
    return render_template('private/instructors/courses/index.html',
                         events_json=json.dumps(events),
                         current_user=current_user,
                         current_instructor_id=instructor.id if instructor else None,
                         instructors=Instructor.get_all(),
                         role='instructor')


# =============== STUDENT ROUTES ===============

@courses_bp.route('/student/checkout/<int:course_id>')
@login_required
@role_required('student')
def student_checkout(course_id):
    """Display checkout page for course enrollment."""
    try:
        current_user = _get_current_user()
        student = Student.query.filter_by(user_id=current_user.id).first()
        
        if not student:
            flash('Student record not found', 'error')
            return redirect(url_for('student.dashboard'))
        
        checkout_data = course_instance_service.get_checkout_data(course_id, student.id)
        
        return render_template('private/students/checkout/index.html',
                             current_user=current_user,
                             student=checkout_data['student'],
                             course=checkout_data['course_instance'],
                             course_name=checkout_data['course_name'],
                             course_price=checkout_data['course_price'])
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('student.dashboard'))


@courses_bp.route('/student/process-payment', methods=['POST'])
@login_required
@role_required('student')
def student_process_payment():
    """Process mock payment and create enrollment."""
    try:
        data = request.get_json()
        course_instance_id = data.get('course_instance_id')
        
        if not course_instance_id:
            return jsonify({'success': False, 'message': 'Missing course_instance_id'}), 400
        
        current_user = _get_current_user()
        student = Student.query.filter_by(user_id=current_user.id).first()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student record not found'}), 404
        
        # Verify course exists
        instance = course_instance_service.get_course_instance_by_id(course_instance_id)
        if not instance:
            return jsonify({'success': False, 'message': 'Course instance not found'}), 404
        
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
