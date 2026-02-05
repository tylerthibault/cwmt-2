"""
Calendar controller for displaying course instances in calendar views.
Provides role-based calendar views with formatted event data.
"""
import json
from flask import Blueprint, render_template, session
from src.models.doorman import Doorman
from src.models.course_folder.course_instances import CourseInstance
from src.models.course_folder.course_templates import CourseTemplate
from src.models.user_folder.instructors import Instructor
from src.models.locations import Location
from src.utils.custom_decorators import login_required, role_required, doorman_optional

calendar_bp = Blueprint('calendar', __name__, url_prefix='/calendar')


def _get_current_user():
    """Get current user from session if logged in."""
    token = session.get('doorman_token')
    if token:
        doorman = Doorman.get_by_token(token)
        return doorman.user if doorman else None
    return None


def _format_events_for_calendar(instances):
    """
    Format course instances into calendar event objects.
    
    Args:
        instances: List of CourseInstance objects
        
    Returns:
        List of event dictionaries with calendar-ready data
    """
    events = []
    
    for instance in instances:
        # Get template for name and color
        template = instance.course_template
        if not template:
            continue
            
        # Get instructor names
        c1_name = instance.c1_instructor.user.get_full_name() if instance.c1_instructor else None
        c2_name = instance.c2_instructor.user.get_full_name() if instance.c2_instructor else None
        
        instructor_text = None
        if c1_name and c2_name:
            instructor_text = f"{c1_name} & {c2_name}"
        elif c1_name:
            instructor_text = c1_name
        elif c2_name:
            instructor_text = c2_name
        
        # Get enrollment count
        enrollment_count = len([e for e in instance.enrollments if e.status == 'enrolled'])
        
        # Build event object
        event = {
            'id': instance.id,
            'title': template.name,
            'start': instance.start_date.isoformat(),
            'startTime': instance.start_time.strftime('%H:%M') if instance.start_time else None,
            'duration': instance.duration_days,
            'location': instance.location,
            'color': template.color or '#0d6efd',
            'maxStudents': instance.max_students,
            'enrollmentCount': enrollment_count,
            'status': instance.status,
            'instructorC1Id': instance.c1_instructor_id,
            'instructorC2Id': instance.c2_instructor_id,
            'instructorText': instructor_text,
            'experienceLevel': template.experience_level,
            'templateId': template.id,
            'description': template.description or '',
            'shortBlurb': template.short_blurb or ''
        }
        
        events.append(event)
    
    return events


# =============== PUBLIC ROUTES ===============

@calendar_bp.route('/public')
@doorman_optional
def public_calendar():
    """Public calendar view showing all scheduled courses."""
    instances = CourseInstance.query.filter_by(status='scheduled').all()
    events = _format_events_for_calendar(instances)
    
    current_user = _get_current_user()
    
    return render_template('public/calendar.html',
                         events_json=json.dumps(events),
                         current_user=current_user,
                         role='public')


# =============== STUDENT ROUTES ===============

@calendar_bp.route('/student')
@login_required
@role_required('student')
def student_calendar():
    """Student calendar view with enrollment features."""
    instances = CourseInstance.query.filter_by(status='scheduled').all()
    events = _format_events_for_calendar(instances)
    
    current_user = _get_current_user()
    
    # Get student's enrollments for highlighting
    student = current_user.student if hasattr(current_user, 'student') else None
    enrolled_course_ids = []
    if student:
        enrolled_course_ids = [e.course_instance_id for e in student.enrollments if e.status == 'enrolled']
    
    return render_template('private/students/calendar.html',
                         events_json=json.dumps(events),
                         enrolled_course_ids=json.dumps(enrolled_course_ids),
                         current_user=current_user,
                         role='student')


# =============== INSTRUCTOR ROUTES ===============

@calendar_bp.route('/instructor')
@login_required
@role_required('instructor')
def instructor_calendar():
    """Instructor calendar view with signup features."""
    instances = CourseInstance.query.filter_by(status='scheduled').all()
    events = _format_events_for_calendar(instances)
    
    current_user = _get_current_user()
    instructor = Instructor.query.filter_by(user_id=current_user.id).first()
    
    return render_template('private/instructors/calendar.html',
                         events_json=json.dumps(events),
                         current_user=current_user,
                         current_instructor_id=instructor.id if instructor else None,
                         instructors=Instructor.get_all(),
                         role='instructor')


# =============== ADMIN ROUTES ===============

@calendar_bp.route('/admin')
@login_required
@role_required('admin')
def admin_calendar():
    """Admin calendar view with full management features."""
    instances = CourseInstance.get_all()
    events = _format_events_for_calendar(instances)
    
    current_user = _get_current_user()
    
    # Serialize locations for JavaScript
    locations = Location.get_active_locations()
    locations_json = [{'id': loc.id, 'name': loc.name, 'location': loc.location, 'tax_rate': float(loc.tax_rate) if loc.tax_rate else 0.0} for loc in locations]
    
    return render_template('private/admins/calendar.html',
                         events_json=json.dumps(events),
                         current_user=current_user,
                         course_templates=CourseTemplate.get_all(),
                         instructors=Instructor.get_all(),
                         locations=locations_json,
                         role='admin')
