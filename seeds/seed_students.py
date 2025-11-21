"""
Seed student profiles and enrollments
Creates example students with profiles and course enrollments
"""
from datetime import datetime
from src.models import db
from src.models.user import User
from src.models.student_profile import StudentProfile
from src.models.course_enrollment import CourseEnrollment
from src.models.courses_model import Course
from src.models.roles import Role


def seed_student_profiles(app):
    """
    Seed student profiles for existing users with student role.
    
    Args:
        app: Flask application instance
    """
    # Get all users with student role who don't have student profiles yet
    students = User.query.join(User.role_list).filter(Role.name == 'student').all()
    
    if not students:
        print("  ⚠ No users with student role found")
        return
    
    profiles_created = 0
    profiles_existing = 0
    
    for user in students:
        # Check if user already has a student profile
        existing_profile = StudentProfile.query.filter_by(user_id=user.id).first()
        if existing_profile:
            profiles_existing += 1
            continue
        
        # Create student profile
        student_data = {
            'user_id': user.id,
            'student_number': f'STU{user.id:05d}',
            'grade_level': 'Beginner',
            'overall_score': 0.0,
            'emergency_contact_name': f'{user.first_name} Contact',
            'emergency_contact_phone': f'555-010{user.id}'
        }
        
        profile = StudentProfile(**student_data)
        db.session.add(profile)
        profiles_created += 1
        print(f"  ✓ Created student profile for {user.username}")
    
    if profiles_created > 0:
        try:
            db.session.commit()
            print(f"\n✓ Seeded {profiles_created} profile(s), {profiles_existing} already existed")
        except Exception as e:
            db.session.rollback()
            print(f"  ✗ Error seeding student profiles: {str(e)}")
            raise
    else:
        print(f"\n✓ All {profiles_existing} profile(s) already exist")


def seed_sample_enrollments(app):
    """
    Seed sample course enrollments with vehicle information.
    
    Args:
        app: Flask application instance
    """
    # Get some students and courses
    students = StudentProfile.query.limit(5).all()
    courses = Course.query.filter_by(status='scheduled').all()
    
    if not students:
        print("  ⚠ No student profiles found, skipping enrollment seeding")
        return
    
    if not courses:
        print("  ⚠ No scheduled courses found, skipping enrollment seeding")
        return
    
    enrollments_created = 0
    enrollments_existing = 0
    
    # Enroll each student in first 2 courses with different vehicle configurations
    for i, student in enumerate(students):
        for j, course in enumerate(courses[:2] if len(courses) >= 2 else courses):
            # Check if already enrolled
            existing = CourseEnrollment.query.filter_by(
                student_id=student.id,
                course_id=course.id
            ).first()
            
            if existing:
                enrollments_existing += 1
                continue
            
            # Create enrollment with different vehicle configurations
            enrollment_data = {
                'student_id': student.id,
                'course_id': course.id,
                'status': 'active',
                'enrollment_date': datetime.utcnow(),
                'course_score': 0.0,
                'attendance_percentage': 0.0,
                'notes': f'Sample enrollment for testing'
            }
            
            # Every other student brings a motorcycle
            if i % 2 == 0:
                enrollment_data.update({
                    'brings_motorcycle': True,
                    'motorcycle_make': 'Honda' if i % 4 == 0 else 'Yamaha',
                    'motorcycle_model': 'CBR500R' if i % 4 == 0 else 'YZF-R3',
                    'motorcycle_year': 2020 + i,
                    'motorcycle_license_plate': f'MC{i}{j}123'
                })
            
            enrollment = CourseEnrollment(**enrollment_data)
            db.session.add(enrollment)
            enrollments_created += 1
            print(f"  ✓ Enrolled {student.student_number} in course {course.id}")
    
    if enrollments_created > 0:
        try:
            db.session.commit()
            print(f"\n✓ Seeded {enrollments_created} enrollment(s), {enrollments_existing} already existed")
        except Exception as e:
            db.session.rollback()
            print(f"  ✗ Error seeding enrollments: {str(e)}")
            raise
    else:
        print(f"\n✓ All {enrollments_existing} enrollment(s) already exist")


def seed_completed_courses(app):
    """
    Seed some completed courses with scores for testing.
    
    Args:
        app: Flask application instance
    """
    # Get some active enrollments to mark as completed
    active_enrollments = CourseEnrollment.query.filter_by(status='active').limit(2).all()
    
    if not active_enrollments:
        print("  ⚠ No active enrollments found, skipping completion seeding")
        return
    
    completions = 0
    scores = [95.5, 87.0, 92.5, 78.0, 88.5]
    
    for i, enrollment in enumerate(active_enrollments):
        final_score = scores[i % len(scores)]
        enrollment.status = 'completed'
        enrollment.course_score = final_score
        enrollment.completion_date = datetime.utcnow()
        enrollment.attendance_percentage = 100.0
        completions += 1
        print(f"  ✓ Marked enrollment {enrollment.id} as completed with score {final_score}")
    
    if completions > 0:
        try:
            db.session.commit()
            print(f"\n✓ Completed {completions} enrollment(s)")
        except Exception as e:
            db.session.rollback()
            print(f"  ✗ Error completing enrollments: {str(e)}")
            raise


def seed_all_students(app):
    """
    Run all student-related seeding operations.
    
    Args:
        app: Flask application instance
    """
    seed_student_profiles(app)
    seed_sample_enrollments(app)
    seed_completed_courses(app)


if __name__ == '__main__':
    from run import app
    seed_all_students(app)


__all__ = ['seed_student_profiles', 'seed_sample_enrollments', 'seed_completed_courses', 'seed_all_students']
