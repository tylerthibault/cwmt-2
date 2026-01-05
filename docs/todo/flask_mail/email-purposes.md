# Email Purposes for CWMT

This document defines all email purposes (triggers) for the Course/Workshop Management Training application.

---

## User Account Management

### `new_user`
**When:** New user account is created (by admin or self-registration)
**Recipient:** New user
**Required Variables:**
- `user_name` - User's full name
- `user_email` - User's email address
- `temp_password` - Temporary password for first login
- `login_link` - URL to login page
- `support_email` - Contact email for help

**Example Context:**
```python
{
    'user_name': 'John Smith',
    'user_email': 'john.smith@example.com',
    'temp_password': 'TempPass123!',
    'login_link': 'https://cwmt.example.com/login',
    'support_email': 'support@cwmt.example.com'
}
```

---

### `password_reset`
**When:** User requests password reset
**Recipient:** User who requested reset
**Required Variables:**
- `user_name` - User's full name
- `reset_link` - URL with reset token
- `expiry_hours` - Hours until link expires (e.g., 24)
- `user_email` - User's email address

**Example Context:**
```python
{
    'user_name': 'Jane Doe',
    'reset_link': 'https://cwmt.example.com/reset/abc123token',
    'expiry_hours': 24,
    'user_email': 'jane.doe@example.com'
}
```

---

### `password_changed`
**When:** User successfully changes password
**Recipient:** User whose password changed
**Required Variables:**
- `user_name` - User's full name
- `change_date` - Date/time of change
- `support_email` - Contact email if unauthorized

**Example Context:**
```python
{
    'user_name': 'Jane Doe',
    'change_date': '2026-01-02 14:30:00',
    'support_email': 'support@cwmt.example.com'
}
```

---

### `account_verified`
**When:** User verifies their email address
**Recipient:** User who verified
**Required Variables:**
- `user_name` - User's full name
- `login_link` - URL to login page

**Example Context:**
```python
{
    'user_name': 'John Smith',
    'login_link': 'https://cwmt.example.com/login'
}
```

---

## Course Enrollment

### `course_enrollment_confirmation`
**When:** Student enrolls in a course
**Recipient:** Student who enrolled
**Required Variables:**
- `user_name` - Student's full name
- `course_name` - Name of the course
- `course_start_date` - When course begins
- `course_end_date` - When course ends
- `course_location` - Where course takes place
- `instructor_name` - Instructor's full name
- `instructor_email` - Instructor's contact email
- `course_details_link` - URL to course details page

**Example Context:**
```python
{
    'user_name': 'Sarah Johnson',
    'course_name': 'Advanced Python Programming',
    'course_start_date': 'February 15, 2026',
    'course_end_date': 'March 15, 2026',
    'course_location': 'Room 204, Main Building',
    'instructor_name': 'Dr. Emily Chen',
    'instructor_email': 'emily.chen@cwmt.example.com',
    'course_details_link': 'https://cwmt.example.com/courses/12345'
}
```

---

### `course_waitlist_added`
**When:** Student is added to course waitlist (course is full)
**Recipient:** Student on waitlist
**Required Variables:**
- `user_name` - Student's full name
- `course_name` - Name of the course
- `waitlist_position` - Their position on waitlist (optional)
- `course_start_date` - When course begins

**Example Context:**
```python
{
    'user_name': 'Mike Wilson',
    'course_name': 'Introduction to Machine Learning',
    'waitlist_position': 3,
    'course_start_date': 'March 1, 2026'
}
```

---

### `course_waitlist_opening`
**When:** Spot opens up in a full course and waitlisted student can enroll
**Recipient:** Next student on waitlist
**Required Variables:**
- `user_name` - Student's full name
- `course_name` - Name of the course
- `enrollment_deadline` - How long they have to claim spot
- `enrollment_link` - Direct link to enroll

**Example Context:**
```python
{
    'user_name': 'Mike Wilson',
    'course_name': 'Introduction to Machine Learning',
    'enrollment_deadline': 'January 5, 2026 at 5:00 PM',
    'enrollment_link': 'https://cwmt.example.com/enroll/confirm/67890'
}
```

---

### `course_unenrollment_confirmation`
**When:** Student drops/unenrolls from a course
**Recipient:** Student who unenrolled
**Required Variables:**
- `user_name` - Student's full name
- `course_name` - Name of the course
- `unenroll_date` - When they unenrolled
- `refund_info` - Refund status/information (if applicable)

**Example Context:**
```python
{
    'user_name': 'Sarah Johnson',
    'course_name': 'Advanced Python Programming',
    'unenroll_date': 'January 10, 2026',
    'refund_info': 'Full refund will be processed within 5-7 business days.'
}
```

---

## Course Reminders

### `course_starting_soon`
**When:** Course is starting soon (e.g., 1 week before, 1 day before)
**Recipient:** All enrolled students
**Required Variables:**
- `user_name` - Student's full name
- `course_name` - Name of the course
- `course_start_date` - When course begins
- `course_start_time` - Time course begins
- `course_location` - Where course takes place
- `instructor_name` - Instructor's full name
- `preparation_notes` - What to bring/prepare (optional)

