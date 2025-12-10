# Payment System Database Schema

## Overview
This document outlines the database structure for the Stripe payment integration system, including payable items, enrollments, payments, refunds, and discount codes.

---

## dbdiagram.io Schema

Copy the code below directly into dbdiagram.io to visualize the schema:

---

```
// Payment System Schema for CWMT
// Copy this entire block into dbdiagram.io

Table payable_item_templates {
  id integer [pk, increment]
  name varchar(255) [not null]
  description text
  base_price decimal(10,2) [not null]
  item_type varchar(50) [not null, note: 'tuition, rental, equipment, misc']
  is_taxable boolean [default: false]
  is_active boolean [default: true]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
  
  indexes {
    item_type
    is_active
  }
}

Table course_template_payable_items {
  id integer [pk, increment]
  course_template_id integer [not null]
  payable_item_template_id integer [not null]
  is_required boolean [default: false]
  display_order integer [default: 0]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
  
  indexes {
    (course_template_id, payable_item_template_id) [unique]
    display_order
  }
}

Table course_payable_items {
  id integer [pk, increment]
  course_id integer [not null]
  payable_item_template_id integer [not null]
  price decimal(10,2) [not null, note: 'Snapshot from template at course creation']
  is_required boolean [default: false, note: 'Copied from template']
  is_available boolean [default: true]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
  
  indexes {
    course_id
    (course_id, payable_item_template_id)
  }
}

Table enrollment_line_items {
  id integer [pk, increment]
  enrollment_id integer [not null]
  course_payable_item_id integer [not null]
  quantity integer [default: 1]
  unit_price decimal(10,2) [not null, note: 'Snapshot at enrollment time']
  subtotal decimal(10,2) [not null, note: 'unit_price * quantity']
  discount_amount decimal(10,2) [default: 0.00]
  tax_amount decimal(10,2) [default: 0.00]
  total decimal(10,2) [not null, note: 'subtotal - discount + tax']
  status varchar(50) [default: 'pending', note: 'pending, paid, refunded']
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
  
  indexes {
    enrollment_id
    status
    (enrollment_id, course_payable_item_id)
  }
}

Table payments {
  id integer [pk, increment]
  enrollment_id integer [not null]
  amount decimal(10,2) [not null]
  payment_method varchar(50) [not null, note: 'stripe, cash, check, other']
  stripe_payment_intent_id varchar(255) [null]
  status varchar(50) [default: 'pending', note: 'pending, completed, failed']
  payment_date timestamp [default: `now()`]
  notes text [note: 'e.g., Student paid $100 in cash']
  processed_by_user_id integer [not null]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
  
  indexes {
    enrollment_id
    status
    stripe_payment_intent_id [unique]
    payment_date
  }
}

Table payment_allocations {
  id integer [pk, increment]
  payment_id integer [not null]
  enrollment_line_item_id integer [not null]
  amount_applied decimal(10,2) [not null]
  created_at timestamp [default: `now()`]
  
  indexes {
    payment_id
    enrollment_line_item_id
    (payment_id, enrollment_line_item_id) [unique]
  }
}

Table refunds {
  id integer [pk, increment]
  original_payment_id integer [not null]
  enrollment_line_item_id integer [not null]
  amount decimal(10,2) [not null]
  refund_method varchar(50) [not null, note: 'stripe, cash, check']
  stripe_refund_id varchar(255) [null]
  reason text
  refund_date timestamp [default: `now()`]
  processed_by_user_id integer [not null]
  created_at timestamp [default: `now()`]
  
  indexes {
    original_payment_id
    enrollment_line_item_id
    stripe_refund_id [unique]
    refund_date
  }
}

Table discount_codes {
  id integer [pk, increment]
  code varchar(100) [unique, not null]
  description text
  discount_type varchar(50) [not null, note: 'percentage, fixed_amount']
  discount_value decimal(10,2) [not null]
  applies_to varchar(50) [not null, note: 'course_template, payable_item_template']
  target_id integer [not null, note: 'ID of course_template or payable_item_template']
  max_uses_total integer [null, note: 'null = unlimited']
  max_uses_per_user integer [default: 1]
  current_uses integer [default: 0]
  valid_from timestamp [not null]
  valid_until timestamp [not null]
  is_active boolean [default: true]
  created_by_user_id integer [not null]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
  
  indexes {
    code [unique]
    is_active
    valid_until
    applies_to
  }
}

Table discount_usages {
  id integer [pk, increment]
  discount_code_id integer [not null]
  user_id integer [not null]
  enrollment_id integer [not null]
  amount_discounted decimal(10,2) [not null]
  used_at timestamp [default: `now()`]
  
  indexes {
    discount_code_id
    user_id
    enrollment_id
    (discount_code_id, user_id, enrollment_id) [unique]
  }
}

// Relationships
Ref: course_template_payable_items.payable_item_template_id > payable_item_templates.id
Ref: course_payable_items.course_id > courses.id
Ref: course_payable_items.payable_item_template_id > payable_item_templates.id
Ref: enrollment_line_items.enrollment_id > course_enrollment.id
Ref: enrollment_line_items.course_payable_item_id > course_payable_items.id
Ref: payments.enrollment_id > course_enrollment.id
Ref: payments.processed_by_user_id > users.id
Ref: payment_allocations.payment_id > payments.id
Ref: payment_allocations.enrollment_line_item_id > enrollment_line_items.id
Ref: refunds.original_payment_id > payments.id
Ref: refunds.enrollment_line_item_id > enrollment_line_items.id
Ref: refunds.processed_by_user_id > users.id
Ref: discount_codes.created_by_user_id > users.id
Ref: discount_usages.discount_code_id > discount_codes.id
Ref: discount_usages.user_id > users.id
Ref: discount_usages.enrollment_id > course_enrollment.id
```

