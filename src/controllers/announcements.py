from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from datetime import datetime
from src.models.announcements import Announcement
from src.models.doorman import Doorman
from src.models.flask_mail.email_logs import Log
from src.utils.custom_decorators import login_required, role_required

# Create blueprint
announcements_bp = Blueprint('announcement', __name__, url_prefix='/announcements')


# =============== ADMIN ROUTES ===============

@announcements_bp.route('/')
@login_required
@role_required('admin')
def admin_list():
    """List all announcements for admin management."""
    status_filter = request.args.get('status', 'active')
    
    if status_filter == 'active':
        announcements = Announcement.query.filter_by(is_active=True, deleted_at=None).order_by(Announcement.created_at.desc()).all()
    elif status_filter == 'inactive':
        announcements = Announcement.query.filter_by(is_active=False, deleted_at=None).order_by(Announcement.created_at.desc()).all()
    elif status_filter == 'deleted':
        announcements = Announcement.query.filter(Announcement.deleted_at.isnot(None)).order_by(Announcement.deleted_at.desc()).all()
    else:  # all
        announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    
    # Count by status
    active_count = Announcement.query.filter_by(is_active=True, deleted_at=None).count()
    inactive_count = Announcement.query.filter_by(is_active=False, deleted_at=None).count()
    deleted_count = Announcement.query.filter(Announcement.deleted_at.isnot(None)).count()
    
    context = {
        'current_user': Doorman.get_by_token(session['doorman_token']).user,
        'announcements': announcements,
        'status_filter': status_filter,
        'active_count': active_count,
        'inactive_count': inactive_count,
        'deleted_count': deleted_count
    }
    return render_template('private/admins/announcements/index.html', **context)


@announcements_bp.route('/admin/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create():
    """Create a new announcement."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get current user
        current_user = Doorman.get_by_token(session['doorman_token']).user
        
        # Create announcement
        announcement = Announcement(
            message=message,
            created_by_user_id=current_user.id,
            is_active=True
        )
        announcement.save()
        
        # Log the creation
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='create_announcement',
            description=f'Announcement created: {message[:50]}...' if len(message) > 50 else f'Announcement created: {message}',
            user_id=current_user.id,
            target_type='announcement',
            target_id=announcement.id,
            status='success',
            extra_data={
                'message': message,
                'is_active': True
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Announcement created successfully',
            'announcement_id': announcement.id
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@announcements_bp.route('/admin/update/<int:announcement_id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_update(announcement_id):
    """Update an existing announcement."""
    try:
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get current user
        current_user = Doorman.get_by_token(session['doorman_token']).user
        
        old_message = announcement.message
        announcement.message = message
        announcement.save()
        
        # Log the update
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='update_announcement',
            description=f'Announcement #{announcement_id} updated',
            user_id=current_user.id,
            target_type='announcement',
            target_id=announcement.id,
            status='success',
            extra_data={
                'old_message': old_message,
                'new_message': message
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Announcement updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@announcements_bp.route('/admin/delete/<int:announcement_id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_delete(announcement_id):
    """Soft delete an announcement."""
    try:
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        # Get current user
        current_user = Doorman.get_by_token(session['doorman_token']).user
        
        announcement.soft_delete()
        
        # Log the deletion
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='delete_announcement',
            description=f'Announcement #{announcement_id} deleted',
            user_id=current_user.id,
            target_type='announcement',
            target_id=announcement.id,
            status='success',
            extra_data={
                'message': announcement.message
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Announcement deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@announcements_bp.route('/admin/restore/<int:announcement_id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_restore(announcement_id):
    """Restore a soft-deleted announcement."""
    try:
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        # Get current user
        current_user = Doorman.get_by_token(session['doorman_token']).user
        
        announcement.restore()
        
        # Log the restoration
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='restore_announcement',
            description=f'Announcement #{announcement_id} restored',
            user_id=current_user.id,
            target_type='announcement',
            target_id=announcement.id,
            status='success',
            extra_data={
                'message': announcement.message
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Announcement restored successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@announcements_bp.route('/admin/toggle-status/<int:announcement_id>', methods=['POST'])
@login_required
@role_required('admin')
def admin_toggle_status(announcement_id):
    """Toggle announcement active/inactive status."""
    try:
        announcement = Announcement.query.get(announcement_id)
        if not announcement:
            return jsonify({'error': 'Announcement not found'}), 404
        
        # Get current user
        current_user = Doorman.get_by_token(session['doorman_token']).user
        
        # Toggle status
        if announcement.is_active:
            announcement.deactivate()
            action = 'deactivate'
            status_text = 'deactivated'
        else:
            announcement.activate()
            action = 'activate'
            status_text = 'activated'
        
        # Log the status change
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action=f'{action}_announcement',
            description=f'Announcement #{announcement_id} {status_text}',
            user_id=current_user.id,
            target_type='announcement',
            target_id=announcement.id,
            status='success',
            extra_data={
                'message': announcement.message,
                'new_status': announcement.is_active
            }
        )
        
        return jsonify({
            'success': True,
            'message': f'Announcement {status_text} successfully',
            'is_active': announcement.is_active
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


# =============== PUBLIC ROUTES (for all authenticated users) ===============

@announcements_bp.route('/')
@login_required
def list_announcements():
    """List active announcements for all users."""
    announcements = Announcement.get_active_announcements()
    
    context = {
        'current_user': Doorman.get_by_token(session['doorman_token']).user,
        'announcements': announcements
    }
    return render_template('private/components/announcements/list.html', **context)


@announcements_bp.route('/recent')
@login_required
def recent_announcements():
    """Get recent announcements (for dashboard widgets, etc.)."""
    limit = request.args.get('limit', 5, type=int)
    announcements = Announcement.get_recent_announcements(limit=limit)
    
    return jsonify({
        'success': True,
        'announcements': [{
            'id': a.id,
            'message': a.message,
            'created_at': a.created_at.isoformat(),
            'created_by': f"{a.created_by.first_name} {a.created_by.last_name}" if a.created_by else 'Unknown'
        } for a in announcements]
    }), 200