**Example Context:**
```python
{
    'user_name': 'Sarah Johnson',
    'course_name': 'Advanced Python Programming',
    'course_start_date': 'February 15, 2026',
    'course_start_time': '9:00 AM',
    'course_location': 'Room 204, Main Building',
    'instructor_name': 'Dr. Emily Chen',
    'preparation_notes': 'Please bring a laptop with Python 3.10+ installed.'
}
```

---

### `course_assignment_reminder`
**When:** Assignment deadline is approaching
**Recipient:** Students with pending assignments
**Required Variables:**
- `user_name` - Student's full name
- `course_name` - Name of the course
- `assignment_name` - Name of assignment
- `due_date` - When assignment is due
- `assignment_link` - URL to assignment details

**Example Context:**
```python
{
    'user_name': 'Sarah Johnson',
    'course_name': 'Advanced Python Programming',
    'assignment_name': 'Final Project Submission',
    'due_date': 'March 14, 2026 at 11:59 PM',
    'assignment_link': 'https://cwmt.example.com/courses/12345/assignments/5'
}
```

---

## Course Changes & Updates

### `course_cancellation`
**When:** Course is cancelled by admin/instructor
**Recipient:** All enrolled students
**Required Variables:**
- `user_name` - Student's full name
- `course_name` - Name of the course
- `cancellation_reason` - Why course was cancelled
- `refund_info` - Refund information
- `alternative_courses` - Suggested alternative courses (optional)
- `support_email` - Contact for questions

**Example Context:**
```python
{
    'user_name': 'Sarah Johnson',
    'course_name': 'Advanced Python Programming',
    'cancellation_reason': 'Insufficient enrollment',
    'refund_info': 'Full refund will be automatically processed within 3 business days.',
    'alternative_courses': 'Consider enrolling in "Python Fundamentals" or "Web Development with Flask".',
    'support_email': 'support@cwmt.example.com'
}
```

---

### `course_schedule_change`
**When:** Course date, time, or location changes
**Recipient:** All enrolled students
**Required Variables:**
- `user_name` - Student's full name
- `course_name` - Name of the course
- `change_type` - What changed (date/time/location)
- `old_value` - Previous value
- `new_value` - New value
- `change_reason` - Why it changed (optional)
- `support_email` - Contact for questions

**Example Context:**
```python
{
    'user_name': 'Sarah Johnson',
    'course_name': 'Advanced Python Programming',
    'change_type': 'location',
    'old_value': 'Room 204, Main Building',
    'new_value': 'Room 305, South Building',
    'change_reason': 'Room 204 under maintenance',
    'support_email': 'support@cwmt.example.com'
}
```

---

### `course_materials_available`
**When:** New course materials/resources are uploaded
**Recipient:** All enrolled students
**Required Variables:**
- `user_name` - Student's full name
- `course_name` - Name of the course
- `materials_description` - What was added
- `materials_link` - URL to access materials

**Example Context:**
```python
{
    'user_name': 'Sarah Johnson',
    'course_name': 'Advanced Python Programming',
    'materials_description': 'Week 3 lecture slides and code examples',
    'materials_link': 'https://cwmt.example.com/courses/12345/materials'
}
```

---

## Payment & Billing

### `payment_confirmation`
**When:** Student completes payment for course
**Recipient:** Student who paid
**Required Variables:**
- `user_name` - Student's full name
- `course_name` - Name of the course
- `payment_amount` - Amount paid
- `payment_date` - When payment was made
- `payment_method` - Last 4 digits of card, etc.
- `receipt_number` - Transaction ID/receipt number
- `receipt_link` - URL to download full receipt

**Example Context:**
```python
{
    'user_name': 'Sarah Johnson',
    'course_name': 'Advanced Python Programming',
    'payment_amount': '$299.00',
    'payment_date': 'January 15, 2026',
    'payment_method': 'Visa ending in 4242',
    'receipt_number': 'RCP-2026-001234',
    'receipt_link': 'https://cwmt.example.com/receipts/001234'
}
```

---

### `payment_failed`
**When:** Payment attempt fails
**Recipient:** Student whose payment failed
**Required Variables:**
- `user_name` - Student's full name
- `course_name` - Name of the course
- `payment_amount` - Amount attempted
- `failure_reason` - Why payment failed
- `retry_link` - URL to retry payment
- `support_email` - Contact for help

**Example Context:**
```python
{
    'user_name': 'Sarah Johnson',
    'course_name': 'Advanced Python Programming',
    'payment_amount': '$299.00',
    'failure_reason': 'Insufficient funds',
    'retry_link': 'https://cwmt.example.com/payment/retry/12345',
    'support_email': 'billing@cwmt.example.com'
}
```

---

