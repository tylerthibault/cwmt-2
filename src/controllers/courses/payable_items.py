"""
Payable Items Controller - THIN controller following constitutional principles

Manages payable item templates, course template attachments, and course items.
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
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from functools import wraps
from decimal import Decimal, InvalidOperation
from src.models.logbook import Logbook
from src.logic.user_logic import UserLogic
from src.logic.payable_item_logic import (
    PayableItemLogic,
    CourseTemplatePayableItemLogic,
    CoursePayableItemLogic,
    PayableItemValidationError,
    PayableItemBusinessError
)
from src.models.payable_item_model import PayableItemTemplate, CourseTemplatePayableItem
from src.models.courses_model import CourseTemplate


payable_items_bp = Blueprint('payables', __name__, url_prefix='/super/payable-items')


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
# PAYABLE ITEM TEMPLATE MANAGEMENT
# ============================================================================

@payable_items_bp.route('/')
@payable_items_bp.route('/payable_items')
@superuser_required
def payable_items():
    """
    Payable items dashboard - main landing page.
    Shows all payable item templates grouped by type.
    """
    user_context = UserLogic.get_context(view_as='superuser')
    
    # Get all payable item templates grouped by type
    all_items = PayableItemLogic.get_all_templates(include_inactive=True)
    
    # Group by type
    items_by_type = {
        'tuition': [],
        'rental': [],
        'equipment': [],
        'misc': []
    }
    
    for item in all_items:
        if item.item_type in items_by_type:
            items_by_type[item.item_type].append(item)
    
    # Get stats
    total_items = len(all_items)
    active_items = len([i for i in all_items if i.is_active])
    
    context = {
        **user_context,
        'items_by_type': items_by_type,
        'total_items': total_items,
        'active_items': active_items,
        'page_title': 'Payable Items Management'
    }
    
    return render_template('private/superuser/payables/index.html', **context)


@payable_items_bp.route('/create', methods=['GET', 'POST'])
@superuser_required
def create_item():
    """
    Create a new payable item template.
    GET: Display form
    POST: Process form submission
    """
    if request.method == 'POST':
        # Extract form data
        data = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'base_price': request.form.get('base_price'),
            'item_type': request.form.get('item_type'),
            'is_taxable': request.form.get('is_taxable') == 'on',
            'is_active': request.form.get('is_active', 'on') == 'on'
        }
        
        try:
            # Logic layer handles validation
            item = PayableItemLogic.create_template(data)
            current_app.logger.info(f'Successfully created payable item: {item.name} (id={item.id}, type={item.item_type})')
            flash(f'Successfully created payable item: {item.name}', 'success')
            return redirect(url_for('payables.payable_items'))
        
        except PayableItemValidationError as e:
            current_app.logger.warning(f'Validation error creating payable item {data.get("name")}: {str(e)}')
            flash('Invalid item information. Please check your input and try again.', 'error')
        except PayableItemBusinessError as e:
            current_app.logger.warning(f'Business error creating payable item {data.get("name")}: {str(e)}')
            flash('Unable to create payable item. Please verify your information.', 'error')
        except Exception as e:
            current_app.logger.error(f'Unexpected error creating payable item {data.get("name")}: {str(e)}', exc_info=True)
            flash('Unable to create payable item. Please try again.', 'error')
    
    # GET request - show form
    user_context = UserLogic.get_context(view_as='superuser')
    
    context = {
        **user_context,
        'item_types': PayableItemLogic.VALID_ITEM_TYPES,
        'page_title': 'Create Payable Item'
    }
    
    return redirect(url_for('payables.payable_items'))
    # return render_template('private/superuser/payables/create.html', **context)


@payable_items_bp.route('/<int:item_id>')
@superuser_required
def view_item(item_id):
    """
    View details of a specific payable item template.
    Shows where it's used (course templates and courses).
    """
    item = PayableItemTemplate.get_by_id(item_id)
    if not item:
        flash('Payable item not found', 'error')
        return redirect(url_for('payables.payable_items'))
    
    user_context = UserLogic.get_context(view_as='superuser')
    
    # Get course templates using this item
    template_attachments = CourseTemplatePayableItem.query.filter_by(
        payable_item_template_id=item_id
    ).all()
    
    # Get course instances using this item (via CoursePayableItem)
    from src.models.payable_item_model import CoursePayableItem
    course_usages = CoursePayableItem.query.filter_by(
        payable_item_template_id=item_id
    ).all()
    
    context = {
        **user_context,
        'item': item,
        'template_attachments': template_attachments,
        'course_usages': course_usages,
        'page_title': f'View: {item.name}'
    }
    
    return render_template('private/superuser/payables/view.html', **context)


@payable_items_bp.route('/<int:item_id>/edit', methods=['GET', 'POST'])
@superuser_required
def edit_item(item_id):
    """
    Edit an existing payable item template.
    GET: Display form with current data
    POST: Process form submission
    """
    item = PayableItemTemplate.get_by_id(item_id)
    if not item:
        flash('Payable item not found', 'error')
        return redirect(url_for('payables.payable_items'))
    
    if request.method == 'POST':
        # Extract form data (only fields provided will be updated)
        data = {}
        
        if request.form.get('name'):
            data['name'] = request.form.get('name')
        if request.form.get('description') is not None:  # Allow empty string
            data['description'] = request.form.get('description')
        if request.form.get('base_price'):
            data['base_price'] = request.form.get('base_price')
        if request.form.get('item_type'):
            data['item_type'] = request.form.get('item_type')
        
        # Checkboxes
        data['is_taxable'] = request.form.get('is_taxable') == 'on'
        data['is_active'] = request.form.get('is_active') == 'on'
        
        try:
            # Logic layer handles validation
            updated_item = PayableItemLogic.update_template(item_id, data)
            current_app.logger.info(f'Successfully updated payable item: {updated_item.name} (id={item_id})')
            flash(f'Successfully updated: {updated_item.name}', 'success')
            return redirect(url_for('payables.view_item', item_id=item_id))
        
        except PayableItemValidationError as e:
            current_app.logger.warning(f'Validation error updating payable item {item_id}: {str(e)}')
            flash('Invalid item information. Please check your input and try again.', 'error')
        except PayableItemBusinessError as e:
            current_app.logger.warning(f'Business error updating payable item {item_id}: {str(e)}')
            flash('Unable to update payable item. Please verify your information.', 'error')
        except Exception as e:
            current_app.logger.error(f'Unexpected error updating payable item {item_id}: {str(e)}', exc_info=True)
            flash('Unable to update payable item. Please try again.', 'error')
    
    # GET request - show form with current data
    user_context = UserLogic.get_context(view_as='superuser')
    
    context = {
        **user_context,
        'item': item,
        'item_types': PayableItemLogic.VALID_ITEM_TYPES,
        'page_title': f'Edit: {item.name}'
    }
    return redirect(url_for('payables.view_item', item_id=item_id))
    # return render_template('private/superuser/payables/edit.html', **context)


@payable_items_bp.route('/<int:item_id>/delete', methods=['POST'])
@superuser_required
def delete_item(item_id):
    """
    Delete a payable item template.
    Logic layer will prevent deletion if item is in use.
    """
    try:
        PayableItemLogic.delete_template(item_id)
        current_app.logger.info(f'Successfully deleted payable item (id={item_id})')
        flash('Successfully deleted payable item', 'success')
    except PayableItemBusinessError as e:
        current_app.logger.warning(f'Cannot delete payable item {item_id}: {str(e)}')
        flash('Unable to delete item. It may be in use by courses.', 'error')
    except Exception as e:
        current_app.logger.error(f'Error deleting payable item {item_id}: {str(e)}', exc_info=True)
        flash('Unable to delete payable item. Please try again.', 'error')
    
    return redirect(url_for('payables.payable_items'))


@payable_items_bp.route('/<int:item_id>/toggle-active', methods=['POST'])
@superuser_required
def toggle_active(item_id):
    """
    Toggle the active status of a payable item.
    Safer alternative to deletion.
    """
    item = PayableItemTemplate.get_by_id(item_id)
    if not item:
        flash('Payable item not found', 'error')
        return redirect(url_for('payables.payable_items'))
    
    try:
        # Toggle active status
        new_status = not item.is_active
        PayableItemLogic.update_template(item_id, {'is_active': new_status})
        
        status_text = 'activated' if new_status else 'deactivated'
        current_app.logger.info(f'Successfully {status_text} payable item: {item.name} (id={item_id})')
        flash(f'Successfully {status_text}: {item.name}', 'success')
    except Exception as e:
        current_app.logger.error(f'Error toggling status for payable item {item_id}: {str(e)}', exc_info=True)
        flash('Unable to update item status. Please try again.', 'error')
    
    return redirect(url_for('payables.view_item', item_id=item_id))


# ============================================================================
# COURSE TEMPLATE ATTACHMENT MANAGEMENT
# ============================================================================

@payable_items_bp.route('/templates')
@superuser_required
def template_management():
    """
    Manage payable items attached to course templates.
    Shows which items are attached to which templates.
    """
    user_context = UserLogic.get_context(view_as='superuser')
    
    # Get all course templates
    all_templates = CourseTemplate.query.order_by(CourseTemplate.name).all()
    
    # For each template, get attached items
    templates_with_items = []
    for template in all_templates:
        items = CourseTemplatePayableItemLogic.get_items_for_template(template.id)
        templates_with_items.append({
            'template': template,
            'items': items,
            'required_count': len([i for i in items if i.is_required]),
            'optional_count': len([i for i in items if not i.is_required])
        })
    
    context = {
        **user_context,
        'templates_with_items': templates_with_items,
        'page_title': 'Course Template Items'
    }
    
    return redirect(url_for('course_management.course_management'))
    # return render_template('private/superuser/payables/templates.html', **context)


@payable_items_bp.route('/templates/<int:template_id>/attach', methods=['GET', 'POST'])
@superuser_required
def attach_to_template(template_id):
    """
    Attach a payable item to a course template.
    GET: Show form with available items
    POST: Process attachment
    """
    template = CourseTemplate.get_by_id(template_id)
    if not template:
        flash('Course template not found', 'error')
        return redirect(url_for('payables.template_management'))
    
    if request.method == 'POST':
        item_id = request.form.get('item_id')
        is_required = request.form.get('is_required') == 'on'
        display_order = request.form.get('display_order', 0)
        
        try:
            CourseTemplatePayableItemLogic.attach_item_to_template(
                course_template_id=template_id,
                payable_item_template_id=int(item_id),
                is_required=is_required,
                display_order=int(display_order)
            )
            current_app.logger.info(f'Successfully attached payable item {item_id} to course template {template_id} (required={is_required})')
            flash('Successfully attached item to course template', 'success')
            return redirect(url_for('payables.template_management'))
        
        except PayableItemValidationError as e:
            current_app.logger.warning(f'Validation error attaching item {item_id} to template {template_id}: {str(e)}')
            flash('Invalid attachment configuration. Please check your input.', 'error')
        except PayableItemBusinessError as e:
            current_app.logger.warning(f'Business error attaching item {item_id} to template {template_id}: {str(e)}')
            flash('Unable to attach item. It may already be attached to this template.', 'error')
        except Exception as e:
            current_app.logger.error(f'Unexpected error attaching item {item_id} to template {template_id}: {str(e)}', exc_info=True)
            flash('Unable to attach item. Please try again.', 'error')
    
    # GET request - show form
    user_context = UserLogic.get_context(view_as='superuser')
    
    # Get available items (active only)
    available_items = PayableItemLogic.get_all_templates(include_inactive=False)
    
    # Get already attached items to exclude from selection
    already_attached = CourseTemplatePayableItemLogic.get_items_for_template(template_id)
    attached_ids = [a.payable_item_template_id for a in already_attached]
    
    available_items = [i for i in available_items if i.id not in attached_ids]
    
    context = {
        **user_context,
        'template': template,
        'available_items': available_items,
        'page_title': f'Attach Item to: {template.name}'
    }
    
    return render_template('private/superuser/payables/attach.html', **context)


@payable_items_bp.route('/templates/<int:template_id>/detach/<int:item_id>', methods=['POST'])
@superuser_required
def detach_from_template(template_id, item_id):
    """
    Remove a payable item from a course template.
    """
    try:
        CourseTemplatePayableItemLogic.detach_item_from_template(
            course_template_id=template_id,
            payable_item_template_id=item_id
        )
        current_app.logger.info(f'Successfully detached payable item {item_id} from course template {template_id}')
        flash('Successfully removed item from course template', 'success')
    except PayableItemBusinessError as e:
        current_app.logger.warning(f'Business error detaching item {item_id} from template {template_id}: {str(e)}')
        flash('Unable to remove item. It may be required by active courses.', 'error')
    except Exception as e:
        current_app.logger.error(f'Unexpected error detaching item {item_id} from template {template_id}: {str(e)}', exc_info=True)
        flash('Unable to remove item. Please try again.', 'error')
    
    return redirect(url_for('payables.template_management'))


@payable_items_bp.route('/templates/attachment/<int:template_id>/<int:item_id>/edit', methods=['POST'])
@superuser_required
def edit_attachment(template_id, item_id):
    """
    Update attachment configuration (is_required, display_order).
    AJAX endpoint for quick updates.
    """
    is_required = request.form.get('is_required') == 'true'
    display_order = request.form.get('display_order')
    
    try:
        update_data = {}
        if is_required is not None:
            update_data['is_required'] = is_required
        if display_order is not None:
            update_data['display_order'] = int(display_order)
        
        CourseTemplatePayableItemLogic.update_attachment(
            course_template_id=template_id,
            payable_item_template_id=item_id,
            **update_data
        )
        current_app.logger.info(f'Successfully updated attachment for item {item_id} on template {template_id}: {update_data}')
        return jsonify({'success': True, 'message': 'Updated successfully'})
    
    except Exception as e:
        current_app.logger.error(f'Error updating attachment for item {item_id} on template {template_id}: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': 'Unable to update attachment. Please try again.'}), 400


# ============================================================================
# API ENDPOINTS (for AJAX/JSON responses)
# ============================================================================

@payable_items_bp.route('/api/items')
@superuser_required
def api_get_items():
    """
    Get all payable items as JSON.
    Useful for AJAX/dynamic forms.
    """
    include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
    item_type = request.args.get('type')
    
    if item_type:
        items = PayableItemLogic.get_templates_by_type(item_type, include_inactive)
    else:
        items = PayableItemLogic.get_all_templates(include_inactive)
    
    items_json = [item.to_dict() for item in items]
    return jsonify({'items': items_json})


@payable_items_bp.route('/api/templates/<int:template_id>/items')
@superuser_required
def api_get_template_items(template_id):
    """
    Get all items attached to a course template as JSON.
    """
    try:
        items = CourseTemplatePayableItemLogic.get_items_for_template(template_id)
        items_json = []
        
        for attachment in items:
            item_data = attachment.payable_item_template.to_dict()
            item_data['is_required'] = attachment.is_required
            item_data['display_order'] = attachment.display_order
            items_json.append(item_data)
        
        return jsonify({'items': items_json})
    except Exception as e:
        current_app.logger.error(f'Error getting items for template {template_id}: {str(e)}', exc_info=True)
        return jsonify({'error': 'Unable to retrieve template items'}), 400
