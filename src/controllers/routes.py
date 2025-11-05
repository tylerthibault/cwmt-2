from flask import Blueprint, jsonify, current_app as app, render_template, redirect, url_for, flash

# Create a blueprint for main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Example route showing logger usage"""
    app.looger.info("Index route accessed", route="/", method="GET")
    
    return render_template('public/landing/index.html')

@main_bp.route('/courses')
def courses():
    """Courses page route - displays available courses in calendar view"""
    app.looger.info("Courses route accessed", route="/courses", method="GET")
    
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
            
            courses_data.append({
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
        app.looger.error(f"Error fetching available courses: {str(e)}")
        return jsonify({'error': 'Failed to load courses'}), 500

@main_bp.route('/about')
def about():
    """About page route"""
    app.looger.info("About route accessed", route="/about", method="GET")
    
    return render_template('public/about/index.html')

@main_bp.route('/contact')
def contact():
    """Contact page route"""
    app.looger.info("Contact route accessed", route="/contact", method="GET")
    
    return render_template('public/contact.html')

@main_bp.route('/seed')
def seed():
    """Route to trigger seeding of student profiles"""
    from seeds.seed_students import seed_student_profiles, seed_sample_enrollments
    
    try:
        seed_student_profiles(app)
        seed_sample_enrollments(app)
        flash('Seeding completed successfully.', 'success')
    except Exception as e:
        app.looger.error(f"Seeding failed: {str(e)}")
        flash(f'Seeding failed: {str(e)}', 'error')
    
    return redirect(url_for('main.index'))