### `payment_refund_processed`
**When:** Refund is processed
**Recipient:** Student receiving refund
**Required Variables:**
- `user_name` - Student's full name
- `course_name` - Name of the course
- `refund_amount` - Amount refunded
- `refund_date` - When refund was processed
- `refund_method` - How refund will be returned
- `processing_days` - Expected days to receive

**Example Context:**
```python
{
    'user_name': 'Sarah Johnson',
    'course_name': 'Advanced Python Programming',
    'refund_amount': '$299.00',
    'refund_date': 'January 20, 2026',
    'refund_method': 'Original payment method (Visa ending in 4242)',
    'processing_days': '5-7 business days'
}
```

---

## Instructor Communications

### `instructor_course_assigned`
**When:** Instructor is assigned to teach a course
**Recipient:** Instructor
**Required Variables:**
- `user_name` - Instructor's full name
- `course_name` - Name of the course
- `course_start_date` - When course begins
- `course_end_date` - When course ends
- `enrolled_count` - Number of students enrolled
- `course_management_link` - URL to manage course

**Example Context:**
```python
{
    'user_name': 'Dr. Emily Chen',
    'course_name': 'Advanced Python Programming',
    'course_start_date': 'February 15, 2026',
    'course_end_date': 'March 15, 2026',
    'enrolled_count': 15,
    'course_management_link': 'https://cwmt.example.com/instructor/courses/12345'
}
```

---

### `student_enrolled_notification`
**When:** New student enrolls in instructor's course
**Recipient:** Course instructor
**Required Variables:**
- `instructor_name` - Instructor's full name
- `student_name` - Student who enrolled
- `course_name` - Name of the course
- `enrolled_count` - Total students now enrolled
- `max_capacity` - Maximum course capacity

**Example Context:**
```python
{
    'instructor_name': 'Dr. Emily Chen',
    'student_name': 'Mike Wilson',
    'course_name': 'Advanced Python Programming',
    'enrolled_count': 16,
    'max_capacity': 20
}
```

---

## Admin Notifications

### `course_capacity_reached`
**When:** Course reaches maximum capacity
**Recipient:** Admin users
**Required Variables:**
- `course_name` - Name of the course
- `instructor_name` - Instructor's full name
- `enrolled_count` - Number of students enrolled
- `waitlist_count` - Number of students on waitlist
- `course_management_link` - URL to manage course

**Example Context:**
```python
{
    'course_name': 'Advanced Python Programming',
    'instructor_name': 'Dr. Emily Chen',
    'enrolled_count': 20,
    'waitlist_count': 5,
    'course_management_link': 'https://cwmt.example.com/admin/courses/12345'
}
```

---

### `payment_dispute`
**When:** Student disputes a payment
**Recipient:** Admin/billing team
**Required Variables:**
- `student_name` - Student who disputed
- `student_email` - Student's email
- `course_name` - Name of the course
- `payment_amount` - Amount disputed
- `dispute_reason` - Reason given for dispute
- `dispute_date` - When dispute was filed

**Example Context:**
```python
{
    'student_name': 'John Smith',
    'student_email': 'john.smith@example.com',
    'course_name': 'Introduction to Machine Learning',
    'payment_amount': '$399.00',
    'dispute_reason': 'Service not as described',
    'dispute_date': 'January 25, 2026'
}
```

---

## Completion & Certificates

### `course_completion_certificate`
**When:** Student completes course and earns certificate
**Recipient:** Student who completed
**Required Variables:**
- `user_name` - Student's full name
- `course_name` - Name of the course
- `completion_date` - When course was completed
- `certificate_link` - URL to download/view certificate
- `instructor_name` - Instructor's full name

**Example Context:**
```python
{
    'user_name': 'Sarah Johnson',
    'course_name': 'Advanced Python Programming',
    'completion_date': 'March 15, 2026',
    'certificate_link': 'https://cwmt.example.com/certificates/cert-123456',
    'instructor_name': 'Dr. Emily Chen'
}
```

---

## Summary

**Total Email Purposes:** 20

### Categories:
- **User Account Management:** 4 purposes
- **Course Enrollment:** 4 purposes  
- **Course Reminders:** 2 purposes
- **Course Changes & Updates:** 3 purposes
- **Payment & Billing:** 3 purposes
- **Instructor Communications:** 2 purposes
- **Admin Notifications:** 2 purposes
- **Completion & Certificates:** 1 purpose

---

## Implementation Notes

1. **Priority for Initial Launch:**
   - `new_user` - Critical
   - `password_reset` - Critical
   - `course_enrollment_confirmation` - Critical
   - `payment_confirmation` - Critical
   - `course_starting_soon` - High priority
   - `course_cancellation` - High priority

2. **Can Be Added Later:**
   - Waitlist functionality emails
   - Assignment reminders
   - Dispute notifications
   - Material upload notifications

3. **Configuration Considerations:**
   - Some purposes may need timing configuration (e.g., "send reminder X days before course")
   - Consider adding a `days_before` or similar config for reminder emails
