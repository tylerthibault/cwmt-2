"""Business logic service for enrollment operations."""
import os
import stripe
from src.models.logs import Log
from src.models.main import db

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


def get_unenrollment_requests(status_filter='pending'):
    """
    Get unenrollment requests filtered by status.
    
    Args:
        status_filter: 'pending', 'processed', or 'all'
    
    Returns:
        list: Filtered enrollments
    """
    from src.models.course_folder.enrollments import Enrollment
    
    if status_filter == 'pending':
        return Enrollment.get_pending_unenrollments()
    elif status_filter == 'processed':
        return Enrollment.query.filter(
            Enrollment.unenrollment_requested == True,
            Enrollment.unenrollment_processed_at.isnot(None)
        ).order_by(Enrollment.unenrollment_processed_at.desc()).all()
    else:  # all
        return Enrollment.query.filter_by(
            unenrollment_requested=True
        ).order_by(Enrollment.unenrollment_requested_at.desc()).all()


def get_unenrollment_counts():
    """Get counts of unenrollment requests by status."""
    from src.models.course_folder.enrollments import Enrollment
    
    return {
        'pending_count': Enrollment.query.filter_by(
            unenrollment_requested=True, 
            status='enrolled'
        ).count(),
        'processed_count': Enrollment.query.filter(
            Enrollment.unenrollment_requested == True,
            Enrollment.unenrollment_processed_at.isnot(None)
        ).count()
    }


def process_unenrollment_refund(payment, refund_percentage):
    """
    Process refund for an unenrollment.
    
    Args:
        payment: Payment object
        refund_percentage: Percentage to refund (e.g., 80)
    
    Returns:
        int: Refund amount in cents (0 if no refund)
    """
    from src.models.stripe.payment_line_items import PaymentLineItem
    from src.models.course_folder.payable_templates import PayableTemplate
    
    if not payment or payment.status != 'succeeded' or not payment.stripe_charge_id:
        return 0
    
    # Calculate refund amount
    refund_amount = int((payment.total_cost * refund_percentage) / 100)
    
    if refund_amount <= 0:
        return 0
    
    # Check actual Stripe refund status
    try:
        stripe_charge = stripe.Charge.retrieve(payment.stripe_charge_id)
        actual_stripe_refunded = stripe_charge.amount_refunded
    except stripe.error.StripeError:
        actual_stripe_refunded = 0
    
    # Calculate total already refunded in database
    total_refunded = sum(
        item.amount_refunded if item.amount_refunded else 0 
        for item in payment.line_items.all()
    )
    
    # Check if there's enough remaining to refund
    remaining_refundable = payment.total_cost - max(total_refunded, actual_stripe_refunded)
    
    if refund_amount > remaining_refundable:
        refund_amount = remaining_refundable
    
    if refund_amount <= 0:
        return 0
    
    # Create Stripe refund
    refund = stripe.Refund.create(
        charge=payment.stripe_charge_id,
        amount=refund_amount,
        reason='requested_by_customer',
        metadata={
            'payment_id': payment.id,
            'refund_percentage': refund_percentage
        }
    )
    
    # Create "Unenrollment Refund" line item
    unenroll_template = PayableTemplate.query.filter_by(name='Unenrollment Refund').first()
    if not unenroll_template:
        unenroll_template = PayableTemplate(
            name='Unenrollment Refund',
            description=f'Refund for unenrollment ({refund_percentage}% of payment)',
            amount=0,
            is_required=False
        )
        unenroll_template.save()
    
    # Create line item for this refund
    refund_line_item = PaymentLineItem(
        payment_id=payment.id,
        payable_template_id=unenroll_template.id,
        cost_of_item=refund_amount,
        quantity=1
    )
    refund_line_item.amount_refunded = refund_amount
    refund_line_item.save()
    
    # Update payment status if fully refunded
    new_total_refunded = total_refunded + refund_amount
    if new_total_refunded >= payment.total_cost:
        payment.status = 'refunded'
        payment.save()
    
    return refund_amount


def approve_unenrollment(enrollment, refund_percentage, admin_notes, user_id):
    """
    Approve an unenrollment request.
    
    Args:
        enrollment: Enrollment object
        refund_percentage: Percentage to refund
        admin_notes: Admin notes
        user_id: ID of user approving
    
    Returns:
        int: Refund amount issued
    
    Raises:
        ValueError: If validation fails
    """
    if not enrollment.unenrollment_requested:
        raise ValueError('No unenrollment request found')
    
    if enrollment.status != 'enrolled':
        raise ValueError('Enrollment is not active')
    
    # Process refund if applicable
    payment = enrollment.get_payment()
    refund_amount = process_unenrollment_refund(payment, refund_percentage)
    
    # Update enrollment - approve unenrollment
    enrollment.refund_percentage = refund_percentage
    enrollment.approve_unenrollment(user_id, admin_notes)
    
    # Log the approval
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='approve_unenrollment',
        description=f'Unenrollment approved for {enrollment.student.user.email} from {enrollment.course_instance.course_template.name}',
        user_id=user_id,
        target_type='enrollment',
        target_id=enrollment.id,
        status='success',
        extra_data={
            'student_email': enrollment.student.user.email,
            'course_name': enrollment.course_instance.course_template.name,
            'refund_percentage': refund_percentage,
            'refund_amount': refund_amount,
            'admin_notes': admin_notes,
            'payment_id': payment.id if payment else None
        }
    )
    
    return refund_amount


