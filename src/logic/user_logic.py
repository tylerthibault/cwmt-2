from src.models.user import User
from src.models.logbook import Logbook
from flask import session
from flask import current_app as app

class UserLogic:

    @staticmethod
    def get_context():
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
        
        if 'super-user' in roles:
            return UserLogic._build_superuser_context(user)
        elif 'admin' in roles:
            return UserLogic._build_admin_context(user)
        elif 'instructor' in roles:
            return UserLogic._build_instructor_context(user)
        elif 'student' in roles:
            return UserLogic._build_student_context(user)
        else:
            print("No matching role found")
            return {}
    
    @staticmethod
    def _build_instructor_context(user):
        """Build context for instructor dashboard"""
        app.looger.info(f"Building context for instructor: {user.email}")
        context = {
            'user': user,
            'dashboard_template': 'private/dashboard/instructor/index.html'
        }
        return context
    
    @staticmethod
    def _build_student_context(user):
        """Build context for student dashboard"""
        app.logger.info(f"Building context for student: {user.email}")
        context = {
            'user': user,
            'dashboard_template': 'private/dashboard/student/index.html'
        }
        return context
    
    @staticmethod
    def _build_admin_context(user):
        """Build context for admin dashboard"""
        app.logger.info(f"Building context for admin: {user.email}")
        context = {
            'user': user,
            'dashboard_template': 'private/dashboard/admin/index.html'
        }
        return context
    
    @staticmethod
    def _build_superuser_context(user):
        """Build context for super-user dashboard"""
        app.logger.info(f"Building context for super-user: {user.email}")
        context = {
            'user': user,
            'dashboard_template': 'private/dashboard/super_user/index.html'
        }
        return context