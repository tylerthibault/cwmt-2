# Stripe Integration Todo List

## Overview
Implementing Stripe payment processing for course enrollments with webhook handling for payment confirmation.

## Prerequisites
- ✅ Stripe account created
- ✅ Development API keys obtained:
  - `stripe_publishable_key`
  - `stripe_secret_key`
  - `stripe_webhook_secret`

---

## Implementation Steps

### 1. Configuration & Setup
- [x] **Add Stripe credentials to config.py**
  - Add environment variables for all three Stripe keys
  - Ensure keys are loaded from environment variables

- [x] **Install stripe Python package**
  - Add `stripe` to requirements.txt
  - Run `pip install stripe`

### 2. Database Models
- [x] **Create Payment model for tracking transactions**
  - Fields: id, amount, currency, status, stripe_payment_intent_id, student_id, course_instance_id
  - Timestamps: created_at, updated_at
  - ✅ Created in `src/models/stripe/payments.py`
  - BONUS: Added additional fields (enrollment_id, stripe_charge_id, idempotency_key, payment_method_type, last4, customer_email, receipt_url, amount_refunded)

- [x] **Create Enrollment model linking students to courses**
  - Fields: id, student_id, course_instance_id, payment_id, enrollment_date, status
  - Relationships to Student, CourseInstance, Payment
  - ✅ Created in `src/models/course_folder/enrollment.py`
  - Added completion_date and unique constraint for student/course

- [x] **Add payment status field to track transaction states**
  - Status enum: pending, succeeded, failed, refunded, canceled
  - Add to both Payment and Enrollment models
  - ✅ Status fields added with proper enums

- [x] **BONUS: Create PaymentLineItem model for itemized billing**
  - Tracks individual payable items (tuition, fees, etc.)
  - ✅ Created in `src/models/stripe/payment_line_items.py`

- [x] **BONUS: Create StripeWebhookEvent model for audit trail**
  - Logs all Stripe webhook events for debugging
  - ✅ Created in `src/models/stripe/stripe_webhook_events.py`

### 3. Backend Routes & Logic
- [ ] **Create checkout route to display payment page**
  - Route: `/courses/student/checkout/<course_instance_id>`
  - Fetch course details and calculate total (tuition + other payables)
  - Render checkout template

- [ ] **Create payment intent endpoint for Stripe**
  - Route: `/courses/student/create-payment-intent` (POST)
  - Create Stripe PaymentIntent with course amount
  - Return client_secret to frontend

- [ ] **Create webhook endpoint for payment confirmation**
  - Route: `/stripe/webhook` (POST)
  - Verify webhook signature
  - Handle Stripe events

- [ ] **Handle payment success in webhook**
  - Update Payment status to 'succeeded'
  - Create Enrollment record
  - Update course enrollment count

- [ ] **Handle payment failure in webhook**
  - Update Payment status to 'failed'
  - Log failure reason

### 4. Frontend Templates & JavaScript
- [ ] **Build checkout template with Stripe Elements**
  - Create `templates/private/students/checkout/checkout.html`
  - Display course info and price breakdown
  - Add Stripe Elements card input
  - Include submit button and error display

- [ ] **Add JavaScript for Stripe payment processing**
  - Initialize Stripe.js with publishable key
  - Mount card element
  - Handle form submission
  - Process payment with PaymentIntent
  - Show loading states and errors

- [ ] **Create success page after payment**
  - Route: `/courses/student/payment-success/<enrollment_id>`
  - Display confirmation message
  - Show enrollment details
  - Link to student dashboard

- [ ] **Create cancel/failure page**
  - Route: `/courses/student/payment-failed`
  - Display error message
  - Offer option to retry
  - Link back to courses

### 5. Integration & Polish
- [ ] **Add email confirmation for successful enrollment**
  - Send email with course details
  - Include enrollment confirmation number
  - Add course start date and location

- [ ] **Update student dashboard to show enrolled courses**
  - Display list of enrolled courses
  - Show payment status
  - Add links to course details

### 6. Testing & Deployment
- [ ] **Test with Stripe test cards**
  - Success: 4242 4242 4242 4242
  - Decline: 4000 0000 0000 0002
  - 3D Secure: 4000 0027 6000 3184
  - Test webhook events locally

- [ ] **Configure webhook in Stripe dashboard**
  - Add webhook endpoint URL
  - Select events to listen to:
    - `payment_intent.succeeded`
    - `payment_intent.payment_failed`
  - Copy webhook signing secret

---

## Notes
- All prices should be in cents for Stripe (multiply by 100)
- Use idempotency keys for payment creation
- Store PaymentIntent ID for tracking
- Handle edge cases (duplicate payments, refunds)
- Ensure proper error handling and user feedback
- Log all payment-related events for audit trail

## Next Steps
Start with Configuration & Setup (steps 1-2), then move to Database Models (steps 3-5).
