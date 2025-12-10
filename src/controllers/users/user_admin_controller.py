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
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
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
# DASHBOARD ROUTE
# ============================================================================

@user_admin_bp.route('/')
@user_admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """
    Admin dashboard - main landing page for admin users.
    Shows quick stats and recent activity.
    """
    # Get context for admin view
    user_context = UserLogic.get_context(view_as='admin')
    
    # Get quick stats
    from datetime import date, timedelta
    today = date.today()
    week_from_now = today + timedelta(days=7)
    
    upcoming_courses = Course.query.filter(
        Course.course_date >= today,
        Course.course_date <= week_from_now,
        Course.status == 'scheduled'
    ).count()
    
    total_templates = CourseTemplate.query.filter_by(is_active=True).count()
    total_courses = Course.query.filter_by(status='scheduled').count()
    
    context = {
        **user_context,
        'upcoming_courses': upcoming_courses,
        'total_templates': total_templates,
        'total_courses': total_courses,
        'page_title': 'Admin Dashboard'
    }
    
    return render_template('private/admin/dashboard/index.html', **context)


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
        course_dict = course.to_dict(include_enrollments=True, include_template=True)
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
            current_app.logger.warning(f'Validation error creating course instance: {str(e)}')
            flash('Invalid course information. Please check your input and try again.', 'error')
            return redirect(url_for('user_admin.schedule_management'))
        except Exception as e:
            current_app.logger.error(f'Error creating course instance: {str(e)}', exc_info=True)
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
            current_app.logger.warning(f'Validation error updating course instance {course_id}: {str(e)}')
            flash('Invalid course information. Please check your input and try again.', 'error')
        except Exception as e:
            current_app.logger.error(f'Error updating course instance {course_id}: {str(e)}', exc_info=True)
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
    course_dict = course.to_dict(include_enrollments=True, include_template=True)
    
    # Get all payments for this course's enrollments
    from src.models.payment_models import Payment
    enrollment_ids = [e.id for e in course.enrollments if e.status not in ['withdrawn', 'cancelled']]
    payments = Payment.query.filter(
        Payment.enrollment_id.in_(enrollment_ids)
    ).order_by(Payment.payment_date.desc()).all() if enrollment_ids else []
    
    context = {
        **user_context,
        'course': course,
        'course_dict': course_dict,
        'payments': payments,
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
        current_app.logger.warning(f'Validation error deleting course instance {course_id}: {str(e)}')
        flash('Unable to delete course. This course may have active enrollments.', 'error')
    except Exception as e:
        current_app.logger.error(f'Error deleting course instance {course_id}: {str(e)}', exc_info=True)
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


# ============================================================================
# STUDENT MANAGEMENT ROUTES
# ============================================================================

@user_admin_bp.route('/students')
@admin_required
def students_list():
    """
    Display list of all students.
    Admin can view all students and access their details.
    """
    from src.models.student_profile import StudentProfile
    from src.models.user import User
    
    user_context = UserLogic.get_context(view_as='admin')
    
    # Get all student profiles with user information
    students = StudentProfile.query.join(User).order_by(User.last_name, User.first_name).all()
    
    context = {
        **user_context,
        'students': students,
        'page_title': 'Student Management'
    }
    
    return render_template('private/admin/students/list.html', **context)


@user_admin_bp.route('/students/<int:student_id>')
@admin_required
def student_detail(student_id):
    """
    Display detailed information about a student.
    Shows profile, enrollments, scores, and vehicle info.
    
    Args:
        student_id: StudentProfile ID (not User ID)
    """
    from src.logic.student_logic import StudentLogic
    from src.models.student_profile import StudentProfile
    
    user_context = UserLogic.get_context(view_as='admin')
    
    # Get student profile
    student = StudentProfile.query.get_or_404(student_id)
    
    # Get all enrollments for this student
    enrollments = StudentLogic.get_student_courses(student_id)
    
    # Calculate GPA
    gpa = StudentLogic.calculate_student_gpa(student_id)
    
    context = {
        **user_context,
        'student': student,
        'enrollments': enrollments,
        'gpa': gpa,
        'page_title': f'Student: {student.user.first_name} {student.user.last_name}'
    }
    
    return render_template('private/admin/students/detail.html', **context)


@user_admin_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_student(student_id):
    """
    Edit student profile information.
    
    Args:
        student_id: StudentProfile ID (not User ID)
    """
    from src.logic.student_logic import StudentLogic
    from src.models.student_profile import StudentProfile
    
    student = StudentProfile.query.get_or_404(student_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            update_data = {
                'student_number': request.form.get('student_number'),
                'grade_level': request.form.get('grade_level'),
                'emergency_contact_name': request.form.get('emergency_contact_name'),
                'emergency_contact_phone': request.form.get('emergency_contact_phone')
            }
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            # Update student profile
            StudentLogic.update_student_profile(student_id, update_data)
            
            flash('Student profile updated successfully', 'success')
            return redirect(url_for('user_admin.student_detail', student_id=student_id))
            
        except ValueError as e:
            current_app.logger.warning(f'Validation error updating student profile {student_id}: {str(e)}')
            flash('Invalid student information. Please check your input and try again.', 'error')
        except Exception as e:
            current_app.logger.error(f'Error updating student profile {student_id}: {str(e)}', exc_info=True)
            flash('Failed to update student profile. Please try again.', 'error')
    
    # GET request - display form
    user_context = UserLogic.get_context(view_as='admin')
    
    context = {
        **user_context,
        'student': student,
        'page_title': f'Edit Student: {student.user.first_name} {student.user.last_name}'
    }
    
    return render_template('private/admin/students/edit.html', **context)


@user_admin_bp.route('/api/students/<int:student_id>/enrollment/<int:enrollment_id>', methods=['PUT'])
@admin_required
def update_enrollment(student_id, enrollment_id):
    """
    Update enrollment details via AJAX.
    
    Args:
        student_id: StudentProfile ID
        enrollment_id: CourseEnrollment ID
    """
    from src.logic.student_logic import StudentLogic
    import json
    
    try:
        data = request.get_json()
        
        # Update enrollment
        enrollment = StudentLogic.update_enrollment(enrollment_id, data)
        
        return json.dumps({
            'success': True,
            'message': 'Enrollment updated successfully',
            'enrollment': enrollment.to_dict()
        }), 200
        
    except ValueError as e:
        current_app.logger.warning(f'Validation error updating enrollment {enrollment_id}: {str(e)}')
        return json.dumps({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f'Error updating enrollment {enrollment_id}: {str(e)}', exc_info=True)
        return json.dumps({
            'success': False,
            'message': 'Failed to update enrollment. Please try again.'
        }), 500


@user_admin_bp.route('/api/students/<int:student_id>/enrollment/<int:enrollment_id>/score', methods=['PUT'])
@admin_required
def update_enrollment_score(student_id, enrollment_id):
    """
    Update course score for an enrollment via AJAX.
    
    Args:
        student_id: StudentProfile ID
        enrollment_id: CourseEnrollment ID
    """
    from src.logic.student_logic import StudentLogic
    import json
    
    try:
        data = request.get_json()
        score = float(data.get('score', 0))
        
        # Update score
        enrollment = StudentLogic.update_course_score(enrollment_id, score)
        
        # Get updated student profile for overall score
        student = StudentLogic.get_student_profile_by_id(student_id)
        
        return json.dumps({
            'success': True,
            'message': 'Score updated successfully',
            'course_score': enrollment.course_score,
            'overall_score': student.overall_score
        }), 200
        
    except ValueError as e:
        current_app.logger.warning(f'Validation error updating score for enrollment {enrollment_id}: {str(e)}')
        return json.dumps({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f'Error updating score for enrollment {enrollment_id}: {str(e)}', exc_info=True)
        return json.dumps({
            'success': False,
            'message': 'Failed to update score. Please try again.'
        }), 500


@user_admin_bp.route('/api/students/<int:student_id>/enrollment/<int:enrollment_id>/complete', methods=['POST'])
@admin_required
def complete_enrollment(student_id, enrollment_id):
    """
    Mark enrollment as completed via AJAX.
    
    Args:
        student_id: StudentProfile ID
        enrollment_id: CourseEnrollment ID
    """
    from src.logic.student_logic import StudentLogic
    import json
    
    try:
        data = request.get_json()
        final_score = data.get('final_score')
        
        if final_score is not None:
            final_score = float(final_score)
        
        # Complete course
        enrollment = StudentLogic.complete_course(enrollment_id, final_score)
        
        return json.dumps({
            'success': True,
            'message': 'Course marked as completed',
            'enrollment': enrollment.to_dict()
        }), 200
        
    except ValueError as e:
        current_app.logger.warning(f'Validation error completing enrollment {enrollment_id}: {str(e)}')
        return json.dumps({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f'Error completing enrollment {enrollment_id}: {str(e)}', exc_info=True)
        return json.dumps({
            'success': False,
            'message': 'Failed to complete course. Please try again.'
        }), 500


# ============================================================================
# EMAIL TEMPLATE MANAGEMENT ROUTES
# ============================================================================

@user_admin_bp.route('/email-templates', methods=['GET'])
@admin_required
def email_templates():
    """
    Display email template management dashboard.
    Admin can view, create, edit, and assign email templates.
    """
    from src.logic.email_template_logic import EmailTemplateLogic
    
    # Get context for admin view
    user_context = UserLogic.get_context(view_as='admin')
    
    # Get all templates and actions
    templates = EmailTemplateLogic.get_all_templates(include_inactive=True)
    actions = EmailTemplateLogic.get_all_actions()
    
    context = {
        **user_context,
        'templates': templates,
        'actions': actions,
        'page_title': 'Email Template Management'
    }
    
    return render_template('private/admin/email_templates/index.html', **context)


@user_admin_bp.route('/email-templates/create', methods=['GET', 'POST'])
@admin_required
def create_email_template():
    """
    Create new email template.
    """
    from src.logic.email_template_logic import EmailTemplateLogic
    
    if request.method == 'POST':
        try:
            # Extract form data
            data = {
                'name': request.form.get('name'),
                'subject': request.form.get('subject'),
                'body_text': request.form.get('body_text'),
                'body_html': request.form.get('body_html', ''),
                'body_mjml': request.form.get('body_mjml', ''),
                'description': request.form.get('description', ''),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            # Create template via logic layer
            template = EmailTemplateLogic.create_template(data)
            
            flash(f'Email template "{template.name}" created successfully', 'success')
            return redirect(url_for('user_admin.email_templates'))
            
        except ValueError as e:
            current_app.logger.warning(f'Validation error creating email template: {str(e)}')
            flash('Invalid template information. Please check all required fields.', 'error')
        except Exception as e:
            current_app.logger.error(f'Error creating email template: {str(e)}', exc_info=True)
            flash('Failed to create template. Please try again.', 'error')
    
    # GET request - show form
    user_context = UserLogic.get_context(view_as='admin')
    actions = EmailTemplateLogic.get_all_actions()
    
    context = {
        **user_context,
        'actions': actions,
        'page_title': 'Create Email Template'
    }
    
    return render_template('private/admin/email_templates/form.html', **context)


@user_admin_bp.route('/email-templates/<int:template_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_email_template(template_id):
    """
    Edit existing email template.
    """
    from src.logic.email_template_logic import EmailTemplateLogic
    
    template = EmailTemplateLogic.get_template_by_id(template_id)
    if not template:
        flash('Template not found', 'error')
        return redirect(url_for('user_admin.email_templates'))
    
    if request.method == 'POST':
        try:
            # Extract form data
            data = {
                'name': request.form.get('name'),
                'subject': request.form.get('subject'),
                'body_text': request.form.get('body_text'),
                'body_html': request.form.get('body_html', ''),
                'body_mjml': request.form.get('body_mjml', ''),
                'description': request.form.get('description', ''),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            # Update template via logic layer
            template = EmailTemplateLogic.update_template(template_id, data)
            
            flash(f'Email template "{template.name}" updated successfully', 'success')
            return redirect(url_for('user_admin.email_templates'))
            
        except ValueError as e:
            current_app.logger.warning(f'Validation error updating email template {template_id}: {str(e)}')
            flash('Invalid template information. Please check all required fields.', 'error')
        except Exception as e:
            current_app.logger.error(f'Error updating email template {template_id}: {str(e)}', exc_info=True)
            flash('Failed to update template. Please try again.', 'error')
    
    # GET request - show form
    user_context = UserLogic.get_context(view_as='admin')
    actions = EmailTemplateLogic.get_all_actions()
    
    context = {
        **user_context,
        'template': template,
        'actions': actions,
        'page_title': f'Edit Email Template: {template.name}'
    }
    
    return render_template('private/admin/email_templates/form.html', **context)


@user_admin_bp.route('/email-templates/<int:template_id>/delete', methods=['POST'])
@admin_required
def delete_email_template(template_id):
    """
    Delete (deactivate) email template.
    """
    from src.logic.email_template_logic import EmailTemplateLogic
    
    try:
        EmailTemplateLogic.delete_template(template_id)
        flash('Email template deleted successfully', 'success')
    except ValueError as e:
        current_app.logger.warning(f'Validation error deleting email template {template_id}: {str(e)}')
        flash('Unable to delete template. This template may be in use.', 'error')
    except Exception as e:
        current_app.logger.error(f'Error deleting email template {template_id}: {str(e)}', exc_info=True)
        flash('Failed to delete template. Please try again.', 'error')
    
    return redirect(url_for('user_admin.email_templates'))


@user_admin_bp.route('/email-templates/actions/<int:action_id>/assign', methods=['POST'])
@admin_required
def assign_template_to_action(action_id):
    """
    Assign a template to an email action.
    """
    from src.logic.email_template_logic import EmailTemplateLogic
    
    try:
        template_id = request.form.get('template_id')
        if template_id:
            template_id = int(template_id)
        else:
            template_id = None
        
        action = EmailTemplateLogic.assign_template_to_action(action_id, template_id)
        
        if template_id:
            flash(f'Template assigned to action "{action.name}" successfully', 'success')
        else:
            flash(f'Template unassigned from action "{action.name}"', 'success')
            
    except ValueError as e:
        current_app.logger.warning(f'Validation error assigning template to action {action_id}: {str(e)}')
        flash('Invalid template or action. Please verify your selection.', 'error')
    except Exception as e:
        current_app.logger.error(f'Error assigning template to action {action_id}: {str(e)}', exc_info=True)
        flash('Failed to assign template. Please try again.', 'error')
    
    return redirect(url_for('user_admin.email_templates'))


@user_admin_bp.route('/email-templates/<int:template_id>/preview', methods=['GET'])
@admin_required
def preview_email_template(template_id):
    """
    Preview email template with sample variables.
    """
    from src.logic.email_template_logic import EmailTemplateLogic
    
    template = EmailTemplateLogic.get_template_by_id(template_id)
    if not template:
        flash('Template not found', 'error')
        return redirect(url_for('user_admin.email_templates'))
    
    # Get sample variables from query string or use defaults
    sample_vars = {
        'user_name': request.args.get('user_name', 'John Doe'),
        'user_email': request.args.get('user_email', 'john.doe@example.com'),
        'reset_link': request.args.get('reset_link', 'https://example.com/reset/abc123'),
        'expiry_time': request.args.get('expiry_time', '1 hour'),
        'course_name': request.args.get('course_name', 'Sample Course'),
        'app_name': request.args.get('app_name', 'CWMT'),
    }
    
    try:
        # Render template with sample variables
        rendered = EmailTemplateLogic.render_template(template, sample_vars)
        
        user_context = UserLogic.get_context(view_as='admin')
        
        context = {
            **user_context,
            'template': template,
            'rendered': rendered,
            'sample_vars': sample_vars,
            'page_title': f'Preview: {template.name}'
        }
        
        return render_template('private/admin/email_templates/preview.html', **context)
        
    except ValueError as e:
        current_app.logger.warning(f'Template preview error for template {template_id}: {str(e)}')
        flash('Unable to preview template. Please check template syntax.', 'error')
        return redirect(url_for('user_admin.email_templates'))


@user_admin_bp.route('/email-templates/convert-mjml', methods=['POST'])
@admin_required
def convert_mjml_to_html():
    """
    Convert MJML markup to HTML.
    AJAX endpoint for the template editor.
    """
    from flask import jsonify
    from src.utils.mjml_service import MJMLService
    
    data = request.get_json()
    mjml_content = data.get('mjml', '')
    
    if not mjml_content:
        return jsonify({
            'success': False,
            'error': 'No MJML content provided'
        }), 400
    
    # Convert MJML to HTML
    result = MJMLService.mjml_to_html(mjml_content)
    
    if result['success']:
        return jsonify({
            'success': True,
            'html': result['html']
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Unknown error')
        }), 400


# ============================================================================
# PAYMENT MANAGEMENT ROUTES
# ============================================================================

@user_admin_bp.route('/payment/line-item/<int:line_item_id>/override', methods=['POST'])
@admin_required
def override_payment_status(line_item_id):
    """
    Allow admin to manually override payment status of a line item.
    POST only for safety.
    """
    from src.logic.payment_logic import PaymentLogic, PaymentValidationError
    from flask import jsonify
    
    # Get current admin user
    token = session.get('token')
    logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
    admin_user_id = logbook_entry.user_id
    
    data = request.form.to_dict()
    new_status = data.get('status')
    remarks = data.get('remarks', '').strip()
    
    try:
        PaymentLogic.admin_override_line_item_status(
            line_item_id=line_item_id,
            new_status=new_status,
            admin_user_id=admin_user_id,
            remarks=remarks
        )
        
        flash(f'Payment status updated to "{new_status}" successfully', 'success')
        
        # Redirect back to referrer or course view
        return redirect(request.referrer or url_for('user_admin.schedule_management'))
        
    except PaymentValidationError as e:
        current_app.logger.warning(f'Payment validation error overriding line item {line_item_id} status: {str(e)}')
        flash('Invalid payment status change. Please verify the payment details.', 'error')
        return redirect(request.referrer or url_for('user_admin.schedule_management'))
    except Exception as e:
        current_app.logger.error(f'Error overriding payment status for line item {line_item_id}: {str(e)}', exc_info=True)
        flash('Unable to update payment status. Please try again.', 'error')
        return redirect(request.referrer or url_for('user_admin.schedule_management'))


@user_admin_bp.route('/course/<int:course_id>/sync-stripe-payments', methods=['POST'])
@admin_required
def sync_stripe_payments(course_id):
    """
    Manually sync all Stripe payments by checking their status with Stripe.
    Checks for payment success, failures, cancellations, and disputes.
    Useful when webhooks are not running or payments were missed.
    """
    import stripe
    import os
    from decimal import Decimal
    from datetime import datetime
    from src.models.payment_models import Payment
    from src.logic.payment_logic import PaymentLogic
    from src.models import db
    
    try:
        # Get course and validate
        course = Course.query.get_or_404(course_id)
        
        # Get current user
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        
        if not logbook_entry or not logbook_entry.user_id:
            return jsonify({'success': False, 'message': 'Session expired'}), 401
        
        # Initialize Stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        
        # Get all Stripe payments for this course (not just pending)
        enrollment_ids = [e.id for e in course.enrollments if e.status not in ['withdrawn', 'cancelled']]
        stripe_payments = Payment.query.filter(
            Payment.enrollment_id.in_(enrollment_ids),
            Payment.stripe_payment_intent_id.isnot(None)
        ).all() if enrollment_ids else []
        
        checked_count = 0
        updated_count = 0
        errors = []
        
        for payment in stripe_payments:
            checked_count += 1
            
            try:
                # Retrieve payment intent from Stripe
                intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
                
                # Get the charge if it exists
                charge = None
                charge_id = None
                if hasattr(intent, 'charges') and intent.charges and hasattr(intent.charges, 'data') and intent.charges.data:
                    charge_id = intent.charges.data[0].id
                    charge = stripe.Charge.retrieve(charge_id)
                
                # Check payment intent status
                if intent.status == 'succeeded' and payment.status != 'completed':
                    # Extract metadata
                    metadata = intent.metadata
                    line_item_ids = metadata.get('line_item_ids', '').split(',')
                    
                    if line_item_ids and line_item_ids[0]:
                        # Record/update the payment
                        PaymentLogic.record_payment(
                            enrollment_id=payment.enrollment_id,
                            line_item_ids=[int(id) for id in line_item_ids if id],
                            amount=Decimal(intent.amount) / 100,
                            payment_method='stripe',
                            processed_by_user_id=logbook_entry.user_id,
                            stripe_payment_intent_id=intent.id,
                            stripe_charge_id=charge_id,
                            notes='Manually synced from Stripe by admin'
                        )
                        updated_count += 1
                        
                elif intent.status == 'canceled' and payment.status not in ['failed', 'canceled']:
                    # Mark as failed
                    payment.status = 'failed'
                    payment.notes = (payment.notes or '') + '\nPayment was canceled in Stripe'
                    db.session.commit()
                    updated_count += 1
                    
                elif intent.status in ['requires_payment_method', 'requires_action'] and payment.status == 'completed':
                    # Payment was marked completed but actually requires action
                    payment.status = 'pending'
                    payment.notes = (payment.notes or '') + f'\nReverted to pending - Stripe status: {intent.status}'
                    db.session.commit()
                    updated_count += 1
                
                # Check for disputes on the charge
                if charge and hasattr(charge, 'disputed') and charge.disputed and payment.status != 'disputed':
                    # Payment has been disputed
                    payment.status = 'disputed'
                    dispute_info = f'\n[DISPUTE DETECTED] Synced at {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} - Payment is under dispute'
                    payment.notes = (payment.notes or '') + dispute_info
                    db.session.commit()
                    updated_count += 1
                    
                # Check if dispute was resolved
                if charge and hasattr(charge, 'disputed') and not charge.disputed and payment.status == 'disputed':
                    # Dispute was resolved - check outcome
                    if intent.status == 'succeeded':
                        payment.status = 'completed'
                        payment.notes = (payment.notes or '') + f'\n[DISPUTE RESOLVED] Won - Payment restored'
                    else:
                        payment.status = 'failed'
                        payment.notes = (payment.notes or '') + f'\n[DISPUTE RESOLVED] Lost - Payment failed'
                    db.session.commit()
                    updated_count += 1
                    
            except stripe.error.StripeError as e:
                errors.append(f"Payment {payment.id}: {str(e)}")
            except Exception as e:
                errors.append(f"Payment {payment.id}: {str(e)}")
        
        message = f"Sync completed. "
        if updated_count > 0:
            message += f"{updated_count} payment(s) updated. "
        else:
            message += "No payments needed updating. "
        
        if errors:
            message += f"\n\nErrors: {'; '.join(errors[:3])}"
            if len(errors) > 3:
                message += f"... and {len(errors) - 3} more"
        
        return jsonify({
            'success': True,
            'checked': checked_count,
            'updated': updated_count,
            'message': message
        })
        
    except Exception as e:
        current_app.logger.error(f'Error syncing Stripe payments for course {course_id}: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Unable to sync payments. Please try again.'
        }), 500