---

## Business Logic Summary

### Checkout Flow
1. Student selects items → creates `enrollment_line_items` (status="pending")
2. Student enters discount code(s)
3. System validates codes (expiration + 30s grace, max uses, user eligibility)
4. System calculates discount for applicable line items
5. System picks **single best code** (maximum discount amount)
6. System updates `enrollment_line_items.discount_amount` and recalculates `total`
7. Student pays → creates `payment` record
8. System creates `payment_allocations` linking payment to line items
9. Update `enrollment_line_items.status` to "paid"
10. Create `discount_usages` record if code was used

### Refund Flow
1. Admin selects specific line item to refund
2. System creates `refund` record with `amount = enrollment_line_items.total`
3. Process Stripe refund (if original payment method was Stripe)
4. Update `enrollment_line_items.status` to "refunded"
5. Check if all required items are refunded → update enrollment status if needed

### Partial Payment Flow (Cash + Card)
1. Instructor enters $100 cash → creates `payment` record (method="cash", notes="Paid in cash")
2. Creates `payment_allocations` records (proportional or specific line items)
3. Remaining balance shown to student
4. Student pays $400 via Stripe → creates second `payment` record
5. Both payments linked to same line items via `payment_allocations`

### Discount Code Logic
- **No stacking:** Only one discount code per checkout
- **Best code wins:** System automatically selects the code giving maximum discount
- **Item-specific:** Course codes apply only to tuition, rental codes only to rentals
- **Validation window:** Code valid until expiration timestamp + 30 seconds grace period
- **Usage limits:** Tracks both per-user and total usage limits

---

## Key Design Decisions

### Price Snapshots
- **PayableItemTemplate.base_price:** Owner's master price
- **CoursePayableItem.price:** Price when course instance created (copied from template)
- **EnrollmentLineItem.unit_price:** Price when student enrolled (copied from course item)

This three-tier snapshot ensures price changes don't affect existing enrollments.

### Refund Accuracy
- Always refund what the student actually paid: `EnrollmentLineItem.total`
- Each line item tracks its own discount, so refunds are accurate even with discounts applied
- No recalculation needed on refund—amount is already recorded

### Status Management
- **EnrollmentLineItem.status:** Tracks individual item payment status
- **Enrollment status:** Changes to "unpaid" only if required items are refunded
- **Payment.status:** Tracks transaction state (pending, completed, failed)

### Discount Application
- Discount codes target specific templates (course or payable item)
- Code applies only to matching line items in the cart
- For course codes: applies to tuition only, not accessories
- Discount amount stored per line item for accurate refund handling

---

## Implementation Notes

### Required Models
1. `PayableItemTemplate` - Master catalog of payable items
2. `CourseTemplatePayableItem` - M2M join for template configuration
3. `CoursePayableItem` - Per-course pricing and availability
4. `EnrollmentLineItem` - Student's selected items and pricing
5. `Payment` - Transaction records (Stripe, cash, check)
6. `PaymentAllocation` - Maps payments to line items
7. `Refund` - Refund transaction records
8. `DiscountCode` - Promotional codes configuration
9. `DiscountUsage` - Tracks code redemptions

### Integration Points
- **Stripe API:** Payment intents for card payments
- **Stripe API:** Refund processing for card refunds
- **Flask-Mail:** Payment confirmation emails
- **Admin Dashboard:** Payment/refund processing interface
- **Student Portal:** Checkout and payment interface

### Security Considerations
- Store Stripe payment intent IDs for audit trail
- Track `processed_by_user_id` for all manual transactions
- Validate discount codes server-side (never trust client)
- Implement idempotency for payment processing
- Use database transactions for payment/allocation creation

---

Generated: November 19, 2025
