from flask import Blueprint, render_template, redirect, url_for, flash
from src.controllers.auth_controller import login_required

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard page"""
    context = {}
    return render_template('private/dashboard/student/index.html', **context)


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