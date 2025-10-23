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
        {
            'name': 'Basic Rider Course (BRC)',
            'description': 'MSF-approved basic rider training covering fundamentals of motorcycle operation, safety, and control.',
            'duration_days': 3,
            'experience_level': 'beginner',
            'max_students': 12,
            'is_active': True
        },
        {
            'name': 'First Time Rider',
            'description': 'Perfect for those who have never sat on a motorcycle. Learn the absolute basics in a safe, controlled environment.',
            'duration_days': 1,
            'experience_level': 'beginner',
            'max_students': 8,
            'is_active': True
        },
        {
            'name': 'Clutch Control Fundamentals',
            'description': 'Master the art of smooth clutch operation, essential for confident riding and slow-speed maneuvers.',
            'duration_days': 1,
            'experience_level': 'beginner',
            'max_students': 10,
            'is_active': True
        },
        {
            'name': 'Pre-License Preparation',
            'description': 'Intensive preparation for your motorcycle license test, covering all required skills and knowledge.',
            'duration_days': 2,
            'experience_level': 'beginner',
            'max_students': 8,
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
            'name': 'Advanced Street Riding',
            'description': 'Elevate your street riding skills with advanced techniques for traffic negotiation, cornering, and hazard avoidance.',
            'duration_days': 2,
            'experience_level': 'intermediate',
            'max_students': 10,
            'is_active': True
        },
        {
            'name': 'Canyon Carving Techniques',
            'description': 'Learn proper body positioning, line selection, and throttle control for spirited mountain road riding.',
            'duration_days': 2,
            'experience_level': 'intermediate',
            'max_students': 8,
            'is_active': True
        },
        {
            'name': 'Emergency Braking & Swerving',
            'description': 'Master critical emergency maneuvers including maximum braking, swerving, and obstacle avoidance.',
            'duration_days': 1,
            'experience_level': 'intermediate',
            'max_students': 12,
            'is_active': True
        },
        {
            'name': 'Group Riding Safety',
            'description': 'Essential skills and protocols for safe group motorcycle riding, including formations, communication, and etiquette.',
            'duration_days': 1,
            'experience_level': 'intermediate',
            'max_students': 15,
            'is_active': True
        },
        {
            'name': 'Cornering Confidence',
            'description': 'Build confidence in corners with progressive exercises focusing on lean angle, vision, and throttle control.',
            'duration_days': 2,
            'experience_level': 'intermediate',
            'max_students': 10,
            'is_active': True
        },
        {
            'name': 'Long Distance Touring',
            'description': 'Preparation for multi-day motorcycle tours covering route planning, bike loading, fatigue management, and comfort.',
            'duration_days': 1,
            'experience_level': 'intermediate',
            'max_students': 12,
            'is_active': True
        },
        {
            'name': 'Urban Commuter Tactics',
            'description': 'Specialized training for daily urban commuting, lane positioning, filtering techniques, and city-specific hazards.',
            'duration_days': 1,
            'experience_level': 'intermediate',
            'max_students': 10,
            'is_active': True
        },
        
        # Advanced Courses
        {
            'name': 'Track Day Preparation',
            'description': 'Essential skills and techniques for your first track day, including body positioning, racing lines, and track etiquette.',
            'duration_days': 1,
            'experience_level': 'advanced',
            'max_students': 8,
            'is_active': True
        },
        {
            'name': 'Advanced Cornering Dynamics',
            'description': 'Deep dive into cornering physics, trail braking, late apexing, and maximizing lean angle safely.',
            'duration_days': 2,
            'experience_level': 'advanced',
            'max_students': 8,
            'is_active': True
        },
        {
            'name': 'Sport Riding Performance',
            'description': 'Advanced techniques for spirited sport riding including aggressive braking, fast transitions, and maximum corner speed.',
            'duration_days': 3,
            'experience_level': 'advanced',
            'max_students': 8,
            'is_active': True
        },
        {
            'name': 'Off-Road Adventure Basics',
            'description': 'Introduction to off-road motorcycle riding covering standing, balance, terrain reading, and basic trail techniques.',
            'duration_days': 2,
            'experience_level': 'advanced',
            'max_students': 8,
            'is_active': True
        },
        {
            'name': 'Motorcycle Racing Fundamentals',
            'description': 'Entry-level racing course covering starts, passing, race craft, and competitive riding techniques.',
            'duration_days': 3,
            'experience_level': 'advanced',
            'max_students': 8,
            'is_active': True
        },
        {
            'name': 'Dirt Bike Mastery',
            'description': 'Advanced off-road techniques including jumps, whoops, hill climbs, and technical terrain navigation.',
            'duration_days': 2,
            'experience_level': 'advanced',
            'max_students': 8,
            'is_active': True
        },
        {
            'name': 'Supermoto Skills',
            'description': 'Combine street and dirt skills with supermoto techniques including flat track sliding and mixed-surface riding.',
            'duration_days': 2,
            'experience_level': 'advanced',
            'max_students': 8,
            'is_active': True
        },
        
        # Specialized Courses
        {
            'name': 'Cruiser Handling Workshop',
            'description': 'Specialized training for cruiser and touring bike riders focusing on low-speed control and weight management.',
            'duration_days': 1,
            'experience_level': 'intermediate',
            'max_students': 10,
            'is_active': True
        },
        {
            'name': 'Adventure Bike Techniques',
            'description': 'Master the unique challenges of adventure bikes including standing position, off-road basics, and bike recovery.',
            'duration_days': 2,
            'experience_level': 'intermediate',
            'max_students': 10,
            'is_active': True
        },
        {
            'name': 'Scooter Safety Course',
            'description': 'Essential safety training for scooter riders covering urban navigation, maintenance, and defensive strategies.',
            'duration_days': 1,
            'experience_level': 'beginner',
            'max_students': 12,
            'is_active': True
        },
        {
            'name': 'Electric Motorcycle Orientation',
            'description': 'Introduction to electric motorcycle operation, charging, range management, and unique handling characteristics.',
            'duration_days': 1,
            'experience_level': 'beginner',
            'max_students': 12,
            'is_active': True
        },
        {
            'name': 'Sidecar Operation Training',
            'description': 'Specialized course for sidecar outfit operation covering asymmetric handling, turning techniques, and passenger safety.',
            'duration_days': 2,
            'experience_level': 'intermediate',
            'max_students': 10,
            'is_active': True
        },
        {
            'name': 'Three-Wheeler Riding Course',
            'description': 'Training for three-wheeled motorcycles (trikes) covering stability, cornering differences, and safe operation.',
            'duration_days': 1,
            'experience_level': 'beginner',
            'max_students': 12,
            'is_active': True
        },
        
        # Safety & Maintenance
        {
            'name': 'Motorcycle Safety Refresher',
            'description': 'One-day refresher covering latest safety techniques, hazard perception, and risk management for experienced riders.',
            'duration_days': 1,
            'experience_level': 'intermediate',
            'max_students': 10,
            'is_active': True
        },
        {
            'name': 'Senior Rider Safety',
            'description': 'Tailored safety course for mature riders addressing age-related considerations and adaptive riding techniques.',
            'duration_days': 1,
            'experience_level': 'intermediate',
            'max_students': 10,
            'is_active': True
        },
        {
            'name': 'Returning Rider Course',
            'description': 'Designed for riders getting back on a bike after years away, rebuilding skills and confidence safely.',
            'duration_days': 2,
            'experience_level': 'intermediate',
            'max_students': 10,
            'is_active': True
        },
        {
            'name': 'Basic Motorcycle Maintenance',
            'description': 'Learn essential motorcycle maintenance including chain care, fluid checks, tire maintenance, and basic troubleshooting.',
            'duration_days': 1,
            'experience_level': 'beginner',
            'max_students': 12,
            'is_active': True
        },
        {
            'name': 'Pre-Ride Safety Inspection',
            'description': 'Comprehensive training on performing thorough pre-ride safety checks and identifying potential issues.',
            'duration_days': 1,
            'experience_level': 'beginner',
            'max_students': 12,
            'is_active': True
        },
        
        # Weather & Conditions
        {
            'name': 'Wet Weather Riding',
            'description': 'Build confidence riding in rain with techniques for traction management, visibility, and hazard recognition.',
            'duration_days': 1,
            'experience_level': 'intermediate',
            'max_students': 10,
            'is_active': True
        },
        {
            'name': 'Night Riding Skills',
            'description': 'Master the challenges of night riding including vision adaptation, headlight usage, and reduced visibility tactics.',
            'duration_days': 1,
            'experience_level': 'intermediate',
            'max_students': 10,
            'is_active': True
        },
        {
            'name': 'Cold Weather Riding Preparation',
            'description': 'Essential knowledge for cold weather riding covering gear, bike preparation, and cold-specific hazards.',
            'duration_days': 1,
            'experience_level': 'intermediate',
            'max_students': 10,
            'is_active': True
        },
        
        # Skills Clinics
        {
            'name': 'Slow Speed Mastery',
            'description': 'Intensive clinic focused exclusively on slow-speed control, U-turns, and parking lot maneuvers.',
            'duration_days': 1,
            'experience_level': 'beginner',
            'max_students': 12,
            'is_active': True
        },
        {
            'name': 'Parking Lot Practice',
            'description': 'Structured practice session covering fundamental exercises in a safe parking lot environment.',
            'duration_days': 1,
            'experience_level': 'beginner',
            'max_students': 12,
            'is_active': True
        },
        {
            'name': 'Trail Braking Workshop',
            'description': 'Advanced technique workshop focusing on trail braking for improved corner entry and control.',
            'duration_days': 1,
            'experience_level': 'advanced',
            'max_students': 8,
            'is_active': True
        },
        {
            'name': 'Body Position Clinic',
            'description': 'Detailed instruction on proper body positioning for various riding situations and bike types.',
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
