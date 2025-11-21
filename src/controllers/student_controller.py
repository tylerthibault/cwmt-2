"""
Student Controller - Routes for student dashboard and operations
Handles all student-facing routes including dashboard, course viewing, enrollment management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from src.controllers.auth_controller import login_required
from src.logic.student_logic import StudentLogic
from src.logic.course_logic import CourseLogic, CourseBusinessError
from src.models.logbook import Logbook
from src.models.courses_model import Course
from src.models.course_enrollment import CourseEnrollment

# Create blueprint for student routes
student_bp = Blueprint('student', __name__, url_prefix='/student')


@student_bp.route('/')
@student_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Student dashboard - shows enrolled courses and overview
    """
    try:
        # Get current user from session
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        
        if not logbook_entry or not logbook_entry.user_id:
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for('auth.login'))
        
        user_id = logbook_entry.user_id
        user = logbook_entry.user
        
        # Get student profile
        student_profile = StudentLogic.get_student_profile(user_id)
        
        if not student_profile:
            flash("Student profile not found. Please contact support.", "error")
            return redirect(url_for('main.index'))
        
        # Get enrolled courses
        enrolled_courses = StudentLogic.get_student_courses(student_profile.id)
        
        # Filter out withdrawn courses - only show active and completed
        active_enrollments = [e for e in enrolled_courses if e.status not in ['withdrawn', 'cancelled']]
        
        # Organize courses by status
        active_courses = [e for e in active_enrollments if e.status == 'active']
        completed_courses = [e for e in active_enrollments if e.status == 'completed']
        
        context = {
            'user': user,
            'current_role': 'student',
            'student_profile': student_profile,
            'enrolled_courses': [enrollment.course for enrollment in active_enrollments],
            'active_courses': active_courses,
            'completed_courses': completed_courses,
            'total_enrollments': len(active_enrollments),
            'active_count': len(active_courses),
            'completed_count': len(completed_courses)
        }
        
        return render_template('private/student/index.html', **context)
        
    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", "error")
        return redirect(url_for('main.index'))


@student_bp.route('/my-courses')
@login_required
def my_courses():
    """
    View all enrolled courses with filtering options
    """
    try:
        # Get current user
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        
        if not logbook_entry or not logbook_entry.user_id:
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for('auth.login'))
        
        user_id = logbook_entry.user_id
        student_profile = StudentLogic.get_student_profile(user_id)
        
        if not student_profile:
            flash("Student profile not found.", "error")
            return redirect(url_for('main.index'))
        
        # Get filter parameter
        status_filter = request.args.get('status', 'all')
        
        # Get enrollments
        enrollments = StudentLogic.get_student_courses(student_profile.id)
        
        # Apply filter
        if status_filter != 'all':
            enrollments = [e for e in enrollments if e.status == status_filter]
        
        context = {
            'user': logbook_entry.user,
            'current_role': 'student',
            'enrollments': enrollments,
            'status_filter': status_filter
        }
        
        return render_template('private/student/my_courses.html', **context)
        
    except Exception as e:
        flash(f"Error loading courses: {str(e)}", "error")
        return redirect(url_for('student.dashboard'))


