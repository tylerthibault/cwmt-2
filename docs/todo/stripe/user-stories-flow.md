# Stripe Payment User Stories & Flow

## Overview
This document outlines the user journey and technical flow for course enrollment payments using Stripe.

---

## User Story 1: Student Enrolls in a Course

### Actor
Student (logged in)

### Preconditions
- Student is logged in
- Student is viewing available courses on calendar/dashboard
- Course has available spots
- Student is not already enrolled

### Flow

#### Step 1: Navigate to Checkout
**User Action:** Student clicks "Sign Up" or "Enroll" button on a course

**Route:** `GET /student/checkout/<course_instance_id>`

**Backend Process:**
1. Verify student is logged in
2. Get course instance details
3. Check if student already enrolled → redirect to dashboard if yes
4. Check if course is full → show error if full
5. Fetch all payable items (tuition + fees) from course template
6. Calculate total amount in cents
7. Render checkout page with:
   - Course details (name, date, location)
   - Itemized costs breakdown
   - Total amount
   - Stripe publishable key

**User Sees:** Checkout page with course info and payment form

---

#### Step 2: Student Fills Payment Information
**User Action:** Student enters credit card information in Stripe Elements form

**Frontend Process:**
1. Stripe.js loads on page
2. Card Element mounts to form
3. User enters card details (handled securely by Stripe, never touches your server)
4. User clicks "Pay Now" button

---

#### Step 3: Create Payment Intent
**User Action:** Clicks "Pay Now"

**Frontend Action:** JavaScript calls `POST /api/payments/create-intent`

**Request Body:**
```json
{
  "course_instance_id": 123
}
```

**Backend Process:**
1. Verify student is authenticated
2. Fetch course instance and validate
3. Re-check enrollment status and capacity
4. Calculate total from payable templates
5. Generate unique idempotency key (UUID)
6. Create Stripe PaymentIntent via API:
   - Amount in cents
   - Currency: USD
   - Metadata: student_id, course_instance_id, email
7. Create Payment record in database:
   - Status: 'pending'
   - Link to student and course
   - Store PaymentIntent ID
8. Create PaymentLineItem records for each payable
9. Return client_secret to frontend

**Response:**
```json
{
  "clientSecret": "pi_xxx_secret_yyy",
  "paymentId": 456,
  "amount": 50000
}
```

**User Sees:** Loading indicator

---

#### Step 4: Confirm Payment with Stripe
**Frontend Process:**
1. Receives client_secret
2. Calls `stripe.confirmCardPayment(clientSecret, paymentMethod)`
3. Stripe processes payment (may show 3D Secure if required)
4. Wait for confirmation

**User Sees:** Payment processing, possible 3D Secure modal

---

#### Step 5A: Payment Succeeds (Happy Path)

**Frontend Process:**
1. `confirmCardPayment` returns success
2. Poll `GET /api/payments/status/<payment_id>` until status is 'succeeded'
3. Redirect to success page: `/student/payment-success/<enrollment_id>`

**Stripe Backend (Webhook):**
1. Stripe sends webhook: `payment_intent.succeeded`
2. Route: `POST /webhooks/stripe`
3. Verify webhook signature
4. Check if event already processed (idempotency)
5. Log webhook event in database
6. Call `handle_payment_success()`:
   - Find Payment by PaymentIntent ID
   - Update payment status to 'succeeded'
   - Store receipt URL and payment method details
   - Create Enrollment record (student + course)
   - Link enrollment to payment
   - Mark webhook as processed
7. (TODO) Send confirmation email

**Route:** `GET /student/payment-success/<enrollment_id>`

**Backend Process:**
1. Verify enrollment exists and belongs to student
2. Fetch enrollment, course, and payment details
3. Render success page

**User Sees:**
- Success message
- Enrollment confirmation
- Course details (date, location, time)
- Receipt link
- Link to "My Enrollments"

---

#### Step 5B: Payment Fails (Failure Path)

**Frontend Process:**
1. `confirmCardPayment` returns error
2. Show error message on checkout page
3. Allow user to try again or redirect to `/student/payment-failed`

**Stripe Backend (Webhook):**
1. Stripe sends webhook: `payment_intent.payment_failed`
2. Route: `POST /webhooks/stripe`
3. Verify webhook signature
4. Log webhook event
5. Call `handle_payment_failure()`:
   - Find Payment by PaymentIntent ID
   - Update payment status to 'failed'
   - Mark webhook as processed
6. (TODO) Send failure notification email

**Route:** `GET /student/payment-failed`

**Backend Process:**
1. Render failure page

**User Sees:**
- Error message explaining failure
- Option to try again
- Link back to available courses
- Support contact information

---

## User Story 2: Student Views Their Enrollments

### Actor
Student (logged in)

### Flow

**Route:** `GET /student/my-enrollments`

