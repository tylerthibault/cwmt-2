from datetime import datetime
import json
import os
from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify
from src.models.user_folder import students, users
from src.models.course_folder import course_instances
from src.models.course_folder.enrollments import Enrollment
from src.models.stripe.payments import Payment
from src.models.doorman import Doorman
from src.models.logs import Log
from src.models.app_settings import AppSettings
from src.utils.custom_decorators import login_required, role_required
from src.utils.password_management import generate_simple_password, hash_string

# Create blueprint
student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@login_required
@role_required('student')
def dashboard():
    """Student dashboard route."""
    user = Doorman.get_by_token(session['doorman_token']).user
    student = students.Student.query.filter_by(user_id=user.id).first()
    
    # Get student's enrollments
    enrollments = []
    active_count = 0
    completed_count = 0
    upcoming_count = 0
    enrolled_course_ids = []  # Track which courses student is enrolled in
    
    if student:
        enrollments = Enrollment.get_by_student(student.id)
        today = datetime.now().date()
        
        for enrollment in enrollments:
            if enrollment.status == 'enrolled':
                # Track enrolled course IDs
                enrolled_course_ids.append(enrollment.course_instance_id)
                
                # Check if course is upcoming or active
                if enrollment.course_instance.start_date > today:
                    upcoming_count += 1
                else:
                    active_count += 1
            elif enrollment.status == 'completed':
                completed_count += 1
    
    # Get ALL scheduled courses for calendar (not just enrolled ones)
    all_instances = course_instances.CourseInstance.query.filter_by(status='scheduled').all()
    events = []
    
    for instance in all_instances:
        template = instance.course_template
        if template:
            # Get instructor names
            c1_name = instance.c1_instructor.user.get_full_name() if instance.c1_instructor else None
            c2_name = instance.c2_instructor.user.get_full_name() if instance.c2_instructor else None
            
            instructor_text = None
            if c1_name and c2_name:
                instructor_text = f"{c1_name} & {c2_name}"
            elif c1_name:
                instructor_text = c1_name
            elif c2_name:
                instructor_text = c2_name
            
            # Get enrollment count
            enrollment_count = len([e for e in instance.enrollments if e.status == 'enrolled'])
            
            # Get location name (instance.location might be a Location object or string)
            location_name = instance.location
            if hasattr(instance.location, 'name'):
                location_name = instance.location.name
            elif hasattr(instance.location, 'location'):
                location_name = instance.location.location
            
            events.append({
                'id': instance.id,
                'title': template.name,
                'start': instance.start_date.isoformat(),
                'startTime': instance.start_time.strftime('%H:%M') if instance.start_time else None,
                'duration': instance.duration_days,
                'durationDays': instance.duration_days,
                'location': location_name,
                'color': template.color or '#0d6efd',
                'maxStudents': instance.max_students,
                'capacity': instance.max_students,
                'enrolled': enrollment_count,
                'enrollmentCount': enrollment_count,
                'status': instance.status,
                'instructorC1Id': instance.c1_instructor_id,
                'instructorC2Id': instance.c2_instructor_id,
                'instructorText': instructor_text,
                'experienceLevel': template.experience_level,
                'templateId': template.id,
                'description': template.description or '',
                'shortBlurb': template.short_blurb or ''
            })
    
    # Get guest students created by this student
    guest_students = []
    guest_students_data = []
    if student:
        guest_students = students.Student.query.filter_by(created_by_student_id=student.id).all()
        # Add enrollment count for each guest
        for guest in guest_students:
            guest.enrollment_count = len(Enrollment.get_by_student(guest.id))
            guest_students_data.append({
                'id': guest.id,
                'first_name': guest.first_name,
                'last_name': guest.last_name,
                'relationship': guest.relationship
            })
    
    context = {
        'current_user': user,
        'current_student_id': student.id if student else None,
        'events_json': json.dumps(events),
        'enrolled_course_ids': json.dumps(enrolled_course_ids),
        'guest_students_json': json.dumps(guest_students_data),
        'enrollments': enrollments,
        'active_count': active_count,
        'completed_count': completed_count,
        'upcoming_count': upcoming_count,
        'total_enrollments': len(enrollments),
        'guest_students': guest_students
    }
    return render_template('private/students/dashboard/index.html', **context)


