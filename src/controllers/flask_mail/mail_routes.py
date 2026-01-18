"""
Email template management controller.
"""
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from src.models.doorman import Doorman
from src.services.flask_mail.email_config import EMAIL_PURPOSES, get_purpose
from src.services.flask_mail import email_template_service
from src.controllers.flask_mail.seed_templates import seed_default_templates
from src.utils.custom_decorators import login_required, role_required

mail_bp = Blueprint('mail', __name__, url_prefix='/email')


def _get_current_user():
    """Get current user from session."""
    return Doorman.get_by_token(session['doorman_token']).user


@mail_bp.route('/')
@login_required
@role_required('admin')
def management():
    """Render the email management dashboard for admins."""
    dashboard_data = email_template_service.get_management_dashboard_data()
    
    return render_template('private/flask_mail/management.html',
                         current_user=_get_current_user(),
                         stats=dashboard_data['stats'],
                         templates=dashboard_data['templates'],
                         recent_logs=dashboard_data['recent_logs'],
                         mail_configured=dashboard_data['mail_configured'],
                         mail_server=dashboard_data['mail_server'],
                         mail_port=dashboard_data['mail_port'])


@mail_bp.route('/create', methods=['GET'])
@login_required
@role_required('admin')
def create_template_form():
    """Render the create email template form."""
    return render_template('private/flask_mail/form.html',
                         current_user=_get_current_user(),
                         purposes=EMAIL_PURPOSES)


@mail_bp.route('/edit/<int:template_id>', methods=['GET'])
@login_required
@role_required('admin')
def edit_template_form(template_id):
    """Render the edit email template form."""
    template = email_template_service.get_email_template_by_id(template_id)
    if not template:
        flash('Template not found.', 'error')
        return redirect(url_for('mail.management'))
    
    purpose_config = get_purpose(template.purpose)
    
    return render_template('private/flask_mail/form.html',
                         current_user=_get_current_user(),
                         template=template,
                         purposes=EMAIL_PURPOSES,
                         purpose_config=purpose_config)


@mail_bp.route('/seed-defaults', methods=['POST'])
@login_required
@role_required('admin')
def seed_defaults():
    """Seed default email templates into the database."""
    try:
        created_count = seed_default_templates()
        flash(f'Successfully created {created_count} default email templates!', 'success')
    except Exception as e:
        flash(f'Error seeding templates: {str(e)}', 'error')
    
    return redirect(url_for('mail.management'))


@mail_bp.route('/create', methods=['POST'])
@login_required
@role_required('admin')
def create_template():
    """Create a new email template."""
    try:
        template = email_template_service.create_email_template(
            purpose=request.form.get('purpose'),
            name=request.form.get('name'),
            subject_template=request.form.get('subject_template'),
            body_html_template=request.form.get('body_html_template'),
            body_text_template=request.form.get('body_text_template'),
            current_user_id=_get_current_user().id
        )
        
        flash(f'Email template "{template.name}" created successfully!', 'success')
        return redirect(url_for('mail.edit_template_form', template_id=template.id))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('mail.create_template_form'))
    except Exception as e:
        flash(f'Error creating template: {str(e)}', 'error')
        return redirect(url_for('mail.create_template_form'))


@mail_bp.route('/edit/<int:template_id>', methods=['POST'])
@login_required
@role_required('admin')
def update_template(template_id):
    """Update an existing email template."""
    try:
        template = email_template_service.update_email_template(
            template_id=template_id,
            name=request.form.get('name'),
            subject_template=request.form.get('subject_template'),
            body_html_template=request.form.get('body_html_template'),
            body_text_template=request.form.get('body_text_template')
        )
        
        flash(f'Template "{template.name}" updated successfully!', 'success')
        return redirect(url_for('mail.edit_template_form', template_id=template_id))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('mail.edit_template_form', template_id=template_id))
    except Exception as e:
        flash(f'Error updating template: {str(e)}', 'error')
        return redirect(url_for('mail.edit_template_form', template_id=template_id))


@mail_bp.route('/activate/<int:template_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def activate_template(template_id):
    """Activate an email template."""
    try:
        template = email_template_service.activate_email_template(template_id)
        flash(f'Template "{template.name}" is now active for {template.purpose}!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error activating template: {str(e)}', 'error')
    
    return redirect(url_for('mail.edit_template_form', template_id=template_id))


@mail_bp.route('/deactivate/<int:template_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def deactivate_template(template_id):
    """Deactivate an email template."""
    try:
        template = email_template_service.deactivate_email_template(template_id)
        flash(f'Template "{template.name}" has been deactivated.', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error deactivating template: {str(e)}', 'error')
    
    return redirect(url_for('mail.edit_template_form', template_id=template_id))


@mail_bp.route('/delete/<int:template_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_template(template_id):
    """Delete an email template."""
    try:
        template_name = email_template_service.delete_email_template(template_id)
        flash(f'Template "{template_name}" has been deleted.', 'success')
        return redirect(url_for('mail.management'))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('mail.edit_template_form', template_id=template_id))
    except Exception as e:
        flash(f'Error deleting template: {str(e)}', 'error')
        return redirect(url_for('mail.edit_template_form', template_id=template_id))


@mail_bp.route('/preview/<int:template_id>', methods=['GET'])
@login_required
@role_required('admin')
def preview_template(template_id):
    """Render a preview of the email template with example data."""
    try:
        preview_data = email_template_service.generate_template_preview(template_id)
        
        return render_template('private/flask_mail/preview.html',
                             current_user=_get_current_user(),
                             template=preview_data['template'],
                             email_content=preview_data['email_content'],
                             example_data=preview_data['example_data'])
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('mail.edit_template_form', template_id=template_id))
    except Exception as e:
        flash(f'Error generating preview: {str(e)}', 'error')
        return redirect(url_for('mail.edit_template_form', template_id=template_id))


@mail_bp.route('/send-test/<int:template_id>', methods=['POST'])
@login_required
@role_required('admin')
def send_test_email(template_id):
    """Send a test email using the template with custom variable values."""
    to_address = request.form.get('to_address')
    
    # Extract variable values from form (they're prefixed with 'var_')
    test_data = {}
    for key, value in request.form.items():
        if key.startswith('var_'):
            var_name = key[4:]  # Remove 'var_' prefix
            test_data[var_name] = value
    
    try:
        email_template_service.send_template_test_email(template_id, to_address, test_data)
        flash(f'✓ Test email sent successfully to {to_address}!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error sending test email: {str(e)}', 'error')
    
    return redirect(url_for('mail.preview_template', template_id=template_id))
