"""
Payable template service for payable template business logic.
"""
from src.models.course_folder.payable_templates import PayableTemplate


def get_all_payable_templates():
    """Get all payable templates."""
    return PayableTemplate.get_all()


def get_payable_template_by_id(template_id):
    """
    Get a payable template by ID.
    
    Args:
        template_id: ID of the template
        
    Returns:
        PayableTemplate or None
    """
    return PayableTemplate.get_by_id(template_id)


def create_payable_template(name, amount, description=None):
    """
    Create a new payable template.
    
    Args:
        name: Name of the payable template
        amount: Amount in dollars
        description: Optional description
        
    Returns:
        PayableTemplate: The created template
        
    Raises:
        ValueError: If name or amount is missing or invalid
    """
    if not name or not amount:
        raise ValueError("Name and amount are required")
    
    try:
        amount_float = float(amount)
    except (ValueError, TypeError):
        raise ValueError("Amount must be a valid number")
    
    new_template = PayableTemplate(
        name=name,
        amount=amount_float,
        description=description
    )
    new_template.save()
    
    return new_template


def update_payable_template(template_id, name, amount, description=None, is_required=False):
    """
    Update an existing payable template.
    
    Args:
        template_id: ID of the template to update
        name: Updated name
        amount: Updated amount
        description: Updated description
        is_required: Whether the template is required
        
    Returns:
        PayableTemplate: The updated template
        
    Raises:
        ValueError: If template not found or invalid data
    """
    template = PayableTemplate.query.get(template_id)
    if not template:
        raise ValueError("Payable template not found")
    
    if not name or not amount:
        raise ValueError("Name and amount are required")
    
    try:
        amount_float = float(amount)
    except (ValueError, TypeError):
        raise ValueError("Amount must be a valid number")
    
    template.name = name
    template.amount = amount_float
    template.description = description
    template.is_required = 1 if is_required else 0
    template.save()
    
    return template


def delete_payable_template(template_id):
    """
    Delete a payable template.
    
    Args:
        template_id: ID of the template to delete
        
    Raises:
        ValueError: If template not found
    """
    template = PayableTemplate.get_by_id(template_id)
    if not template:
        raise ValueError("Payable template not found")
    
    template.delete()
