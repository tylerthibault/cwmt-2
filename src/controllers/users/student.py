from datetime import datetime
import json
import os
from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify
from src.models.user_folder import students, users
from src.models.course_folder import course_instances
from src.models.course_folder.enrollments import Enrollment
from src.models.stripe.payments import Payment
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required
from src.utils.password_management import generate_simple_password, hash_string
from src.services.calendar import format_course_instances_for_calendar

# Create blueprint
student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@login_required
@role_required('student')
def dashboard():
    """Student dashboard route."""
    user = Doorman.get_by_token(session['doorman_token']).user
    student = students.Student.query.filter_by(user_id=user.id).first()
    
    # Get all course instances for the calendar
    all_courses = course_instances.CourseInstance.query.filter_by(status='scheduled').all()
    events = format_course_instances_for_calendar(all_courses)
    
    # Get student's enrollments
    enrollments = []
    active_count = 0
    completed_count = 0
    upcoming_count = 0
    
    if student:
        enrollments = Enrollment.get_by_student(student.id)
        today = datetime.now().date()
        
        for enrollment in enrollments:
            if enrollment.status == 'enrolled':
                # Check if course is upcoming or active
                if enrollment.course_instance.start_date > today:
                    upcoming_count += 1
                else:
                    active_count += 1
            elif enrollment.status == 'completed':
                completed_count += 1
    
    # Get guest students created by this student
    guest_students = []
    if student:
        guest_students = students.Student.query.filter_by(created_by_student_id=student.id).all()
        # Add enrollment count for each guest
        for guest in guest_students:
            guest.enrollment_count = len(Enrollment.get_by_student(guest.id))
    
    context = {
        'current_user': user,
        'current_student_id': student.id if student else None,
        'events_json': json.dumps(events),
        'enrollments': enrollments,
        'active_count': active_count,
        'completed_count': completed_count,
        'upcoming_count': upcoming_count,
        'total_enrollments': len(enrollments),
        'guest_students': guest_students
    }
    return render_template('private/students/dashboard/index.html', **context)


@student_bp.route('/set-student/<int:user_id>/<status>', methods=['GET', 'POST'])
@login_required
@role_required('instructor', 'admin', 'superuser')
def student_status(user_id, status='add'):
    """
        Route to set a user as a student.
    """
    user = users.User.query.get(user_id)
    if not user:
        return "User not found", 404

    if status == 'add':
        # Check if the user already has a student profile
        existing_student = students.Student.query.filter_by(user_id=user.id).first()
        if existing_student:
            return "User already has a student profile", 400

        # Create a new Student entry
        new_student = students.Student.create(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name
        )

        return redirect(url_for('student.dashboard'))

    if status == 'remove':
        # Find the student entry
        existing_student = students.Student.query.filter_by(user_id=user.id).first()
        if not existing_student:
            return "User does not have a student profile", 400

        # Delete the student entry
        existing_student.delete()

        return redirect(url_for('auth.dashboard'))


