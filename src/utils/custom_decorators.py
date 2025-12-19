from functools import wraps
from flask import session, redirect, url_for, flash, request


def login_required(f):
    """
    Decorator to check if user has a valid doorman_token in session.
    Redirects to login if token is missing or invalid.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if doorman_token exists in session
        if 'doorman_token' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        # Import here to avoid circular imports
        from src.models.doorman import Doorman
        
        # Verify the token exists in database
        doorman = Doorman.get_by_token(session['doorman_token'])
        
        if not doorman:
            # Token not found in database
            session.pop('doorman_token', None)
            flash('Invalid session. Please log in again.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        # Check if session was signed out
        if doorman.sign_out_time:
            session.pop('doorman_token', None)
            flash('Your session has ended. Please log in again.', 'info')
            return redirect(url_for('auth.login', next=request.url))
        
        # Check if last activity is within 10 minutes
        from datetime import datetime, timedelta
        ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
        
        if doorman.last_activity < ten_minutes_ago:
            # Session has expired due to inactivity
            doorman.sign_out()
            session.pop('doorman_token', None)
            flash('Your session has expired due to inactivity. Please log in again.', 'info')
            return redirect(url_for('auth.login', next=request.url))
        
        # Update last activity
        doorman.update_activity()
        
        # All checks passed, proceed with the request
        return f(*args, **kwargs)
    
    return decorated_function


def doorman_optional(f):
    """
    Decorator that checks for doorman_token but doesn't redirect if missing.
    Useful for pages that work differently for logged in vs logged out users.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'doorman_token' in session:
            # Import here to avoid circular imports
            from ..models.doorman import Doorman
            from datetime import datetime, timedelta
            
            doorman = Doorman.get_by_token(session['doorman_token'])
            
            if doorman and not doorman.sign_out_time:
                ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
                if doorman.last_activity >= ten_minutes_ago:
                    # Update last activity for valid sessions
                    doorman.update_activity()
                else:
                    # Session expired, clear it
                    session.pop('doorman_token', None)
            else:
                # Clear invalid session
                session.pop('doorman_token', None)
        
        return f(*args, **kwargs)
    
    return decorated_function


def role_required(*role_names):
    """
    Decorator to check if user has one or more specific roles.
    Must be used with @doorman_required.
    
    Usage:
        @doorman_required
        @role_required('admin', 'superuser')
        def admin_only_route():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'doorman_token' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            # Import here to avoid circular imports
            from ..models.doorman import Doorman
            
            doorman = Doorman.get_by_token(session['doorman_token'])
            
            if not doorman:
                flash('Invalid session.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            user = doorman.user
            
            # Check if user has at least one of the required roles
            has_role = False
            for role_name in role_names:
                if user.has_role_by_name(role_name):
                    has_role = True
                    break
            
            if not has_role:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
