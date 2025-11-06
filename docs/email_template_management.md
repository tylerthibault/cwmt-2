# Email Template Management System

## Overview

The email template management system allows admin users to create, edit, and manage email templates for automated system emails. Templates can be assigned to predefined email actions (like password reset, welcome email, etc.) that are triggered by the application code.

## Features

- **Email Templates**: Admin-created email templates with HTML and plain text versions
- **Email Actions**: Predefined system actions that can trigger emails
- **Template Assignment**: Assign templates to actions through the admin interface
- **Template Variables**: Dynamic content using placeholder variables
- **Preview**: Preview templates with sample data before deploying

## Architecture

### Models

1. **EmailTemplate** (`src/models/email_template_model.py`)
   - Stores email template details (name, subject, body_html, body_text, description)
   - Can be assigned to multiple email actions
   - Supports active/inactive status

2. **EmailAction** (`src/models/email_action_model.py`)
   - Predefined actions created via seed data
   - Cannot be created by admins (only assigned templates)
   - Includes metadata about available variables for each action

### Logic Layer

**EmailTemplateLogic** (`src/logic/email_template_logic.py`)
- CRUD operations for email templates
- Assign/unassign templates to actions
- Retrieve templates for specific actions (for use in code)
- Render templates with variable substitution

### Controller

**user_admin_controller.py**
Routes available under `/admin/email-templates`:
- `GET /admin/email-templates` - List all templates and actions
- `GET /admin/email-templates/create` - Create new template form
- `POST /admin/email-templates/create` - Submit new template
- `GET /admin/email-templates/<id>/edit` - Edit template form
- `POST /admin/email-templates/<id>/edit` - Submit template updates
- `POST /admin/email-templates/<id>/delete` - Delete template
- `POST /admin/email-templates/actions/<id>/assign` - Assign template to action
- `GET /admin/email-templates/<id>/preview` - Preview template with sample data

## Usage

### For Admins (Web Interface)

1. **Navigate to Email Templates**
   - Log in as an admin user
   - Go to `/admin/email-templates`

2. **Create a Template**
   - Click "Create Template" button
   - Fill in template details:
     - Name (internal reference)
     - Subject (supports variables like `{user_name}`)
     - Plain Text Body (required)
     - HTML Body (optional, for rich formatting)
     - Description (admin notes)
   - Click "Create Template"

3. **Assign Template to Action**
   - In the Email Actions table, click "Assign Template"
   - Select a template from the dropdown
   - Click "Assign Template"

4. **Preview Template**
   - Click the eye icon next to a template
   - View how it renders with sample data
   - Check HTML and plain text versions

5. **Edit Template**
   - Click the pencil icon next to a template
   - Make changes
   - Click "Update Template"

### For Developers (Code)

#### Using Templates in Code

```python
from src.logic.email_template_logic import EmailTemplateLogic

# Get template for a specific action
template = EmailTemplateLogic.get_template_for_action('password_reset')

if template:
    # Render template with actual variables
    variables = {
        'user_name': user.name,
        'user_email': user.email,
        'reset_link': f'https://example.com/reset/{token}',
        'expiry_time': '1 hour',
        'app_name': 'CWMT'
    }
    
    rendered = EmailTemplateLogic.render_template(template, variables)
    
    # Send email using Flask-Mail
    from flask_mail import Message, Mail
    
    msg = Message(
        subject=rendered['subject'],
        recipients=[user.email],
        body=rendered['body_text'],
        html=rendered['body_html']
    )
    
    mail.send(msg)
else:
    # Fallback if no template assigned
    # Use hardcoded email or skip
    pass
```

#### Available Email Actions

The following actions are seeded by default:

- `password_reset` - Password reset emails
- `welcome_email` - New user welcome
- `account_verification` - Email verification
- `password_changed` - Password change confirmation
- `course_enrollment` - Course enrollment confirmation
- `course_completion` - Course completion certificate
- `course_reminder` - Upcoming course reminder
- `assignment_due` - Assignment deadline reminder
- `grade_posted` - Grade notification
- `announcement` - System announcements
- `account_locked` - Account lock notification
- `role_assignment` - Role assignment notification

## Template Variables

Templates support variable substitution using Python's `str.format()` syntax:
- Use `{variable_name}` in subject and body text
- Variables are replaced at render time
- Each action defines its available variables (see action's `available_variables` field)

### Common Variables

- `{user_name}` - User's full name
- `{user_email}` - User's email address
- `{app_name}` - Application name

### Action-Specific Variables

Check each action's "Available Variables" in the admin interface to see what's available.

Example for `password_reset`:
- `{reset_link}` - Password reset URL
- `{expiry_time}` - How long link is valid

## Database Setup

1. **Run Migrations**
   ```bash
   # Models are auto-created via init_db()
   # Or manually create tables if needed
   ```

2. **Seed Email Actions**
   ```bash
   python seeds/run_seeds.py --email-actions
   ```

3. **Seed All Data (includes email actions)**
   ```bash
   python seeds/run_seeds.py --all
   ```

## Best Practices

1. **Always provide plain text version**
   - Some email clients don't support HTML
   - Plain text is required, HTML is optional

2. **Test templates before assigning**
   - Use the preview feature
   - Check both HTML and plain text versions

3. **Use descriptive names**
   - Template names should clearly indicate their purpose
   - Add descriptions for other admins

4. **Handle missing templates gracefully**
   - Always check if template exists before rendering
   - Provide fallback behavior in code

5. **Keep templates simple**
   - Avoid complex HTML that might break in email clients
   - Test in multiple email clients if possible

## Security Considerations

- Templates are stored in database, not code
- Only admin users can create/modify templates
- Template variables are substituted using safe `str.format()`
- No eval() or exec() - just string substitution
- HTML content should be sanitized if user-generated

## Future Enhancements

Potential improvements:
- Template versioning
- Template preview with custom test data
- Template testing (send test email)
- Template categories/tags
- Template cloning
- Rich text editor for HTML body
- Email sending logs/history
- A/B testing support
