from flask import Blueprint, render_template, redirect, url_for, request
import json
from src.models.announcements import Announcement
from src.models.course_folder.course_instances import CourseInstance
from src.services.calendar import format_course_instances_for_calendar
from src.services.database_manipulation import reset_database as reset_db_service

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page route."""
    latest_announcement = Announcement.query.filter_by(
        is_active=True, 
        deleted_at=None
    ).order_by(Announcement.created_at.desc()).first()
    
    return render_template('public/landing/index.html', latest_announcement=latest_announcement)


@main_bp.route('/courses')
def public_courses():
    """Public courses page."""
    courses = CourseInstance.query.filter_by(status='scheduled').all()
    events = format_course_instances_for_calendar(courses)
    
    return render_template('public/courses/index.html', 
                         events_json=json.dumps(events),
                         courses=courses)


@main_bp.route('/signup')
def signup_page():
    """Public signup page with course information."""
    course_id = request.args.get('course')
    course = CourseInstance.query.get(course_id) if course_id else None
    
    return render_template('public/auth/signup.html', course=course)




@main_bp.route('/reset-database')
def reset_database():
    """Reset the database by dropping and recreating all tables."""
    reset_db_service()
    return redirect(url_for('auth.loginReg'))



@main_bp.app_errorhandler(404)
def page_not_found(error):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors."""
    return render_template('errors/500.html'), 500