@student_bp.route('/checkout/<int:course_instance_id>')
@login_required
@role_required('student')
def checkout(course_instance_id):
    """Display checkout page for course enrollment."""
    user = Doorman.get_by_token(session['doorman_token']).user
    student = students.Student.query.filter_by(user_id=user.id).first()
    
    if not student:
        return "Student profile not found", 404
    
    # Check if enrolling a guest student
    guest_student_id = request.args.get('guest_student_id', type=int)
    enrolling_student = student  # Default to current student
    is_guest_enrollment = False
    
    if guest_student_id:
        # Verify the guest student belongs to the current student
        guest_student = students.Student.query.get(guest_student_id)
        if not guest_student or guest_student.created_by_student_id != student.id:
            return "Invalid guest student", 403
        enrolling_student = guest_student
        is_guest_enrollment = True
    
    # Get course instance
    course = course_instances.CourseInstance.query.get(course_instance_id)
    if not course:
        return "Course not found", 404
    
    # Check if already enrolled
    if Enrollment.enrollment_exists(enrolling_student.id, course_instance_id):
        return redirect(url_for('student.dashboard'))
    
    # Check if course is full
    current_enrollments = Enrollment.count_active_enrollments_for_course(course_instance_id)
    if current_enrollments >= course.max_students:
        return "Course is full", 400
    
    # Get payable items for this course
    payable_items = []
    total_amount = 0
    
    if course.course_template:
        for payable_template in course.course_template.payable_templates.all():
            amount = int(payable_template.amount * 100)  # Convert to cents
            payable_items.append({
                'name': payable_template.name,
                'description': payable_template.description,
                'amount': amount,
                'amount_dollars': amount / 100
            })
            total_amount += amount
    
    context = {
        'current_user': user,
        'course': course,
        'payable_items': payable_items,
        'total_amount': total_amount,
        'total_amount_dollars': total_amount / 100,
        'stripe_publishable_key': os.getenv('STRIPE_PUBLISHABLE_KEY'),
        'enrolling_student': enrolling_student,
        'is_guest_enrollment': is_guest_enrollment,
        'guest_student_id': guest_student_id
    }
    
    return render_template('private/students/checkout/index.html', **context)


@student_bp.route('/payment-success/<int:enrollment_id>')
@login_required
@role_required('student')
def payment_success(enrollment_id):
    """Display payment success page."""
    user = Doorman.get_by_token(session['doorman_token']).user
    student = students.Student.query.filter_by(user_id=user.id).first()
    
    if not student:
        return "Student profile not found", 404
    
    # Get enrollment
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return "Enrollment not found", 404
    
    # Verify enrollment belongs to current student OR to a guest student created by current student
    enrolling_student = students.Student.query.get(enrollment.student_id)
    if not enrolling_student:
        return "Enrolling student not found", 404
    
    # Allow if enrollment is for current student OR for their guest student
    is_own_enrollment = enrollment.student_id == student.id
    is_guest_enrollment = enrolling_student.created_by_student_id == student.id
    
    if not (is_own_enrollment or is_guest_enrollment):
        return "Unauthorized", 403
    
    # Get payment
    payment = enrollment.get_payment()
    
    context = {
        'current_user': user,
        'enrollment': enrollment,
        'course': enrollment.course_instance,
        'payment': payment,
        'enrolling_student': enrolling_student,
        'is_guest_enrollment': is_guest_enrollment
    }
    
    return render_template('private/students/checkout/success.html', **context)


@student_bp.route('/payment-failed')
@login_required
@role_required('student')
def payment_failed():
    """Display payment failed page."""
    user = Doorman.get_by_token(session['doorman_token']).user
    
    context = {
        'current_user': user
    }
    
    return render_template('private/students/checkout/failed.html', **context)


@student_bp.route('/my-enrollments')
@login_required
@role_required('student')
def my_enrollments():
    """Display student's enrolled courses."""
    user = Doorman.get_by_token(session['doorman_token']).user
    student = students.Student.query.filter_by(user_id=user.id).first()
    
    if not student:
        return "Student profile not found", 404
    
    # Get all enrollments
    enrollments = Enrollment.get_by_student(student.id)
    
    context = {
        'current_user': user,
        'enrollments': enrollments
    }
    
    return render_template('private/students/enrollments/index.html', **context)


@student_bp.route('/guest/create', methods=['GET', 'POST'])
@login_required
@role_required('student')
def create_guest_student():
    """Route to create a guest student profile."""
    user = Doorman.get_by_token(session['doorman_token']).user
    student = students.Student.query.filter_by(user_id=user.id).first()
    
    if not student:
        return "Student profile not found", 404
    
    if request.method == 'POST':
        guest_first_name = request.form.get('guest_first_name')
        guest_last_name = request.form.get('guest_last_name')
        guest_email = request.form.get('guest_email')
        
        if not guest_first_name or not guest_last_name or not guest_email:
            return "All fields are required", 400
        
        # Create guest student profile
        guest_student = students.GuestStudent.create(
            student_id=student.id,
            first_name=guest_first_name,
            last_name=guest_last_name,
            email=guest_email
        )
        
        return redirect(url_for('student.dashboard'))
    
    context = {
        'current_user': user
    }
    
    return render_template('private/students/guests/create.html', **context)

