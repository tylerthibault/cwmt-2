from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from src.models.doorman import Doorman
from src.models.flask_mail.email_templates import EmailTemplate
from src.models.flask_mail.email_logs import EmailLog
from src.models.app_settings import AppSettings
from src.services.flask_mail.email_config import EMAIL_PURPOSES, get_purpose
from src.controllers.flask_mail.seed_templates import seed_default_templates

# Create blueprint
mail_bp = Blueprint('mail', __name__, url_prefix='/email')

@mail_bp.route('/')
def management():
    """Render the email management dashboard for admins."""
    
    # Get current user
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    # Get email statistics
    stats = {
        'sent': 0,
        'failed': 0,
        'pending': 0,
        'active_templates': 0
    }
    
    # Get stats from email logs (30 days)
    status_counts = EmailLog.count_by_status(days=30)
    stats['sent'] = status_counts.get('sent', 0)
    stats['failed'] = status_counts.get('failed', 0)
    stats['pending'] = status_counts.get('pending', 0)
    
    # Count active templates
    stats['active_templates'] = EmailTemplate.query.filter_by(is_active=True).count()
    
    # Get recent templates (limit 10)
    templates = EmailTemplate.query.order_by(
        EmailTemplate.is_active.desc(),
        EmailTemplate.updated_at.desc()
    ).limit(10).all()
    
    # Get recent email logs (limit 10) - filter to only email type logs
    recent_logs = EmailLog.get_recent_logs(limit=10, log_type=EmailLog.TYPE_EMAIL)
    
    # Get mail configuration status
    settings = AppSettings.get_settings()
    mail_configured, missing_fields = settings.test_mail_config()
    
    context = {
        'current_user': current_user,
        'stats': stats,
        'templates': templates,
        'recent_logs': recent_logs,
        'mail_configured': mail_configured,
        'mail_server': settings.mail_server,
        'mail_port': settings.mail_port
    }
    
    return render_template('private/flask_mail/management.html', **context)


@mail_bp.route('/create', methods=['GET'])
def create_template_form():
    """Render the create email template form."""
    
    # Get current user
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    context = {
        'current_user': current_user,
        'purposes': EMAIL_PURPOSES
    }
    
    return render_template('private/flask_mail/form.html', **context)


@mail_bp.route('/edit/<int:template_id>', methods=['GET'])
def edit_template_form(template_id):
    """Render the edit email template form."""
    
    # Get current user
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    # Get the template
    template = EmailTemplate.query.get_or_404(template_id)
    
    # Get purpose config
    purpose_config = get_purpose(template.purpose)
    
    context = {
        'current_user': current_user,
        'template': template,
        'purposes': EMAIL_PURPOSES,
        'purpose_config': purpose_config
    }
    
    return render_template('private/flask_mail/form.html', **context)


@mail_bp.route('/seed-defaults', methods=['POST'])
def seed_defaults():
    """Seed default email templates into the database."""
    
    # Get current user
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    # Only allow admins/superusers
    if not (current_user.is_admin or current_user.is_superuser):
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('mail.management'))
    
    try:
        created_count = seed_default_templates()
        flash(f'Successfully created {created_count} default email templates!', 'success')
    except Exception as e:
        flash(f'Error seeding templates: {str(e)}', 'danger')
    
    return redirect(url_for('mail.management'))


@mail_bp.route('/create', methods=['POST'])
def create_template():
    """Create a new email template."""
    
    # Get current user
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    try:
        # Get form data
        purpose = request.form.get('purpose')
        name = request.form.get('name')
        subject_template = request.form.get('subject_template')
        body_html_template = request.form.get('body_html_template')
        body_text_template = request.form.get('body_text_template')
        
        # Validate required fields
        if not all([purpose, name, subject_template, body_html_template, body_text_template]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('mail.create_template_form'))
        
        # Validate purpose exists
        if purpose not in EMAIL_PURPOSES:
            flash('Invalid email purpose selected.', 'danger')
            return redirect(url_for('mail.create_template_form'))
        
        # Create template
        template = EmailTemplate(
            purpose=purpose,
            name=name,
            subject_template=subject_template,
            body_html_template=body_html_template,
            body_text_template=body_text_template,
            is_active=False,  # Start as inactive
            is_default=False,
            created_by=current_user.id
        )
        
        # Validate Jinja2 syntax
        is_valid, errors = template.validate_jinja2_syntax()
        if not is_valid:
            flash(f'Template validation failed: {"; ".join(errors)}', 'danger')
            return redirect(url_for('mail.create_template_form'))
        
        template.save()
        flash(f'Email template "{name}" created successfully!', 'success')
        return redirect(url_for('mail.edit_template_form', template_id=template.id))
        
    except Exception as e:
        flash(f'Error creating template: {str(e)}', 'danger')
        return redirect(url_for('mail.create_template_form'))


