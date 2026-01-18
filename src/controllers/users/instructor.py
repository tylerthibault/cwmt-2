"""
Instructor controller for instructor-specific operations.

NOTE: Instructor privilege management (add/remove instructor status) has been moved to admin.py
This controller focuses on instructor dashboard and instructor-specific views.
"""
from flask import Blueprint, render_template, redirect, url_for, session, jsonify
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required
from src.services.calendar import format_course_instances_for_calendar
from src.services import instructor_service
import json

instructor_bp = Blueprint('instructor', __name__, url_prefix='/instructor')


def _get_current_user():
    """Helper to get current user from session."""
    return Doorman.get_by_token(session['doorman_token']).user

@instructor_bp.route('/dashboard')
@login_required
@role_required('instructor')
def dashboard():
    """Instructor dashboard with course calendar and overview."""
    current_user = _get_current_user()
    dashboard_data = instructor_service.get_instructor_dashboard_data(current_user)
    
    events = format_course_instances_for_calendar(dashboard_data['course_instances'])
    
    context = {
        'current_user': current_user,
        'current_instructor_id': dashboard_data['current_instructor_id'],
        'course_instances': dashboard_data['course_instances'],
        'instructors': dashboard_data['instructors'],
        'events_json': json.dumps(events),
        'role': 'instructor'
    }
    return render_template('private/instructors/dashboard/index.html', **context)