# ------------------------------------------------------
# --------------------- API ROUTES ---------------------
# ------------------------------------------------------

@student_bp.route('/create-guest-account', methods=['POST'])
@login_required
@role_required('student')
def create_guest_account():
    """API route to create a guest student account."""
    try:
        user = Doorman.get_by_token(session['doorman_token']).user
        student = students.Student.query.filter_by(user_id=user.id).first()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'relationship']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field.replace("_", " ").title()} is required'}), 400
        
        # Check if email already exists
        existing_user = users.User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'A user with this email already exists'}), 400
        
        # Generate temporary password
        temp_password = generate_simple_password(10)
        
        # Create User account
        new_user = users.User.create(
            email=data['email'],
            password=hash_string(temp_password),
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data.get('phone_number', '')
        )
        
        # Create Student profile linked to the current student
        new_student = students.Student.create(
            user_id=new_user.id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            created_by_student_id=student.id,
            relationship=data['relationship']
        )
        
        # TODO: Send email with temporary password
        # send_guest_account_email(new_user.email, temp_password)
        
        return jsonify({
            'success': True, 
            'message': 'Guest account created successfully',
            'guest_id': new_student.id,
            'guest_student_id': new_student.id,
            'temp_password': temp_password  # TEMPORARY: Remove in production, only send via email
        }), 201
        
    except Exception as e:
        print(f"Error creating guest account: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while creating the guest account'}), 500


@student_bp.route('/guest-students', methods=['GET'])
@login_required
@role_required('student')
def get_guest_students():
    """API route to get all guest students for the current student."""
    try:
        user = Doorman.get_by_token(session['doorman_token']).user
        student = students.Student.query.filter_by(user_id=user.id).first()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        # Get all guest students created by this student
        guest_students = students.Student.query.filter_by(created_by_student_id=student.id).all()
        
        # Format guest student data
        guest_data = []
        for guest in guest_students:
            guest_user = users.User.query.get(guest.user_id)
            guest_data.append({
                'id': guest.id,
                'first_name': guest.first_name,
                'last_name': guest.last_name,
                'email': guest_user.email if guest_user else '',
                'phone_number': guest_user.phone_number if guest_user else '',
                'relationship': guest.relationship
            })
        
        return jsonify({
            'success': True,
            'guest_students': guest_data
        }), 200
        
    except Exception as e:
        print(f"Error fetching guest students: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred while fetching guest students'}), 500

@student_bp.route('/enrollment-details/<int:enrollment_id>')
@login_required
@role_required('student')
def enrollment_details(enrollment_id):
    """Display enrollment details page."""
    user = Doorman.get_by_token(session['doorman_token']).user
    student = students.Student.query.filter_by(user_id=user.id).first()
    
    if not student:
        return "Student profile not found", 404
    
    # Get enrollment
    enrollment = Enrollment.query.get(enrollment_id)
    if not enrollment:
        return "Enrollment not found", 404
    
    # Verify enrollment belongs to current student OR to a guest student created by current student
    enrolling_student = students.Student.query.get(enrollment.student_id)
    if not enrolling_student:
        return "Enrolling student not found", 404
    
    # Allow if enrollment is for current student OR for their guest student
    is_own_enrollment = enrollment.student_id == student.id
    is_guest_enrollment = enrolling_student.created_by_student_id == student.id
    
    if not (is_own_enrollment or is_guest_enrollment):
        return "Unauthorized", 403
    
    # Get payment
    payment = enrollment.get_payment()
    
    context = {
        'current_user': user,
        'enrollment': enrollment,
        'course': enrollment.course_instance,
        'payment': payment,
        'enrolling_student': enrolling_student,
        'is_guest_enrollment': is_guest_enrollment
    }
    
    return render_template('private/students/enrollments/details.html', **context)