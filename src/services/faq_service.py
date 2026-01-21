"""Business logic service for FAQ operations."""
from src.models.faq import FAQ
from src.models.logs import Log


def get_all_faqs():
    """Get all FAQs ordered by display order."""
    return FAQ.query.order_by(FAQ.display_order, FAQ.created_at).all()


def get_active_faqs():
    """Get all active FAQs ordered by display order."""
    return FAQ.get_active_faqs()


def get_faqs_by_status(is_active=None):
    """
    Get FAQs filtered by active status.
    
    Args:
        is_active: True for active, False for inactive, None for all
    
    Returns:
        list: Filtered FAQs
    """
    if is_active is None:
        return get_all_faqs()
    return FAQ.query.filter_by(is_active=is_active).order_by(FAQ.display_order, FAQ.created_at).all()


def get_grouped_faqs():
    """Get all active FAQs grouped by category."""
    return FAQ.get_grouped_faqs()


def get_faq_by_id(faq_id):
    """Get a single FAQ by ID."""
    return FAQ.get_by_id(faq_id)


def create_faq(question, answer, category=None, display_order=0, user_id=None):
    """
    Create a new FAQ.
    
    Args:
        question: The question text
        answer: The answer text
        category: Optional category for grouping
        display_order: Order for displaying (lower numbers first)
        user_id: ID of user creating the FAQ (for logging)
    
    Returns:
        FAQ: The created FAQ
        
    Raises:
        ValueError: If required fields are missing
    """
    if not question or not answer:
        raise ValueError("Question and answer are required")
    
    faq = FAQ(
        question=question.strip(),
        answer=answer.strip(),
        category=category.strip() if category else None,
        display_order=int(display_order) if display_order else 0
    )
    faq.save()
    
    # Log the creation
    if user_id:
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='create_faq',
            description=f'FAQ created: {faq.question[:50]}',
            user_id=user_id,
            target_type='faq',
            target_id=faq.id,
            status='success'
        )
    
    return faq


def update_faq(faq_id, question=None, answer=None, category=None, display_order=None, user_id=None):
    """
    Update an existing FAQ.
    
    Args:
        faq_id: ID of the FAQ to update
        question: New question text
        answer: New answer text
        category: New category
        display_order: New display order
        user_id: ID of user updating the FAQ (for logging)
    
    Returns:
        FAQ: The updated FAQ
        
    Raises:
        ValueError: If FAQ not found or invalid data
    """
    faq = FAQ.get_by_id(faq_id)
    if not faq:
        raise ValueError(f"FAQ with ID {faq_id} not found")
    
    if question:
        faq.question = question.strip()
    if answer:
        faq.answer = answer.strip()
    if category is not None:
        faq.category = category.strip() if category else None
    if display_order is not None:
        faq.display_order = int(display_order)
    
    faq.save()
    
    # Log the update
    if user_id:
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='update_faq',
            description=f'FAQ updated: {faq.question[:50]}',
            user_id=user_id,
            target_type='faq',
            target_id=faq.id,
            status='success'
        )
    
    return faq


def toggle_faq_status(faq_id, user_id=None):
    """
    Toggle the active status of an FAQ.
    
    Args:
        faq_id: ID of the FAQ to toggle
        user_id: ID of user toggling status (for logging)
    
    Returns:
        FAQ: The updated FAQ
        
    Raises:
        ValueError: If FAQ not found
    """
    faq = FAQ.get_by_id(faq_id)
    if not faq:
        raise ValueError(f"FAQ with ID {faq_id} not found")
    
    faq.is_active = not faq.is_active
    faq.save()
    
    # Log the status change
    if user_id:
        action = 'activate_faq' if faq.is_active else 'deactivate_faq'
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action=action,
            description=f'FAQ {"activated" if faq.is_active else "deactivated"}: {faq.question[:50]}',
            user_id=user_id,
            target_type='faq',
            target_id=faq.id,
            status='success'
        )
    
    return faq


def delete_faq(faq_id, user_id=None):
    """
    Permanently delete an FAQ.
    
    Args:
        faq_id: ID of the FAQ to delete
        user_id: ID of user deleting the FAQ (for logging)
    
    Raises:
        ValueError: If FAQ not found
    """
    faq = FAQ.get_by_id(faq_id)
    if not faq:
        raise ValueError(f"FAQ with ID {faq_id} not found")
    
    question_preview = faq.question[:50]
    
    # Log before deletion
    if user_id:
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='delete_faq',
            description=f'FAQ deleted: {question_preview}',
            user_id=user_id,
            target_type='faq',
            target_id=faq.id,
            status='success'
        )
    
    faq.delete()


def get_all_categories():
    """Get all unique categories from active FAQs."""
    return FAQ.get_all_categories()


def reorder_faqs(faq_order_list, user_id=None):
    """
    Reorder FAQs based on a list of IDs.
    
    Args:
        faq_order_list: List of FAQ IDs in desired order
        user_id: ID of user reordering (for logging)
    
    Returns:
        bool: True if successful
    """
    for index, faq_id in enumerate(faq_order_list):
        faq = FAQ.get_by_id(faq_id)
        if faq:
            faq.display_order = index
            faq.save()
    
    # Log the reorder
    if user_id:
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='reorder_faqs',
            description=f'Reordered {len(faq_order_list)} FAQs',
            user_id=user_id,
            status='success'
        )
    
    return True
