"""
Quick seed file for basic roles
"""
from src.models.roles import Role

def seed_basic_roles(app):
    """Seed the basic roles: superuser, admin, instructor, student"""

    roles_data = [
        {
            'name': 'superuser',
            'description': 'Super user with full system access'
        },
        {
            'name': 'admin',
            'description': 'Administrator with user and course management access'
        },
        {
            'name': 'instructor',
            'description': 'Instructor with course teaching and student management access'
        },
        {
            'name': 'student',
            'description': 'Student with course enrollment and viewing access'
        }
    ]

    with app.app_context():
        for role_data in roles_data:
            # Check if role already exists
            existing_role = Role.query.filter_by(name=role_data['name']).first()
            if not existing_role:
                role = Role.create_role(
                    name=role_data['name'],
                    description=role_data['description']
                )
                print(f"✓ Created role: {role.name}")
            else:
                print(f"⚠ Role already exists: {role_data['name']}")

        print("Basic roles seeding completed!")