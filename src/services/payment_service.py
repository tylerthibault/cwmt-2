"""Business logic service for payment operations."""
import os
import stripe
from src.models.logs import Log

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


def sync_payment_with_stripe(payment):
    """
    Sync payment refund status with Stripe.
    
    Args:
        payment: Payment object to sync
    
    Returns:
        dict: Result with success status and details
    
    Raises:
        ValueError: If payment validation fails
        stripe.error.StripeError: If Stripe API fails
    """
    from src.models.stripe.payment_line_items import PaymentLineItem
    from src.models.course_folder.payable_templates import PayableTemplate
    
    if not payment.stripe_charge_id:
        raise ValueError('No Stripe charge ID found')
    
    # Retrieve charge from Stripe
    stripe_charge = stripe.Charge.retrieve(payment.stripe_charge_id)
    actual_stripe_refunded = stripe_charge.amount_refunded
    
    # Calculate total already refunded in our database
    total_refunded = sum(
        item.amount_refunded if item.amount_refunded else 0 
        for item in payment.line_items.all()
    )
    
    if actual_stripe_refunded <= total_refunded:
        return {
            'success': True,
            'message': 'Database is already in sync with Stripe',
            'stripe_refunded': actual_stripe_refunded,
            'db_refunded': total_refunded
        }
    
    # There's a discrepancy - Stripe has more refunded
    difference = actual_stripe_refunded - total_refunded
    
    # Create a "Stripe Sync Adjustment" line item for the difference
    sync_template = PayableTemplate.query.filter_by(name='Stripe Sync Adjustment').first()
    if not sync_template:
        sync_template = PayableTemplate(
            name='Stripe Sync Adjustment',
            description='Automatic sync adjustment to match Stripe records',
            amount=0,
            is_required=False
        )
        sync_template.save()
    
    # Create line item for the missing refund amount
    sync_line_item = PaymentLineItem(
        payment_id=payment.id,
        payable_template_id=sync_template.id,
        cost_of_item=difference,
        quantity=1
    )
    sync_line_item.amount_refunded = difference
    sync_line_item.save()
    
    # Update payment status if now fully refunded
    new_total_refunded = total_refunded + difference
    if new_total_refunded >= payment.total_cost:
        payment.status = 'refunded'
        payment.save()
    
    return {
        'success': True,
        'message': f'Synced ${difference/100:.2f} from Stripe',
        'stripe_refunded': actual_stripe_refunded,
        'db_refunded_before': total_refunded,
        'db_refunded_after': new_total_refunded
    }


def validate_refund_request(payment, amount):
    """
    Validate a refund request.
    
    Args:
        payment: Payment object
        amount: Refund amount in cents
    
    Returns:
        tuple: (total_refunded, actual_stripe_refunded)
    
    Raises:
        ValueError: If validation fails
    """
    if payment.status != 'succeeded':
        raise ValueError('Can only refund succeeded payments')
    
    if not payment.stripe_charge_id:
        raise ValueError('No Stripe charge ID found')
    
    if not amount or amount <= 0:
        raise ValueError('Invalid refund amount')
    
    # Check actual refund status from Stripe
    try:
        stripe_charge = stripe.Charge.retrieve(payment.stripe_charge_id)
        actual_stripe_refunded = stripe_charge.amount_refunded
    except stripe.error.StripeError:
        actual_stripe_refunded = 0
    
    # Calculate total already refunded in our database
    total_refunded = sum(
        item.amount_refunded if item.amount_refunded else 0 
        for item in payment.line_items.all()
    )
    
    # Sync check
    if actual_stripe_refunded > total_refunded:
        raise ValueError(
            f'Database out of sync with Stripe. Stripe shows ${actual_stripe_refunded/100:.2f} '
            f'refunded, but database shows ${total_refunded/100:.2f}. Please sync records first.'
        )
    
    # Check if payment is already fully refunded
    if total_refunded >= payment.total_cost or actual_stripe_refunded >= payment.total_cost:
        raise ValueError('Payment has already been fully refunded')
    
    # Calculate remaining refundable amount
    remaining_refundable = payment.total_cost - total_refunded
    
    # Validate amount doesn't exceed remaining refundable
    if amount > remaining_refundable:
        raise ValueError(f'Refund amount exceeds remaining refundable amount (${remaining_refundable/100:.2f})')
    
    return total_refunded, actual_stripe_refunded


def process_stripe_refund(payment, amount, line_item_id=None, reason=None):
    """
    Process a refund through Stripe.
    
    Args:
        payment: Payment object
        amount: Refund amount in cents
        line_item_id: Optional specific line item ID
        reason: Optional refund reason
    
    Returns:
        dict: Refund result with refund_id
    """
    # Create Stripe refund
    refund = stripe.Refund.create(
        charge=payment.stripe_charge_id,
        amount=amount,
        reason='requested_by_customer',
        metadata={
            'payment_id': payment.id,
            'line_item_id': line_item_id if line_item_id else None,
            'admin_reason': reason if reason else None
        }
    )
    
    return {'refund_id': refund.id, 'amount': amount}


def update_line_item_refund(payment, amount, line_item_id=None):
    """
    Update line item with refund amount.
    
    Args:
        payment: Payment object
        amount: Refund amount in cents
        line_item_id: Optional specific line item ID
    """
    from src.models.stripe.payment_line_items import PaymentLineItem
    from src.models.course_folder.payable_templates import PayableTemplate
    
    if line_item_id:
        line_item = PaymentLineItem.query.get(line_item_id)
        if line_item and line_item.payment_id == payment.id:
            current_refunded = line_item.amount_refunded if line_item.amount_refunded else 0
            line_item.amount_refunded = current_refunded + amount
            line_item.save()
    else:
        # For custom refunds without a specific line item, create a special line item
        custom_template = PayableTemplate.query.filter_by(name='Custom Refund').first()
        if not custom_template:
            custom_template = PayableTemplate(
                name='Custom Refund',
                description='Administrative custom refund',
                amount=0,
                is_required=False
            )
            custom_template.save()
        
        # Create a line item for this custom refund
        custom_line_item = PaymentLineItem(
            payment_id=payment.id,
            payable_template_id=custom_template.id,
            cost_of_item=amount,
            quantity=1
        )
        custom_line_item.amount_refunded = amount
        custom_line_item.save()


def update_payment_status_if_fully_refunded(payment, additional_refund):
    """
    Update payment status to 'refunded' if fully refunded.
    
    Args:
        payment: Payment object
        additional_refund: Additional refund amount just processed
    """
    total_refunded = sum(
        item.amount_refunded if item.amount_refunded else 0 
        for item in payment.line_items.all()
    )
    
    if total_refunded >= payment.total_cost:
        payment.status = 'refunded'
        payment.save()


def log_refund(payment_id, amount, refund_id, user_id, line_item_id=None, reason=None, student_email=None):
    """Log a refund action."""
    Log.create_log(
        log_type=Log.TYPE_PAYMENT,
        action='issue_refund',
        description=f'Refund of ${amount/100:.2f} issued for payment #{payment_id}',
        user_id=user_id,
        target_type='payment',
        target_id=payment_id,
        status='success',
        extra_data={
            'refund_id': refund_id,
            'amount': amount,
            'reason': reason,
            'student_email': student_email,
            'line_item_id': line_item_id
        }
    )
