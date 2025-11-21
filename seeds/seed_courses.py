"""
Utility to seed default course templates into the database
Run this after initial database setup or to add sample course templates
"""
from datetime import date, time
from src.models import db
from src.models.courses_model import CourseTemplate, Course
from src.models.user import User
from src.models.roles import Role


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
        {
            'name': 'Basic Rider Course',
            'description': 'Essential safety and riding skills for new motorcyclists. Covers basics of motorcycle operation, safety, and traffic strategies.',
            'duration_days': 3,
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
        },
        {
            'name': 'Advanced Rider Course',
            'description': 'For experienced riders looking to refine their skills. Covers advanced techniques, emergency maneuvers, and risk management.',
            'duration_days': 1,
            'experience_level': 'intermediate',
            'max_students': 8,
            'is_active': True
        }
    ]
    
    templates_created = 0
    templates_existing = 0
    
    for template_data in default_templates:
        # Check if template already exists by name
        existing = CourseTemplate.query.filter_by(name=template_data['name']).first()
        
        if not existing:
            template = CourseTemplate(**template_data)
            db.session.add(template)
            templates_created += 1
            print(f"  ✓ Created template: {template_data['name']}")
        else:
            templates_existing += 1
            print(f"  - Template already exists: {template_data['name']}")
    
    if templates_created > 0:
        try:
            db.session.commit()
            print(f"\n✓ Seeded {templates_created} template(s), {templates_existing} already existed")
        except Exception as e:
            db.session.rollback()
            print(f"  ✗ Error seeding course templates: {str(e)}")
            raise
    else:
        print(f"\n✓ All {templates_existing} template(s) already exist")


def seed_sample_courses(app):
    """
    Seed sample course instances for testing/demonstration.
    Note: This requires users to already exist in the database.
    
    Args:
        app: Flask application instance with app context
    """
    # First check if we have course templates
    templates = CourseTemplate.query.all()
    if not templates:
        print("  ⚠ No course templates found. Run seed_default_course_templates first.")
        return
    
    # Check if we have users with appropriate roles
    instructors = User.query.join(User.role_list).filter(Role.name == 'instructor').all()
    
    if len(instructors) < 2:
        print(f"  ⚠ Not enough instructors in database ({len(instructors)} found, need 2)")
        return
    
    # Create sample courses for upcoming months
    sample_courses = [
        {
            'course_template_id': templates[0].id,
            'course_date': date(2025, 12, 15),
            'course_time': time(9, 0),
            'status': 'scheduled',
            'location': 'Seattle Training Center',
            'instructor1_id': instructors[0].id,
            'instructor2_id': instructors[1].id
        },
        {
            'course_template_id': templates[0].id if len(templates) == 1 else templates[1].id,
            'course_date': date(2025, 12, 22),
            'course_time': time(9, 0),
            'status': 'scheduled',
            'location': 'Portland Training Facility',
            'instructor1_id': instructors[0].id,
            'instructor2_id': instructors[1].id
        },
        {
            'course_template_id': templates[-1].id,
            'course_date': date(2026, 1, 5),
            'course_time': time(13, 0),
            'status': 'scheduled',
            'location': 'Seattle Training Center',
            'instructor1_id': instructors[0].id,
            'instructor2_id': instructors[1].id
        }
    ]
    
    courses_created = 0
    courses_existing = 0
    
    for course_data in sample_courses:
        # Check if course already exists
        existing = Course.query.filter_by(
            course_template_id=course_data['course_template_id'],
            course_date=course_data['course_date'],
            course_time=course_data['course_time']
        ).first()
        
        if not existing:
            # Create the course
            course = Course(**course_data)
            db.session.add(course)
            courses_created += 1
            template = CourseTemplate.query.get(course_data['course_template_id'])
            print(f"  ✓ Created course: {template.name} on {course_data['course_date']}")
        else:
            courses_existing += 1
    
    if courses_created > 0:
        try:
            db.session.commit()
            print(f"\n✓ Seeded {courses_created} course(s), {courses_existing} already existed")
        except Exception as e:
            db.session.rollback()
            print(f"  ✗ Error seeding sample courses: {str(e)}")
            raise
    else:
        print(f"\n✓ All {courses_existing} course(s) already exist")


def seed_all_courses(app):
    """
    Run all course-related seeding operations.
    
    Args:
        app: Flask application instance
    """
    seed_default_course_templates(app)
    seed_sample_courses(app)


if __name__ == '__main__':
    # This allows running the seed script directly
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    from src import create_app
    
    app = create_app()
    with app.app_context():
        print("Seeding courses...")
        seed_all_courses(app)
        print("\nSeeding complete!")


__all__ = ['seed_default_course_templates', 'seed_sample_courses', 'seed_all_courses']

