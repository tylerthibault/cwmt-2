"""
User Admin Controller - THIN controller following constitutional principles

Admin is a secretary-level role with access to:
- Schedule Management: Create course instances on calendar
- Reports: View and generate reports
- Announcements: Create and manage announcements

Contains ONLY:
- Route definitions
- Request/response handling
- Calls to logic layer

Does NOT contain:
- Business logic (belongs in logic layer)
- Data validation (belongs in logic layer)
- Complex calculations (belongs in logic layer)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from src.models.logbook import Logbook
from src.logic.user_logic import UserLogic
from src.logic.course_logic import CourseLogic
from src.models.courses_model import Course, CourseTemplate

user_admin_bp = Blueprint('user_admin', __name__, url_prefix='/admin')


def admin_required(f):
    """
    Decorator to require admin role for route access.
    Checks session token and verifies user has admin role.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash('Authentication required', 'error')
            return redirect(url_for('auth.login'))
        
        # Find token in logbook
        token = session.get('token')
        logbook_page = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        if not logbook_page or logbook_page.is_timed_out():
            session.pop('token', None)
            flash('Session expired. Please log in again.', 'error')
            return redirect(url_for('auth.login'))
        
        user = logbook_page.user
        if not user or 'admin' not in [role.name for role in user.role_list]:
            flash('Admin access required', 'error')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# SCHEDULE MANAGEMENT ROUTES
# ============================================================================

@user_admin_bp.route('/schedule', methods=['GET'])
@admin_required
def schedule_management():
    """
    Display schedule management dashboard.
    Admin can view and manage course schedules.
    """
    # Get context for admin view
    user_context = UserLogic.get_context(view_as='admin')
    
    # Get all courses and templates for schedule display
    # Logic layer will handle filtering and business rules
    all_courses_raw = Course.get_all()
    all_templates_raw = CourseTemplate.get_all()
    
    # Serialize courses with template information for JavaScript
    all_courses = []
    for course in all_courses_raw:
        course_dict = course.to_dict(include_users=True, include_template=True)
        all_courses.append(course_dict)
    
    # Serialize templates for JavaScript
    all_templates_serialized = []
    for template in all_templates_raw:
        template_dict = template.to_dict()
        all_templates_serialized.append(template_dict)
    
    context = {
        **user_context,
        'all_courses': all_courses,
        'all_templates': all_templates_raw,  # Keep raw objects for Jinja template rendering
        'all_templates_json': all_templates_serialized,  # Serialized for JavaScript
        'page_title': 'Schedule Management'
    }
    
    return render_template('private/admin/schedule_management/index.html', **context)


@user_admin_bp.route('/schedule/create', methods=['GET', 'POST'])
@admin_required
def create_course_instance():
    """
    Create a new course instance on the calendar.
    GET: Display form to create course instance
    POST: Process form submission and create course instance
    """
    if request.method == 'POST':
        # Extract form data
        data = request.form.to_dict()
        
        # Delegate to logic layer for validation and creation
        try:
            course = CourseLogic.create_course_instance(data)
            # Get template name for flash message
            template_name = course.template.name if course.template else "Course"
            flash(f'Course instance "{template_name}" created successfully', 'success')
            return redirect(url_for('user_admin.schedule_management'))
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('user_admin.schedule_management'))
        except Exception as e:
            flash('Failed to create course instance. Please try again.', 'error')
            return redirect(url_for('user_admin.schedule_management'))
    
    # GET request - display form
    user_context = UserLogic.get_context(view_as='admin')
    all_templates = CourseTemplate.get_all()
    
    context = {
        **user_context,
        'all_templates': all_templates,
        'page_title': 'Create Course Instance'
    }
    
    return render_template('private/admin/schedule_management/create.html', **context)


@user_admin_bp.route('/schedule/edit/<int:course_id>', methods=['GET', 'POST'])
@admin_required
def edit_course_instance(course_id):
    """
    Edit an existing course instance.
    GET: Display form to edit course instance
    POST: Process form submission and update course instance
    """
    course = Course.get_by_id(course_id)
    if not course:
        flash('Course instance not found', 'error')
        return redirect(url_for('user_admin.schedule_management'))
    
    if request.method == 'POST':
        # Extract form data
        data = request.form.to_dict()
        
        # Delegate to logic layer for validation and update
        try:
            updated_course = CourseLogic.update_course_instance(course_id, data)
            flash(f'Course instance "{updated_course.template.name}" updated successfully', 'success')
            return redirect(url_for('user_admin.schedule_management'))
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('Failed to update course instance. Please try again.', 'error')
    
    # GET request - display form
    user_context = UserLogic.get_context(view_as='admin')
    all_templates = CourseTemplate.get_all()
    
    context = {
        **user_context,
        'course': course,
        'all_templates': all_templates,
        'page_title': f'Edit Course: {course.template.name}'
    }
    
    return render_template('private/admin/schedule_management/edit.html', **context)


@user_admin_bp.route('/schedule/view/<int:course_id>')
@admin_required
def view_course_instance(course_id):
    """
    View detailed information about a course instance.
    Read-only view with full roster and details.
    """
    course = Course.query.get_or_404(course_id)
    user_context = UserLogic.get_context(view_as='admin')
    
    # Get course data with all relationships
    course_dict = course.to_dict(include_users=True, include_template=True)
    
    context = {
        **user_context,
        'course': course,
        'course_dict': course_dict,
        'page_title': f'View Course: {course.template.name if course.template else "Course Details"}'
    }
    
    return render_template('private/admin/schedule_management/view.html', **context)


