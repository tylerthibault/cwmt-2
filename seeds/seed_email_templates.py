"""
Utility module for seeding default email templates in the database.
Provides default email templates that admins can use as starting points.
"""
from src.models.email_template_model import EmailTemplate
from src.models import db


def seed_email_templates(app):
    """
    Seed the database with default email templates.
    These templates can be edited or deleted by admins, and new ones can be created.
    
    Args:
        app: Flask application instance
    """
    email_templates = [
        {
            'name': 'Test Email Template',
            'subject': 'Test Email - {app_name}',
            'body_text': '''Hello {user_name},

This is a test email from {app_name}.

Test Message: {test_message}

Best regards,
{app_name} Team''',
            'body_html': '''<p>Hello <strong>{user_name}</strong>,</p>
<p>This is a test email from {app_name}.</p>
<p><strong>Test Message:</strong> {test_message}</p>
<p>Best regards,<br>
{app_name} Team</p>''',
            'description': 'Default test email template for verifying email configuration',
            'is_active': True
        },
        {
            'name': 'New Student Welcome',
            'subject': 'Welcome to {app_name}, {user_name}!',
            'body_text': '''Dear {user_name},

Welcome to {app_name}!

We're excited to have you join our learning community. Your student account has been created successfully.

Student ID: {student_id}
Email: {user_email}

You can log in to your account at: {login_link}

If you have any questions or need assistance, please don't hesitate to contact us.

Best regards,
The {app_name} Team''',
            'body_html': '''<h2>Welcome to {app_name}!</h2>
<p>Dear <strong>{user_name}</strong>,</p>
<p>We're excited to have you join our learning community. Your student account has been created successfully.</p>
<p><strong>Your Account Details:</strong></p>
<ul>
    <li>Student ID: {student_id}</li>
    <li>Email: {user_email}</li>
</ul>
<p><a href="{login_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Log In to Your Account</a></p>
<p>If you have any questions or need assistance, please don't hesitate to contact us.</p>
<p>Best regards,<br>
The {app_name} Team</p>''',
            'description': 'Welcome email sent to new students',
            'is_active': True
        },
        {
            'name': 'New Instructor Welcome',
            'subject': 'Welcome to {app_name} - Instructor Account Created',
            'body_text': '''Dear {user_name},

Welcome to {app_name}!

Your instructor account has been successfully created. We're thrilled to have you as part of our teaching team.

Email: {user_email}

You can log in to your account at: {login_link}

Access instructor resources: {instructor_resources_link}

If you have any questions or need support, please reach out to us.

Best regards,
The {app_name} Team''',
            'body_html': '''<h2>Welcome to {app_name}!</h2>
<p>Dear <strong>{user_name}</strong>,</p>
<p>Your instructor account has been successfully created. We're thrilled to have you as part of our teaching team.</p>
<p><strong>Account Email:</strong> {user_email}</p>
<p><a href="{login_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-right: 10px;">Log In</a>
<a href="{instructor_resources_link}" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Instructor Resources</a></p>
<p>If you have any questions or need support, please reach out to us.</p>
<p>Best regards,<br>
The {app_name} Team</p>''',
            'description': 'Welcome email sent to new instructors',
            'is_active': True
        },
        {
            'name': 'Password Reset',
            'subject': 'Reset Your {app_name} Password',
            'body_text': '''Hello {user_name},

We received a request to reset your password for your {app_name} account.

Click the link below to reset your password:
{reset_link}

This link will expire in {expiry_time}.

If you didn't request this password reset, please ignore this email or contact support if you have concerns.

Best regards,
{app_name} Team''',
            'body_html': '''<h2>Password Reset Request</h2>
<p>Hello <strong>{user_name}</strong>,</p>
<p>We received a request to reset your password for your {app_name} account.</p>
<p><a href="{reset_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Your Password</a></p>
<p><small>This link will expire in {expiry_time}.</small></p>
<p>If you didn't request this password reset, please ignore this email or contact support if you have concerns.</p>
<p>Best regards,<br>
{app_name} Team</p>''',
            'description': 'Password reset email with secure link',
            'is_active': True
        },
        {
            'name': 'Student Course Reminder',
            'subject': 'Reminder: {course_name} - {days_until} days away',
            'body_text': '''Hello {user_name},

This is a friendly reminder about your upcoming course:

Course: {course_name}
Date: {course_date}
Time: {course_time}
Location: {course_location}
Instructor: {instructor_name}

We look forward to seeing you there!

Best regards,
{app_name} Team''',
            'body_html': '''<h2>Course Reminder</h2>
<p>Hello <strong>{user_name}</strong>,</p>
<p>This is a friendly reminder about your upcoming course:</p>
<ul>
    <li><strong>Course:</strong> {course_name}</li>
    <li><strong>Date:</strong> {course_date}</li>
    <li><strong>Time:</strong> {course_time}</li>
    <li><strong>Location:</strong> {course_location}</li>
    <li><strong>Instructor:</strong> {instructor_name}</li>
</ul>
<p>We look forward to seeing you there!</p>
<p>Best regards,<br>
{app_name} Team</p>''',
            'description': 'Reminder email for students about upcoming courses',
            'is_active': True
        },
        {
            'name': 'Instructor Course Reminder',
            'subject': 'Reminder: Teaching {course_name} - {days_until} days away',
            'body_text': '''Hello {user_name},

This is a reminder about the course you're scheduled to teach:

Course: {course_name}
Date: {course_date}
Time: {course_time}
Location: {course_location}
Enrolled Students: {student_count}

Student List: {enrolled_students}

Please ensure you're prepared for the session.

Best regards,
{app_name} Team''',
            'body_html': '''<h2>Teaching Reminder</h2>
<p>Hello <strong>{user_name}</strong>,</p>
<p>This is a reminder about the course you're scheduled to teach:</p>
<ul>
    <li><strong>Course:</strong> {course_name}</li>
    <li><strong>Date:</strong> {course_date}</li>
    <li><strong>Time:</strong> {course_time}</li>
    <li><strong>Location:</strong> {course_location}</li>
    <li><strong>Enrolled Students:</strong> {student_count}</li>
</ul>
<p><strong>Student List:</strong><br>{enrolled_students}</p>
<p>Please ensure you're prepared for the session.</p>
<p>Best regards,<br>
{app_name} Team</p>''',
            'description': 'Reminder email for instructors about upcoming courses they are teaching',
            'is_active': True
        }
    ]
    
    templates_created = 0
    templates_updated = 0
    
    for template_data in email_templates:
        # Check if template already exists by name
        existing_template = EmailTemplate.query.filter_by(
            name=template_data['name']
        ).first()
        
        if existing_template:
            # Update existing template
            existing_template.subject = template_data['subject']
            existing_template.body_text = template_data['body_text']
            existing_template.body_html = template_data['body_html']
            existing_template.description = template_data['description']
            existing_template.is_active = template_data['is_active']
            templates_updated += 1
            print(f"  - Updated: {template_data['name']}")
        else:
            # Create new template
            new_template = EmailTemplate(
                name=template_data['name'],
                subject=template_data['subject'],
                body_text=template_data['body_text'],
                body_html=template_data['body_html'],
                description=template_data['description'],
                is_active=template_data['is_active']
            )
            db.session.add(new_template)
            templates_created += 1
            print(f"  ✓ Created: {template_data['name']}")
    
    try:
        db.session.commit()
        print(f"\n✓ Seeded {templates_created} template(s), updated {templates_updated}")
    except Exception as e:
        db.session.rollback()
        print(f"  ✗ Error seeding email templates: {str(e)}")
        raise


if __name__ == '__main__':
    print("This script should be run through the main seeding process.")
    print("Use: python seeds/run_seeds.py")


__all__ = ['seed_email_templates']

