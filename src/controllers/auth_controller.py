from flask import Blueprint, request, render_template, session, redirect, url_for, flash, current_app
from src.logic.auth_logic import AuthLogic
from src.logic.email_logic import EmailLogic
from functools import wraps
from src.models.logbook import Logbook

# from src import current_app.logger

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def get_user_dashboard_url(user):
    """
    Determine the appropriate dashboard URL based on user's highest role.
    Priority: super-user > admin > instructor > student
    
    Args:
        user: User object with role_list
        
    Returns:
        str: URL for the appropriate dashboard
    """
    role_names = [role.name for role in user.role_list]
    
    if 'superuser' in role_names:
        return url_for('superuser.dashboard')
    elif 'admin' in role_names:
        return url_for('user_admin.dashboard')
    elif 'instructor' in role_names:
        return url_for('instructor.dashboard')
    elif 'student' in role_names:
        return url_for('student.dashboard')
    else:
        # Default to main index if no recognized role
        return url_for('main.index')


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
            current_app.logger.info(f'Session expired or invalid for token: {token[:8]}...')
            session.pop('token', None)
            flash('Session expired. Please log in again.', 'error')
            return redirect(url_for('auth.login'))
        
        user = logbook_page.user
        if not user:
            current_app.logger.warning(f'Logbook entry found but user missing for token: {token[:8]}...')
            flash('Authentication required', 'error')
            return redirect(url_for('auth.login'))
        
        if not user.is_active:
            current_app.logger.warning(f'Deactivated account access attempt by user {user.id} ({user.username})')
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
            current_app.logger.info(f'New user registered successfully: user_id={user_id}, username={data.get("username")}')
            flash('User registered successfully', 'success')
            return redirect(url_for('auth.login'))
    
        current_app.logger.warning(f'Registration failed for username: {data.get("username")}')
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
            current_app.logger.info(f'User logged in successfully: user_id={user.id}, username={user.username}')
            flash('Login successful', 'success')
            # Redirect to appropriate dashboard based on user role
            return redirect(get_user_dashboard_url(user))
        
        current_app.logger.warning(f'Login failed for username: {data.get("username")}')
        flash('Login failed. Please check your credentials and try again.', 'error')

    from src.models.user import User
    all_users = User.query.all()
    context = {
        'all_users': all_users
    }
    return render_template('public/auth/login/index.html', **context)


@auth_bp.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    token = session.get('token')
    if token:
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        if logbook_entry and logbook_entry.user:
            current_app.logger.info(f'User logged out: user_id={logbook_entry.user_id}, username={logbook_entry.user.username}')
        Logbook.sign_out(token)
    session.pop('token', None)
    flash('Logout successful', 'success')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Email is required', 'error')
            return render_template('auth/forgot_password.html')
        
        # Create password reset token
        token_info = AuthLogic.create_password_reset_token(email)
        
        # Always show success message for security (don't reveal if email exists)
        if token_info:
            current_app.logger.info(f'Password reset requested for user: {token_info["user"].username} (email: {email})')
            # Generate reset link
            reset_link = url_for('auth.reset_password', token=token_info['token'], _external=True)
            
            # Send password reset email
            try:
                EmailLogic.send_password_reset_email(
                    user_email=email,
                    user_name=token_info['user'].first_name or token_info['user'].username,
                    reset_link=reset_link,
                    expiry_time="24 hours"
                )
                current_app.logger.info(f'Password reset email sent successfully to {email}')
                flash('Password reset instructions have been sent to your email', 'success')
            except Exception as e:
                # Log error but still show success message for security
                current_app.logger.error(f'Error sending password reset email to {email}: {str(e)}', exc_info=True)
                flash('Password reset instructions have been sent to your email if it exists in our system', 'success')
        else:
            # Show same message even if user doesn't exist (security)
            flash('Password reset instructions have been sent to your email if it exists in our system', 'success')
        
        return redirect(url_for('auth.login'))
    
    return render_template('public/auth/forgot_password/index.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Verify token is valid
    user = AuthLogic.verify_reset_token(token)
    
    if not user:
        current_app.logger.warning(f'Invalid or expired password reset token attempted: {token[:8]}...')
        flash('Invalid or expired password reset link. Please request a new one.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate passwords match
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('public/auth/reset_password/index.html', token=token, user=user)
        
        # Reset password using token
        if AuthLogic.reset_password_with_token(token, new_password):
            current_app.logger.info(f'Password reset successful for user: {user.username}')
            flash('Password reset successful! You can now log in with your new password.', 'success')
            return redirect(url_for('auth.login'))
        else:
            current_app.logger.warning(f'Password reset failed for token: {token}')
            flash('Unable to reset password. Please try again or request a new reset link.', 'error')
            return render_template('public/auth/reset_password/index.html', token=token, user=user)
    
    return render_template('public/auth/reset_password/index.html', token=token, user=user)