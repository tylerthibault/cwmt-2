"""
Course Management Controller - THIN controller following constitutional principles

Manages course templates and course instances.
Restricted to super-user access only.

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
from src.models.courses_model import CourseTemplate
from src.logic.course_logic import CourseTemplateLogic, CourseValidationError, CourseBusinessError

course_management_bp = Blueprint('course_management', __name__, url_prefix='/super/course-management')


def super_user_required(f):
    """
    Decorator to require super-user role for route access.
    Checks session token and verifies user has super-user role.
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
        if not user or 'super-user' not in [role.name for role in user.role_list]:
            flash('Super-user access required', 'error')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# COURSE TEMPLATE MANAGEMENT
# ============================================================================

@course_management_bp.route('/')
@course_management_bp.route('/index')
@super_user_required
def course_management():
    """
    Course management dashboard - main landing page.
    Shows all course templates with their attached payable items.
    """
    from src.models.payable_item_model import PayableItemTemplate, CourseTemplatePayableItem
    from src.logic.payable_item_logic import CourseTemplatePayableItemLogic
    
    user_context = UserLogic.get_context(view_as='super-user')
    
    # Get all course templates
    all_templates = CourseTemplate.query.all()
    
    # Get all available payable items
    all_payable_items = PayableItemTemplate.query.filter_by(is_active=True).order_by(PayableItemTemplate.name).all()
    
    # Get attached items for each template
    template_items = {}
    for template in all_templates:
        template_items[template.id] = CourseTemplatePayableItemLogic.get_items_for_template(template.id)
    
    context = {
        **user_context,
        'all_courses': all_templates,
        'all_payable_items': all_payable_items,
        'template_items': template_items,
        'page_title': 'Course Management'
    }
    
    return render_template('private/super_user/course_management/index.html', **context)


@course_management_bp.route('/create-template', methods=['POST'])
@super_user_required
def create_course_template():
    """
    Create a new course template.
    POST: Process form submission
    """
    # Get form data
    data = {
        'name': request.form.get('name'),
        'description': request.form.get('description', ''),
        'duration_days': int(request.form.get('duration_days', 1)),
        'experience_level': request.form.get('experience_level'),
        'is_active': True
    }
    
    try:
        template = CourseTemplateLogic.create_template(data)
        flash(f'Successfully created course template: {template.name}', 'success')
    except (CourseValidationError, CourseBusinessError) as e:
        flash(f'Error creating template: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    return redirect(url_for('course_management.course_management'))


@course_management_bp.route('/update-template', methods=['POST'])
@super_user_required
def update_course_template():
    """
    Update an existing course template.
    POST: Process form submission
    """
    template_id = request.form.get('template_id')
    
    if not template_id:
        flash('Missing template ID', 'error')
        return redirect(url_for('course_management.course_management'))
    
    # Get form data
    data = {
        'name': request.form.get('name'),
        'description': request.form.get('description', ''),
        'duration_days': int(request.form.get('duration_days', 1)),
        'experience_level': request.form.get('experience_level')
    }
    
    try:
        template = CourseTemplateLogic.update_template(int(template_id), data)
        flash(f'Successfully updated course template: {template.name}', 'success')
    except (CourseValidationError, CourseBusinessError) as e:
        flash(f'Error updating template: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    return redirect(url_for('course_management.course_management'))


@course_management_bp.route('/deactivate-template', methods=['POST'])
@super_user_required
def deactivate_course_template():
    """
    Deactivate a course template.
    Safer alternative to deletion.
    """
    template_id = request.form.get('template_id')
    
    if not template_id:
        flash('Missing template ID', 'error')
        return redirect(url_for('course_management.course_management'))
    
    try:
        template = CourseTemplateLogic.deactivate_template(int(template_id))
        flash(f'Successfully deactivated course template: {template.name}', 'success')
    except CourseBusinessError as e:
        flash(f'Error deactivating template: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    return redirect(url_for('course_management.course_management'))


@course_management_bp.route('/activate-template', methods=['POST'])
@super_user_required
def activate_course_template():
    """
    Activate a course template.
    """
    template_id = request.form.get('template_id')
    
    if not template_id:
        flash('Missing template ID', 'error')
        return redirect(url_for('course_management.course_management'))
    
    try:
        template = CourseTemplateLogic.get_template(int(template_id))
        template.is_active = True
        from src.models import db
        db.session.commit()
        flash(f'Successfully activated course template: {template.name}', 'success')
    except CourseBusinessError as e:
        flash(f'Error activating template: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    return redirect(url_for('course_management.course_management'))
