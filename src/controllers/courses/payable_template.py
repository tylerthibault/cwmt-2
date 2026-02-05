"""
Payable template controller for managing course payment items.
"""
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required
from src.services import payable_template_service

payable_temp_bp = Blueprint('payable_temp', __name__, url_prefix='/payable_template')


def _get_current_user():
    """Get current user from session."""
    return Doorman.get_by_token(session['doorman_token']).user


@payable_temp_bp.route('/list')
@login_required
@role_required('superuser')
def list_payable_temps():
    """List all payable templates."""
    templates = payable_template_service.get_all_payable_templates()
    return render_template('private/superusers/payables/index.html',
                         payable_templates=templates,
                         current_user=_get_current_user())


@payable_temp_bp.route('/create', methods=['POST'])
@login_required
@role_required('superuser')
def create_payable_temp():
    """Create a new payable template."""
    try:
        payable_template_service.create_payable_template(
            name=request.form.get('name'),
            amount=request.form.get('amount'),
            description=request.form.get('description'),
            is_required=bool(request.form.get('edit_is_required'))
        )
        flash('Payable template created successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('payable_temp.list_payable_temps'))


@payable_temp_bp.route('/update', methods=['POST'])
@login_required
@role_required('superuser')
def update_payable_temp():
    """Update an existing payable template."""
    try:
        payable_template_service.update_payable_template(
            template_id=request.form.get('template_id'),
            name=request.form.get('name'),
            amount=request.form.get('amount'),
            description=request.form.get('description'),
            is_required=bool(request.form.get('is_required'))
        )
        flash('Payable template updated successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('payable_temp.list_payable_temps'))


@payable_temp_bp.route('/delete', methods=['POST'])
@login_required
@role_required('superuser')
def delete_payable_temp():
    """Delete a payable template."""
    try:
        payable_template_service.delete_payable_template(
            template_id=int(request.form.get('template_id'))
        )
        flash('Payable template deleted successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('payable_temp.list_payable_temps'))
