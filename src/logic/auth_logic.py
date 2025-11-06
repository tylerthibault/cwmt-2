from flask import flash, current_app as app
from src.models.user import User
from src.models.roles import Role, UserHasRoles
from src.models.password_reset_token import PasswordResetToken
from src.models import db
from datetime import datetime, timedelta
import secrets


class AuthLogic:

    @staticmethod
    def validate_registration(data):
        # validate username, email, password, confirm_password
        is_valid = True

        if not data.get('username'):
            flash('Username is required', 'user_register_username_error')
            is_valid = False
        if not data.get('email'):
            flash('Email is required', 'user_register_email_error')
            is_valid = False
        if not data.get('password') or len(data.get('password')) < 6:
            flash('Password must be at least 6 characters', 'user_register_password_error')
            is_valid = False
        if data.get('password') != data.get('confirm_password'):
            flash('Passwords do not match', 'user_register_confirm_password_error')
            is_valid = False

        if is_valid:
            # check to see if email or username already exists in the database
            if User.query.filter_by(email=data.get('email')).first():
                flash('Email already registered', 'user_register_email_error')
                is_valid = False
            if User.query.filter_by(username=data.get('username')).first():
                flash('Username already registered', 'user_register_username_error')
                is_valid = False
            
        if is_valid:
            # create the user
            user = User.create(
                username=data.get('username'),
                email=data.get('email'),
                password_hash=AuthLogic.generate_password_hash(data.get('password')),
                first_name=data.get('first_name'),
                last_name=data.get('last_name')
            )
            # link the new user to a role of student
            role = Role.query.filter_by(name='student').first()
            UserHasRoles.assign_role(user.id, role.id)
            
            # Create student profile for the new student
            from src.logic.student_logic import StudentLogic
            try:
                StudentLogic.create_student_profile(user.id)
            except Exception as e:
                flash(f'Warning: Student profile creation failed: {str(e)}', 'warning')

            flash('Registration successful! Please log in.', 'success')
            return user.id

        return is_valid
    
    @staticmethod
    def validate_login(data):
        # validate email and password
        if not data.get('email') or not data.get('password'):
            flash('Email and password are required', 'user_login_error')
            return None
        
        user = User.query.filter_by(email=data.get('email')).first()
        if not user or not AuthLogic.check_password_hash(user.password_hash, data.get('password')):
            flash('Invalid email or password', 'user_login_error')
            return None
        
        return user
    
    @staticmethod
    def generate_password_hash(password):
        return app.bcrypt.generate_password_hash(password).decode('utf-8')
    
    @staticmethod
    def check_password_hash(password_hash, password):
        return app.bcrypt.check_password_hash(password_hash, password)
    
    @staticmethod
    def create_password_reset_token(email):
        """
        Create a password reset token for the given email.
        
        Args:
            email (str): User's email address
            
        Returns:
            dict: Token information with token string and expiry, or None if user not found
            
        Business Logic:
        - Validates user exists and is active
        - Generates secure random token
        - Sets 24-hour expiration
        - Invalidates any existing unused tokens for this user
        """
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Don't reveal if email exists or not for security
            app.looger.warning(f"Password reset requested for non-existent email: {email}")
            return None
        
        if not user.is_active:
            app.looger.warning(f"Password reset requested for inactive user: {email}")
            return None
        
        # Invalidate any existing unused tokens for this user
        existing_tokens = PasswordResetToken.query.filter_by(
            user_id=user.id,
            is_used=False
        ).all()
        
        for token in existing_tokens:
            token.is_used = True
            token.updated_at = datetime.utcnow()
        
        # Generate secure random token
        token_string = secrets.token_urlsafe(32)
        
        # Set expiration to 24 hours from now
        expiry_time = datetime.utcnow() + timedelta(hours=24)
        
        # Create new token record
        reset_token = PasswordResetToken(
            token=token_string,
            email=email,
            user_id=user.id,
            expires_at=expiry_time
        )
        
        db.session.add(reset_token)
        db.session.commit()
        
        app.looger.info(f"Password reset token created for user: {email}")
        
        return {
            'token': token_string,
            'expires_at': expiry_time,
            'user': user
        }
    
    @staticmethod
    def verify_reset_token(token):
        """
        Verify a password reset token is valid.
        
        Args:
            token (str): Reset token string
            
        Returns:
            User: User object if token is valid, None otherwise
        """
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        
        if not reset_token:
            app.looger.warning(f"Invalid password reset token attempted: {token[:10]}...")
            return None
        
        if not reset_token.is_valid():
            app.looger.warning(f"Expired or used password reset token attempted: {token[:10]}...")
            return None
        
        return reset_token.user
    
    @staticmethod
    def reset_password_with_token(token, new_password):
        """
        Reset user password using a valid token.
        
        Args:
            token (str): Reset token string
            new_password (str): New password to set
            
        Returns:
            bool: True if password was reset successfully, False otherwise
        """
        # Verify token
        user = AuthLogic.verify_reset_token(token)
        
        if not user:
            return False
        
        # Validate new password
        if not new_password or len(new_password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return False
        
        # Update password
        user.password_hash = AuthLogic.generate_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        
        # Mark token as used
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        reset_token.is_used = True
        reset_token.used_at = datetime.utcnow()
        reset_token.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        app.looger.info(f"Password reset successful for user: {user.email}")
        
        return True
