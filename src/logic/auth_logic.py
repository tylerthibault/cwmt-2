from flask import flash, current_app as app
from src.models.user import User
from src.models.roles import Role, UserHasRoles
from src.utils.encryption import compute_search_hash


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
            if User.query.filter_by(email_search_hash=compute_search_hash(data.get('email'))).first():
                flash('Email already registered', 'user_register_email_error')
                is_valid = False
            if User.query.filter_by(username_search_hash=compute_search_hash(data.get('username'))).first():
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

            flash('Registration successful! Please log in.', 'success')
            return user.id

        return is_valid
    
    @staticmethod
    def validate_login(data):
        # validate email and password
        if not data.get('email') or not data.get('password'):
            flash('Email and password are required', 'user_login_error')
            return None
        
        user = User.query.filter_by(email_search_hash=compute_search_hash(data.get('email'))).first()
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