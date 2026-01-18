"""Business logic service for announcement operations."""
from src.models.announcements import Announcement
from src.models.logs import Log


def get_announcements_by_status(status_filter='active'):
    """
    Get announcements filtered by status.
    
    Args:
        status_filter: 'active', 'inactive', 'deleted', or 'all'
    
    Returns:
        list: Filtered announcements
    """
    query_map = {
        'active': lambda: Announcement.query.filter_by(is_active=True, deleted_at=None),
        'inactive': lambda: Announcement.query.filter_by(is_active=False, deleted_at=None),
        'deleted': lambda: Announcement.query.filter(Announcement.deleted_at.isnot(None)),
        'all': lambda: Announcement.query
    }
    
    query = query_map.get(status_filter, query_map['active'])()
    order_col = Announcement.deleted_at if status_filter == 'deleted' else Announcement.created_at
    
    return query.order_by(order_col.desc()).all()


def get_announcement_counts():
    """Get counts of announcements by status."""
    return {
        'active_count': Announcement.query.filter_by(is_active=True, deleted_at=None).count(),
        'inactive_count': Announcement.query.filter_by(is_active=False, deleted_at=None).count(),
        'deleted_count': Announcement.query.filter(Announcement.deleted_at.isnot(None)).count()
    }


def create_announcement(message, user_id):
    """
    Create a new announcement.
    
    Args:
        message: Announcement message text
        user_id: ID of user creating the announcement
    
    Returns:
        Announcement: The created announcement
    """
    announcement = Announcement(
        message=message,
        created_by_user_id=user_id,
        is_active=True
    )
    announcement.save()
    
    _log_announcement_action(
        action='create_announcement',
        description=f'Announcement created: {_truncate_message(message)}',
        user_id=user_id,
        announcement=announcement,
        extra_data={'message': message, 'is_active': True}
    )
    
    return announcement


def update_announcement(announcement, message, user_id):
    """
    Update an existing announcement.
    
    Args:
        announcement: Announcement object to update
        message: New message text
        user_id: ID of user updating the announcement
    
    Returns:
        Announcement: The updated announcement
    """
    old_message = announcement.message
    announcement.message = message
    announcement.save()
    
    _log_announcement_action(
        action='update_announcement',
        description=f'Announcement #{announcement.id} updated',
        user_id=user_id,
        announcement=announcement,
        extra_data={'old_message': old_message, 'new_message': message}
    )
    
    return announcement


def delete_announcement(announcement, user_id):
    """
    Soft delete an announcement.
    
    Args:
        announcement: Announcement object to delete
        user_id: ID of user deleting the announcement
    """
    announcement.soft_delete()
    
    _log_announcement_action(
        action='delete_announcement',
        description=f'Announcement #{announcement.id} deleted',
        user_id=user_id,
        announcement=announcement,
        extra_data={'message': announcement.message}
    )


def restore_announcement(announcement, user_id):
    """
    Restore a soft-deleted announcement.
    
    Args:
        announcement: Announcement object to restore
        user_id: ID of user restoring the announcement
    """
    announcement.restore()
    
    _log_announcement_action(
        action='restore_announcement',
        description=f'Announcement #{announcement.id} restored',
        user_id=user_id,
        announcement=announcement,
        extra_data={'message': announcement.message}
    )


def toggle_announcement_status(announcement, user_id):
    """
    Toggle announcement active/inactive status.
    
    Args:
        announcement: Announcement object to toggle
        user_id: ID of user toggling the status
    
    Returns:
        tuple: (status_text, is_active)
    """
    if announcement.is_active:
        announcement.deactivate()
        action = 'deactivate'
        status_text = 'deactivated'
    else:
        announcement.activate()
        action = 'activate'
        status_text = 'activated'
    
    _log_announcement_action(
        action=f'{action}_announcement',
        description=f'Announcement #{announcement.id} {status_text}',
        user_id=user_id,
        announcement=announcement,
        extra_data={'message': announcement.message, 'new_status': announcement.is_active}
    )
    
    return status_text, announcement.is_active


def format_announcements_for_json(announcements):
    """Format announcements list for JSON response."""
    return [{
        'id': a.id,
        'message': a.message,
        'created_at': a.created_at.isoformat(),
        'created_by': f"{a.created_by.first_name} {a.created_by.last_name}" if a.created_by else 'Unknown'
    } for a in announcements]


def _log_announcement_action(action, description, user_id, announcement, extra_data=None):
    """Helper to log announcement actions."""
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action=action,
        description=description,
        user_id=user_id,
        target_type='announcement',
        target_id=announcement.id,
        status='success',
        extra_data=extra_data or {}
    )


def _truncate_message(message, max_length=50):
    """Truncate message for logging."""
    return f'{message[:max_length]}...' if len(message) > max_length else message
