"""
Seed student profiles and enrollments
Creates example students with profiles and course enrollments
"""
from datetime import datetime, timedelta
from src.models import db
from src.models.user import User
from src.models.student_profile import StudentProfile
from src.models.course_enrollment import CourseEnrollment
from src.models.courses_model import Course
from src.logic.student_logic import StudentLogic


def seed_student_profiles(app):
    """
    Seed student profiles for existing users.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        app.looger.info("Seeding student profiles...")
        
        try:
            # Get all users who don't have student profiles yet
            users = User.query.all()
            students_created = 0
            
            for user in users:
                # Check if user already has a student profile
                existing_profile = StudentProfile.query.filter_by(user_id=user.id).first()
                if existing_profile:
                    continue
                
                # Create student profile for users who aren't admins
                if not user.is_admin:
                    try:
                        student_data = {
                            'student_number': f'STU{user.id:05d}',
                            'grade_level': 'Beginner',
                            'overall_score': 0.0,
                            'emergency_contact_name': f'{user.first_name or "Parent"} Contact',
                            'emergency_contact_phone': '555-0100'
                        }
                        
                        StudentLogic.create_student_profile(user.id, student_data)
                        students_created += 1
                        app.looger.info(f"Created student profile for user {user.username}")
                    except Exception as e:
                        app.looger.error(f"Failed to create student profile for user {user.username}: {str(e)}")
            
            if students_created > 0:
                app.looger.info(f"Successfully created {students_created} student profiles")
            else:
                app.looger.info("No new student profiles created (all users already have profiles or are admins)")
                
        except Exception as e:
            app.looger.error(f"Error seeding student profiles: {str(e)}")
            db.session.rollback()


def seed_sample_enrollments(app):
    """
    Seed sample course enrollments with vehicle information.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        app.looger.info("Seeding sample course enrollments...")
        
        try:
            # Get some students and courses
            students = StudentProfile.query.limit(5).all()
            courses = Course.query.filter_by(status='scheduled').limit(3).all()
            
            if not students:
                app.looger.info("No students found, skipping enrollment seeding")
                return
            
            if not courses:
                app.looger.info("No scheduled courses found, skipping enrollment seeding")
                return
            
            enrollments_created = 0
            
            # Create sample enrollments
            for i, student in enumerate(students):
                for j, course in enumerate(courses):
                    # Check if already enrolled
                    existing = CourseEnrollment.query.filter_by(
                        student_id=student.id,
                        course_id=course.id
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Create enrollment with different vehicle configurations
                    enrollment_data = {}
                    
                    # Every other student brings a motorcycle
                    if i % 2 == 0:
                        enrollment_data.update({
                            'brings_motorcycle': True,
                            'motorcycle_make': 'Honda' if i % 4 == 0 else 'Yamaha',
                            'motorcycle_model': 'CBR500R' if i % 4 == 0 else 'YZF-R3',
                            'motorcycle_year': 2020 + i,
                            'motorcycle_license_plate': f'MC{i}{j}123'
                        })
                    
                    # Some students bring cars
                    if i % 3 == 0:
                        enrollment_data.update({
                            'brings_car': True,
                            'car_make': 'Toyota',
                            'car_model': 'Corolla',
                            'car_year': 2019 + i,
                            'car_license_plate': f'CAR{i}{j}456'
                        })
                    
                    # Add some notes
                    enrollment_data['notes'] = f'Sample enrollment for testing - Student {i+1} in Course {j+1}'
                    
                    try:
                        StudentLogic.enroll_in_course(
                            student.id,
                            course.id,
                            enrollment_data
                        )
                        enrollments_created += 1
                        app.looger.info(f"Enrolled student {student.student_number} in course {course.id}")
                    except Exception as e:
                        app.looger.error(f"Failed to enroll student {student.student_number}: {str(e)}")
            
            if enrollments_created > 0:
                app.looger.info(f"Successfully created {enrollments_created} course enrollments")
            else:
                app.looger.info("No new enrollments created (students already enrolled)")
                
        except Exception as e:
            app.looger.error(f"Error seeding enrollments: {str(e)}")
            db.session.rollback()


def seed_completed_courses(app):
    """
    Seed some completed courses with scores for testing.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        app.looger.info("Seeding completed course enrollments...")
        
        try:
            # Get some active enrollments to mark as completed
            active_enrollments = CourseEnrollment.query.filter_by(status='active').limit(3).all()
            
            if not active_enrollments:
                app.looger.info("No active enrollments found, skipping completion seeding")
                return
            
            completions = 0
            scores = [95.5, 87.0, 92.5, 78.0, 88.5]
            
            for i, enrollment in enumerate(active_enrollments):
                try:
                    final_score = scores[i % len(scores)]
                    StudentLogic.complete_course(enrollment.id, final_score)
                    completions += 1
                    app.looger.info(f"Marked enrollment {enrollment.id} as completed with score {final_score}")
                except Exception as e:
                    app.looger.error(f"Failed to complete enrollment {enrollment.id}: {str(e)}")
            
            if completions > 0:
                app.looger.info(f"Successfully completed {completions} enrollments")
            else:
                app.looger.info("No enrollments marked as completed")
                
        except Exception as e:
            app.looger.error(f"Error seeding completed courses: {str(e)}")
            db.session.rollback()


def seed_all_students(app):
    """
    Run all student-related seeding operations.
    
    Args:
        app: Flask application instance
    """
    seed_student_profiles(app)
    seed_sample_enrollments(app)
    seed_completed_courses(app)


# Auto-run seeding if this file is executed directly
if __name__ == '__main__':
    from run import app
    seed_all_students(app)
