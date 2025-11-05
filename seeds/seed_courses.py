"""
Utility to seed default course templates into the database
Run this after initial database setup or to add sample course templates
"""
from src.models import db
from src.models.courses_model import CourseTemplate


def seed_default_course_templates(app):
    """
    Seed default course templates if they don't exist.
    
    Args:
        app: Flask application instance with app context
    """
    default_templates = [
        # Beginner Courses
        {
            'name': 'Get Riding',
            'description': 'A comprehensive two-day course covering essential motorcycle riding skills and techniques for absolute beginners.',
            'duration_days': 2,
            'experience_level': 'beginner',
            'max_students': 12,
            'is_active': True
        },
        
        # Intermediate Courses
        {
            'name': 'Street Smart',
            'description': 'A focused one-day course on street riding awareness, urban navigation, and defensive riding strategies.',
            'duration_days': 1,
            'experience_level': 'intermediate',
            'max_students': 10,  
            'is_active': True
        }
    ]
    
    templates_created = 0
    
    for template_data in default_templates:
        # Check if template already exists by name
        existing = CourseTemplate.query.filter_by(name=template_data['name']).first()
        
        if not existing:
            template = CourseTemplate(**template_data)
            db.session.add(template)
            templates_created += 1
            app.looger.info(f"Created course template: {template_data['name']}")
    
    if templates_created > 0:
        try:
            db.session.commit()
            app.looger.info(f"Successfully seeded {templates_created} course template(s)")
        except Exception as e:
            db.session.rollback()
            app.looger.error(f"Error seeding course templates: {str(e)}")
    else:
        app.looger.info("Course templates already exist, skipping seed")


def seed_sample_courses(app):
    """
    Seed sample course instances for testing/demonstration.
    Note: This requires users to already exist in the database.
    
    Args:
        app: Flask application instance with app context
    """
    from datetime import date, time
    from src.models.courses_model import Course
    from src.models.user import User
    
    # First check if we have course templates
    templates = CourseTemplate.query.all()
    if not templates:
        app.looger.warning("No course templates found. Run seed_default_course_templates first.")
        return
    
    # Check if we have users with appropriate roles
    students = User.query.filter(User.role_list.any(name='student')).all()
    instructors = User.query.filter(User.role_list.any(name='instructor')).all()
    
    if len(students) < 1:
        app.looger.warning("Not enough students in database to seed sample courses.")
        return
    
    if len(instructors) < 2:
        app.looger.warning("Not enough instructors in database to seed sample courses.")
        return
    
    # Create sample courses
    sample_courses = [
        {
            'course_template_id': templates[0].id,
            'course_date': date(2025, 11, 15),
            'course_time': time(9, 0),
            'status': 'scheduled',
            'location': 'Seattle Training Center',
            'instructor1_id': instructors[0].id,
            'instructor2_id': instructors[1].id if len(instructors) > 1 else instructors[0].id
        }
    ]
    
    courses_created = 0
    
    for course_data in sample_courses:
        # Check if course already exists
        existing = Course.query.filter_by(
            course_template_id=course_data['course_template_id'],
            course_date=course_data['course_date'],
            course_time=course_data['course_time']
        ).first()
        
        if not existing:
            # Remove student_id from course_data if present (use enrollment instead)
            student_to_enroll = None
            if 'student_id' in course_data:
                student_to_enroll = course_data.pop('student_id')
            
            # Create the course without student
            course = Course(**course_data)
            db.session.add(course)
            db.session.flush()  # Flush to get the course ID
            
            # Enroll student if specified - use CourseLogic to handle new enrollment system
            if student_to_enroll:
                from src.logic.course_logic import CourseLogic
                try:
                    CourseLogic.enroll_student(course.id, student_to_enroll, is_admin_override=True)
                except Exception as e:
                    app.looger.warning(f"Could not enroll student {student_to_enroll}: {str(e)}")
            
            courses_created += 1
            app.looger.info(f"Created sample course on {course_data['course_date']}")
    
    if courses_created > 0:
        try:
            db.session.commit()
            app.looger.info(f"Successfully seeded {courses_created} sample course(s)")
        except Exception as e:
            db.session.rollback()
            app.looger.error(f"Error seeding sample courses: {str(e)}")
    else:
        app.looger.info("Sample courses already exist, skipping seed")


if __name__ == '__main__':
    # This allows running the seed script directly
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    from src import create_app
    
    app = create_app()
    with app.app_context():
        print("Seeding course templates...")
        seed_default_course_templates(app)
        
        print("\nSeeding sample courses...")
        seed_sample_courses(app)
        
        print("\nSeeding complete!")
