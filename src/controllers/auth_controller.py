from flask import Blueprint, request, render_template, session, redirect, url_for, flash
from src.logic.auth_logic import AuthLogic
from functools import wraps
from src.models.logbook import Logbook

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash('Authentication required', 'error')
            return redirect(url_for('auth.login'))
        # find token in logbook
        
        token = session.get('token')
        logbook_page = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        if not logbook_page or logbook_page.is_timed_out():
            session.pop('token', None)
            flash('Session expired. Please log in again.', 'error')
            return redirect(url_for('auth.login'))
        
        user = logbook_page.user
        if not user:
            flash('Authentication required', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            flash('Account is deactivated. Please contact support.', 'error')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        # Add your user registration logic here
        user_id = AuthLogic.validate_registration(data)
        if user_id:
            # sign the user in (for example, by setting session variables)
            token = Logbook.sign_logbook(user_id)
            session['token'] = token


            flash('User registered successfully', 'success')
            return redirect(url_for('auth.login'))
    
        flash('Registration failed. Please check the errors and try again.', 'error')
    return render_template('public/auth/register/index.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = AuthLogic.validate_login(data)
        if user:
            token = Logbook.sign_logbook(user.id)
            session['token'] = token
            flash('Login successful', 'success')
            return redirect(url_for('user.dashboard'))  # or wherever you want to redirect after login
        
        flash('Login failed. Please check your credentials and try again.', 'error')
    return render_template('public/auth/login/index.html')


@auth_bp.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    token = session.get('token')
    if token:
        Logbook.sign_out(token)
    session.pop('token', None)
    flash('Logout successful', 'success')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        # Add logic to send password reset email
        flash('Password reset instructions sent to your email', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = request.form.get('password')
        # Add logic to verify token and update password
        flash('Password reset successful', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', token=token)