@student_bp.route('/family-friends')
@login_required
@role_required('student')
def family_friends():
    """Family and friends management page."""
    user = Doorman.get_by_token(session['doorman_token']).user
    student = students.Student.query.filter_by(user_id=user.id).first()
    
    if not student:
        return render_template('errors/404.html'), 404
    
    # Get all guest students created by this student
    guest_students_query = students.Student.query.filter_by(created_by_student_id=student.id).all()
    
    # Build guest data with enrollment count and user details
    guest_students = []
    for guest in guest_students_query:
        guest_user = users.User.query.get(guest.user_id)
        guest_data = {
            'id': guest.id,
            'first_name': guest.first_name,
            'last_name': guest.last_name,
            'relationship': guest.relationship,
            'email': guest_user.email if guest_user else '',
            'phone_number': guest_user.phone_number if guest_user else '',
            'enrollment_count': len(Enrollment.get_by_student(guest.id)),
            'is_active': True
        }
        guest_students.append(guest_data)
    
    return render_template('private/students/family_friends/index.html', 
                         guest_students=guest_students,
                         current_user=user)



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
    subtotal = 0
    
    if course.course_template:
        for payable_template in course.course_template.payable_templates.all():
            amount = int(payable_template.amount * 100)  # Convert to cents
            payable_items.append({
                'id': payable_template.id,
                'name': payable_template.name,
                'description': payable_template.description,
                'amount': amount,
                'amount_dollars': amount / 100,
                'is_required': payable_template.is_required
            })
            subtotal += amount
    
    # Calculate pricing with tax
    subtotal_dollars = subtotal / 100
    subtotal_amount, tax_amount, total_amount = course.calculate_pricing()
    
    # Convert to cents for Stripe
    total_amount_cents = int(total_amount * 100)
    tax_amount_cents = int(tax_amount * 100)
    
    # Get Stripe publishable key from AppSettings
    settings = AppSettings.get_settings()
    stripe_pub_key = settings.stripe_publishable_key or os.getenv('STRIPE_PUBLISHABLE_KEY')
    
    context = {
        'current_user': user,
        'course': course,
        'payable_items': payable_items,
        'subtotal': subtotal,
        'subtotal_dollars': subtotal_dollars,
        'tax_amount': tax_amount_cents,
        'tax_amount_dollars': tax_amount,
        'tax_rate': float(course.tax_rate),
        'total_amount': total_amount_cents,
        'total_amount_dollars': total_amount,
        'stripe_publishable_key': stripe_pub_key,
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
        try:
            new_user = users.User.create(
                email=data['email'],
                password=hash_string(temp_password),
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone_number=data.get('phone_number', '')
            )
        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)}), 400
        
        # Create Student profile linked to the current student
        new_student = students.Student.create(
            user_id=new_user.id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            created_by_student_id=student.id,
            relationship=data['relationship']
        )
        
        # Log guest account creation
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='create_guest_account',
            description=f'{user.first_name} {user.last_name} created guest account for {new_student.first_name} {new_student.last_name}',
            user_id=user.id,
            target_type='student',
            target_id=new_student.id,
            status='success',
            extra_data={
                'guest_email': data['email'],
                'relationship': data['relationship']
            }
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

@student_bp.route('/guest/<int:guest_id>')
@login_required
@role_required('student')
def view_guest(guest_id):
    """View details of a guest student account."""
    user = Doorman.get_by_token(session['doorman_token']).user
    current_student = students.Student.query.filter_by(user_id=user.id).first()
    
    if not current_student:
        return render_template('errors/404.html'), 404
    
    # Get the guest student
    guest = students.Student.query.get_or_404(guest_id)
    
    # Verify that this guest was created by the current student
    if guest.created_by_student_id != current_student.id:
        return render_template('errors/403.html'), 403
    
    # Get the guest's user account
    guest_user = users.User.query.get(guest.user_id)
    
    # Get guest's enrollments
    guest_enrollments = Enrollment.get_by_student(guest.id)

    # current user
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    return render_template('private/students/guest/view.html', 
                         guest=guest, 
                         guest_user=guest_user,
                         enrollments=guest_enrollments,
                         current_user=current_user)

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
        'is_guest_enrollment': is_guest_enrollment,
        'current_student_id': student.id
    }
    
    return render_template('private/students/enrollments/details.html', **context)