@mail_bp.route('/edit/<int:template_id>', methods=['POST'])
def update_template(template_id):
    """Update an existing email template."""
    
    # Get current user
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    # Get the template
    template = EmailTemplate.query.get_or_404(template_id)
    
    try:
        # Get form data
        name = request.form.get('name')
        subject_template = request.form.get('subject_template')
        body_html_template = request.form.get('body_html_template')
        body_text_template = request.form.get('body_text_template')
        
        # Validate required fields
        if not all([name, subject_template, body_html_template, body_text_template]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('mail.edit_template_form', template_id=template_id))
        
        # Update template
        template.name = name
        template.subject_template = subject_template
        template.body_html_template = body_html_template
        template.body_text_template = body_text_template
        
        # Validate Jinja2 syntax
        is_valid, errors = template.validate_jinja2_syntax()
        if not is_valid:
            flash(f'Template validation failed: {"; ".join(errors)}', 'danger')
            return redirect(url_for('mail.edit_template_form', template_id=template_id))
        
        template.save()
        flash(f'Template "{name}" updated successfully!', 'success')
        return redirect(url_for('mail.edit_template_form', template_id=template_id))
        
    except Exception as e:
        flash(f'Error updating template: {str(e)}', 'danger')
        return redirect(url_for('mail.edit_template_form', template_id=template_id))


@mail_bp.route('/activate/<int:template_id>', methods=['GET', 'POST'])
def activate_template(template_id):
    """Activate an email template."""
    
    # Get current user
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    # Get the template
    template = EmailTemplate.query.get_or_404(template_id)
    
    try:
        template.activate()
        flash(f'Template "{template.name}" is now active for {template.purpose}!', 'success')
    except Exception as e:
        flash(f'Error activating template: {str(e)}', 'danger')
    
    return redirect(url_for('mail.edit_template_form', template_id=template_id))


@mail_bp.route('/deactivate/<int:template_id>', methods=['GET', 'POST'])
def deactivate_template(template_id):
    """Deactivate an email template."""
    
    # Get current user
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    # Get the template
    template = EmailTemplate.query.get_or_404(template_id)
    
    try:
        template.is_active = False
        template.save()
        flash(f'Template "{template.name}" has been deactivated.', 'success')
    except Exception as e:
        flash(f'Error deactivating template: {str(e)}', 'danger')
    
    return redirect(url_for('mail.edit_template_form', template_id=template_id))


@mail_bp.route('/delete/<int:template_id>', methods=['POST'])
def delete_template(template_id):
    """Delete an email template."""
    
    # Get current user
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    # Get the template
    template = EmailTemplate.query.get_or_404(template_id)
    
    # Prevent deleting default templates
    if template.is_default:
        flash('Cannot delete default templates.', 'danger')
        return redirect(url_for('mail.edit_template_form', template_id=template_id))
    
    # Prevent deleting active templates
    if template.is_active:
        flash('Cannot delete active templates. Deactivate it first.', 'danger')
        return redirect(url_for('mail.edit_template_form', template_id=template_id))
    
    try:
        template_name = template.name
        template.delete()
        flash(f'Template "{template_name}" has been deleted.', 'success')
        return redirect(url_for('mail.management'))
    except Exception as e:
        flash(f'Error deleting template: {str(e)}', 'danger')
        return redirect(url_for('mail.edit_template_form', template_id=template_id))


@mail_bp.route('/preview/<int:template_id>', methods=['GET'])
def preview_template(template_id):
    """Render a preview of the email template with example data."""
    
    # Get current user
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    # Get the template
    template = EmailTemplate.query.get_or_404(template_id)
    
    # Get purpose config
    purpose_config = get_purpose(template.purpose)
    
    if not purpose_config:
        flash('Invalid email purpose for this template.', 'danger')
        return redirect(url_for('mail.edit_template_form', template_id=template_id))
    
    # Get example data from purpose config
    example_data = purpose_config.get_example_data()
    
    try:
        # Render email content
        from src.services.flask_mail.email_service import generate_email
        email_content = generate_email(template.purpose, **example_data)
        
        context = {
            'current_user': current_user,
            'template': template,
            'email_content': email_content,
            'example_data': example_data
        }
        
        return render_template('private/flask_mail/preview.html', **context)
        
    except Exception as e:
        flash(f'Error generating preview: {str(e)}', 'danger')
        return redirect(url_for('mail.edit_template_form', template_id=template_id))


@mail_bp.route('/send-test/<int:template_id>', methods=['POST'])
def send_test_email(template_id):
    """Send a test email using the template with custom variable values."""
    
    # Get current user
    current_user = Doorman.get_by_token(session['doorman_token']).user
    
    # Get the template
    template = EmailTemplate.query.get_or_404(template_id)
    
    # Get recipient email
    to_address = request.form.get('to_address')
    
    if not to_address:
        flash('Recipient email address is required.', 'danger')
        return redirect(url_for('mail.preview_template', template_id=template_id))
    
    # Extract variable values from form (they're prefixed with 'var_')
    test_data = {}
    for key, value in request.form.items():
        if key.startswith('var_'):
            var_name = key[4:]  # Remove 'var_' prefix
            test_data[var_name] = value
    
    try:
        # Import send_email function
        from src.services.flask_mail.email_service import send_email
        
        # Send the test email
        success = send_email(template.purpose, to_address, **test_data)
        
        if success:
            flash(f'✓ Test email sent successfully to {to_address}!', 'success')
        else:
            flash(f'Failed to send test email to {to_address}. Check email logs for details.', 'danger')
            
    except Exception as e:
        flash(f'Error sending test email: {str(e)}', 'danger')
    
    return redirect(url_for('mail.preview_template', template_id=template_id))


