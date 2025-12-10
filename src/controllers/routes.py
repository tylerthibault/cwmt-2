from flask import Blueprint, jsonify, current_app, render_template, redirect, url_for, flash

# Create a blueprint for main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Example route showing logger usage"""
    current_app.logger.info("Index route accessed", route="/", method="GET")
    
    return render_template('public/landing/index.html')

@main_bp.route('/courses')
def courses():
    """Courses page route - displays available courses in calendar view"""
    current_app.logger.info("Courses route accessed", route="/courses", method="GET")
    
    return render_template('public/courses/index.html')


@main_bp.route('/api/courses/available')
def api_available_courses():
    """API endpoint to get available courses for public viewing"""
    from src.logic.course_logic import CourseLogic
    from datetime import timedelta
    
    try:
        # Get available courses (not full, scheduled, future)
        courses = CourseLogic.get_available_courses(include_full=True)
        
        # Get unique locations for filtering
        locations = set()
        for course in courses:
            if course.location:
                locations.add(course.location)
        
        # Serialize courses for calendar
        courses_data = []
        for course in courses:
            # Calculate end date based on duration
            end_date = course.course_date + timedelta(days=course.template.duration_days if course.template else 1)
            
            courses_data.current_append({
                'id': course.id,
                'title': course.template.name if course.template else 'Course',
                'start': course.course_date.isoformat(),
                'end': end_date.isoformat(),  # End date for multi-day display
                'time': course.course_time.strftime('%H:%M') if course.course_time else '00:00',
                'location': course.location,
                'status': course.status,
                'template_name': course.template.name if course.template else 'Unknown',
                'experience_level': course.template.experience_level if course.template else 'beginner',
                'duration_days': course.template.duration_days if course.template else 1,
                'max_students': course.get_max_students(),
                'enrolled_count': len(course.enrollments),
                'available_slots': course.get_available_slots(),
                'is_full': course.is_full()
            })
        
        return jsonify({
            'courses': courses_data,
            'locations': sorted(list(locations))
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching available courses: {str(e)}")
        return jsonify({'error': 'Failed to load courses'}), 500

@main_bp.route('/about')
def about():
    """About page route"""
    current_app.logger.info("About route accessed", route="/about", method="GET")
    
    return render_template('public/about/index.html')

@main_bp.route('/contact')
def contact():
    """Contact page route"""
    current_app.logger.info("Contact route accessed", route="/contact", method="GET")
    
    return render_template('public/contact.html')


@main_bp.route('/seed')
def seed():
    """Route to trigger seeding - for development/testing only"""
    try:

        from src.development.seeds import roles
        roles.seed_basic_roles(current_app)

        from src.development.seeds import users
        users.seed_users(current_app)

        from src.development.seeds import courses
        courses.seed_courses(current_app)

        
        Logger.info("Seeding completed successfully via /seed route")
        flash('Seeding completed successfully!', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        Logger.error(f"Seeding failed via /seed route: {str(e)}")
        return f"Seeding failed: {str(e)}", 500
    
@main_bp.route('/reset_db')
def reset_db():
    """
        Route to reset the database for development/testing only. This will delete the database completely and recreate it and then redirect to the seeding route.
    """
    try:
        from src.models import db
        db.drop_all()
        db.create_all()
        
        Logger.info("Database reset completed successfully via /reset_db route")
        flash('Database reset successfully!', 'success')
        return redirect(url_for('main.seed'))
    except Exception as e:
        Logger.error(f"Database reset failed via /reset_db route: {str(e)}")
        return redirect(url_for('main.index'))
