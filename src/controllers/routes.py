from flask import Blueprint, render_template

# Create blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page route."""
    return render_template('public/landing/index.html')


@main_bp.app_errorhandler(404)
def page_not_found(error):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404


@main_bp.app_errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors."""
    return render_template('errors/500.html'), 500
