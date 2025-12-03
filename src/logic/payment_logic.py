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
            EnrollmentLineItem.status == 'pending'
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
        
        # Create payment record
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
        
        for line_item in line_items:
            amount_due = line_item.total - line_item.amount_paid
            
            if amount_due <= 0:
                continue
            
            # Allocate up to the amount due
            allocation_amount = min(remaining_amount, amount_due)
            
            # Create allocation
            allocation = PaymentAllocation(
                payment_id=payment.id,
                enrollment_line_item_id=line_item.id,
                amount_applied=allocation_amount
            )
            
            db.session.add(allocation)
            
            # Update line item
            line_item.amount_paid += allocation_amount
            
            if line_item.amount_paid >= line_item.total:
                line_item.status = 'paid'
            
            remaining_amount -= allocation_amount
            
            if remaining_amount <= 0:
                break
        
        db.session.commit()
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
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            raise PaymentBusinessError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise PaymentBusinessError("Invalid signature")
        
        # Handle payment intent succeeded
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            
            # Extract metadata
            metadata = payment_intent.get('metadata', {})
            enrollment_id = metadata.get('enrollment_id')
            user_id = metadata.get('user_id')
            line_item_ids = metadata.get('line_item_ids', '').split(',')
            
            if not all([enrollment_id, user_id, line_item_ids]):
                raise PaymentBusinessError("Missing required metadata")
            
            # Record the payment
            amount = Decimal(payment_intent['amount']) / 100  # Convert cents to dollars
            
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
            
            return {
                'success': True,
                'payment_id': payment.id
            }
        
        return {'success': True, 'message': 'Event type not handled'}