@student_bp.route('/course/<int:course_id>')
@login_required
def view_course(course_id):
    """
    View details of a specific enrolled course
    """
    try:
        # Get current user
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()

        print("*"*100)
        
        if not logbook_entry or not logbook_entry.user_id:
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for('auth.login'))
        
        user_id = logbook_entry.user_id
        student_profile = StudentLogic.get_student_profile(user_id)
        
        if not student_profile:
            flash("Student profile not found.", "error")
            return redirect(url_for('main.index'))
        
        # Get course
        course = Course.query.get(course_id)
        if not course:
            flash("Course not found.", "error")
            return redirect(url_for('student.my_courses'))
        
        # Verify student is enrolled in this course
        enrollment = CourseEnrollment.query.filter_by(
            student_id=student_profile.id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            flash("You are not enrolled in this course.", "error")
            return redirect(url_for('student.my_courses'))
        
        context = {
            'user': logbook_entry.user,
            'current_role': 'student',
            'course': course,
            'enrollment': enrollment,
            'student_profile': student_profile
        }
        
        return render_template('private/student/my_course/index.html', **context)
        
    except Exception as e:
        flash(f"Error loading course: {str(e)}", "error")
        return redirect(url_for('student.dashboard'))


@student_bp.route('/available-courses')
@login_required
def available_courses():
    """
    Browse available courses for enrollment
    """
    try:
        # Get current user
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        
        if not logbook_entry or not logbook_entry.user_id:
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for('auth.login'))
        
        user_id = logbook_entry.user_id
        student_profile = StudentLogic.get_student_profile(user_id)
        
        # Get available courses (scheduled, not full, in the future)
        all_available = CourseLogic.get_available_courses()
        
        # Debug: Log what we got
        from flask import current_app
        current_app.logger.info(f"Total available courses from CourseLogic: {len(all_available)}")
        
        # Get student's current ACTIVE enrollments to filter out (allow re-enrollment if withdrawn)
        active_enrolled_course_ids = []
        if student_profile:
            enrollments = StudentLogic.get_student_courses(student_profile.id)
            active_enrolled_course_ids = [e.course_id for e in enrollments if e.status not in ['withdrawn', 'cancelled']]
            current_app.logger.info(f"Student has {len(active_enrolled_course_ids)} active enrollments to filter out")
        
        available_courses = [c for c in all_available if c.id not in active_enrolled_course_ids]
        current_app.logger.info(f"Available courses for student after filtering: {len(available_courses)}")
        
        context = {
            'user': logbook_entry.user,
            'current_role': 'student',
            'available_courses': available_courses,
            'student_profile': student_profile
        }
        
        return render_template('private/student/available_courses/index.html', **context)
        
    except Exception as e:
        flash(f"Error loading available courses: {str(e)}", "error")
        return redirect(url_for('student.dashboard'))


@student_bp.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_in_course(course_id):
    """
    Enroll student in a course
    """
    try:
        # Get current user
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        
        if not logbook_entry or not logbook_entry.user_id:
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for('auth.login'))
        
        user_id = logbook_entry.user_id
        
        # Attempt enrollment
        course = CourseLogic.enroll_student(
            course_id=course_id,
            student_id=user_id,  # This is the user_id which enroll_student expects
            is_admin_override=False
        )
        
        # After successful enrollment, update vehicle information if provided
        student_profile = StudentLogic.get_student_profile(user_id)
        if student_profile:
            # Find the enrollment we just created
            enrollment = CourseEnrollment.query.filter_by(
                student_id=student_profile.id,
                course_id=course_id
            ).first()
            
            if enrollment:
                # Update with vehicle information from form
                vehicle_data = {
                    'brings_motorcycle': request.form.get('brings_motorcycle') == 'on',
                    'motorcycle_make': request.form.get('motorcycle_make'),
                    'motorcycle_model': request.form.get('motorcycle_model'),
                    'motorcycle_year': request.form.get('motorcycle_year'),
                    'motorcycle_license_plate': request.form.get('motorcycle_license_plate'),
                    'notes': request.form.get('notes')
                }
                StudentLogic.update_enrollment(enrollment.id, vehicle_data)
        
        flash(f"Successfully enrolled in {course.template.name}!", "success")
        return redirect(url_for('student.view_course', course_id=course_id))
        
    except CourseBusinessError as e:
        flash(str(e), "error")
        return redirect(url_for('student.available_courses'))
    except Exception as e:
        flash(f"Enrollment failed: {str(e)}", "error")
        return redirect(url_for('student.available_courses'))


