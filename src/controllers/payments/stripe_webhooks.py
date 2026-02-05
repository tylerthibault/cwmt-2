from flask import Blueprint, request, jsonify
import stripe
import os
import json
from src.models.stripe.payments import Payment
from src.models.stripe.stripe_webhook_events import StripeWebhookEvent
from src.models.course_folder.enrollments import Enrollment
from src.models.app_settings import AppSettings

# Create blueprint
stripe_webhooks_bp = Blueprint('stripe_webhooks', __name__, url_prefix='/webhooks')


def _get_stripe_credentials():
    """Get Stripe credentials from AppSettings."""
    settings = AppSettings.get_settings()
    secret_key = settings.get_stripe_secret_key()
    webhook_secret = settings.get_stripe_webhook_secret()
    
    # Fallback to environment variables for backward compatibility
    if not secret_key:
        secret_key = os.getenv('STRIPE_SECRET_KEY')
    if not webhook_secret:
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    return secret_key, webhook_secret


@stripe_webhooks_bp.route('/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events."""
    # Get Stripe credentials from settings
    secret_key, webhook_secret = _get_stripe_credentials()
    stripe.api_key = secret_key
    
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error - 298bd934': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error - 726993e2': 'Invalid signature'}), 400
    
    # Check if event already processed (idempotency)
    if StripeWebhookEvent.event_exists(event['id']):
        return jsonify({'message': 'Event already processed'}), 200
    
    # Log webhook event
    webhook_event = StripeWebhookEvent(
        stripe_event_id=event['id'],
        event_type=event['type'],
        payload=json.dumps(event)
    )
    webhook_event.save()
    
    # Handle the event
    try:
        if event['type'] == 'payment_intent.succeeded':
            handle_payment_success(event, webhook_event)
        elif event['type'] == 'payment_intent.payment_failed':
            handle_payment_failure(event, webhook_event)
        elif event['type'] == 'charge.succeeded':
            handle_charge_succeeded(event, webhook_event)
        else:
            # Unhandled event type
            webhook_event.mark_as_processed()
            
    except Exception as e:
        webhook_event.mark_as_failed(str(e))
        return jsonify({'error - 1b9ce5ac': str(e)}), 500
    
    return jsonify({'message': 'Webhook processed'}), 200


def handle_payment_success(event, webhook_event):
    """Handle successful payment intent."""
    payment_intent = event['data']['object']
    payment_intent_id = payment_intent['id']
    
    # Find payment record
    payment = Payment.get_by_payment_intent_id(payment_intent_id)
    if not payment:
        raise Exception(f'Payment not found for intent: {payment_intent_id}')
    
    # Update payment status
    payment.status = 'succeeded'
    payment.receipt_url = payment_intent.get('charges', {}).get('data', [{}])[0].get('receipt_url')
    
    # Get payment method details
    if 'charges' in payment_intent and len(payment_intent['charges']['data']) > 0:
        charge = payment_intent['charges']['data'][0]
        if 'payment_method_details' in charge:
            pm_details = charge['payment_method_details']
            payment.payment_method_type = pm_details.get('type')
            if 'card' in pm_details:
                payment.last4 = pm_details['card'].get('last4')
    
    payment.save()
    
    # Create enrollment if it doesn't exist
    enrollment = Enrollment.get_enrollment(payment.student_id, payment.course_instance_id)
    if not enrollment:
        enrollment = Enrollment(
            student_id=payment.student_id,
            course_instance_id=payment.course_instance_id,
            status='enrolled'
        )
        enrollment.save()
        
        # Link enrollment to payment
        payment.enrollment_id = enrollment.id
        payment.save()
    
    # Update webhook event
    webhook_event.payment_id = payment.id
    webhook_event.mark_as_processed()
    
    # TODO: Send confirmation email
    

def handle_payment_failure(event, webhook_event):
    """Handle failed payment intent."""
    payment_intent = event['data']['object']
    payment_intent_id = payment_intent['id']
    
    # Find payment record
    payment = Payment.get_by_payment_intent_id(payment_intent_id)
    if not payment:
        raise Exception(f'Payment not found for intent: {payment_intent_id}')
    
    # Update payment status
    payment.status = 'failed'
    payment.save()
    
    # Update webhook event
    webhook_event.payment_id = payment.id
    webhook_event.mark_as_processed()
    
    # TODO: Send failure notification email


def handle_charge_succeeded(event, webhook_event):
    """Handle successful charge (update charge ID)."""
    charge = event['data']['object']
    payment_intent_id = charge.get('payment_intent')
    
    if payment_intent_id:
        payment = Payment.get_by_payment_intent_id(payment_intent_id)
        if payment:
            payment.stripe_charge_id = charge['id']
            payment.receipt_url = charge.get('receipt_url')
            payment.save()
            
            webhook_event.payment_id = payment.id
    
    webhook_event.mark_as_processed()
