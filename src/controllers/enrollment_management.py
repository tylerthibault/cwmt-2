"""Enrollment controller for enrollment and unenrollment management."""
from flask import Blueprint, render_template, request, jsonify
from src.models.course_folder.enrollments import Enrollment
from src.models.course_folder.course_instances import CourseInstance
from src.models.user_folder.students import Student
from src.models.user_folder.users import User
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required
from src.services import enrollment_service
import stripe

enrollments_bp = Blueprint('enrollments', __name__, url_prefix='/admin/enrollments')


def _get_current_user():
    """Get current user from session."""
    from flask import session
    return Doorman.get_by_token(session['doorman_token']).user


def _success_response(message, data=None, status=200):
    """Create success JSON response."""
    response = {'success': True, 'message': message}
    if data:
        response.update(data)
    return jsonify(response), status


def _error_response(message, status=500):
    """Create error JSON response."""
    return jsonify({'error': message}), status


@enrollments_bp.route('/unenrollment-requests')
@login_required
@role_required('admin')
def unenrollment_requests():
    """View all unenrollment requests."""
    status_filter = request.args.get('status', 'pending')
    
    enrollments = enrollment_service.get_unenrollment_requests(status_filter)
    counts = enrollment_service.get_unenrollment_counts()
    
    return render_template('private/admins/unenrollment_requests/index.html',
                         current_user=_get_current_user(),
                         enrollments=enrollments,
                         status_filter=status_filter,
                         **counts)


@enrollments_bp.route('/<int:enrollment_id>/approve-unenrollment', methods=['POST'])
@login_required
@role_required('admin')
def approve_unenrollment(enrollment_id):
    """Approve an unenrollment request and process refund."""
    try:
        data = request.get_json()
        enrollment = Enrollment.query.get(enrollment_id)
        
        if not enrollment:
            return _error_response('Enrollment not found', 404)
        
        # Get refund percentage from request data or use default
        refund_percentage = data.get('refund_percentage', enrollment.refund_percentage)
        admin_notes = data.get('admin_notes', '')
        
        # Process unenrollment
        refund_amount = enrollment_service.approve_unenrollment(
            enrollment, refund_percentage, admin_notes, _get_current_user().id
        )
        
        return _success_response(
            f'Unenrollment approved and {refund_percentage}% refund issued',
            {'refund_amount': refund_amount}
        )
        
    except ValueError as e:
        return _error_response(str(e), 400)
    except stripe.error.StripeError as e:
        return _error_response(f'Stripe error: {str(e)}', 400)
    except Exception as e:
        return _error_response(f'An error occurred: {str(e)}')


@enrollments_bp.route('/<int:enrollment_id>/deny-unenrollment', methods=['POST'])
@login_required
@role_required('admin')
def deny_unenrollment(enrollment_id):
    """Deny an unenrollment request."""
    try:
        data = request.get_json()
        enrollment = Enrollment.query.get(enrollment_id)
        
        if not enrollment:
            return _error_response('Enrollment not found', 404)
        
        admin_notes = data.get('admin_notes', '')
        
        enrollment_service.deny_unenrollment(enrollment, admin_notes, _get_current_user().id)
        
        return _success_response('Unenrollment request denied')
        
    except ValueError as e:
        return _error_response(str(e), 400)
    except Exception as e:
        return _error_response(f'An error occurred: {str(e)}')


@enrollments_bp.route('/create')
@login_required
@role_required('admin')
def enroll_student_form():
    """Show form to manually enroll a student in a course."""
    students = Student.query.join(User).order_by(User.email).all()
    courses = CourseInstance.query.order_by(CourseInstance.start_date.desc()).all()
    
    return render_template('private/admins/enrollments/create.html',
                         current_user=_get_current_user(),
                         students=students,
                         courses=courses)


@enrollments_bp.route('/create', methods=['POST'])
@login_required
@role_required('admin')
def enroll_student():
    """Manually enroll a student in a course (with or without creating account)."""
    try:
        data = request.get_json()
        course_instance_id = data.get('course_instance_id')
        student_id = data.get('student_id')
        create_new = data.get('create_new', False)
        
        # New student data (if creating)
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        
        # Enrollment options
        waive_payment = data.get('waive_payment', False)
        admin_notes = data.get('admin_notes', '')
        
        if not course_instance_id:
            return _error_response('Course instance ID is required', 400)
        
        # Get course instance
        course_instance = CourseInstance.query.get(course_instance_id)
        if not course_instance:
            return _error_response('Course not found', 404)
        
        # Get or create student
        temp_password = None
        if create_new:
            student, temp_password = enrollment_service.create_student_account(
                first_name, last_name, email, phone
            )
            student_created = True
        else:
            if not student_id:
                return _error_response('Student ID is required', 400)
            
            student = Student.query.get(student_id)
            if not student:
                return _error_response('Student not found', 404)
            
            student_created = False
        
        # Create enrollment
        enrollment = enrollment_service.create_enrollment(student, course_instance)
        
        # Create payment record if not waived
        payment = None
        if not waive_payment:
            student_email = student.user.email if student.user else email
            payment = enrollment_service.create_enrollment_payment(
                enrollment, course_instance, student_email
            )
        
        # Log the manual enrollment
        course_name = course_instance.course_template.name if course_instance.course_template else 'course'
        student_email = student.user.email if student.user else email
        enrollment_service.log_manual_enrollment(
            enrollment, student_email, course_name, _get_current_user().id,
            student_created, temp_password, waive_payment, admin_notes,
            payment.id if payment else None
        )
        
        response_data = {
            'enrollment_id': enrollment.id,
            'student_id': student.id
        }
        
        if student_created:
            response_data['new_account'] = True
            response_data['temp_password'] = temp_password
            response_data['email'] = email
        
        return _success_response('Student enrolled successfully', response_data)
        
    except ValueError as e:
        return _error_response(str(e), 400)
    except Exception as e:
        return _error_response(f'An error occurred: {str(e)}')
