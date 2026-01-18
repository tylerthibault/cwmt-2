"""
Course instance controller for managing course instances.
"""
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from src.models.doorman import Doorman
from src.models.course_folder.course_templates import CourseTemplate
from src.models.user_folder.instructors import Instructor
from src.models.user_folder.students import Student
from src.models.user_folder.users import User
from src.utils.custom_decorators import login_required, role_required
from src.services.calendar import format_course_instances_for_calendar
from src.services import course_instance_service
import json

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')


def _get_current_user():
    """Get current user from session."""
    return Doorman.get_by_token(session['doorman_token']).user


# =============== ADMIN ROUTES ===============

@courses_bp.route('/admin/show')
@login_required
@role_required('admin')
def admin_course_instances():
    """List all course instances for admin."""
    instances = course_instance_service.get_all_course_instances()
    events = format_course_instances_for_calendar(instances)
    
    return render_template('private/admins/courses/index.html',
                         course_instances=instances,
                         all_course_templates=CourseTemplate.get_all(),
                         course_templates=CourseTemplate.get_all(),
                         instructors=Instructor.get_all(),
                         events_json=json.dumps(events),
                         current_user=_get_current_user(),
                         role='admin')


@courses_bp.route('/admin/calendar')
@login_required
@role_required('admin')
def admin_course_calendar():
    """Calendar view of all course instances for admin."""
    instances = course_instance_service.get_all_course_instances()
    events = format_course_instances_for_calendar(instances)
    
    return render_template('private/admins/courses/index.html',
                         course_instances=instances,
                         events_json=json.dumps(events),
                         course_templates=CourseTemplate.get_all(),
                         instructors=Instructor.get_all(),
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
            location=data.get('location'),
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


# =============== INSTRUCTOR ROUTES ===============

@courses_bp.route('/instructor/calendar')
@login_required
@role_required('instructor')
def instructor_course_calendar():
    """Calendar view of all course instances for instructor."""
    instances = course_instance_service.get_all_course_instances()
    events = format_course_instances_for_calendar(instances)
    
    current_user = _get_current_user()
    current_instructor = Instructor.query.filter_by(user_id=current_user.id).first()
    
    return render_template('private/instructors/courses/index.html',
                         course_instances=instances,
                         events_json=json.dumps(events),
                         instructors=Instructor.get_all(),
                         current_user=current_user,
                         current_instructor_id=current_instructor.id if current_instructor else None,
                         role='instructor')


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
