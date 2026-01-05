from flask import Blueprint, render_template, flash, redirect, url_for
import json
import os
from pathlib import Path
from src.models.course_folder import course_instances
from src.services.calendar import format_course_instances_for_calendar

# Create blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page route."""
    from src.models.announcements import Announcement
    
    # Get the latest active announcement
    latest_announcement = Announcement.query.filter_by(
        is_active=True, 
        deleted_at=None
    ).order_by(Announcement.created_at.desc()).first()
    
    context = {
        'latest_announcement': latest_announcement
    }
    return render_template('public/landing/index.html', **context)


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


@main_bp.route('/reset-database')
def reset_database():
    """Reset the database by dropping and recreating all tables."""
    try:
        from src.models.main import db
        
        instance_path = Path('instance')
        seed_flag_path = instance_path / '.seeded'
        
        # Drop all tables
        db.drop_all()
        flash('All database tables dropped.', 'success')
        
        # Recreate all tables
        db.create_all()
        flash('Database tables recreated.', 'success')
        
        # Delete seed flag to trigger reseeding
        if seed_flag_path.exists():
            os.remove(seed_flag_path)
            flash('Seed flag deleted - data will be reseeded on next page load.', 'success')
        
        flash('✅ Database reset complete! Refresh the page to see the empty database.', 'success')
        
    except Exception as e:
        flash(f'Error resetting database: {str(e)}', 'danger')
    
    return redirect(url_for('auth.loginReg'))


@main_bp.app_errorhandler(404)
def page_not_found(error):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors."""
    return render_template('errors/500.html'), 500
