# src/services/email_config.py

class EmailPurpose:
    """Represents an email purpose with its configuration."""
    
    def __init__(self, code, name, description, variables, example_data):
        self.code = code
        self.name = name
        self.description = description
        self.variables = variables  # dict: {var_name: var_description}
        self.example_data = example_data  # dict: {var_name: example_value}
    
    def validate_context(self, context):
        """Validate that context has all required variables."""
        missing = set(self.variables.keys()) - set(context.keys())
        if missing:
            raise ValueError(f"Missing required variables for {self.code}: {missing}")
        return True
    
    def get_example_data(self):
        """Get example data for testing/preview."""
        return self.example_data.copy()


# Store in dictionary for easy lookup
EMAIL_PURPOSES = {
    'new_user': EmailPurpose(
        code='new_user',
        name='New User Welcome',
        description='Sent when new user account is created',
        variables={
            'first_name': "User's first name",
            'last_name': "User's last name",
            'temp_password': 'Temporary password',
            'login_link': 'URL to login page',
        },
        example_data={
            'first_name': 'John',
            'last_name': 'Smith',
            'temp_password': 'TempPass123!',
            'login_link': 'https://cwmt.example.com/login'
        }
    ),
    'password_reset': EmailPurpose(
        code='password_reset',
        name='Password Reset',
        description='Sent when user requests password reset',
        variables={
            'user_name': "User's full name",
            'reset_link': 'URL with reset token',
            'expiry_hours': 'Hours until link expires'
        },
        example_data={
            'user_name': 'Jane Doe',
            'reset_link': 'https://cwmt.example.com/reset/abc123',
            'expiry_hours': 24
        }
    ),
    'course_enrollment_confirmation': EmailPurpose(
        code='course_enrollment_confirmation',
        name='Course Enrollment Confirmation',
        description='Sent when student enrolls in a course',
        variables={
            'user_name': "Student's full name",
            'course_name': 'Name of the course',
            'course_start_date': 'When course begins',
            'course_end_date': 'When course ends',
            'course_location': 'Where course takes place',
            'instructor_name': "Instructor's full name",
            'instructor_email': "Instructor's contact email",
            'course_details_link': 'URL to course details page'
        },
        example_data={
            'user_name': 'Sarah Johnson',
            'course_name': 'Advanced Python Programming',
            'course_start_date': 'February 15, 2026',
            'course_end_date': 'March 15, 2026',
            'course_location': 'Room 204, Main Building',
            'instructor_name': 'Dr. Emily Chen',
            'instructor_email': 'emily.chen@cwmt.example.com',
            'course_details_link': 'https://cwmt.example.com/courses/12345'
        }
    ),
    'payment_confirmation': EmailPurpose(
        code='payment_confirmation',
        name='Payment Confirmation',
        description='Sent when payment is successfully processed',
        variables={
            'user_name': "Student's full name",
            'transaction_id': 'Unique payment transaction ID',
            'payment_date': 'Date payment was processed',
            'course_name': 'Course paid for',
            'amount_paid': 'Payment amount',
            'payment_method': 'Payment method used (e.g., Credit Card)'
        },
        example_data={
            'user_name': 'Michael Brown',
            'transaction_id': 'TXN-2026-001234',
            'payment_date': 'January 2, 2026',
            'course_name': 'Advanced Python Programming',
            'amount_paid': '299.00',
            'payment_method': 'Credit Card ending in 4242'
        }
    ),
}

# Helper functions
def get_purpose(code):
    """Get email purpose by code."""
    if code not in EMAIL_PURPOSES:
        raise ValueError(f"Unknown email purpose: {code}")
    return EMAIL_PURPOSES[code]

def list_all_purposes():
    """Get list of all purpose codes."""
    return list(EMAIL_PURPOSES.keys())