
from src.models.user import User
from src.models.roles import Role, UserHasRoles
from src.logic.auth_logic import AuthLogic


def seed_users(app):
    """
    Seed 8 users: 1 superuser, 1 admin, 2 instructors, and 4 students.
    All users have password 'Pass123!!'.
    """
    password_hash = AuthLogic.generate_password_hash('Pass123!!')

    users_data = [
        # Superuser
        {
            'email': 'superuser@cwmt.com',
            'first_name': 'Tyler',
            'last_name': 'Thibault',
            'role': 'superuser'
        },
        # Admin
        {
            'email': 'admin@cwmt.com',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'role': 'admin'
        },
        # Instructors
        {
            'email': 'instructor1@cwmt.com',
            'first_name': 'Michael',
            'last_name': 'Rodriguez',
            'role': 'instructor'
        },
        {
            'email': 'instructor2@cwmt.com',
            'first_name': 'Jennifer',
            'last_name': 'Chen',
            'role': 'instructor'
        },
        # Students
        {
            'email': 'student1@cwmt.com',
            'first_name': 'David',
            'last_name': 'Williams',
            'role': 'student'
        },
        {
            'email': 'student2@cwmt.com',
            'first_name': 'Emily',
            'last_name': 'Garcia',
            'role': 'student'
        },
        {
            'email': 'student3@cwmt.com',
            'first_name': 'James',
            'last_name': 'Thompson',
            'role': 'student'
        },
        {
            'email': 'student4@cwmt.com',
            'first_name': 'Maria',
            'last_name': 'Martinez',
            'role': 'student'
        }
    ]

    with app.app_context():
        for user_data in users_data:
            # Check if user already exists by email
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if existing_user:
                print(f"⚠ User already exists: {user_data['email']}")
                continue

            # Create the user
            user = User.create(
                email=user_data['email'],
                password_hash=password_hash,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_active=True
            )

            # Assign role
            role = Role.get_by_name(user_data['role'])
            if role:
                UserHasRoles.assign_role(user.id, role.id)
                print(f"✓ Created user: {user_data['email']} ({user_data['role']})")
            else:
                print(f"⚠ Created user but role not found: {user_data['email']} ({user_data['role']})")

            # Create student profile if role is student
            if user_data['role'] == 'student':
                try:
                    from src.logic.student_logic import StudentLogic
                    StudentLogic.create_student_profile(user.id)
                    print(f"✓ Created student profile for: {user_data['email']}")
                except Exception as e:
                    print(f"⚠ Failed to create student profile for {user_data['email']}: {str(e)}")

        print("User seeding completed!")


if __name__ == "__main__":
    from src import create_app
    app = create_app()
    seed_users(app)
