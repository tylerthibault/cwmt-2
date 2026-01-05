"""
Seed default email templates into the database.
Run this script to populate the system with default email templates.
"""

from src.models.flask_mail.email_templates import EmailTemplate
from src.models.main import db


def seed_default_templates():
    """Create default email templates for all purposes."""
    
    templates = [
        # New User Welcome
        {
            'purpose': 'new_user',
            'name': 'Default New User Welcome',
            'subject_template': 'Welcome to CWMT, {{ user_name }}!',
            'body_html_template': '''<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #2196f3; color: white; padding: 20px; text-align: center; }
        .content { background-color: #ffffff; padding: 30px; border: 1px solid #e0e0e0; }
        .button { display: inline-block; padding: 12px 30px; background-color: #2196f3; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }
        .credentials { background-color: #f5f5f5; padding: 15px; border-left: 4px solid #2196f3; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to CWMT!</h1>
        </div>
        <div class="content">
            <h2>Hello {{ user_name }},</h2>
            <p>Welcome to the Course/Workshop Management Training system! Your account has been successfully created.</p>
            
            <div class="credentials">
                <strong>Your Login Credentials:</strong><br>
                Email: {{ user_email }}<br>
                Temporary Password: <strong>{{ temp_password }}</strong>
            </div>
            
            <p><strong>Important:</strong> Please change your password after your first login for security purposes.</p>
            
            <p style="text-align: center;">
                <a href="{{ login_link }}" class="button">Login to Your Account</a>
            </p>
            
            <p>If you have any questions or need assistance, please don't hesitate to contact us at {{ support_email }}.</p>
            
            <p>Best regards,<br>The CWMT Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>''',
            'body_text_template': '''Welcome to CWMT!

Hello {{ user_name }},

Welcome to the Course/Workshop Management Training system! Your account has been successfully created.

YOUR LOGIN CREDENTIALS:
Email: {{ user_email }}
Temporary Password: {{ temp_password }}

IMPORTANT: Please change your password after your first login for security purposes.

Login to your account: {{ login_link }}

If you have any questions or need assistance, please don't hesitate to contact us at {{ support_email }}.

Best regards,
The CWMT Team

---
This is an automated message. Please do not reply to this email.''',
            'is_default': True,
            'is_active': True
        },
        
        # Password Reset
        {
            'purpose': 'password_reset',
            'name': 'Default Password Reset',
            'subject_template': 'Password Reset Request for {{ user_name }}',
            'body_html_template': '''<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #ff9800; color: white; padding: 20px; text-align: center; }
        .content { background-color: #ffffff; padding: 30px; border: 1px solid #e0e0e0; }
        .button { display: inline-block; padding: 12px 30px; background-color: #ff9800; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }
        .warning { background-color: #fff3e0; padding: 15px; border-left: 4px solid #ff9800; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Password Reset Request</h1>
        </div>
        <div class="content">
            <h2>Hello {{ user_name }},</h2>
            <p>We received a request to reset the password for your CWMT account ({{ user_email }}).</p>
            
            <p style="text-align: center;">
                <a href="{{ reset_link }}" class="button">Reset Your Password</a>
            </p>
            
            <div class="warning">
                <strong>⚠️ Important Security Information:</strong><br>
                • This link will expire in {{ expiry_hours }} hours<br>
                • If you didn't request this reset, please ignore this email<br>
                • Your password will remain unchanged unless you click the link above
            </div>
            
            <p>If the button doesn't work, copy and paste this link into your browser:<br>
            {{ reset_link }}</p>
            
            <p>If you need additional assistance, please contact support.</p>
            
            <p>Best regards,<br>The CWMT Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>''',
            'body_text_template': '''Password Reset Request

Hello {{ user_name }},

We received a request to reset the password for your CWMT account ({{ user_email }}).

Reset your password: {{ reset_link }}

IMPORTANT SECURITY INFORMATION:
• This link will expire in {{ expiry_hours }} hours
• If you didn't request this reset, please ignore this email
• Your password will remain unchanged unless you click the link above

If you need additional assistance, please contact support.

Best regards,
The CWMT Team

---
This is an automated message. Please do not reply to this email.''',
            'is_default': True,
            'is_active': True
        },
        
        # Course Enrollment Confirmation
        {
            'purpose': 'course_enrollment_confirmation',
            'name': 'Default Course Enrollment Confirmation',
            'subject_template': 'Enrollment Confirmed: {{ course_name }}',
            'body_html_template': '''<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #4caf50; color: white; padding: 20px; text-align: center; }
        .content { background-color: #ffffff; padding: 30px; border: 1px solid #e0e0e0; }
        .course-details { background-color: #f5f5f5; padding: 20px; border-radius: 4px; margin: 20px 0; }
        .detail-row { padding: 8px 0; border-bottom: 1px solid #e0e0e0; }
        .detail-label { font-weight: 600; display: inline-block; width: 120px; }
        .button { display: inline-block; padding: 12px 30px; background-color: #4caf50; color: white; text-decoration: none; border-radius: 4px; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✓ Enrollment Confirmed!</h1>
        </div>
        <div class="content">
            <h2>Congratulations {{ user_name }}!</h2>
            <p>You have been successfully enrolled in the following course:</p>
            
            <div class="course-details">
                <h3 style="margin-top: 0;">{{ course_name }}</h3>
                <div class="detail-row">
                    <span class="detail-label">Start Date:</span> {{ course_start_date }}
                </div>
                <div class="detail-row">
                    <span class="detail-label">End Date:</span> {{ course_end_date }}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Location:</span> {{ course_location }}
                </div>
                <div class="detail-row">
                    <span class="detail-label">Instructor:</span> {{ instructor_name }}
                </div>
                <div class="detail-row" style="border-bottom: none;">
                    <span class="detail-label">Contact:</span> {{ instructor_email }}
                </div>
            </div>
            
            <p style="text-align: center;">
                <a href="{{ course_details_link }}" class="button">View Course Details</a>
            </p>
            
            <p><strong>What's Next?</strong></p>
            <ul>
                <li>Mark your calendar for the course dates</li>
                <li>Review any pre-course materials (available on the course page)</li>
                <li>Prepare any questions you may have for the instructor</li>
            </ul>
            
            <p>We look forward to seeing you in class!</p>
            
            <p>Best regards,<br>The CWMT Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>''',
            'body_text_template': '''Enrollment Confirmed!

Congratulations {{ user_name }}!

You have been successfully enrolled in the following course:

{{ course_name }}

COURSE DETAILS:
Start Date: {{ course_start_date }}
End Date: {{ course_end_date }}
Location: {{ course_location }}
Instructor: {{ instructor_name }}
Contact: {{ instructor_email }}

View full course details: {{ course_details_link }}

WHAT'S NEXT?
• Mark your calendar for the course dates
• Review any pre-course materials (available on the course page)
• Prepare any questions you may have for the instructor

We look forward to seeing you in class!

Best regards,
The CWMT Team

---
This is an automated message. Please do not reply to this email.''',
            'is_default': True,
            'is_active': True
        },
        
        # Payment Confirmation
        {
            'purpose': 'payment_confirmation',
            'name': 'Default Payment Confirmation',
            'subject_template': 'Payment Received - Receipt #{{ transaction_id }}',
            'body_html_template': '''<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #2196f3; color: white; padding: 20px; text-align: center; }
        .content { background-color: #ffffff; padding: 30px; border: 1px solid #e0e0e0; }
        .receipt { background-color: #f5f5f5; padding: 20px; border-radius: 4px; margin: 20px 0; }
        .receipt-row { padding: 10px 0; border-bottom: 1px solid #e0e0e0; display: flex; justify-content: space-between; }
        .total { font-size: 1.2em; font-weight: bold; padding-top: 15px; border-top: 2px solid #2196f3; }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Payment Received</h1>
        </div>
        <div class="content">
            <h2>Thank you {{ user_name }}!</h2>
            <p>Your payment has been successfully processed. Here are your receipt details:</p>
            
            <div class="receipt">
                <h3 style="margin-top: 0;">Receipt #{{ transaction_id }}</h3>
                <div class="receipt-row">
                    <span>Date:</span>
                    <span>{{ payment_date }}</span>
                </div>
                <div class="receipt-row">
                    <span>Course:</span>
                    <span>{{ course_name }}</span>
                </div>
                <div class="receipt-row">
                    <span>Payment Method:</span>
                    <span>{{ payment_method }}</span>
                </div>
                <div class="receipt-row" style="border-bottom: none;">
                    <span>Amount Paid:</span>
                    <span><strong>${{ amount_paid }}</strong></span>
                </div>
            </div>
            
            <p>Your enrollment is now confirmed and you're all set for the course!</p>
            
            <p>If you have any questions about this payment, please contact our finance team with your receipt number.</p>
            
            <p>Best regards,<br>The CWMT Team</p>
        </div>
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>Keep this receipt for your records.</p>
        </div>
    </div>
</body>
</html>''',
            'body_text_template': '''Payment Received

Thank you {{ user_name }}!

Your payment has been successfully processed. Here are your receipt details:

RECEIPT #{{ transaction_id }}
Date: {{ payment_date }}
Course: {{ course_name }}
Payment Method: {{ payment_method }}
Amount Paid: ${{ amount_paid }}

Your enrollment is now confirmed and you're all set for the course!

If you have any questions about this payment, please contact our finance team with your receipt number.

Best regards,
The CWMT Team

---
This is an automated message. Please do not reply to this email.
Keep this receipt for your records.''',
            'is_default': True,
            'is_active': True
        },
    ]
    
    created_count = 0
    skipped_count = 0
    
    for template_data in templates:
        # Check if default template already exists for this purpose
        existing = EmailTemplate.query.filter_by(
            purpose=template_data['purpose'],
            is_default=True
        ).first()
        
        if existing:
            print(f"⏭️  Skipping {template_data['purpose']} - default already exists")
            skipped_count += 1
            continue
        
        # Create the template
        template = EmailTemplate(
            purpose=template_data['purpose'],
            name=template_data['name'],
            subject_template=template_data['subject_template'],
            body_html_template=template_data['body_html_template'],
            body_text_template=template_data['body_text_template'],
            is_default=template_data['is_default'],
            is_active=template_data['is_active'],
            created_by=1  # System user - adjust as needed
        )
        
        template.save()
        print(f"✓ Created default template: {template_data['name']}")
        created_count += 1
    
    print(f"\n{'='*50}")
    print(f"Template seeding complete!")
    print(f"Created: {created_count} templates")
    print(f"Skipped: {skipped_count} templates (already exist)")
    print(f"{'='*50}")
    
    return created_count


if __name__ == '__main__':
    from src import create_app
    
    app = create_app()
    with app.app_context():
        seed_default_templates()
