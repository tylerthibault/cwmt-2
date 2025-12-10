"""
Course Management Controller - THIN controller following constitutional principles

Manages course templates and course instances.
Restricted to superuser access only.

Contains ONLY:
- Route definitions
- Request/response handling
- Calls to logic layer

Does NOT contain:
- Business logic (belongs in logic layer)
- Data validation (belongs in logic layer)
- Complex calculations (belongs in logic layer)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from functools import wraps
from src.models.logbook import Logbook
from src.logic.user_logic import UserLogic
from src.models.courses_model import CourseTemplate
from src.logic.course_logic import CourseTemplateLogic, CourseValidationError, CourseBusinessError

course_management_bp = Blueprint('course_management', __name__, url_prefix='/super/course-management')


def superuser_required(f):
    """
    Decorator to require superuser role for route access.
    Checks session token and verifies user has superuser role.
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
        if not user or 'superuser' not in [role.name for role in user.role_list]:
            flash('Superuser access required', 'error')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# COURSE TEMPLATE MANAGEMENT
# ============================================================================

@course_management_bp.route('/')
@course_management_bp.route('/index')
@superuser_required
def course_management():
    """
    Course management dashboard - main landing page.
    Shows all course templates with their attached payable items.
    """
    from src.models.payable_item_model import PayableItemTemplate, CourseTemplatePayableItem
    from src.logic.payable_item_logic import CourseTemplatePayableItemLogic
    
    user_context = UserLogic.get_context(view_as='superuser')
    
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
    
    return render_template('private/superuser/course_management/index.html', **context)


@course_management_bp.route('/create-template', methods=['POST'])
@superuser_required
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
        'max_students': int(request.form.get('max_students', 12)),
        'experience_level': request.form.get('experience_level'),
        'is_active': True
    }
    
    tuition = request.form.get('tuition')
    
    try:
        template = CourseTemplateLogic.create_template(data)
        
        # If tuition is provided, create and attach tuition payable item
        if tuition and float(tuition) > 0:
            from src.logic.payable_item_logic import PayableItemLogic, CourseTemplatePayableItemLogic
            
            # Create tuition payable item template
            tuition_data = {
                'name': f'{template.name} - Tuition',
                'description': f'Course tuition for {template.name}',
                'base_price': float(tuition),
                'item_type': 'tuition',
                'is_taxable': False,
                'is_active': True
            }
            
            try:
                payable_item = PayableItemLogic.create_template(tuition_data)
                
                # Attach to course template as required
                CourseTemplatePayableItemLogic.attach_item_to_template(
                    course_template_id=template.id,
                    payable_item_template_id=payable_item.id,
                    is_required=True,
                    display_order=0
                )
                current_app.logger.info(f'Successfully created course template: {template.name} (id={template.id}) with tuition item (id={payable_item.id})')
                flash(f'Successfully created course template: {template.name} with tuition item', 'success')
            except Exception as e:
                # Template created but tuition failed - warn but don't fail
                current_app.logger.error(f'Template {template.name} (id={template.id}) created but tuition setup failed: {str(e)}', exc_info=True)
                flash(f'Course template created but tuition setup failed: {str(e)}', 'warning')
        else:
            current_app.logger.info(f'Successfully created course template: {template.name} (id={template.id})')
            flash(f'Successfully created course template: {template.name}', 'success')
            
    except (CourseValidationError, CourseBusinessError) as e:
        current_app.logger.warning(f'Validation/business error creating course template {data.get("name")}: {str(e)}')
        flash('Invalid template information. Please check your input and try again.', 'error')
    except Exception as e:
        current_app.logger.error(f'Unexpected error creating course template {data.get("name")}: {str(e)}', exc_info=True)
        flash('Unable to create course template. Please try again.', 'error')
    
    return redirect(url_for('course_management.course_management'))


@course_management_bp.route('/update-template', methods=['POST'])
@superuser_required
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
        'max_students': int(request.form.get('max_students', 12)),
        'experience_level': request.form.get('experience_level')
    }
    
    try:
        template = CourseTemplateLogic.update_template(int(template_id), data)
        current_app.logger.info(f'Successfully updated course template: {template.name} (id={template_id})')
        flash(f'Successfully updated course template: {template.name}', 'success')
    except (CourseValidationError, CourseBusinessError) as e:
        current_app.logger.warning(f'Validation/business error updating course template {template_id}: {str(e)}')
        flash('Invalid template information. Please check your input and try again.', 'error')
    except Exception as e:
        current_app.logger.error(f'Unexpected error updating course template {template_id}: {str(e)}', exc_info=True)
        flash('Unable to update course template. Please try again.', 'error')
    
    return redirect(url_for('course_management.course_management'))


@course_management_bp.route('/deactivate-template', methods=['POST'])
@superuser_required
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
        current_app.logger.info(f'Successfully deactivated course template: {template.name} (id={template_id})')
        flash(f'Successfully deactivated course template: {template.name}', 'success')
    except CourseBusinessError as e:
        current_app.logger.warning(f'Business error deactivating course template {template_id}: {str(e)}')
        flash('Unable to deactivate template. It may have active courses.', 'error')
    except Exception as e:
        current_app.logger.error(f'Unexpected error deactivating course template {template_id}: {str(e)}', exc_info=True)
        flash('Unable to deactivate course template. Please try again.', 'error')
    
    return redirect(url_for('course_management.course_management'))


@course_management_bp.route('/activate-template', methods=['POST'])
@superuser_required
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
        current_app.logger.info(f'Successfully activated course template: {template.name} (id={template_id})')
        flash(f'Successfully activated course template: {template.name}', 'success')
    except CourseBusinessError as e:
        current_app.logger.warning(f'Business error activating course template {template_id}: {str(e)}')
        flash('Unable to activate template. Please verify the template details.', 'error')
    except Exception as e:
        current_app.logger.error(f'Unexpected error activating course template {template_id}: {str(e)}', exc_info=True)
        flash('Unable to activate course template. Please try again.', 'error')
    
    return redirect(url_for('course_management.course_management'))
