from flask import Blueprint, jsonify, current_app as app, render_template, redirect, url_for, flash

# Create a blueprint for main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Example route showing logger usage"""
    app.looger.info("Index route accessed", route="/", method="GET")
    
    return render_template('public/landing/index.html')

@main_bp.route('/about')
def about():
    """About page route"""
    app.looger.info("About route accessed", route="/about", method="GET")
    
    return render_template('public/about.html')

@main_bp.route('/contact')
def contact():
    """Contact page route"""
    app.looger.info("Contact route accessed", route="/contact", method="GET")
    
    return render_template('public/contact.html')