def deny_unenrollment(enrollment, admin_notes, user_id):
    """
    Deny an unenrollment request.
    
    Args:
        enrollment: Enrollment object
        admin_notes: Admin notes
        user_id: ID of user denying
    
    Raises:
        ValueError: If validation fails
    """
    if not enrollment.unenrollment_requested:
        raise ValueError('No unenrollment request found')
    
    # Deny unenrollment
    enrollment.deny_unenrollment(user_id, admin_notes)
    
    # Log the denial
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='deny_unenrollment',
        description=f'Unenrollment denied for {enrollment.student.user.email} from {enrollment.course_instance.course_template.name}',
        user_id=user_id,
        target_type='enrollment',
        target_id=enrollment.id,
        status='success',
        extra_data={
            'student_email': enrollment.student.user.email,
            'course_name': enrollment.course_instance.course_template.name,
            'admin_notes': admin_notes
        }
    )


def create_student_account(first_name, last_name, email, phone=None):
    """
    Create a new student user account.
    
    Args:
        first_name: Student's first name
        last_name: Student's last name
        email: Student's email
        phone: Optional phone number
    
    Returns:
        tuple: (student, temp_password)
    
    Raises:
        ValueError: If validation fails
    """
    from src.models.user_folder.users import User
    from src.models.user_folder.students import Student
    from src.utils.password_management import generate_random_password
    
    if not first_name or not last_name or not email:
        raise ValueError('First name, last name, and email are required')
    
    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValueError('A user with this email already exists')
    
    # Create new user account
    temp_password = generate_random_password()
    new_user = User(
        email=email,
        password=temp_password,
        first_name=first_name,
        last_name=last_name,
        phone_number=phone if phone else None,
        is_active=True
    )
    new_user.save()
    
    # Create student record
    student = Student(
        user_id=new_user.id,
        first_name=first_name,
        last_name=last_name,
        is_active=True
    )
    student.save()
    
    return student, temp_password


def create_enrollment(student, course_instance):
    """
    Create an enrollment.
    
    Args:
        student: Student object
        course_instance: CourseInstance object
    
    Returns:
        Enrollment: Created enrollment
    
    Raises:
        ValueError: If validation fails
    """
    from src.models.course_folder.enrollments import Enrollment
    
    # Check if already enrolled
    if Enrollment.enrollment_exists(student.id, course_instance.id):
        raise ValueError('Student is already enrolled in this course')
    
    # Check if course is full
    current_enrollments = Enrollment.count_active_enrollments_for_course(course_instance.id)
    if current_enrollments >= course_instance.max_students:
        raise ValueError('Course is full')
    
    # Create enrollment
    enrollment = Enrollment(
        student_id=student.id,
        course_instance_id=course_instance.id,
        status='enrolled'
    )
    enrollment.save()
    
    return enrollment


def create_enrollment_payment(enrollment, course_instance, student_email):
    """
    Create payment record for an enrollment.
    
    Args:
        enrollment: Enrollment object
        course_instance: CourseInstance object
        student_email: Student's email
    
    Returns:
        Payment or None
    """
    from src.models.stripe.payments import Payment
    from src.models.stripe.payment_line_items import PaymentLineItem
    
    if not course_instance.course_template:
        return None
    
    # Calculate total cost
    total_cost = 0
    line_items_data = []
    
    for payable_template in course_instance.course_template.payable_templates.all():
        if payable_template.is_required:
            amount_in_cents = int(payable_template.amount * 100)
            total_cost += amount_in_cents
            line_items_data.append({
                'payable_template_id': payable_template.id,
                'amount': amount_in_cents
            })
    
    if total_cost <= 0:
        return None
    
    # Create payment record (marked as admin-enrolled)
    payment = Payment(
        student_id=enrollment.student_id,
        course_instance_id=course_instance.id,
        total_cost=total_cost,
        customer_email=student_email,
        status='succeeded',
        stripe_payment_intent_id=f'admin_enrolled_{enrollment.id}'
    )
    payment.save()
    
    # Create line items
    for item_data in line_items_data:
        line_item = PaymentLineItem(
            payment_id=payment.id,
            payable_template_id=item_data['payable_template_id'],
            cost_of_item=item_data['amount'],
            quantity=1
        )
        line_item.save()
    
    # Link payment to enrollment
    enrollment.payment_id = payment.id
    enrollment.save()
    
    return payment


def log_manual_enrollment(enrollment, student_email, course_name, user_id, student_created=False, 
                         temp_password=None, waive_payment=False, admin_notes='', payment_id=None):
    """Log a manual enrollment action."""
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='admin_enroll_student',
        description=f'Admin manually enrolled {student_email} in {course_name}',
        user_id=user_id,
        target_type='enrollment',
        target_id=enrollment.id,
        status='success',
        extra_data={
            'student_id': enrollment.student_id,
            'student_email': student_email,
            'course_instance_id': enrollment.course_instance_id,
            'course_name': course_name,
            'student_created': student_created,
            'waive_payment': waive_payment,
            'admin_notes': admin_notes,
            'temp_password': temp_password if student_created else None,
            'payment_id': payment_id
        }
    )
