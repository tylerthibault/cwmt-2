"""
Superuser service for superuser-related business logic.
"""
from datetime import datetime
from src.models.user_folder.users import User
from src.models.user_folder.students import Student
from src.models.user_folder.instructors import Instructor
from src.models.user_folder.admins import Admin
from src.models.user_folder.superusers import Superuser
from src.models.app_settings import AppSettings
from src.models.logs import Log


def get_all_users_with_counts(focus='all'):
    """
    Get all users with role counts.
    
    Args:
        focus: Filter focus ('all', 'student', 'instructor', 'admin', 'superuser')
        
    Returns:
        dict: users list and role counts
    """
    all_users = User.query.all()
    
    role_counts = {
        'all': len(all_users),
        'student': sum(1 for u in all_users if u.is_student),
        'instructor': sum(1 for u in all_users if u.is_instructor),
        'admin': sum(1 for u in all_users if u.is_admin),
        'superuser': sum(1 for u in all_users if u.is_superuser)
    }
    
    return {
        'users': all_users,
        'role_counts': role_counts,
        'focus': focus
    }


def get_user_roles_data(user_id):
    """
    Get user roles data for role management.
    
    Args:
        user_id: ID of the user
        
    Returns:
        dict: user, current_roles, and available_roles
        
    Raises:
        ValueError: If user not found
    """
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")
    
    return {
        'user': user,
        'current_roles': user.get_roles(),
        'available_roles': ['student', 'instructor', 'admin', 'superuser']
    }


def add_role_to_user(user_id, role_name, current_user_id):
    """
    Add a role to a user.
    
    Args:
        user_id: ID of the user
        role_name: Name of the role to add
        current_user_id: ID of the user performing the action
        
    Returns:
        dict: The created role record and user
        
    Raises:
        ValueError: If user not found, invalid role, or user already has role
    """
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")
    
    valid_roles = ['student', 'instructor', 'admin', 'superuser']
    if role_name not in valid_roles:
        raise ValueError(f"Invalid role: {role_name}")
    
    if user.has_role_by_name(role_name):
        raise ValueError(f"User already has {role_name} role")
    
    # Create the role record
    role_record = None
    if role_name == 'student':
        role_record = Student.create(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number
        )
    elif role_name == 'instructor':
        role_record = Instructor.create(user_id=user.id)
    elif role_name == 'admin':
        role_record = Admin.create(user_id=user.id)
    elif role_name == 'superuser':
        role_record = Superuser.create(user_id=user.id)
    
    # Log the action
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action=f'add_{role_name}_role',
        description=f'{role_name.capitalize()} role added to {user.email}',
        user_id=current_user_id,
        target_type='user',
        target_id=user.id,
        status='success',
        extra_data={
            'target_email': user.email,
            'role_added': role_name
        }
    )
    
    return {'role_record': role_record, 'user': user}


def remove_role_from_user(user_id, role_name, current_user_id):
    """
    Remove a role from a user.
    
    Args:
        user_id: ID of the user
        role_name: Name of the role to remove
        current_user_id: ID of the user performing the action
        
    Returns:
        dict: user object
        
    Raises:
        ValueError: If user not found, invalid role, user doesn't have role, or last role
    """
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")
    
    valid_roles = ['student', 'instructor', 'admin', 'superuser']
    if role_name not in valid_roles:
        raise ValueError(f"Invalid role: {role_name}")
    
    if not user.has_role_by_name(role_name):
        raise ValueError(f"User does not have {role_name} role")
    
    if len(user.get_roles()) == 1:
        raise ValueError("Cannot remove the last role from a user")
    
    # Remove the role
    role_record = None
    if role_name == 'student':
        role_record = Student.query.filter_by(user_id=user.id).first()
    elif role_name == 'instructor':
        role_record = Instructor.query.filter_by(user_id=user.id).first()
    elif role_name == 'admin':
        role_record = Admin.query.filter_by(user_id=user.id).first()
    elif role_name == 'superuser':
        role_record = Superuser.query.filter_by(user_id=user.id).first()
    
    if not role_record:
        raise ValueError("Role record not found")
    
    role_record.delete()
    
    # Log the action
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action=f'remove_{role_name}_role',
        description=f'{role_name.capitalize()} role removed from {user.email}',
        user_id=current_user_id,
        target_type='user',
        target_id=user.id,
        status='success',
        extra_data={
            'target_email': user.email,
            'role_removed': role_name
        }
    )
    
    return {'user': user}


