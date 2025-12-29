from flask import Blueprint, render_template
import json
from src.models.course_folder import course_instances
from src.services.calendar import format_course_instances_for_calendar

# Create blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page route."""
    return render_template('public/landing/index.html')


@main_bp.route('/courses')
def public_courses():
    """Public courses page."""
    # Get all scheduled course instances
    all_courses = course_instances.CourseInstance.query.filter_by(status='scheduled').all()
    events = format_course_instances_for_calendar(all_courses)
    
    context = {
        'events_json': json.dumps(events),
        'courses': all_courses
    }
    return render_template('public/courses/index.html', **context)


@main_bp.route('/signup')
def signup_page():
    """Public signup page with course information."""
    from flask import request
    course_id = request.args.get('course')
    
    course = None
    if course_id:
        course = course_instances.CourseInstance.query.get(course_id)
    
    context = {
        'course': course
    }
    return render_template('public/auth/signup.html', **context)


@main_bp.app_errorhandler(404)
def page_not_found(error):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors."""
    return render_template('errors/500.html'), 500
