from flask import Blueprint, render_template, redirect, url_for, flash, request
from src.controllers.auth_controller import login_required
from src.logic.user_logic import UserLogic

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard page"""
    view_as = request.args.get('view_as', None)  # Get 'view_as' parameter from query string if needed
    context = UserLogic.get_context(view_as=view_as)
    if not context:
        flash("Unable to load dashboard context.", "error")
        return redirect(url_for('main.index'))
    return render_template(context.get('dashboard_template', 'private/dashboard/student/index.html'), **context)


@user_bp.route('/settings')
@login_required
def settings():
    """User settings page"""
    context = {}
    return render_template('user/settings.html', **context)

@user_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    context = {}
    return render_template('user/profile.html', **context)