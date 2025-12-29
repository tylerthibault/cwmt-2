from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from datetime import datetime
from src.models.user_folder import users
from src.models.course_folder import course_templates, payable_templates
from src.utils.custom_decorators import login_required, role_required
from src.models.doorman import Doorman


# Create blueprint
payable_temp_bp = Blueprint('payable_temp', __name__, url_prefix='/payable_template')

@payable_temp_bp.route('/list')
@login_required
@role_required('superuser')
def list_payable_temps():
    """List all payable templates."""
    templates = payable_templates.PayableTemplate.get_all()
    context = {
        'payable_templates': templates,
        'current_user': Doorman.get_by_token(session['doorman_token']).user
    }
    return render_template('private/superusers/payables/index.html', **context)

@payable_temp_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('superuser')
def create_payable_temp():
    """Create a new payable template."""
    if request.method == 'POST':
        name = request.form.get('name')
        amount = request.form.get('amount')
        description = request.form.get('description')
        
        # Validate inputs
        if not name or not amount:
            flash('Name and amount are required!', 'error')
            return redirect(url_for('payable_temp.list_payable_temps'))
        
        # Create and save the new payable template
        new_template = payable_templates.PayableTemplate(
            name=name,
            amount=float(amount),
            description=description
        )
        new_template.save()
        
        flash('Payable template created successfully!', 'success')
        return redirect(url_for('payable_temp.list_payable_temps'))
    
    return redirect(url_for('payable_temp.list_payable_temps'))

@payable_temp_bp.route('/update', methods=['POST'])
@login_required
@role_required('superuser')
def update_payable_temp():
    """Update an existing payable template."""
    template_id = request.form.get('template_id')
    name = request.form.get('name')
    amount = request.form.get('amount')
    description = request.form.get('description')
    is_required = 1 if request.form.get('is_required') else 0
    
    template = payable_templates.PayableTemplate.query.get(template_id)
    if not template:
        flash('Payable template not found.', 'error')
        return redirect(url_for('payable_temp.list_payable_temps'))
    
    # Update fields
    template.name = name
    template.amount = float(amount)
    template.description = description
    template.is_required = is_required
    template.save()
    
    flash('Payable template updated successfully!', 'success')
    return redirect(url_for('payable_temp.list_payable_temps'))

@payable_temp_bp.route('/delete', methods=['POST'])
@login_required
@role_required('superuser')
def delete_payable_temp():
    template_id = request.form.get('template_id')
    template = payable_templates.PayableTemplate.get_by_id(int(template_id))
    if template:
        template.delete()
        flash('Payable template deleted successfully!', 'success')
    else:
        flash('Payable template not found!', 'error')
    return redirect(url_for('payable_temp.list_payable_temps'))