@student_bp.route('/course/<int:course_id>/update-vehicle', methods=['POST'])
@login_required
def update_vehicle_info(course_id):
    """
    Update vehicle information for an enrollment
    """
    try:
        # Get current user
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        
        if not logbook_entry or not logbook_entry.user_id:
            return jsonify({'success': False, 'message': 'Session expired'}), 401
        
        user_id = logbook_entry.user_id
        student_profile = StudentLogic.get_student_profile(user_id)
        
        if not student_profile:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        # Get enrollment
        enrollment = CourseEnrollment.query.filter_by(
            student_id=student_profile.id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            return jsonify({'success': False, 'message': 'Enrollment not found'}), 404
        
        # Update vehicle data
        vehicle_data = {
            'brings_motorcycle': request.form.get('brings_motorcycle') == 'true',
            'motorcycle_make': request.form.get('motorcycle_make'),
            'motorcycle_model': request.form.get('motorcycle_model'),
            'motorcycle_year': request.form.get('motorcycle_year'),
            'motorcycle_license_plate': request.form.get('motorcycle_license_plate')
        }
        
        StudentLogic.update_enrollment(enrollment.id, vehicle_data)
        
        return jsonify({'success': True, 'message': 'Vehicle information updated'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@student_bp.route('/course/<int:course_id>/withdraw', methods=['POST'])
@login_required
def withdraw_from_course(course_id):
    """
    Withdraw from a course
    """
    try:
        # Get current user
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        
        if not logbook_entry or not logbook_entry.user_id:
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for('auth.login'))
        
        user_id = logbook_entry.user_id
        student_profile = StudentLogic.get_student_profile(user_id)
        
        if not student_profile:
            flash("Student profile not found.", "error")
            return redirect(url_for('main.index'))
        
        # Get enrollment to withdraw
        enrollment = CourseEnrollment.query.filter_by(
            student_id=student_profile.id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            raise ValueError("Enrollment not found")
        
        # Get withdrawal reason and add to notes
        reason = request.form.get('reason', '')
        if reason:
            current_notes = enrollment.notes or ''
            enrollment.notes = f"{current_notes}\nWithdrawal reason: {reason}".strip()
        
        # Attempt withdrawal
        StudentLogic.unenroll_from_course(enrollment.id)
        
        flash("Successfully withdrawn from course.", "success")
        return redirect(url_for('student.my_courses'))
        
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for('student.view_course', course_id=course_id))
    except Exception as e:
        flash(f"Withdrawal failed: {str(e)}", "error")
        return redirect(url_for('student.view_course', course_id=course_id))


@student_bp.route('/profile')
@login_required
def profile():
    """
    View and edit student profile
    """
    try:
        # Get current user
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        
        if not logbook_entry or not logbook_entry.user_id:
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for('auth.login'))
        
        user = logbook_entry.user
        student_profile = StudentLogic.get_student_profile(user.id)
        
        if not student_profile:
            flash("Student profile not found.", "error")
            return redirect(url_for('main.index'))
        
        context = {
            'current_user': user,
            'student_profile': student_profile
        }
        
        return render_template('private/student/profile.html', **context)
        
    except Exception as e:
        flash(f"Error loading profile: {str(e)}", "error")
        return redirect(url_for('student.dashboard'))


@student_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """
    Update student profile information
    """
    try:
        # Get current user
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        
        if not logbook_entry or not logbook_entry.user_id:
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for('auth.login'))
        
        user_id = logbook_entry.user_id
        student_profile = StudentLogic.get_student_profile(user_id)
        
        if not student_profile:
            flash("Student profile not found.", "error")
            return redirect(url_for('main.index'))
        
        # Get update data from form
        update_data = {
            'emergency_contact_name': request.form.get('emergency_contact_name'),
            'emergency_contact_phone': request.form.get('emergency_contact_phone'),
            'grade_level': request.form.get('grade_level')
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        # Update profile
        StudentLogic.update_student_profile(student_profile.id, update_data)
        
        flash("Profile updated successfully!", "success")
        return redirect(url_for('student.profile'))
        
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for('student.profile'))
    except Exception as e:
        flash(f"Update failed: {str(e)}", "error")
        return redirect(url_for('student.profile'))


@student_bp.route('/payments')
@login_required
def payments():
    """
    View payment history and pending payments
    """
    try:
        # Get current user
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        
        if not logbook_entry or not logbook_entry.user_id:
            flash("Session expired. Please log in again.", "error")
            return redirect(url_for('auth.login'))
        
        user_id = logbook_entry.user_id
        student_profile = StudentLogic.get_student_profile(user_id)
        
        if not student_profile:
            flash("Student profile not found.", "error")
            return redirect(url_for('main.index'))
        
        # TODO: Get payment history from payment system
        # This will be implemented when payment models are added
        
        context = {
            'user': logbook_entry.user,
            'current_role': 'student',
            'student_profile': student_profile,
            'payments': [],  # Placeholder for payment data
            'pending_payments': []  # Placeholder for pending payments
        }
        
        return render_template('private/student/payments.html', **context)
        
    except Exception as e:
        flash(f"Error loading payments: {str(e)}", "error")
        return redirect(url_for('student.dashboard'))
