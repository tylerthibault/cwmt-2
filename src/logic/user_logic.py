from src.models.user import User
from src.models.logbook import Logbook
from flask import session, flash
from flask import current_app as app

class UserLogic:

    @staticmethod
    def create_user(data):
        """
        Create a new user with validation and business logic.
        
        Args:
            data (dict): User data including username, email, password, etc.
            
        Returns:
            User: The created user instance
            
        Raises:
            ValueError: If validation fails
        """
        # Validation
        if not data.get('username'):
            raise ValueError('Username is required')
        
        if not data.get('email'):
            raise ValueError('Email is required')
        
        if not data.get('password') or len(data.get('password')) < 6:
            raise ValueError('Password must be at least 6 characters')
        
        if data.get('password') != data.get('confirm_password'):
            raise ValueError('Passwords do not match')
        
        # Business rules - check uniqueness
        if User.query.filter_by(email=data.get('email')).first():
            raise ValueError('Email already registered')
        
        if User.query.filter_by(username=data.get('username')).first():
            raise ValueError('Username already registered')
        
        # Import auth logic for password hashing
        from src.logic.auth_logic import AuthLogic
        
        # Create the user
        user = User.create(
            username=data.get('username'),
            email=data.get('email'),
            password_hash=AuthLogic.generate_password_hash(data.get('password')),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            is_active=True
        )
        
        # Assign initial role if provided
        if data.get('role_name'):
            from src.models.roles import Role, UserHasRoles
            role = Role.get_by_name(data.get('role_name'))
            if role:
                UserHasRoles.assign_role(user.id, role.id)
        
        return user

    @staticmethod
    def get_context(view_as=None):
        """Build context for user dashboard based on role"""
        token = session.get('token')
        logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
        if not logbook_entry:
            return {}
        
        user = User.query.get(logbook_entry.user_id)
        if not user:
            return {}
        
        # roles = [role.name for role in user.roles]
        roles = user.role_list  
        roles = [role.name for role in roles]

        # Determine the current role based on view_as parameter or user's highest role
        current_role = view_as if view_as and view_as in roles else None
        
        if not current_role:
            # Default to highest priority role
            if 'super-user' in roles:
                current_role = 'super-user'
            elif 'admin' in roles:
                current_role = 'admin'
            elif 'instructor' in roles:
                current_role = 'instructor'
            elif 'student' in roles:
                current_role = 'student'
        
        # Build context based on the current role
        if current_role == 'super-user':
            return UserLogic._build_superuser_context(user, current_role)
        elif current_role == 'admin':
            return UserLogic._build_admin_context(user, current_role)
        elif current_role == 'instructor':
            return UserLogic._build_instructor_context(user, current_role)
        elif current_role == 'student':
            return UserLogic._build_student_context(user, current_role)
        else:
            print("No matching role found")
            return {}
        
    @staticmethod
    def _build_instructor_context(user, current_role):
        """Build context for instructor dashboard"""
        app.looger.info(f"Building context for instructor: {user.email}")
        context = {
            'user': user,
            'current_role': current_role,
            'dashboard_template': 'private/dashboard/instructor/index.html'
        }
        return context
    
    @staticmethod
    def _build_student_context(user, current_role):
        """Build context for student dashboard"""
        from src.logic.course_logic import CourseLogic, CourseTemplateLogic
        
        app.logger.info(f"Building context for student: {user.email}")
        
        # Get available courses
        available_courses = CourseLogic.get_available_courses()
        
        # Get all course templates for filtering
        course_templates = CourseTemplateLogic.get_all_templates(active_only=True)
        
        # Get all locations for filtering
        locations = CourseLogic.get_all_locations()
        
        # Get student's enrolled courses
        enrolled_courses = CourseLogic.get_courses_for_student(user.id)
        
        context = {
            'user': user,
            'current_user': user,  # Add current_user for template compatibility
            'current_role': current_role,
            'dashboard_template': 'private/dashboard/student/index.html',
            'available_courses': available_courses,
            'course_templates': course_templates,
            'locations': locations,
            'enrolled_courses': enrolled_courses
        }
        return context
    
    @staticmethod
    def _build_admin_context(user, current_role):
        """Build context for admin dashboard"""
        app.logger.info(f"Building context for admin: {user.email}")
        context = {
            'user': user,
            'current_role': current_role,
            'dashboard_template': 'private/dashboard/admin/index.html'
        }
        return context
    
    @staticmethod
    def _build_superuser_context(user, current_role):
        """Build context for super-user dashboard"""
        from src.models.roles import Role
        from datetime import datetime, timedelta
        
        app.logger.info(f"Building context for super-user: {user.email}")
        
        # Get system statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        total_roles = Role.query.count()
        
        # Get recent user activity from logbook
        recent_cutoff = datetime.utcnow() - timedelta(days=7)
        recent_logbook_entries = Logbook.query.filter(
            Logbook.created_at >= recent_cutoff
        ).order_by(Logbook.created_at.desc()).limit(10).all()
        
        # Transform logbook entries to activity format
        recent_user_activity = []
        for entry in recent_logbook_entries:
            entry_user = User.query.get(entry.user_id)
            if entry_user:
                recent_user_activity.append({
                    'timestamp': entry.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'username': entry_user.username,
                    'email': entry_user.email,
                    'action': 'Login' if not entry.has_logged_out else 'Logout',
                    'details': f"Session: {entry.token[:8]}...",
                    'ip_address': 'N/A',  # IP address not tracked in current model
                    'status': 'Success',
                    'status_class': 'success'
                })
        
        # Get recent system logs (simplified)
        recent_logs = [
            {
                'level': 'INFO',
                'level_class': 'info',
                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                'message': 'System running normally'
            }
        ]
        
        # Get last user and role updates
        last_user = User.query.order_by(User.created_at.desc()).first()
        last_user_created = last_user.created_at.strftime('%Y-%m-%d %H:%M') if last_user else 'N/A'
        
        last_role = Role.query.order_by(Role.updated_at.desc()).first()
        last_role_updated = last_role.updated_at.strftime('%Y-%m-%d %H:%M') if last_role else 'N/A'
        
        context = {
            'user': user,
            'current_role': current_role,
            'dashboard_template': 'private/dashboard/super_user/index.html',
            
            # System statistics
            'total_users': total_users,
            'active_users': active_users,
            'total_roles': total_roles,
            'system_health': 'Good',
            'pending_actions': 0,
            
            # Recent activity
            'recent_user_activity': recent_user_activity,
            'recent_logs': recent_logs,
            
            # Last updates
            'last_user_created': last_user_created,
            'last_role_updated': last_role_updated,
            'last_config_change': 'N/A'
        }
        return context
    
    @staticmethod
    def update_user_profile(user_id, data):
        """
        Update user profile information.
        
        Args:
            user_id (int): ID of the user to update
            data (dict): Profile data including username, email, first_name, last_name
            
        Returns:
            User: The updated user instance
            
        Raises:
            ValueError: If validation fails
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')
        
        # Validation
        if not data.get('username'):
            raise ValueError('Username is required')
        
        if not data.get('email'):
            raise ValueError('Email is required')
        
        # Check if username is already taken by another user
        existing_user = User.query.filter_by(username=data.get('username')).first()
        if existing_user and existing_user.id != user_id:
            raise ValueError('Username already taken')
        
        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=data.get('email')).first()
        if existing_user and existing_user.id != user_id:
            raise ValueError('Email already registered')
        
        # Check if email has changed
        email_changed = user.email != data.get('email')
        
        # Update user fields
        user.username = data.get('username')
        user.email = data.get('email')
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        
        # If email changed, reset email confirmation
        if email_changed:
            user.email_confirmed = False
            user.email_confirmed_at = None
        
        from src.models import db
        db.session.commit()
        
        return user, email_changed
    
    @staticmethod
    def update_user_password(user_id, data):
        """
        Update user password.
        
        Args:
            user_id (int): ID of the user to update
            data (dict): Password data including current_password, new_password, confirm_password
            
        Returns:
            bool: True if password was updated
            
        Raises:
            ValueError: If validation fails
        """
        from src.logic.auth_logic import AuthLogic
        
        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')
        
        # Validation
        if not data.get('current_password'):
            raise ValueError('Current password is required')
        
        if not data.get('new_password'):
            raise ValueError('New password is required')
        
        if len(data.get('new_password', '')) < 6:
            raise ValueError('New password must be at least 6 characters')
        
        if data.get('new_password') != data.get('confirm_password'):
            raise ValueError('New passwords do not match')
        
        # Verify current password
        if not AuthLogic.check_password_hash(user.password_hash, data.get('current_password')):
            raise ValueError('Current password is incorrect')
        
        # Update password
        user.password_hash = AuthLogic.generate_password_hash(data.get('new_password'))
        
        from src.models import db
        db.session.commit()
        
        return True