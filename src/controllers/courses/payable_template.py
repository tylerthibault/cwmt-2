from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from datetime import datetime
from src.models.user_folder import users
from src.models.course_folder import course_templates
from src.utils.custom_decorators import login_required, role_required
from src.models.doorman import Doorman

# Create blueprint
payable_temp_bp = Blueprint('payable_temp', __name__)

@payable_temp_bp.route('/list')
@login_required
@role_required('superuser')
def list_payable_temps():
    """List all payable templates."""
    # templates = course_templates.PayableTemplate.query.all()
    context = {
        # 'payable_templates': templates,
        'current_user': Doorman.get_by_token(session['doorman_token']).user
    }
    return render_template('private/superusers/payables/index.html', **context)