# Overview
## Tables
1. payments
2. payment_line_items
3. stripe_webhook_events (optional but recommended for debugging)

---

## payments
This is the main payment record that tracks the overall transaction.

### Columns
- **id** - Primary key (link to payment details)
- **student_id** - Foreign key to students table (who made the payment)
- **course_instance_id** - Foreign key to course_instances table (what course is this for)
- **enrollment_id** - Foreign key to enrollments table (direct link to enrollment record)
- **stripe_payment_intent_id** - Stripe PaymentIntent ID (e.g., pi_xxx)
- **stripe_charge_id** - Stripe Charge ID (e.g., ch_xxx)
- **status** - Payment status (see status values below)
- **total_cost** - Total amount charged (in cents)
- **amount_refunded** - Total amount refunded (in cents, default 0)
- **currency** - Currency code (default 'usd')
- **payment_method_type** - Type of payment method (card, bank_transfer, etc.)
- **last4** - Last 4 digits of card (optional, for display purposes)
- **customer_email** - Email address used for payment
- **receipt_url** - Stripe receipt URL
- **idempotency_key** - Unique key to prevent duplicate charges
- **created_at** - Timestamp when payment was created
- **updated_at** - Timestamp when payment was last updated

### Status Values
- `pending` - Payment intent created but not yet confirmed
- `succeeded` - Payment successfully processed
- `failed` - Payment failed
- `canceled` - Payment was canceled
- `refunded` - Fully refunded
- `partially_refunded` - Partially refunded

---

## payment_line_items
Itemized list of all payable items included in the payment.

### Columns
- **id** - Primary key
- **payment_id** - Foreign key to payments table
- **payable_template_id** - Foreign key to payable_templates table (the item being paid for)
- **cost_of_item** - Cost of this specific item (in cents)
- **quantity** - Quantity of this item (default 1)
- **amount_refunded** - Amount refunded for this specific item (in cents, default 0)
- **status** - Status of this line item (see status values below)
- **created_at** - Timestamp when record was created
- **updated_at** - Timestamp when record was last updated

### Status Values
- `active` - Item is active/paid
- `refunded` - Item fully refunded
- `partially_refunded` - Item partially refunded

---

## stripe_webhook_events (Optional but Recommended)
Logs all Stripe webhook events for debugging and audit trail.

### Columns
- **id** - Primary key
- **stripe_event_id** - Stripe event ID (e.g., evt_xxx)
- **event_type** - Type of event (e.g., payment_intent.succeeded)
- **payment_id** - Foreign key to payments (nullable)
- **payload** - JSON payload of the webhook event
- **processed** - Boolean indicating if event was successfully processed
- **error_message** - Error message if processing failed (nullable)
- **created_at** - Timestamp when webhook was received

---

## Relationships

### payments
- Belongs to: Student
- Belongs to: CourseInstance
- Belongs to: Enrollment
- Has many: PaymentLineItems

### payment_line_items
- Belongs to: Payment
- Belongs to: PayableTemplate

### stripe_webhook_events
- Belongs to: Payment (optional)

---

## Notes

1. **All amounts in cents** - Stripe works in cents to avoid floating point issues
2. **Idempotency** - Use idempotency_key to prevent duplicate charges if user clicks submit multiple times
3. **Refunds** - Track at both overview and detail level for accurate accounting
4. **Audit Trail** - Webhook events table provides complete history of all Stripe events
5. **Currency** - Always store and default to 'usd' but allow flexibility for future
6. **Receipt URL** - Stripe provides hosted receipt page, store URL for easy access