def get_users_without_role(role_name):
    """
    Get all users who don't have the specified role.
    
    Args:
        role_name: Name of the role
        
    Returns:
        list: Users without the role
        
    Raises:
        ValueError: If invalid role name
    """
    valid_roles = ['student', 'instructor', 'admin', 'superuser']
    if role_name not in valid_roles:
        raise ValueError(f"Invalid role: {role_name}")
    
    all_users = User.query.all()
    return [u for u in all_users if not u.has_role_by_name(role_name)]


def update_email_settings(settings_data, current_user_id):
    """
    Update email settings in database.
    
    Args:
        settings_data: Dict of settings to update
        current_user_id: ID of user making changes
        
    Returns:
        AppSettings: Updated settings object
    """
    AppSettings.update_settings(
        updated_by_user_id=current_user_id,
        **settings_data
    )
    
    # Log the settings change
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='update_email_settings',
        description='Email settings updated',
        user_id=current_user_id,
        status='success',
        extra_data={'updated_fields': list(settings_data.keys())}
    )
    
    return AppSettings.get_settings()


def get_email_config_status():
    """
    Get comprehensive email configuration status.
    
    Returns:
        dict: Configuration status including validity, missing fields, and configs
    """
    from flask import current_app
    
    settings_obj = AppSettings.get_settings()
    is_valid, missing_fields = settings_obj.test_mail_config()
    
    flask_config = {
        'MAIL_SERVER': current_app.config.get('MAIL_SERVER'),
        'MAIL_PORT': current_app.config.get('MAIL_PORT'),
        'MAIL_USE_TLS': current_app.config.get('MAIL_USE_TLS'),
        'MAIL_USE_SSL': current_app.config.get('MAIL_USE_SSL'),
        'MAIL_USERNAME': current_app.config.get('MAIL_USERNAME'),
        'MAIL_DEFAULT_SENDER': current_app.config.get('MAIL_DEFAULT_SENDER'),
        'MAIL_PASSWORD_SET': bool(current_app.config.get('MAIL_PASSWORD'))
    }
    
    db_config = {
        'mail_server': settings_obj.mail_server,
        'mail_port': settings_obj.mail_port,
        'mail_use_tls': settings_obj.mail_use_tls,
        'mail_use_ssl': settings_obj.mail_use_ssl,
        'mail_username': settings_obj.mail_username,
        'mail_default_sender': settings_obj.mail_default_sender,
        'mail_password_set': bool(settings_obj.mail_password_hash)
    }
    
    return {
        'is_valid': is_valid,
        'missing_fields': missing_fields,
        'flask_config': flask_config,
        'database_config': db_config
    }


def create_superuser(user_id, current_user_id):
    """
    Grant superuser privileges to a user.
    
    Args:
        user_id: ID of user to make superuser
        current_user_id: ID of user performing the action
        
    Returns:
        Superuser: The created superuser record
        
    Raises:
        ValueError: If user not found or already a superuser
    """
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")
    
    existing_superuser = Superuser.query.filter_by(user_id=user.id).first()
    if existing_superuser:
        raise ValueError("User is already a superuser")
    
    new_superuser = Superuser.create(user_id=user.id)
    
    # Log the action
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='grant_superuser',
        description=f'Superuser privileges granted to {user.email}',
        user_id=current_user_id,
        target_type='user',
        target_id=user.id,
        status='success',
        extra_data={
            'target_email': user.email,
            'target_user_id': user.id,
            'superuser_id': new_superuser.id
        }
    )
    
    return new_superuser


def revoke_superuser(user_id, current_user_id):
    """
    Revoke superuser privileges from a user.
    
    Args:
        user_id: ID of user to revoke privileges from
        current_user_id: ID of user performing the action
        
    Raises:
        ValueError: If user not found or not a superuser
    """
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")
    
    existing_superuser = Superuser.query.filter_by(user_id=user.id).first()
    if not existing_superuser:
        raise ValueError("User is not a superuser")
    
    existing_superuser.delete()
    
    # Log the action
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='revoke_superuser',
        description=f'Superuser privileges revoked from {user.email}',
        user_id=current_user_id,
        target_type='user',
        target_id=user.id,
        status='success',
        extra_data={
            'target_email': user.email,
            'target_user_id': user.id
        }
    )
