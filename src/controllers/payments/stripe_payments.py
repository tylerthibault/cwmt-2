from flask import Blueprint, request, jsonify, session
import stripe
import os
from src.models.stripe.payments import Payment
from src.models.course_folder.course_instances import CourseInstance
from src.models.user_folder.students import Student
from src.models.logs import Log
from src.utils.custom_decorators import login_required, role_required
from src.models.doorman import Doorman
from src.models.app_settings import AppSettings
import uuid

# Create blueprint
stripe_payments_bp = Blueprint('stripe_payments', __name__, url_prefix='/api/payments')


def _get_stripe_key():
    """Get Stripe secret key from AppSettings."""
    settings = AppSettings.get_settings()
    key = settings.get_stripe_secret_key()
    if not key:
        # Fallback to environment variable for backward compatibility
        key = os.getenv('STRIPE_SECRET_KEY')
    return key


@stripe_payments_bp.route('/create-intent', methods=['POST'])
@login_required
@role_required('student')
def create_payment_intent():
    """Create a Stripe PaymentIntent for course enrollment."""
    # Set Stripe API key from settings
    stripe.api_key = _get_stripe_key()
    
    try:
        data = request.get_json()
        course_instance_id = data.get('course_instance_id')
        guest_student_id = data.get('guest_student_id')  # Optional: for guest enrollments
        payable_template_ids = data.get('payable_template_ids', [])  # Optional: selected payables
        
        if not course_instance_id:
            return jsonify({'error - c93c6b62': 'Course instance ID is required'}), 400
        
        # Get current user (who is paying)
        doorman = Doorman.get_by_token(session['doorman_token'])
        paying_student = doorman.user.student
        
        if not paying_student:
            return jsonify({'error - af0351c1': 'Student profile not found'}), 404
        
        # Determine which student is enrolling
        enrolling_student = paying_student
        if guest_student_id:
            guest_student = Student.query.get(guest_student_id)
            if not guest_student or guest_student.created_by_student_id != paying_student.id:
                return jsonify({'error - invalid_guest': 'Invalid guest student'}), 403
            enrolling_student = guest_student
        
        # Get course instance
        course_instance = CourseInstance.query.get(course_instance_id)
        if not course_instance:
            return jsonify({'error - 86bed1e3': 'Course not found'}), 404
        
        # Check if course is full
        from src.models.course_folder.enrollments import Enrollment
        current_enrollments = Enrollment.count_active_enrollments_for_course(course_instance_id)
        if current_enrollments >= course_instance.max_students:
            return jsonify({'error - d170295e': 'Course is full'}), 400
        
        # Check if enrolling student is already enrolled
        if Enrollment.enrollment_exists(enrolling_student.id, course_instance_id):
            return jsonify({'error - ba680fe4': 'Already enrolled in this course'}), 400
        
        # Calculate total amount based on selected payables
        subtotal = 0
        line_items = []
        
        if course_instance.course_template:
            for payable_template in course_instance.course_template.payable_templates.all():
                # If specific payables were selected, only include those
                # If none were selected (empty list), include all (backward compatibility)
                # Always include required items regardless of selection
                should_include = (
                    payable_template.is_required or 
                    not payable_template_ids or 
                    payable_template.id in payable_template_ids
                )
                
                if should_include:
                    # Amount is already in cents in the database
                    amount_in_cents = int(payable_template.amount * 100)
                    subtotal += amount_in_cents
                    line_items.append({
                        'payable_template_id': payable_template.id,
                        'name': payable_template.name,
                        'amount': amount_in_cents,
                        'description': payable_template.description
                    })
        
        if subtotal == 0:
            return jsonify({'error - c93a5378': 'No payment items selected'}), 400
        
        # Verify at least one required item is included
        has_required = any(
            pt.is_required for pt in course_instance.course_template.payable_templates.all()
            if pt.id in [item['payable_template_id'] for item in line_items]
        )
        if not has_required and course_instance.course_template.payable_templates.filter_by(is_required=True).first():
            return jsonify({'error - missing_required': 'Required payment items must be included'}), 400
        
        # Calculate tax based on selected items subtotal
        subtotal_dollars = subtotal / 100
        tax_rate = float(course_instance.tax_rate) if course_instance.tax_rate else 0.0
        tax_amount = subtotal * tax_rate  # Already in cents
        total_amount = subtotal + int(tax_amount)
        
        # Generate idempotency key
        idempotency_key = str(uuid.uuid4())
        
        # Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=total_amount,
            currency='usd',
            metadata={
                'student_id': enrolling_student.id,
                'paying_student_id': paying_student.id,
                'course_instance_id': course_instance_id,
                'student_email': doorman.user.email,
                'is_guest_enrollment': 'true' if guest_student_id else 'false'
            },
            idempotency_key=idempotency_key
        )
        
        # Create payment record in database (payment is linked to enrolling student)
        payment = Payment(
            student_id=enrolling_student.id,
            course_instance_id=course_instance_id,
            stripe_payment_intent_id=intent.id,
            idempotency_key=idempotency_key,
            total_cost=total_amount,
            tax_amount=int(tax_amount),
            customer_email=doorman.user.email,
            status='pending'
        )
        payment.save()
        
        # Create payment line items
        from src.models.stripe.payment_line_items import PaymentLineItem
        for item in line_items:
            line_item = PaymentLineItem(
                payment_id=payment.id,
                payable_template_id=item['payable_template_id'],
                cost_of_item=item['amount'],
                quantity=1
            )
            line_item.save()
        
        # Log the payment intent creation
        Log.create_log(
            log_type=Log.TYPE_PAYMENT,
            action='create_payment_intent',
            description=f'Payment intent created for ${total_amount/100:.2f} - {course_instance.course_template.name if course_instance.course_template else "Course"}',
            user_id=doorman.user.id,
            target_type='payment',
            target_id=payment.id,
            status='success',
            extra_data={
                'payment_intent_id': intent.id,
                'amount': total_amount,
                'enrolling_student_id': enrolling_student.id,
                'enrolling_student_email': enrolling_student.user.email if enrolling_student.user else None,
                'paying_student_id': paying_student.id,
                'paying_student_email': doorman.user.email,
                'course_instance_id': course_instance_id,
                'course_name': course_instance.course_template.name if course_instance.course_template else None,
                'is_guest_enrollment': bool(guest_student_id),
                'line_items_count': len(line_items),
                'idempotency_key': idempotency_key
            }
        )
        
        return jsonify({
            'clientSecret': intent.client_secret,
            'paymentId': payment.id,
            'amount': total_amount
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error - 46b191e1': str(e)}), 400
    except Exception as e:
        return jsonify({'error - 29171b38': f'An error occurred: {str(e)}'}), 500


@stripe_payments_bp.route('/status/<int:payment_id>', methods=['GET'])
@login_required
@role_required('student')
def get_payment_status(payment_id):
    """Get the status of a payment."""
    try:
        # Get current user
        doorman = Doorman.get_by_token(session['doorman_token'])
        student = doorman.user.student
        
        if not student:
            return jsonify({'error - 2d547329': 'Student profile not found'}), 404
        
        # Get payment
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error - 576d3ac8': 'Payment not found'}), 404
        
        # Verify payment belongs to current student OR to a guest student created by current student
        enrolling_student = Student.query.get(payment.student_id)
        if not enrolling_student:
            return jsonify({'error - student_not_found': 'Enrolling student not found'}), 404
        
        # Allow if payment is for current student OR for their guest student
        is_own_payment = payment.student_id == student.id
        is_guest_payment = enrolling_student.created_by_student_id == student.id
        
        if not (is_own_payment or is_guest_payment):
            return jsonify({'error - 8c62c376': 'Unauthorized'}), 403
        
        return jsonify({
            'id': payment.id,
            'status': payment.status,
            'amount': payment.total_cost,
            'enrollment_id': payment.enrollment_id
        }), 200
        
    except Exception as e:
        return jsonify({'error - 69c54b37': f'An error occurred: {str(e)}'}), 500