@user_admin_bp.route('/schedule/delete/<int:course_id>', methods=['POST'])
@admin_required
def delete_course_instance(course_id):
    """
    Delete a course instance from the schedule.
    POST only for safety.
    """
    try:
        CourseLogic.delete_course_instance(course_id)
        flash('Course instance deleted successfully', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash('Failed to delete course instance. Please try again.', 'error')
    
    return redirect(url_for('user_admin.schedule_management'))


# ============================================================================
# REPORTS ROUTES
# ============================================================================

@user_admin_bp.route('/reports', methods=['GET'])
@admin_required
def reports():
    """
    Display reports dashboard.
    Admin can view various reports about courses, users, etc.
    """
    # Get context for admin view
    user_context = UserLogic.get_context(view_as='admin')
    
    # Get report data from logic layer
    # TODO: Implement report logic in course_logic.py or create report_logic.py
    
    context = {
        **user_context,
        'page_title': 'Reports',
        'reports_available': [
            {'name': 'Course Enrollment', 'description': 'View enrollment statistics'},
            {'name': 'Attendance', 'description': 'Track student attendance'},
            {'name': 'Completion Rates', 'description': 'Course completion statistics'},
        ]
    }
    
    return render_template('private/admin/reports/index.html', **context)


@user_admin_bp.route('/reports/course-enrollment', methods=['GET'])
@admin_required
def course_enrollment_report():
    """
    Display course enrollment report.
    Shows enrollment statistics for all courses.
    """
    user_context = UserLogic.get_context(view_as='admin')
    
    # Get filters from query parameters
    date_from = request.args.get('date_from', None)
    date_to = request.args.get('date_to', None)
    
    # TODO: Implement report generation logic
    # report_data = ReportLogic.generate_enrollment_report(date_from, date_to)
    
    context = {
        **user_context,
        'page_title': 'Course Enrollment Report',
        'date_from': date_from,
        'date_to': date_to,
        # 'report_data': report_data
    }
    
    return render_template('private/admin/reports/enrollment.html', **context)


# ============================================================================
# ANNOUNCEMENTS ROUTES
# ============================================================================

@user_admin_bp.route('/announcements', methods=['GET'])
@admin_required
def announcements():
    """
    Display announcements management dashboard.
    Admin can view, create, edit, and delete announcements.
    """
    user_context = UserLogic.get_context(view_as='admin')
    
    # TODO: Get all announcements from logic layer
    # all_announcements = AnnouncementLogic.get_all_announcements()
    
    context = {
        **user_context,
        'page_title': 'Announcements',
        # 'all_announcements': all_announcements
    }
    
    return render_template('private/admin/announcements/index.html', **context)


@user_admin_bp.route('/announcements/create', methods=['GET', 'POST'])
@admin_required
def create_announcement():
    """
    Create a new announcement.
    GET: Display form to create announcement
    POST: Process form submission and create announcement
    """
    if request.method == 'POST':
        # Extract form data
        data = request.form.to_dict()
        
        # TODO: Delegate to logic layer for validation and creation
        # try:
        #     announcement = AnnouncementLogic.create_announcement(data)
        #     flash(f'Announcement "{announcement.title}" created successfully', 'success')
        #     return redirect(url_for('user_admin.announcements'))
        # except ValueError as e:
        #     flash(str(e), 'error')
        # except Exception as e:
        #     flash('Failed to create announcement. Please try again.', 'error')
        
        flash('Announcement creation not yet implemented', 'warning')
    
    # GET request - display form
    user_context = UserLogic.get_context(view_as='admin')
    
    context = {
        **user_context,
        'page_title': 'Create Announcement'
    }
    
    return render_template('private/admin/announcements/create.html', **context)


@user_admin_bp.route('/announcements/edit/<int:announcement_id>', methods=['GET', 'POST'])
@admin_required
def edit_announcement(announcement_id):
    """
    Edit an existing announcement.
    GET: Display form to edit announcement
    POST: Process form submission and update announcement
    """
    # TODO: Get announcement from logic layer
    # announcement = AnnouncementLogic.get_announcement_by_id(announcement_id)
    # if not announcement:
    #     flash('Announcement not found', 'error')
    #     return redirect(url_for('user_admin.announcements'))
    
    if request.method == 'POST':
        # Extract form data
        data = request.form.to_dict()
        
        # TODO: Delegate to logic layer for validation and update
        # try:
        #     updated_announcement = AnnouncementLogic.update_announcement(announcement_id, data)
        #     flash(f'Announcement "{updated_announcement.title}" updated successfully', 'success')
        #     return redirect(url_for('user_admin.announcements'))
        # except ValueError as e:
        #     flash(str(e), 'error')
        # except Exception as e:
        #     flash('Failed to update announcement. Please try again.', 'error')
        
        flash('Announcement editing not yet implemented', 'warning')
    
    # GET request - display form
    user_context = UserLogic.get_context(view_as='admin')
    
    context = {
        **user_context,
        # 'announcement': announcement,
        'page_title': f'Edit Announcement'
    }
    
    return render_template('private/admin/announcements/edit.html', **context)


@user_admin_bp.route('/announcements/delete/<int:announcement_id>', methods=['POST'])
@admin_required
def delete_announcement(announcement_id):
    """
    Delete an announcement.
    POST only for safety.
    """
    # TODO: Delegate to logic layer for deletion
    # try:
    #     AnnouncementLogic.delete_announcement(announcement_id)
    #     flash('Announcement deleted successfully', 'success')
    # except ValueError as e:
    #     flash(str(e), 'error')
    # except Exception as e:
    #     flash('Failed to delete announcement. Please try again.', 'error')
    
    flash('Announcement deletion not yet implemented', 'warning')
    return redirect(url_for('user_admin.announcements'))
