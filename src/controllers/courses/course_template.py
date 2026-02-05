"""
Course template controller for managing course templates.
"""
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required
from src.services import course_template_service

course_temp_bp = Blueprint('course_temp', __name__)


def _get_current_user():
    """Get current user from session."""
    return Doorman.get_by_token(session['doorman_token']).user


@course_temp_bp.route('/show')
@login_required
@role_required('superuser')
def list_course_temps():
    """List all course templates with associated payables."""
    data = course_template_service.get_all_course_templates_with_payables()
    return render_template('private/superusers/course_templates/index.html',
                         current_user=_get_current_user(),
                         **data)


@course_temp_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('superuser')
def create_course_temp():
    """Create a new course template or update an existing one."""
    if request.method == 'POST':
        template_id = request.form.get('template_id')
        
        try:
            if template_id:
                # Update existing template
                course_template_service.update_course_template(
                    template_id=template_id,
                    name=request.form.get('name'),
                    description=request.form.get('description'),
                    short_blurb=request.form.get('short_blurb'),
                    experience_level=request.form.get('experience_level'),
                    duration_days=request.form.get('duration_days'),
                    max_students=request.form.get('max_students'),
                    tuition=request.form.get('tuition'),
                    color=request.form.get('color', '#0d6efd'),
                    is_featured=request.form.get('is_featured') == 'on',
                    is_taxable=request.form.get('is_taxable') == 'on',
                    current_user_id=_get_current_user().id
                )
                flash('Course template updated successfully!', 'success')
            else:
                # Create new template
                course_template_service.create_course_template(
                    name=request.form.get('name'),
                    description=request.form.get('description'),
                    short_blurb=request.form.get('short_blurb'),
                    experience_level=request.form.get('experience_level'),
                    duration_days=request.form.get('duration_days'),
                    max_students=request.form.get('max_students'),
                    tuition=request.form.get('tuition'),
                    color=request.form.get('color', '#0d6efd'),
                    is_featured=request.form.get('is_featured') == 'on',
                    is_taxable=request.form.get('is_taxable') == 'on',
                    current_user_id=_get_current_user().id
                )
                flash('Course template created successfully with tuition!', 'success')
        except ValueError as e:
            flash(str(e), 'error')
        
        return redirect(url_for('course_temp.list_course_temps'))
    
    return render_template('create_course_temp.html')


@course_temp_bp.route('/add-remove-payable', methods=['POST'])
@login_required
@role_required('superuser')
def add_payable_to_course():
    """Add or remove a payable template from a course template."""
    course_template_id = request.form.get('course_template_id')
    payable_template_id = request.form.get('payable_template_id')
    action = request.form.get('action')
    
    try:
        if action == 'add':
            course_template_service.add_payable_to_course(
                course_template_id, 
                payable_template_id,
                _get_current_user().id
            )
            flash('Payable template added to course template.', 'success')
        elif action == 'remove':
            course_template_service.remove_payable_from_course(
                course_template_id,
                payable_template_id,
                _get_current_user().id
            )
            flash('Payable template removed from course template.', 'success')
        else:
            flash('Invalid action.', 'error')
    except ValueError as e:
        error_msg = str(e)
        if 'already associated' in error_msg or 'not associated' in error_msg:
            flash(error_msg, 'info')
        else:
            flash(error_msg, 'error')
    except Exception as e:
        flash(f'Error processing request: {str(e)}', 'error')
        print(f"Error in add_payable_to_course: {e}")
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('course_temp.list_course_temps'))
