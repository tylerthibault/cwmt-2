"""
Utility module for seeding default users in the database
Provides functionality to create pre-defined test users on first database initialization
"""
from src.models import db
from src.models.user import User
from src.models.roles import Role, UserHasRoles
from src.logic.auth_logic import AuthLogic


def seed_default_users(app):
    """
    Seed the database with default test users if they don't exist.
    
    Creates the following default users:
    - super-user: Full system access (super-user role)
    - admin: Administrative access (admin role)
    - instructor: Teaching privileges (instructor role)
    - student: Basic access (student role)
    
    Args:
        app: Flask application instance
    """
    # Default password for all test users (should be changed in production)
    default_password = 'Pass123!!'
    password_hash = AuthLogic.generate_password_hash(default_password)
    
    default_users = [
        {
            'username': 'jmitchell',
            'email': 'jennifer.mitchell@cwmt.test',
            'password_hash': password_hash,
            'first_name': 'Jennifer',
            'last_name': 'Mitchell',
            'is_active': True,
            'is_admin': True,
            'email_confirmed': True,
            'role_name': 'super-user'
        },
        {
            'username': 'rthompson',
            'email': 'robert.thompson@cwmt.test',
            'password_hash': password_hash,
            'first_name': 'Robert',
            'last_name': 'Thompson',
            'is_active': True,
            'is_admin': True,
            'email_confirmed': True,
            'role_name': 'admin'
        },
        {
            'username': 'schen',
            'email': 'sarah.chen@cwmt.test',
            'password_hash': password_hash,
            'first_name': 'Sarah',
            'last_name': 'Chen',
            'is_active': True,
            'is_admin': False,
            'email_confirmed': True,
            'role_name': 'instructor'
        },
        {
            'username': 'dgarcia',
            'email': 'david.garcia@cwmt.test',
            'password_hash': password_hash,
            'first_name': 'David',
            'last_name': 'Garcia',
            'is_active': True,
            'is_admin': False,
            'email_confirmed': True,
            'role_name': 'student'
        }
    ]
    
    users_created = 0
    users_existing = 0
    
    for user_data in default_users:
        # Extract role name for separate handling
        role_name = user_data.pop('role_name')
        
        # Check if user already exists by email or username
        existing_user = User.query.filter(
            (User.email == user_data['email']) | 
            (User.username == user_data['username'])
        ).first()
        
        if not existing_user:
            # Create new user
            user = User(**user_data)
            db.session.add(user)
            db.session.flush()  # Flush to get user.id for role assignment
            
            # Assign role to user
            role = Role.get_by_name(role_name)
            if role:
                UserHasRoles.assign_role(user.id, role.id)
                app.looger.info(f"Created user: {user_data['username']} with role: {role_name}")
            else:
                app.looger.warning(f"Created user: {user_data['username']} but role '{role_name}' not found")
            
            users_created += 1
        else:
            users_existing += 1
            app.looger.debug(f"User already exists: {user_data['username']}")
    
    # Commit all new users at once
    if users_created > 0:
        try:
            db.session.commit()
            app.looger.info(
                f"Default users seeded successfully",
                created=users_created,
                existing=users_existing
            )
            app.looger.info(f"Default password for all test users: {default_password}")
        except Exception as e:
            db.session.rollback()
            app.looger.error(f"Error seeding users: {str(e)}")
            raise
    else:
        app.looger.debug(
            f"No new users needed",
            existing=users_existing
        )


__all__ = ['seed_default_users']
