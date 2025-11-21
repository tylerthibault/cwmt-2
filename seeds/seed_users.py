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
            'username': 'mlopez',
            'email': 'maria.lopez@cwmt.test',
            'password_hash': password_hash,
            'first_name': 'Maria',
            'last_name': 'Lopez',
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
        },
        {
            'username': 'ewilson',
            'email': 'emily.wilson@cwmt.test',
            'password_hash': password_hash,
            'first_name': 'Emily',
            'last_name': 'Wilson',
            'is_active': True,
            'is_admin': False,
            'email_confirmed': True,
            'role_name': 'student'
        },
        {
            'username': 'jbrown',
            'email': 'james.brown@cwmt.test',
            'password_hash': password_hash,
            'first_name': 'James',
            'last_name': 'Brown',
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
            
            # Assign role to user - manually add to avoid nested commit
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user_role = UserHasRoles(user_id=user.id, role_id=role.id)
                db.session.add(user_role)
                print(f"  ✓ Created user: {user.username} ({role_name})")
            else:
                print(f"  ⚠ Created user: {user.username} but role '{role_name}' not found")
            
            users_created += 1
        else:
            users_existing += 1
            print(f"  - User already exists: {existing_user.username}")
    
    # Commit all new users at once
    if users_created > 0:
        try:
            db.session.commit()
            print(f"\n✓ Seeded {users_created} user(s), {users_existing} already existed")
            print(f"  Default password for all test users: {default_password}")
        except Exception as e:
            db.session.rollback()
            print(f"  ✗ Error seeding users: {str(e)}")
            raise
    else:
        print(f"\n✓ All {users_existing} user(s) already exist")


__all__ = ['seed_default_users']
