"""
Payment Logic - THIN logic layer following constitutional principles

Handles payment-related business logic including:
- Creating enrollment line items from course payable items
- Processing payments through Stripe
- Allocating payments to line items
- Processing refunds

Contains ONLY:
- Business logic
- Data validation
- Complex calculations
- External service integration (Stripe)

Does NOT contain:
- Route definitions (belongs in controllers)
- Direct request/response handling (belongs in controllers)
"""
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from src.models import db
from src.models.course_enrollment import CourseEnrollment
from src.models.payable_item_model import CoursePayableItem, PayableItemTemplate
from src.models.enrollment_line_items import EnrollmentLineItem
from src.models.payment_models import Payment, PaymentAllocation, Refund
from src.models.user import User
import stripe
import os


class PaymentValidationError(Exception):
    """Raised when payment validation fails"""
    pass


class PaymentBusinessError(Exception):
    """Raised when payment business logic fails"""
    pass


class PaymentLogic:
    """
    Payment business logic handler.
    Manages enrollment line items, payments, and Stripe integration.
    """
    
    @staticmethod
    def get_course_payable_items(course_id: int) -> List[CoursePayableItem]:
        """
        Get all available payable items for a course.
        
        Args:
            course_id: Course ID
            
        Returns:
            List of CoursePayableItem instances
        """
        return CoursePayableItem.query.filter_by(
            course_id=course_id,
            is_available=True
        ).join(PayableItemTemplate).order_by(PayableItemTemplate.item_type).all()
    
    @staticmethod
    def get_enrollment_line_items(enrollment_id: int) -> List[EnrollmentLineItem]:
        """
        Get all line items for an enrollment.
        
        Args:
            enrollment_id: Enrollment ID
            
        Returns:
            List of EnrollmentLineItem instances
        """
        return EnrollmentLineItem.query.filter_by(enrollment_id=enrollment_id).all()
    
    @staticmethod
    def get_enrollment_payment_summary(enrollment_id: int) -> Dict:
        """
        Get payment summary for an enrollment.
        
        Args:
            enrollment_id: Enrollment ID
            
        Returns:
            dict: {
                'total_amount': Decimal,
                'amount_paid': Decimal,
                'amount_due': Decimal,
                'is_paid': bool
            }
        """
        line_items = PaymentLogic.get_enrollment_line_items(enrollment_id)
        
        total_amount = sum(item.total for item in line_items)
        amount_paid = sum(item.amount_paid for item in line_items)
        amount_due = total_amount - amount_paid
        
        return {
            'total_amount': total_amount,
            'amount_paid': amount_paid,
            'amount_due': amount_due,
            'is_paid': amount_due <= 0
        }
    
    @staticmethod
    def create_line_items_for_enrollment(
        enrollment_id: int,
        payable_item_ids: List[int],
        quantities: Optional[Dict[int, int]] = None
    ) -> List[EnrollmentLineItem]:
        """
        Create line items for selected payable items.
        
        Args:
            enrollment_id: Enrollment ID
            payable_item_ids: List of CoursePayableItem IDs to add
            quantities: Optional dict mapping payable_item_id to quantity
            
        Returns:
            List of created EnrollmentLineItem instances
            
        Raises:
            PaymentValidationError: If validation fails
            PaymentBusinessError: If business logic fails
        """
        # Validate enrollment exists
        enrollment = CourseEnrollment.query.get(enrollment_id)
        if not enrollment:
            raise PaymentValidationError(f"Enrollment {enrollment_id} not found")
        
        # Validate payable items exist and belong to the course
        payable_items = CoursePayableItem.query.filter(
            CoursePayableItem.id.in_(payable_item_ids),
            CoursePayableItem.course_id == enrollment.course_id,
            CoursePayableItem.is_available == True
        ).all()
        
        if len(payable_items) != len(payable_item_ids):
            raise PaymentValidationError("One or more payable items not found or not available")
        
        # Check for duplicates
        existing_items = EnrollmentLineItem.query.filter(
            EnrollmentLineItem.enrollment_id == enrollment_id,
            EnrollmentLineItem.course_payable_item_id.in_(payable_item_ids)
        ).all()
        
        if existing_items:
            existing_ids = [item.course_payable_item_id for item in existing_items]
            raise PaymentBusinessError(f"Line items already exist for payable items: {existing_ids}")
        
        # Create line items
        created_items = []
        for payable_item in payable_items:
            quantity = quantities.get(payable_item.id, 1) if quantities else 1
            
            if quantity < 1:
                raise PaymentValidationError(f"Quantity must be at least 1 for item {payable_item.id}")
            
            unit_price = payable_item.price
            subtotal = unit_price * quantity
            
            # TODO: Apply discounts and tax calculation
            discount_amount = Decimal('0.00')
            tax_amount = Decimal('0.00')
            total = subtotal - discount_amount + tax_amount
            
            line_item = EnrollmentLineItem(
                enrollment_id=enrollment_id,
                course_payable_item_id=payable_item.id,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal,
                discount_amount=discount_amount,
                tax_amount=tax_amount,
                total=total,
                status='pending'
            )
            
            db.session.add(line_item)
            created_items.append(line_item)
        
        db.session.commit()
        return created_items
    
    @staticmethod
    def create_stripe_payment_intent(
        enrollment_id: int,
        line_item_ids: List[int],
        user_id: int
    ) -> Dict:
        """
        Create a Stripe Payment Intent for selected line items.
        
        Args:
            enrollment_id: Enrollment ID
            line_item_ids: List of EnrollmentLineItem IDs to pay
            user_id: User ID making the payment
            
        Returns:
            dict: {
                'client_secret': str,
                'payment_intent_id': str,
                'amount': int (in cents)
            }
            
        Raises:
            PaymentValidationError: If validation fails
            PaymentBusinessError: If Stripe API fails
        """
        # Validate line items exist and belong to enrollment
        line_items = EnrollmentLineItem.query.filter(
            EnrollmentLineItem.id.in_(line_item_ids),
            EnrollmentLineItem.enrollment_id == enrollment_id,
            EnrollmentLineItem.status.in_(['pending', 'rejected'])
        ).all()
        
        if len(line_items) != len(line_item_ids):
            raise PaymentValidationError("One or more line items not found or already paid")
        
        # Calculate total amount
        total_amount = sum(item.total - item.amount_paid for item in line_items)
        
        if total_amount <= 0:
            raise PaymentValidationError("No amount due for selected items")
        
        # Convert to cents for Stripe
        amount_cents = int(total_amount * 100)
        
        # Get enrollment info for metadata
        enrollment = CourseEnrollment.query.get(enrollment_id)
        user = User.query.get(user_id)
        
        # Initialize Stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        
        try:
            # Create Payment Intent (card only)
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency='usd',
                payment_method_types=['card'],
                metadata={
                    'enrollment_id': enrollment_id,
                    'user_id': user_id,
                    'course_id': enrollment.course_id,
                    'line_item_ids': ','.join(map(str, line_item_ids))
                },
                description=f"Course payment for {user.email}"
            )
            
            # Create pending payment record
            pending_payment = Payment(
                enrollment_id=enrollment_id,
                processed_by_user_id=user_id,
                amount=total_amount,
                payment_method='stripe',
                status='pending',
                payment_date=datetime.utcnow(),
                stripe_payment_intent_id=intent.id,
                notes=f"Stripe Payment Intent created for {len(line_items)} item(s)"
            )
            
            db.session.add(pending_payment)
            db.session.commit()
            
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': amount_cents
            }
            
        except stripe.error.StripeError as e:
            raise PaymentBusinessError(f"Stripe error: {str(e)}")
    
    @staticmethod
    def record_payment(
        enrollment_id: int,
        line_item_ids: List[int],
        amount: Decimal,
        payment_method: str,
        processed_by_user_id: int,
        stripe_payment_intent_id: Optional[str] = None,
        stripe_charge_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Payment:
        """
        Record a payment and allocate to line items.
        
        Args:
            enrollment_id: Enrollment ID
            line_item_ids: List of EnrollmentLineItem IDs being paid
            amount: Payment amount
            payment_method: Payment method (stripe, cash, check, other)
            processed_by_user_id: User ID processing the payment
            stripe_payment_intent_id: Optional Stripe Payment Intent ID
            stripe_charge_id: Optional Stripe Charge ID
            notes: Optional payment notes
            
        Returns:
            Payment instance
            
        Raises:
            PaymentValidationError: If validation fails
        """
        # Validate line items
        line_items = EnrollmentLineItem.query.filter(
            EnrollmentLineItem.id.in_(line_item_ids),
            EnrollmentLineItem.enrollment_id == enrollment_id
        ).all()
        
        if len(line_items) != len(line_item_ids):
            raise PaymentValidationError("One or more line items not found")
        
        # Check if pending payment already exists for this payment intent
        payment = None
        if stripe_payment_intent_id:
            payment = Payment.query.filter_by(
                stripe_payment_intent_id=stripe_payment_intent_id
            ).first()
        
        if payment:
            # Update existing pending payment to completed
            payment.status = 'completed'
            payment.payment_date = datetime.utcnow()
            payment.stripe_charge_id = stripe_charge_id
            if notes:
                payment.notes = (payment.notes or '') + f"\n{notes}"
        else:
            # Create new payment record
            payment = Payment(
                enrollment_id=enrollment_id,
                processed_by_user_id=processed_by_user_id,
                amount=amount,
                payment_method=payment_method,
                status='completed',
                payment_date=datetime.utcnow(),
                stripe_payment_intent_id=stripe_payment_intent_id,
                stripe_charge_id=stripe_charge_id,
                notes=notes
            )
            db.session.add(payment)
        
        db.session.flush()  # Get payment ID
        
        # Allocate payment to line items
        remaining_amount = amount
        
        print(f"PAYMENT ALLOCATION: Processing {len(line_items)} line items with ${remaining_amount} to allocate", flush=True)
        
        for line_item in line_items:
            amount_due = line_item.total - line_item.amount_paid
            
            print(f"PAYMENT ALLOCATION: Line item {line_item.id} - Total: ${line_item.total}, Paid: ${line_item.amount_paid}, Due: ${amount_due}, Status: {line_item.status}", flush=True)
            
            if amount_due <= 0:
                print(f"PAYMENT ALLOCATION: Line item {line_item.id} already paid, skipping", flush=True)
                continue
            
            # Allocate up to the amount due
            allocation_amount = min(remaining_amount, amount_due)
            
            print(f"PAYMENT ALLOCATION: Allocating ${allocation_amount} to line item {line_item.id}", flush=True)
            
            # Create allocation
            allocation = PaymentAllocation(
                payment_id=payment.id,
                enrollment_line_item_id=line_item.id,
                amount_applied=allocation_amount
            )
            
            db.session.add(allocation)
            
            # Update line item
            old_amount_paid = line_item.amount_paid
            line_item.amount_paid += allocation_amount
            
            print(f"PAYMENT ALLOCATION: Line item {line_item.id} amount_paid updated from ${old_amount_paid} to ${line_item.amount_paid}", flush=True)
            
            if line_item.amount_paid >= line_item.total:
                line_item.status = 'paid'
                print(f"PAYMENT ALLOCATION: Line item {line_item.id} marked as PAID", flush=True)
            else:
                print(f"PAYMENT ALLOCATION: Line item {line_item.id} still pending (${line_item.amount_paid}/${line_item.total})", flush=True)
            
            remaining_amount -= allocation_amount
            
            if remaining_amount <= 0:
                print(f"PAYMENT ALLOCATION: All payment allocated, stopping", flush=True)
                break
        
        print(f"PAYMENT ALLOCATION: Committing changes to database", flush=True)
        db.session.commit()
        print(f"PAYMENT ALLOCATION: Payment {payment.id} recorded successfully", flush=True)
        
        return payment
    
    @staticmethod
    def record_failed_payment(
        enrollment_id: int,
        line_item_ids: List[int],
        amount: Decimal,
        processed_by_user_id: int,
        stripe_payment_intent_id: Optional[str] = None,
        failure_reason: Optional[str] = None
    ) -> Payment:
        """
        Record a failed payment attempt for tracking purposes.
        
        Args:
            enrollment_id: Enrollment ID
            line_item_ids: List of EnrollmentLineItem IDs attempted to be paid
            amount: Payment amount attempted
            processed_by_user_id: User ID who attempted the payment
            stripe_payment_intent_id: Optional Stripe Payment Intent ID
            failure_reason: Reason for payment failure
            
        Returns:
            Payment instance with status='failed'
            
        Raises:
            PaymentValidationError: If validation fails
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Validate line items exist
        line_items = EnrollmentLineItem.query.filter(
            EnrollmentLineItem.id.in_(line_item_ids),
            EnrollmentLineItem.enrollment_id == enrollment_id
        ).all()
        
        if len(line_items) != len(line_item_ids):
            raise PaymentValidationError("One or more line items not found")
        
        # Check if failed payment already recorded for this intent
        if stripe_payment_intent_id:
            existing_payment = Payment.query.filter_by(
                stripe_payment_intent_id=stripe_payment_intent_id
            ).first()
            
            if existing_payment:
                # Update existing payment to failed
                existing_payment.status = 'failed'
                existing_payment.notes = (existing_payment.notes or '') + f"\nFailed: {failure_reason}"
                db.session.commit()
                logger.info(f"Updated existing payment {existing_payment.id} to failed status")
                return existing_payment
        
        # Create failed payment record
        notes = f"Payment failed: {failure_reason}" if failure_reason else "Payment failed"
        
        payment = Payment(
            enrollment_id=enrollment_id,
            processed_by_user_id=processed_by_user_id,
            amount=amount,
            payment_method='stripe',
            status='failed',
            payment_date=datetime.utcnow(),
            stripe_payment_intent_id=stripe_payment_intent_id,
            notes=notes
        )
        
        db.session.add(payment)
        db.session.commit()
        
        logger.info(f"Failed payment recorded - ID: {payment.id}, Amount: ${amount}, Reason: {failure_reason}")
        
        return payment
    
    @staticmethod
    def process_stripe_webhook(payload: dict, sig_header: str) -> Dict:
        """
        Process Stripe webhook event.
        
        Args:
            payload: Webhook payload
            sig_header: Stripe signature header
            
        Returns:
            dict: Processing result
            
        Raises:
            PaymentBusinessError: If webhook processing fails
        """
        import logging
        logger = logging.getLogger(__name__)
        
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        logger.info(f"Processing Stripe webhook - Secret present: {bool(endpoint_secret)}, Secret value: {endpoint_secret[:10] if endpoint_secret else 'None'}...")
        
        # If no webhook secret is configured, skip signature verification (development fallback)
        if not endpoint_secret:
            logger.warning("No STRIPE_WEBHOOK_SECRET configured - parsing webhook without signature verification (INSECURE)")
            try:
                import json
                event = json.loads(payload)
            except Exception as e:
                logger.error(f"Failed to parse webhook payload: {str(e)}")
                raise PaymentBusinessError("Invalid payload")
        else:
            # Production: Verify signature
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, endpoint_secret
                )
            except ValueError as e:
                logger.error(f"Invalid webhook payload: {str(e)}")
                raise PaymentBusinessError("Invalid payload")
            except stripe.error.SignatureVerificationError as e:
                logger.error(f"Invalid webhook signature: {str(e)}")
                raise PaymentBusinessError("Invalid signature")
        
        print(f"WEBHOOK: Processing event type: {event['type']}", flush=True)
        logger.info(f"Webhook event type: {event['type']}")
        
        # Handle payment intent succeeded
        if event['type'] == 'payment_intent.succeeded':
            print("WEBHOOK: Handling payment_intent.succeeded", flush=True)
            payment_intent = event['data']['object']
            
            # Extract metadata
            metadata = payment_intent.get('metadata', {})
            enrollment_id = metadata.get('enrollment_id')
            user_id = metadata.get('user_id')
            line_item_ids = metadata.get('line_item_ids', '').split(',')
            
            print(f"WEBHOOK: Metadata - enrollment: {enrollment_id}, user: {user_id}, line_items: {line_item_ids}", flush=True)
            logger.info(f"Payment intent metadata - enrollment: {enrollment_id}, user: {user_id}, line_items: {line_item_ids}")
            
            if not all([enrollment_id, user_id, line_item_ids]):
                print("WEBHOOK ERROR: Missing required metadata", flush=True)
                logger.error("Missing required metadata in payment intent")
                raise PaymentBusinessError("Missing required metadata")
            
            # Record the payment
            amount = Decimal(payment_intent['amount']) / 100  # Convert cents to dollars
            
            print(f"WEBHOOK: Recording payment of ${amount} for enrollment {enrollment_id}", flush=True)
            logger.info(f"Recording payment of ${amount} for enrollment {enrollment_id}")
            
            payment = PaymentLogic.record_payment(
                enrollment_id=int(enrollment_id),
                line_item_ids=[int(id) for id in line_item_ids if id],
                amount=amount,
                payment_method='stripe',
                processed_by_user_id=int(user_id),
                stripe_payment_intent_id=payment_intent['id'],
                stripe_charge_id=payment_intent.get('charges', {}).get('data', [{}])[0].get('id'),
                notes='Automated Stripe payment'
            )
            
            print(f"WEBHOOK: Payment recorded successfully - Payment ID: {payment.id}", flush=True)
            logger.info(f"Payment recorded successfully - Payment ID: {payment.id}")
            
            return {
                'success': True,
                'payment_id': payment.id
            }
        
        # Handle charge.succeeded (alternative to payment_intent.succeeded)
        elif event['type'] == 'charge.succeeded':
            print("WEBHOOK: Handling charge.succeeded", flush=True)
            charge = event['data']['object']
            
            # Get payment intent from charge
            payment_intent_id = charge.get('payment_intent')
            if not payment_intent_id:
                print("WEBHOOK: No payment_intent in charge.succeeded", flush=True)
                return {'success': True, 'message': 'No payment intent in charge'}
            
            # Check if we already recorded this payment
            existing_payment = Payment.query.filter_by(
                stripe_payment_intent_id=payment_intent_id
            ).first()
            
            if existing_payment:
                # If payment is still pending, we need to update it to completed
                if existing_payment.status == 'pending':
                    print(f"WEBHOOK: Updating pending payment to completed for intent {payment_intent_id}", flush=True)
                    existing_payment.status = 'completed'
                    existing_payment.payment_date = datetime.utcnow()
                    existing_payment.stripe_charge_id = charge['id']
                    existing_payment.notes = (existing_payment.notes or '') + "\nPayment confirmed via charge.succeeded webhook"
                    db.session.commit()
                    print(f"WEBHOOK: Payment {existing_payment.id} updated to completed", flush=True)
                    return {'success': True, 'message': 'Payment updated to completed', 'payment_id': existing_payment.id}
                else:
                    print(f"WEBHOOK: Payment already completed for intent {payment_intent_id}", flush=True)
                    return {'success': True, 'message': 'Payment already completed', 'payment_id': existing_payment.id}
            
            # Retrieve the payment intent to get metadata
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            try:
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                metadata = payment_intent.get('metadata', {})
            except Exception as e:
                print(f"WEBHOOK ERROR: Failed to retrieve payment intent: {str(e)}", flush=True)
                return {'success': False, 'message': f'Failed to retrieve payment intent: {str(e)}'}
            
            enrollment_id = metadata.get('enrollment_id')
            user_id = metadata.get('user_id')
            line_item_ids = metadata.get('line_item_ids', '').split(',')
            
            print(f"WEBHOOK: Metadata from charge - enrollment: {enrollment_id}, user: {user_id}, line_items: {line_item_ids}", flush=True)
            
            if not all([enrollment_id, user_id, line_item_ids]):
                print("WEBHOOK ERROR: Missing required metadata in charge", flush=True)
                return {'success': True, 'message': 'Missing metadata'}
            
            # Record the payment
            amount = Decimal(charge['amount']) / 100
            
            print(f"WEBHOOK: Recording payment of ${amount} for enrollment {enrollment_id} from charge.succeeded", flush=True)
            
            payment = PaymentLogic.record_payment(
                enrollment_id=int(enrollment_id),
                line_item_ids=[int(id) for id in line_item_ids if id],
                amount=amount,
                payment_method='stripe',
                processed_by_user_id=int(user_id),
                stripe_payment_intent_id=payment_intent_id,
                stripe_charge_id=charge['id'],
                notes='Automated Stripe payment (via charge.succeeded)'
            )
            
            print(f"WEBHOOK: Payment recorded successfully from charge - Payment ID: {payment.id}", flush=True)
            
            return {
                'success': True,
                'payment_id': payment.id
            }
        
        # Handle payment intent failed
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            
            # Extract metadata
            metadata = payment_intent.get('metadata', {})
            enrollment_id = metadata.get('enrollment_id')
            user_id = metadata.get('user_id')
            line_item_ids = metadata.get('line_item_ids', '').split(',')
            
            logger.warning(f"Payment intent failed - enrollment: {enrollment_id}, user: {user_id}, line_items: {line_item_ids}")
            
            if not all([enrollment_id, user_id, line_item_ids]):
                logger.error("Missing required metadata in failed payment intent")
                return {'success': True, 'message': 'Missing metadata for failed payment'}
            
            # Get failure reason
            last_payment_error = payment_intent.get('last_payment_error', {})
            failure_message = last_payment_error.get('message', 'Payment declined')
            failure_code = last_payment_error.get('code', 'unknown')
            
            # Record the failed payment
            amount = Decimal(payment_intent['amount']) / 100  # Convert cents to dollars
            
            logger.info(f"Recording failed payment of ${amount} for enrollment {enrollment_id} - Reason: {failure_message}")
            
            failed_payment = PaymentLogic.record_failed_payment(
                enrollment_id=int(enrollment_id),
                line_item_ids=[int(id) for id in line_item_ids if id],
                amount=amount,
                processed_by_user_id=int(user_id),
                stripe_payment_intent_id=payment_intent['id'],
                failure_reason=f"{failure_code}: {failure_message}"
            )
            
            logger.info(f"Failed payment recorded - Payment ID: {failed_payment.id}")
            
            return {
                'success': True,
                'payment_id': failed_payment.id,
                'status': 'failed'
            }
        
        # Handle charge dispute created
        elif event['type'] == 'charge.dispute.created':
            dispute = event['data']['object']
            charge_id = dispute.get('charge')
            amount = Decimal(dispute.get('amount', 0)) / 100
            reason = dispute.get('reason', 'unknown')
            status = dispute.get('status', 'needs_response')
            
            logger.warning(f"Dispute created for charge {charge_id} - Amount: ${amount}, Reason: {reason}")
            
            # Find the payment by charge_id
            payment = Payment.query.filter_by(stripe_charge_id=charge_id).first()
            
            if payment:
                # Update payment with dispute information
                dispute_note = f"\n[DISPUTE CREATED] {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} - Amount: ${amount}, Reason: {reason}, Status: {status}"
                payment.notes = (payment.notes or '') + dispute_note
                payment.status = 'disputed'
                db.session.commit()
                
                logger.info(f"Payment {payment.id} marked as disputed")
                
                return {
                    'success': True,
                    'payment_id': payment.id,
                    'status': 'disputed'
                }
            else:
                logger.warning(f"No payment found for disputed charge {charge_id}")
                return {'success': True, 'message': 'Payment not found for dispute'}
        
        # Handle charge dispute funds withdrawn
        elif event['type'] == 'charge.dispute.funds_withdrawn':
            dispute = event['data']['object']
            charge_id = dispute.get('charge')
            amount = Decimal(dispute.get('amount', 0)) / 100
            
            logger.warning(f"Dispute funds withdrawn for charge {charge_id} - Amount: ${amount}")
            
            # Find the payment by charge_id
            payment = Payment.query.filter_by(stripe_charge_id=charge_id).first()
            
            if payment:
                # Update payment with funds withdrawn information
                withdraw_note = f"\n[FUNDS WITHDRAWN] {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} - Amount: ${amount} withdrawn due to dispute"
                payment.notes = (payment.notes or '') + withdraw_note
                db.session.commit()
                
                logger.info(f"Payment {payment.id} updated with funds withdrawn notice")
                
                return {
                    'success': True,
                    'payment_id': payment.id,
                    'status': 'funds_withdrawn'
                }
            else:
                logger.warning(f"No payment found for charge {charge_id} with funds withdrawn")
                return {'success': True, 'message': 'Payment not found for funds withdrawal'}
        
        # Handle charge dispute closed (won or lost)
        elif event['type'] == 'charge.dispute.closed':
            dispute = event['data']['object']
            charge_id = dispute.get('charge')
            status = dispute.get('status')  # won, lost, etc.
            
            logger.info(f"Dispute closed for charge {charge_id} - Status: {status}")
            
            # Find the payment by charge_id
            payment = Payment.query.filter_by(stripe_charge_id=charge_id).first()
            
            if payment:
                # Update payment based on dispute outcome
                close_note = f"\n[DISPUTE CLOSED] {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} - Outcome: {status}"
                payment.notes = (payment.notes or '') + close_note
                
                if status == 'won':
                    # Dispute won, payment remains valid
                    payment.status = 'completed'
                elif status == 'lost':
                    # Dispute lost, mark as failed
                    payment.status = 'failed'
                
                db.session.commit()
                
                logger.info(f"Payment {payment.id} dispute resolved - Status: {status}")
                
                return {
                    'success': True,
                    'payment_id': payment.id,
                    'dispute_status': status
                }
            else:
                logger.warning(f"No payment found for closed dispute on charge {charge_id}")
                return {'success': True, 'message': 'Payment not found for dispute closure'}
        
        logger.info(f"Event type {event['type']} not handled")
        return {'success': True, 'message': 'Event type not handled'}
    
    @staticmethod
    def admin_override_line_item_status(
        line_item_id: int,
        new_status: str,
        admin_user_id: int,
        remarks: str
    ) -> EnrollmentLineItem:
        """
        Allow admin to manually override payment status of a line item.
        
        Args:
            line_item_id: ID of line item to update
            new_status: New status ('paid', 'rejected', 'pending')
            admin_user_id: ID of admin making the change
            remarks: Admin's explanation for the override
            
        Returns:
            Updated EnrollmentLineItem instance
            
        Raises:
            PaymentValidationError: If validation fails
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Validate line item exists
        line_item = EnrollmentLineItem.query.get(line_item_id)
        if not line_item:
            raise PaymentValidationError(f"Line item {line_item_id} not found")
        
        # Validate status
        valid_statuses = ['paid', 'rejected', 'pending']
        if new_status not in valid_statuses:
            raise PaymentValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        
        # Validate remarks provided
        if not remarks or not remarks.strip():
            raise PaymentValidationError("Admin remarks are required when overriding status")
        
        # Validate admin user exists
        admin_user = User.query.get(admin_user_id)
        if not admin_user:
            raise PaymentValidationError(f"Admin user {admin_user_id} not found")
        
        logger.info(f"Admin {admin_user.username} (ID: {admin_user_id}) overriding line item {line_item_id} status to '{new_status}'")
        
        # Update line item
        old_status = line_item.status
        line_item.status = new_status
        
        # If marking as paid, set amount_paid to total
        if new_status == 'paid':
            line_item.amount_paid = line_item.total
            logger.info(f"Marking line item as paid - amount_paid set to {line_item.total}")
        
        # If marking as rejected or pending, don't change amount_paid
        # (admin might have rejected after partial payment)
        
        # Add admin tracking
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        admin_note = f"[{timestamp}] Admin override by {admin_user.username} (ID: {admin_user_id}): Changed status from '{old_status}' to '{new_status}'. Remarks: {remarks}"
        
        if line_item.admin_remarks:
            line_item.admin_remarks += f"\n\n{admin_note}"
        else:
            line_item.admin_remarks = admin_note
        
        line_item.manually_adjusted_by_user_id = admin_user_id
        
        db.session.commit()
        
        logger.info(f"Line item {line_item_id} status updated successfully")
        
        return line_item
    
    @staticmethod
    def request_refund(
        line_item_id: int,
        user_id: int,
        amount: Decimal,
        reason: str
    ) -> Refund:
        """
        Create a refund request for a paid line item.
        Request goes to superuser for approval.
        
        Args:
            line_item_id: EnrollmentLineItem ID
            user_id: User ID requesting refund (student)
            amount: Amount to refund
            reason: Reason for refund request
            
        Returns:
            Refund instance with status='requested'
            
        Raises:
            PaymentValidationError: If validation fails
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Validate line item
        line_item = EnrollmentLineItem.query.get(line_item_id)
        if not line_item:
            raise PaymentValidationError(f"Line item {line_item_id} not found")
        
        # Validate line item is paid
        if line_item.status != 'paid':
            raise PaymentValidationError("Can only request refund for paid items")
        
        # Check for existing pending refund requests
        existing_refund = Refund.query.filter_by(
            enrollment_line_item_id=line_item_id,
            status='requested'
        ).first()
        if existing_refund:
            raise PaymentValidationError("A refund request for this item is already pending review")
        
        # Validate amount
        if amount <= 0:
            raise PaymentValidationError("Refund amount must be greater than zero")
        
        max_refundable = line_item.amount_paid - line_item.amount_refunded
        if amount > max_refundable:
            raise PaymentValidationError(f"Refund amount cannot exceed ${max_refundable:.2f}")
        
        # Validate user
        user = User.query.get(user_id)
        if not user:
            raise PaymentValidationError(f"User {user_id} not found")
        
        logger.info(f"Creating refund request for line item {line_item_id} by user {user.username}")
        
        # Create refund request
        refund = Refund(
            enrollment_line_item_id=line_item_id,
            requested_by_user_id=user_id,
            amount=amount,
            status='requested',
            request_date=datetime.utcnow(),
            reason=reason
        )
        
        db.session.add(refund)
        db.session.commit()
        
        logger.info(f"Refund request created - ID: {refund.id}")
        
        return refund
    
    @staticmethod
    def get_pending_refund_requests() -> List[Refund]:
        """
        Get all pending refund requests for superuser review.
        
        Returns:
            List of Refund instances with status='requested'
        """
        return Refund.query.filter_by(status='requested').order_by(Refund.request_date.desc()).all()
    
    @staticmethod
    def approve_refund_request(
        refund_id: int,
        superuser_id: int,
        refund_method: str,
        admin_notes: Optional[str] = None
    ) -> Refund:
        """
        Approve a refund request and process the refund.
        Only superusers can approve refunds.
        
        Args:
            refund_id: Refund ID
            superuser_id: Superuser ID approving the refund
            refund_method: Method of refund (stripe, cash, check)
            admin_notes: Optional notes from superuser
            
        Returns:
            Updated Refund instance with status='processed'
            
        Raises:
            PaymentValidationError: If validation fails
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Validate refund exists and is pending
        refund = Refund.query.get(refund_id)
        if not refund:
            raise PaymentValidationError(f"Refund {refund_id} not found")
        
        if refund.status != 'requested':
            raise PaymentValidationError(f"Refund must be in 'requested' status, currently: {refund.status}")
        
        # Validate superuser
        superuser = User.query.get(superuser_id)
        if not superuser:
            raise PaymentValidationError(f"Superuser {superuser_id} not found")
        
        # Validate line item still exists and has enough paid amount
        line_item = refund.enrollment_line_item
        max_refundable = line_item.amount_paid - line_item.amount_refunded
        
        if refund.amount > max_refundable:
            raise PaymentValidationError(f"Cannot refund ${refund.amount:.2f} - only ${max_refundable:.2f} available")
        
        logger.info(f"Superuser {superuser.username} approving refund {refund_id}")
        
        # Update refund status
        refund.status = 'processed'
        refund.refund_method = refund_method
        refund.refund_date = datetime.utcnow()
        refund.processed_by_user_id = superuser_id
        refund.admin_notes = admin_notes
        
        # Update line item
        line_item.amount_refunded += refund.amount
        
        # Update line item status based on refund
        if line_item.amount_refunded >= line_item.amount_paid:
            line_item.status = 'refunded'
        elif line_item.amount_refunded > 0:
            line_item.status = 'partially_refunded'
        
        db.session.commit()
        
        logger.info(f"Refund {refund_id} processed successfully - ${refund.amount} refunded")
        
        return refund
    
    @staticmethod
    def deny_refund_request(
        refund_id: int,
        superuser_id: int,
        admin_notes: str
    ) -> Refund:
        """
        Deny a refund request.
        Only superusers can deny refunds.
        
        Args:
            refund_id: Refund ID
            superuser_id: Superuser ID denying the refund
            admin_notes: Reason for denial
            
        Returns:
            Updated Refund instance with status='denied'
            
        Raises:
            PaymentValidationError: If validation fails
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Validate refund exists and is pending
        refund = Refund.query.get(refund_id)
        if not refund:
            raise PaymentValidationError(f"Refund {refund_id} not found")
        
        if refund.status != 'requested':
            raise PaymentValidationError(f"Refund must be in 'requested' status, currently: {refund.status}")
        
        # Validate superuser
        superuser = User.query.get(superuser_id)
        if not superuser:
            raise PaymentValidationError(f"Superuser {superuser_id} not found")
        
        # Validate admin notes provided
        if not admin_notes or not admin_notes.strip():
            raise PaymentValidationError("Admin notes are required when denying a refund")
        
        logger.info(f"Superuser {superuser.username} denying refund {refund_id}")
        
        # Update refund status
        refund.status = 'denied'
        refund.processed_by_user_id = superuser_id
        refund.admin_notes = admin_notes
        refund.refund_date = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Refund {refund_id} denied")
        
        return refund
