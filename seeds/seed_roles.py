"""
Utility module for seeding default roles in the database
Provides functionality to create pre-defined roles on first database initialization
"""
from src.models import db
from src.models.roles import Role


def seed_default_roles(app):
    """
    Seed the database with default roles if they don't exist
    
    Creates the following default roles:
    - super-user: Full system access and administrative privileges
    - admin: Administrative access for managing users and content
    - instructor: Teaching and content creation privileges
    - student: Basic access for learning and participation
    
    Args:
        app: Flask application instance
    """
    default_roles = [
        {
            'name': 'super-user',
            'description': 'Full system access and administrative privileges'
        },
        {
            'name': 'admin',
            'description': 'Administrative access for managing users and content'
        },
        {
            'name': 'instructor',
            'description': 'Teaching and content creation privileges'
        },
        {
            'name': 'student',
            'description': 'Basic access for learning and participation'
        }
    ]
    
    roles_created = 0
    roles_existing = 0
    
    for role_data in default_roles:
        # Check if role already exists
        existing_role = Role.query.filter_by(name=role_data['name']).first()
        
        if not existing_role:
            # Create new role
            role = Role(
                name=role_data['name'],
                description=role_data['description']
            )
            db.session.add(role)
            roles_created += 1
            print(f"  ✓ Created role: {role_data['name']}")
        else:
            roles_existing += 1
            print(f"  - Role already exists: {role_data['name']}")
    
    # Commit all new roles at once
    if roles_created > 0:
        db.session.commit()
        print(f"\n✓ Seeded {roles_created} role(s), {roles_existing} already existed")
    else:
        print(f"\n✓ All {roles_existing} role(s) already exist")


__all__ = ['seed_default_roles']
