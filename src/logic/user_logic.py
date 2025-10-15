from src.models.user import User
from src.models.logbook import Logbook
from flask import session
from flask import current_app as app

class UserLogic:

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
        app.logger.info(f"Building context for student: {user.email}")
        context = {
            'user': user,
            'current_role': current_role,
            'dashboard_template': 'private/dashboard/student/index.html'
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