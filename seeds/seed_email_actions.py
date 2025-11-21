"""
Utility module for seeding email actions in the database.
Provides predefined email actions that can be referenced in code.
"""
from src.models.email_action_model import EmailAction
from src.models import db


def seed_email_actions(app):
    """
    Seed the database with predefined email actions.
    These actions are referenced in code and cannot be created by admins.
    Admins can only assign templates to these actions.
    
    Args:
        app: Flask application instance
    """
    email_actions = [
        {
            'action_key': 'test_email',
            'name': 'Test Email',
            'description': 'Test email for verifying email configuration and templates',
            'available_variables': '{user_name}, {user_email}, {test_message}, {app_name}'
        },
        {
            'action_key': 'new_student',
            'name': 'New Student Welcome',
            'description': 'Welcome email sent when a new student account is created',
            'available_variables': '{user_name}, {user_email}, {login_link}, {student_id}, {app_name}'
        },
        {
            'action_key': 'new_instructor',
            'name': 'New Instructor Welcome',
            'description': 'Welcome email sent when a new instructor account is created',
            'available_variables': '{user_name}, {user_email}, {login_link}, {instructor_resources_link}, {app_name}'
        },
        {
            'action_key': 'password_reset',
            'name': 'Password Reset',
            'description': 'Sent when a user requests to reset their password',
            'available_variables': '{user_name}, {user_email}, {reset_link}, {expiry_time}, {app_name}'
        },
        {
            'action_key': 'student_course_reminder',
            'name': 'Student Course Reminder',
            'description': 'Reminder sent to students about an upcoming course they are enrolled in',
            'available_variables': '{user_name}, {user_email}, {course_name}, {course_date}, {course_time}, {course_location}, {instructor_name}, {days_until}, {app_name}'
        },
        {
            'action_key': 'instructor_course_reminder',
            'name': 'Instructor Course Reminder',
            'description': 'Reminder sent to instructors about an upcoming course they are teaching',
            'available_variables': '{user_name}, {user_email}, {course_name}, {course_date}, {course_time}, {course_location}, {student_count}, {enrolled_students}, {days_until}, {app_name}'
        },
        {
            'action_key': 'course_enrollment',
            'name': 'Course Enrollment Confirmation',
            'description': 'Sent when a student is enrolled in a course',
            'available_variables': '{user_name}, {user_email}, {course_name}, {course_date}, {course_time}, {course_location}, {instructor_name}, {app_name}'
        },
        {
            'action_key': 'course_completion',
            'name': 'Course Completion Certificate',
            'description': 'Sent when a student completes a course',
            'available_variables': '{user_name}, {user_email}, {course_name}, {completion_date}, {final_score}, {certificate_link}, {app_name}'
        },
        {
            'action_key': 'course_cancellation',
            'name': 'Course Cancellation Notice',
            'description': 'Sent when a course is cancelled',
            'available_variables': '{user_name}, {user_email}, {course_name}, {course_date}, {cancellation_reason}, {app_name}'
        },
        {
            'action_key': 'password_changed',
            'name': 'Password Changed Confirmation',
            'description': 'Sent after a user successfully changes their password',
            'available_variables': '{user_name}, {user_email}, {change_time}, {ip_address}, {app_name}'
        },
        {
            'action_key': 'account_locked',
            'name': 'Account Locked Notification',
            'description': 'Sent when a user account is locked due to security reasons',
            'available_variables': '{user_name}, {user_email}, {lock_reason}, {unlock_instructions}, {support_email}, {app_name}'
        },
        {
            'action_key': 'role_assignment',
            'name': 'Role Assignment Notification',
            'description': 'Sent when a user is assigned a new role',
            'available_variables': '{user_name}, {user_email}, {role_name}, {assigned_by}, {app_name}'
        }
    ]
    
    actions_created = 0
    actions_updated = 0
    
    for action_data in email_actions:
        # Check if action already exists
        existing_action = EmailAction.query.filter_by(
            action_key=action_data['action_key']
        ).first()
        
        if existing_action:
            # Update existing action
            existing_action.name = action_data['name']
            existing_action.description = action_data['description']
            existing_action.available_variables = action_data['available_variables']
            actions_updated += 1
            print(f"  - Updated: {action_data['name']} ({action_data['action_key']})")
        else:
            # Create new action
            new_action = EmailAction(
                action_key=action_data['action_key'],
                name=action_data['name'],
                description=action_data['description'],
                available_variables=action_data['available_variables']
            )
            db.session.add(new_action)
            actions_created += 1
            print(f"  ✓ Created: {action_data['name']} ({action_data['action_key']})")
    
    try:
        db.session.commit()
        print(f"\n✓ Seeded {actions_created} action(s), updated {actions_updated}")
    except Exception as e:
        db.session.rollback()
        print(f"  ✗ Error seeding email actions: {str(e)}")
        raise


if __name__ == '__main__':
    print("This script should be run through the main seeding process.")
    print("Use: python seeds/run_seeds.py")


__all__ = ['seed_email_actions']