**Backend Process:**
1. Verify student is authenticated
2. Fetch all enrollments for student (ordered by date)
3. For each enrollment, include:
   - Course instance details
   - Enrollment status
   - Payment status
   - Course dates and location

**User Sees:**
- List of enrolled courses
- Each course shows:
  - Course name and level
  - Start date and duration
  - Status (enrolled, completed, dropped)
  - Payment status (paid, pending, refunded)
  - Location
  - Action buttons (view details, drop course, etc.)

---

## User Story 3: Webhook Processing (Background)

### Actor
Stripe (automated system)

### Trigger
Any payment event in Stripe

### Flow

**Route:** `POST /webhooks/stripe`

**Headers:**
```
Stripe-Signature: t=xxx,v1=yyy
```

**Body:** Full Stripe event JSON

**Process:**
1. Verify signature with webhook secret
2. Return 400 if signature invalid
3. Check if event already processed (by event ID)
4. Return 200 if already processed (idempotency)
5. Create StripeWebhookEvent record with full payload
6. Route to handler based on event type:
   - `payment_intent.succeeded` → Create enrollment
   - `payment_intent.payment_failed` → Update status
   - `charge.succeeded` → Update charge ID
7. Update webhook event as processed or failed
8. Return 200 (Stripe will retry on 500 errors)

### Important Notes
- **No authentication required** (Stripe needs public access)
- **Signature verification is the security**
- **Idempotency prevents duplicate processing**
- **All events logged for audit trail**

---

## Edge Cases & Error Handling

### 1. Student Already Enrolled
**When:** Student tries to checkout for course they're already in
**Action:** Redirect to dashboard with message
**Where:** Checkout route validation

### 2. Course is Full
**When:** Enrollment limit reached before payment completes
**Action:** Show error on checkout, prevent payment intent creation
**Where:** Checkout and create-intent validation

### 3. Duplicate Payment Intent
**When:** User clicks "Pay Now" multiple times
**Action:** Idempotency key ensures only one intent created
**Where:** Stripe API handles via idempotency_key

### 4. Payment Succeeds but Webhook Fails
**When:** Webhook endpoint is down
**Action:** Stripe retries webhook for 3 days
**Where:** Manual reconciliation may be needed

### 5. Webhook Arrives Before Frontend Confirmation
**When:** Network timing differences
**Action:** Frontend polls payment status until updated
**Where:** Status polling in success flow

### 6. Student Refreshes During Payment
**When:** User hits back/refresh mid-payment
**Action:** Check existing payment record, resume or restart
**Where:** Frontend should track payment_id in session

---

## Data Flow Diagram

```
┌─────────┐     ┌──────────┐     ┌─────────┐     ┌─────────┐
│ Student │────▶│  Checkout │────▶│  Stripe │────▶│ Webhook │
│  Views  │     │   Page   │     │   API   │     │ Handler │
└─────────┘     └──────────┘     └─────────┘     └─────────┘
                      │                │                │
                      ▼                ▼                ▼
                 ┌──────────┐    ┌─────────┐    ┌──────────┐
                 │ Payment  │    │ Payment │    │Enrollment│
                 │  Intent  │    │ Record  │    │  Record  │
                 └──────────┘    └─────────┘    └──────────┘
```

---

## Security Considerations

### 1. Authentication
- All student routes require `@login_required` and `@role_required('student')`
- Webhook route has NO authentication (relies on signature)

### 2. Authorization
- Students can only see their own payments/enrollments
- Payment status endpoint verifies ownership

### 3. Payment Security
- Card details never touch your server (Stripe Elements)
- PaymentIntent uses server-side secret key
- Webhook signature prevents spoofing

### 4. Idempotency
- Payment creation uses UUID idempotency key
- Webhook events checked for duplicates
- Prevents double-charging and double-enrollment

---

## Testing Checklist

### Happy Path
- [ ] Student can view checkout page
- [ ] Payment intent created successfully
- [ ] Card payment processes with test card
- [ ] Webhook received and processed
- [ ] Enrollment created in database
- [ ] Student redirected to success page
- [ ] Enrollment appears in "My Enrollments"

### Failure Cases
- [ ] Declined card shows error
- [ ] Full course prevents enrollment
- [ ] Already enrolled redirects properly
- [ ] Invalid course ID returns 404
- [ ] Webhook signature verification works
- [ ] Failed payment updates status

### Stripe Test Cards
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`
- 3D Secure: `4000 0027 6000 3184`

---

## Future Enhancements

1. **Email Notifications**
   - Confirmation email on successful payment
   - Receipt with course details
   - Failure notification with support info

2. **Refund Handling**
   - Admin refund interface
   - Partial refunds for line items
   - Webhook handler for refund events

3. **Payment Plans**
   - Installment payments
   - Deposit + balance
   - Recurring subscriptions

4. **Reporting**
   - Payment analytics dashboard
   - Revenue reports by course
   - Failed payment tracking
