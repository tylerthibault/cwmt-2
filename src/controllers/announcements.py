from flask import Blueprint, render_template, request, session, jsonify
from src.models.announcements import Announcement
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required
from src.services import announcement_service

announcements_bp = Blueprint('announcements', __name__, url_prefix='/announcements')


def _get_current_user():
    """Get current user from session."""
    return Doorman.get_by_token(session['doorman_token']).user


def _success_response(message, data=None, status=200):
    """Create success JSON response."""
    response = {'success': True, 'message': message}
    if data:
        response.update(data)
    return jsonify(response), status


def _error_response(message, status=500):
    """Create error JSON response."""
    return jsonify({'error': message}), status


# =============== ADMIN ROUTES ===============

@announcements_bp.route('/admin')
@login_required
@role_required('admin')
def admin_list():
    """List all announcements for admin management."""
    status_filter = request.args.get('status', 'active')
    announcements = announcement_service.get_announcements_by_status(status_filter)
    counts = announcement_service.get_announcement_counts()
    
    return render_template('private/admins/announcements/index.html',
                         current_user=_get_current_user(),
                         announcements=announcements,
                         status_filter=status_filter,
                         **counts)


@announcements_bp.route('/admin/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create():
    """Create a new announcement."""
    try:
        message = request.get_json().get('message', '').strip()
        if not message:
            return _error_response('Message is required', 400)
        
        announcement = announcement_service.create_announcement(message, _get_current_user().id)
        return _success_response('Announcement created successfully', 
                               {'announcement_id': announcement.id}, 201)
    except Exception as e:
        return _error_response(f'An error occurred: {str(e)}')


@announcements_bp.route('/admin/update/<int:announcement_id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_update(announcement_id):
    """Update an existing announcement."""
    try:
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return _error_response('Announcement not found', 404)
        
        message = request.get_json().get('message', '').strip()
        if not message:
            return _error_response('Message is required', 400)
        
        announcement_service.update_announcement(announcement, message, _get_current_user().id)
        return _success_response('Announcement updated successfully')
    except Exception as e:
        return _error_response(f'An error occurred: {str(e)}')


@announcements_bp.route('/admin/delete/<int:announcement_id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete(announcement_id):
    """Soft delete an announcement."""
    try:
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return _error_response('Announcement not found', 404)
        
        announcement_service.delete_announcement(announcement, _get_current_user().id)
        return _success_response('Announcement deleted successfully')
    except Exception as e:
        return _error_response(f'An error occurred: {str(e)}')


@announcements_bp.route('/admin/restore/<int:announcement_id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_restore(announcement_id):
    """Restore a soft-deleted announcement."""
    try:
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return _error_response('Announcement not found', 404)
        
        announcement_service.restore_announcement(announcement, _get_current_user().id)
        return _success_response('Announcement restored successfully')
    except Exception as e:
        return _error_response(f'An error occurred: {str(e)}')


@announcements_bp.route('/admin/toggle-status/<int:announcement_id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_toggle_status(announcement_id):
    """Toggle announcement active/inactive status."""
    try:
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return _error_response('Announcement not found', 404)
        
        status_text, is_active = announcement_service.toggle_announcement_status(
            announcement, _get_current_user().id
        )
        
        return _success_response(f'Announcement {status_text} successfully', 
                               {'is_active': is_active})
    except Exception as e:
        return _error_response(f'An error occurred: {str(e)}')


# =============== PUBLIC ROUTES ===============

@announcements_bp.route('/')
@login_required
def list_announcements():
    """List active announcements for all users."""
    announcements = Announcement.get_active_announcements()
    
    return render_template('private/components/announcements/list.html',
                         current_user=_get_current_user(),
                         announcements=announcements)


@announcements_bp.route('/recent')
@login_required
def recent_announcements():
    """Get recent announcements (for dashboard widgets, etc.)."""
    limit = request.args.get('limit', 5, type=int)
    announcements = Announcement.get_recent_announcements(limit=limit)
    formatted = announcement_service.format_announcements_for_json(announcements)
    
    return _success_response('Announcements retrieved', {'announcements': formatted})