@student_bp.route('/api/enrollments/<int:enrollment_id>/request-unenrollment', methods=['POST'])
@login_required
@role_required('student')
def request_unenrollment(enrollment_id):
    """Submit an unenrollment request."""
    try:
        user = Doorman.get_by_token(session['doorman_token']).user
        student = students.Student.query.filter_by(user_id=user.id).first()
        
        if not student:
            return jsonify({'error': 'Student profile not found'}), 404
        
        # Get enrollment
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        # Verify ownership
        enrolling_student = students.Student.query.get(enrollment.student_id)
        is_own_enrollment = enrollment.student_id == student.id
        is_guest_enrollment = enrolling_student.created_by_student_id == student.id
        
        if not (is_own_enrollment or is_guest_enrollment):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get reason from request
        data = request.get_json()
        reason = data.get('reason', '')
        
        # Request unenrollment
        try:
            enrollment.request_unenrollment(reason=reason)
            
            # Log unenrollment request
            Log.create_log(
                log_type=Log.TYPE_USER_ACTION,
                action='request_unenrollment',
                description=f'{user.first_name} {user.last_name} requested unenrollment from {enrollment.course_instance.course_template.name}',
                user_id=user.id,
                target_type='enrollment',
                target_id=enrollment.id,
                status='success',
                extra_data={
                    'course_name': enrollment.course_instance.course_template.name,
                    'reason': reason,
                    'student_id': enrolling_student.id
                }
            )
            
            return jsonify({
                'success': True,
                'message': 'Unenrollment request submitted successfully'
            }), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@student_bp.route('/settings')
@login_required
@role_required('student')
def settings():
    """Student settings page."""
    user = Doorman.get_by_token(session['doorman_token']).user
    student = students.Student.query.filter_by(user_id=user.id).first()
    
    context = {
        'current_user': user,
        'student': student
    }
    return render_template('private/students/settings/index.html', **context)


@student_bp.route('/settings/update-profile', methods=['POST'])
@login_required
@role_required('student')
def update_profile():
    """Update student profile information."""
    from flask import flash
    
    user = Doorman.get_by_token(session['doorman_token']).user
    student = students.Student.query.filter_by(user_id=user.id).first()
    
    try:
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        
        # Validate required fields
        if not all([first_name, last_name, email]):
            flash('First name, last name, and email are required.', 'danger')
            return redirect(url_for('student.settings'))
        
        # Check if email is already taken by another user
        existing_user = users.User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user.id:
            flash('This email address is already in use.', 'danger')
            return redirect(url_for('student.settings'))
        
        # Update user information
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()
        
        # Update student information
        if student:
            student.first_name = first_name
            student.last_name = last_name
            student.phone_number = phone_number
            student.save()
        
        # Log profile update
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='update_profile',
            description=f'{user.first_name} {user.last_name} updated their profile',
            user_id=user.id,
            target_type='user',
            target_id=user.id,
            status='success',
            extra_data={'email': email}
        )
        
        flash('Profile updated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'danger')
    
    return redirect(url_for('student.settings'))


@student_bp.route('/settings/update-password', methods=['POST'])
@login_required
@role_required('student')
def update_password():
    """Update student password."""
    from flask import flash
    from src.utils.password_management import verify_hash
    
    user = Doorman.get_by_token(session['doorman_token']).user
    
    try:
        # Get form data
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate required fields
        if not all([current_password, new_password, confirm_password]):
            flash('All password fields are required.', 'danger')
            return redirect(url_for('student.settings'))
        
        # Verify current password
        if not verify_hash(user.password_hash, current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('student.settings'))
        
        # Validate new password
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'danger')
            return redirect(url_for('student.settings'))
        
        # Check if passwords match
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('student.settings'))
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Log password change
        Log.create_log(
            log_type=Log.TYPE_AUTH,
            action='password_change',
            description=f'{user.first_name} {user.last_name} changed their password',
            user_id=user.id,
            target_type='user',
            target_id=user.id,
            status='success',
            extra_data={'ip_address': request.remote_addr}
        )
        
        flash('Password updated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating password: {str(e)}', 'danger')
    
    return redirect(url_for('student.settings'))

@student_bp.route('/settings/delete-account', methods=['POST'])
@login_required
@role_required('student')
def delete_account():
    """Soft delete student account by setting is_active to False."""
    from flask import flash
    
    user = Doorman.get_by_token(session['doorman_token']).user
    
    try:
        # Get student record
        student = students.Student.query.filter_by(user_id=user.id).first()
        
        # Set is_active to False for soft delete
        user.is_active = False
        user.save()
        
        # Also deactivate student record if it exists
        if student:
            student.is_active = False
            student.save()
        
        # Log account deletion
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='delete_account',
            description=f'{user.first_name} {user.last_name} deleted their account',
            user_id=user.id,
            target_type='user',
            target_id=user.id,
            status='success',
            extra_data={'email': user.email, 'deletion_type': 'self_service'}
        )
        
        # Clear session and log out
        session.clear()
        
        flash('Your account has been deactivated successfully.', 'success')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        flash(f'Error deactivating account: {str(e)}', 'danger')
        return redirect(url_for('student.settings'))
