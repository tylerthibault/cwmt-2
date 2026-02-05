"""Payment controller for payment management operations."""
from flask import Blueprint, render_template, request, jsonify
from src.models.stripe.payments import Payment
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required
from src.services import payment_service
import stripe

payments_bp = Blueprint('payments', __name__, url_prefix='/admin/payments')


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


@payments_bp.route('/<int:payment_id>')
@login_required
@role_required('admin')
def view_payment(payment_id):
    """Route to view a specific payment's details with itemized breakdown."""
    payment = Payment.query.get(payment_id)
    if not payment:
        return "Payment not found", 404
    
    return render_template('private/admins/payments/details.html',
                         current_user=_get_current_user(),
                         payment=payment)


@payments_bp.route('/<int:payment_id>/sync-stripe', methods=['POST'])
@login_required
@role_required('admin')
def sync_payment_with_stripe(payment_id):
    """Sync payment refund status with Stripe."""
    try:
        payment = Payment.query.get(payment_id)
        if not payment:
            return _error_response('Payment not found', 404)
        
        result = payment_service.sync_payment_with_stripe(payment)
        return jsonify(result), 200
        
    except ValueError as e:
        return _error_response(str(e), 400)
    except stripe.error.StripeError as e:
        return _error_response(f'Stripe error: {str(e)}', 400)
    except Exception as e:
        return _error_response(f'An error occurred: {str(e)}')


@payments_bp.route('/<int:payment_id>/refund', methods=['POST'])
@login_required
@role_required('admin')
def refund_payment(payment_id):
    """Issue a refund for a payment or specific line item."""
    try:
        data = request.get_json()
        
        if not data:
            return _error_response('No data provided', 400)
        
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return _error_response('Payment not found', 404)
        
        # Extract request parameters
        line_item_id = data.get('line_item_id')
        amount = data.get('amount')  # in cents
        reason = data.get('reason')
        
        # Validate refund request
        payment_service.validate_refund_request(payment, amount)
        
        # Process Stripe refund
        refund_result = payment_service.process_stripe_refund(
            payment, amount, line_item_id, reason
        )
        
        # Update line item with refund
        payment_service.update_line_item_refund(payment, amount, line_item_id)
        
        # Update payment status if fully refunded
        payment_service.update_payment_status_if_fully_refunded(payment, amount)
        
        # Log the refund
        student_email = payment.student.user.email if payment.student and payment.student.user else None
        payment_service.log_refund(
            payment_id, amount, refund_result['refund_id'], 
            _get_current_user().id, line_item_id, reason, student_email
        )
        
        return _success_response('Refund issued successfully', refund_result)
        
    except ValueError as e:
        # Check if it's a sync error (409) or validation error (400)
        status_code = 409 if 'out of sync' in str(e) else 400
        return _error_response(str(e), status_code)
    except stripe.error.StripeError as e:
        return _error_response(f'Stripe error: {str(e)}', 400)
    except Exception as e:
        print(f"Unexpected error in refund_payment: {str(e)}")
        import traceback
        traceback.print_exc()
        return _error_response(f'An error occurred: {str(e)}', 500)
