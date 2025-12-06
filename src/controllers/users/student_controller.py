"""
Student Controller - Routes for student dashboard and operations
Handles all student-facing routes including dashboard, course viewing, enrollment management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from src.controllers.auth_controller import login_required
from src.logic.student_logic import StudentLogic
from src.logic.course_logic import CourseLogic, CourseBusinessError
from src.logic.payment_logic import PaymentLogic, PaymentValidationError, PaymentBusinessError
from src.models.logbook import Logbook
from src.models.courses_model import Course
from src.models.course_enrollment import CourseEnrollment
from decimal import Decimal
import os
import stripe

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
    import logging
    logger = logging.getLogger(__name__)
    
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
        
        # Check if returning from Stripe payment (payment_intent in query params)
        payment_intent_id = request.args.get('payment_intent')
        if payment_intent_id:
            logger.info(f"Detected return from Stripe with payment_intent: {payment_intent_id}")
            try:
                # Initialize Stripe
                stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
                
                # Retrieve the payment intent from Stripe
                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                logger.info(f"Payment intent status: {intent.status}")
                
                # If payment succeeded and not already recorded
                if intent.status == 'succeeded':
                    # Check if we already recorded this payment
                    from src.models.payment_models import Payment
                    existing_payment = Payment.query.filter_by(
                        stripe_payment_intent_id=payment_intent_id
                    ).first()
                    
                    if not existing_payment:
                        logger.info("Payment succeeded but not recorded - processing now")
                        # Extract metadata and record payment
                        metadata = intent.metadata
                        enrollment_id = metadata.get('enrollment_id')
                        line_item_ids = metadata.get('line_item_ids', '').split(',')
                        
                        if enrollment_id and line_item_ids:
                            amount = Decimal(intent.amount) / 100
                            
                            PaymentLogic.record_payment(
                                enrollment_id=int(enrollment_id),
                                line_item_ids=[int(id) for id in line_item_ids if id],
                                amount=amount,
                                payment_method='stripe',
                                processed_by_user_id=user_id,
                                stripe_payment_intent_id=payment_intent_id,
                                stripe_charge_id=intent.charges.data[0].id if intent.charges.data else None,
                                notes='Payment recorded on return (webhook backup)'
                            )
                            
                            flash("Payment successful! Your items have been paid.", "success")
                            logger.info(f"Payment recorded successfully for intent {payment_intent_id}")
                    else:
                        logger.info("Payment already recorded")
                        flash("Payment confirmed!", "success")
                        
            except Exception as e:
                logger.error(f"Error checking payment intent: {str(e)}", exc_info=True)
                flash("Payment may be processing. Please refresh if items still show as pending.", "info")
        
        # Get payment information for this enrollment
        payment_summary = PaymentLogic.get_enrollment_payment_summary(enrollment.id)
        line_items = PaymentLogic.get_enrollment_line_items(enrollment.id)
        
        context = {
            'user': logbook_entry.user,
            'current_role': 'student',
            'course': course,
            'enrollment': enrollment,
            'student_profile': student_profile,
            'payment_summary': payment_summary,
            'line_items': line_items
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


@student_bp.route('/course/<int:course_id>/payment')
@login_required
def payment_selection(course_id):
    """
    Show payment selection page for a course.
    Displays available payable items that student can select and pay for.
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
        
        # Get course and verify enrollment
        course = Course.query.get_or_404(course_id)
        enrollment = CourseEnrollment.query.filter_by(
            student_id=student_profile.id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            flash("You are not enrolled in this course.", "error")
            return redirect(url_for('student.available_courses'))
        
        # Get available payable items for this course
        payable_items = PaymentLogic.get_course_payable_items(course_id)
        
        # Get existing line items for this enrollment
        existing_line_items = PaymentLogic.get_enrollment_line_items(enrollment.id)
        
        # Get payment summary
        payment_summary = PaymentLogic.get_enrollment_payment_summary(enrollment.id)
        
        # Map existing line items by course_payable_item_id
        existing_map = {item.course_payable_item_id: item for item in existing_line_items}
        
        # Organize items with their status
        items_with_status = []
        for payable_item in payable_items:
            line_item = existing_map.get(payable_item.id)
            items_with_status.append({
                'payable_item': payable_item,
                'line_item': line_item,
                'is_paid': line_item.status == 'paid' if line_item else False,
                'is_pending': line_item.status == 'pending' if line_item else False,
                'is_rejected': line_item.status == 'rejected' if line_item else False,
                'amount_due': (line_item.total - line_item.amount_paid) if line_item else payable_item.price
            })
        
        context = {
            'user': logbook_entry.user,
            'current_role': 'student',
            'student_profile': student_profile,
            'course': course,
            'enrollment': enrollment,
            'items_with_status': items_with_status,
            'payment_summary': payment_summary,
            'stripe_publishable_key': os.getenv('STRIPE_PUBLISHABLE_KEY')
        }
        
        return render_template('private/student/payment_selection.html', **context)
        
    except Exception as e:
        flash(f"Error loading payment page: {str(e)}", "error")
        return redirect(url_for('student.view_course', course_id=course_id))


@student_bp.route('/course/<int:course_id>/add-to-cart', methods=['POST'])
@login_required
def add_items_to_cart(course_id):
    """
    Add selected payable items to the enrollment (create line items).
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
        
        # Get selected items from request
        data = request.get_json()
        payable_item_ids = data.get('payable_item_ids', [])
        
        if not payable_item_ids:
            return jsonify({'success': False, 'message': 'No items selected'}), 400
        
        # Create line items
        line_items = PaymentLogic.create_line_items_for_enrollment(
            enrollment_id=enrollment.id,
            payable_item_ids=payable_item_ids
        )
        
        return jsonify({
            'success': True,
            'message': f'{len(line_items)} item(s) added',
            'line_items': [item.to_dict() for item in line_items]
        })
        
    except PaymentValidationError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except PaymentBusinessError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@student_bp.route('/course/<int:course_id>/create-payment-intent', methods=['POST'])
@login_required
def create_payment_intent(course_id):
    """
    Create a Stripe Payment Intent for selected line items.
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
        
        # Get selected line items from request
        data = request.get_json()
        line_item_ids = data.get('line_item_ids', [])
        
        if not line_item_ids:
            return jsonify({'success': False, 'message': 'No items selected'}), 400
        
        # Create payment intent
        intent_data = PaymentLogic.create_stripe_payment_intent(
            enrollment_id=enrollment.id,
            line_item_ids=line_item_ids,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'client_secret': intent_data['client_secret'],
            'payment_intent_id': intent_data['payment_intent_id'],
            'amount': intent_data['amount']
        })
        
    except PaymentValidationError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except PaymentBusinessError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@student_bp.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """
    Handle Stripe webhook events.
    Note: This route does not require login as it's called by Stripe.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        payload = request.data
        sig_header = request.headers.get('Stripe-Signature')
        
        logger.info(f"Received Stripe webhook - Signature present: {bool(sig_header)}")
        
        if not sig_header:
            logger.error("Missing Stripe signature in webhook")
            return jsonify({'error': 'Missing signature'}), 400
        
        result = PaymentLogic.process_stripe_webhook(payload, sig_header)
        logger.info(f"Webhook processed successfully: {result}")
        
        return jsonify(result), 200
        
    except PaymentBusinessError as e:
        logger.error(f"Payment business error in webhook: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected webhook error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Webhook error: {str(e)}'}), 500


@student_bp.route('/refund-request/<int:line_item_id>', methods=['POST'])
@login_required
def request_refund(line_item_id):
    """
    Create a refund request for a paid line item.
    Request will be sent to superuser for approval.
    """
    try:
        # Get current user
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        
        if not logbook_entry or not logbook_entry.user_id:
            return jsonify({'success': False, 'message': 'Session expired'}), 401
        
        user_id = logbook_entry.user_id
        
        # Get request data
        data = request.get_json()
        amount = Decimal(str(data.get('amount', 0)))
        reason = data.get('reason', '').strip()
        
        if not reason:
            return jsonify({'success': False, 'message': 'Please provide a reason for the refund request'}), 400
        
        # Create refund request
        refund = PaymentLogic.request_refund(
            line_item_id=line_item_id,
            user_id=user_id,
            amount=amount,
            reason=reason
        )
        
        return jsonify({
            'success': True,
            'message': 'Refund request submitted successfully. A superuser will review your request.',
            'refund_id': refund.id
        })
        
    except PaymentValidationError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creating refund request: {str(e)}'}), 500
