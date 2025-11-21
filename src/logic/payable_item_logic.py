"""
Payable Item Logic Layer - THICK logic following constitutional principles
Contains ALL business logic for payable item management
"""
from decimal import Decimal, InvalidOperation
from src.models import db
from src.models.payable_item_model import (
    PayableItemTemplate,
    CourseTemplatePayableItem,
    CoursePayableItem
)
from src.models.courses_model import CourseTemplate, Course


class PayableItemLogicError(Exception):
    """Base exception for payable item logic errors"""
    pass


class PayableItemValidationError(PayableItemLogicError):
    """Exception for validation errors - fail fast"""
    pass


class PayableItemBusinessError(PayableItemLogicError):
    """Exception for business rule violations"""
    pass


class PayableItemLogic:
    """
    Business logic for payable item template management.
    Fail-fast validation, business rules, CRUD operations.
    """
    
    VALID_ITEM_TYPES = ['tuition', 'rental', 'equipment', 'misc']
    
    @staticmethod
    def validate_base_price(price):
        """
        Validate base price is valid Decimal >= 0.
        FAIL FAST on invalid input.
        
        Args:
            price: Price value to validate (can be str, int, float, Decimal)
            
        Returns:
            Decimal: Validated price as Decimal
            
        Raises:
            PayableItemValidationError: If price invalid
        """
        if price is None:
            raise PayableItemValidationError("Price is required")
        
        try:
            price_decimal = Decimal(str(price))
        except (InvalidOperation, ValueError, TypeError) as e:
            raise PayableItemValidationError(f"Invalid price format: {price}") from e
        
        if price_decimal < 0:
            raise PayableItemValidationError(f"Price cannot be negative: {price_decimal}")
        
        # Ensure max 2 decimal places for cents
        if price_decimal.as_tuple().exponent < -2:
            raise PayableItemValidationError(
                f"Price can have at most 2 decimal places: {price_decimal}"
            )
        
        return price_decimal
    
    @staticmethod
    def validate_item_type(item_type):
        """
        Validate item type is in allowed list.
        FAIL FAST on invalid input.
        
        Args:
            item_type (str): Item type to validate
            
        Returns:
            str: Validated item type (lowercase)
            
        Raises:
            PayableItemValidationError: If item type invalid
        """
        if not item_type:
            raise PayableItemValidationError("Item type is required")
        
        item_type_lower = str(item_type).lower().strip()
        
        if item_type_lower not in PayableItemLogic.VALID_ITEM_TYPES:
            raise PayableItemValidationError(
                f"Invalid item type '{item_type}'. Must be one of: {', '.join(PayableItemLogic.VALID_ITEM_TYPES)}"
            )
        
        return item_type_lower
    
    @staticmethod
    def create_template(data):
        """
        Create a new payable item template with full validation.
        FAIL FAST on any validation error.
        
        Args:
            data (dict): Template data with keys:
                - name (str, required): Item name
                - description (str, optional): Item description
                - base_price (Decimal/str/float, required): Base price
                - item_type (str, required): Type of item
                - is_taxable (bool, optional): Whether item is taxable
                - is_active (bool, optional): Whether item is active
            
        Returns:
            PayableItemTemplate: Created template instance
            
        Raises:
            PayableItemValidationError: If validation fails
            PayableItemBusinessError: If business rules violated
        """
        # FAIL FAST: Validate required fields
        if not data.get('name'):
            raise PayableItemValidationError("Item name is required")
        
        name = str(data['name']).strip()
        if len(name) > 255:
            raise PayableItemValidationError("Item name cannot exceed 255 characters")
        
        # FAIL FAST: Validate price
        base_price = PayableItemLogic.validate_base_price(data.get('base_price'))
        
        # FAIL FAST: Validate item type
        item_type = PayableItemLogic.validate_item_type(data.get('item_type'))
        
        # Business rule: Check for duplicate names (case-insensitive)
        existing = PayableItemTemplate.query.filter(
            db.func.lower(PayableItemTemplate.name) == name.lower()
        ).first()
        if existing:
            raise PayableItemBusinessError(
                f"Payable item with name '{name}' already exists (ID: {existing.id})"
            )
        
        # Create template
        template = PayableItemTemplate(
            name=name,
            description=data.get('description', '').strip() if data.get('description') else None,
            base_price=base_price,
            item_type=item_type,
            is_taxable=bool(data.get('is_taxable', False)),
            is_active=bool(data.get('is_active', True))
        )
        
        db.session.add(template)
        db.session.commit()
        
        return template
    
    @staticmethod
    def update_template(template_id, data):
        """
        Update an existing payable item template.
        FAIL FAST on validation errors.
        
        Args:
            template_id (int): ID of template to update
            data (dict): Updated template data
            
        Returns:
            PayableItemTemplate: Updated template instance
            
        Raises:
            PayableItemValidationError: If validation fails
            PayableItemBusinessError: If template not found or business rules violated
        """
        # FAIL FAST: Template must exist
        template = PayableItemTemplate.get_by_id(template_id)
        if not template:
            raise PayableItemBusinessError(f"Payable item template with ID {template_id} not found")
        
        # Update name if provided
        if 'name' in data:
            name = str(data['name']).strip()
            if not name:
                raise PayableItemValidationError("Item name cannot be empty")
            if len(name) > 255:
                raise PayableItemValidationError("Item name cannot exceed 255 characters")
            
            # Check for duplicate name (excluding current template)
            existing = PayableItemTemplate.query.filter(
                db.func.lower(PayableItemTemplate.name) == name.lower(),
                PayableItemTemplate.id != template_id
            ).first()
            if existing:
                raise PayableItemBusinessError(
                    f"Payable item with name '{name}' already exists (ID: {existing.id})"
                )
            
            template.name = name
        
        # Update description if provided
        if 'description' in data:
            template.description = data['description'].strip() if data['description'] else None
        
        # Update price if provided
        if 'base_price' in data:
            template.base_price = PayableItemLogic.validate_base_price(data['base_price'])
        
        # Update item type if provided
        if 'item_type' in data:
            template.item_type = PayableItemLogic.validate_item_type(data['item_type'])
        
        # Update boolean flags if provided
        if 'is_taxable' in data:
            template.is_taxable = bool(data['is_taxable'])
        
        if 'is_active' in data:
            template.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        return template
    
    @staticmethod
    def delete_template(template_id):
        """
        Delete a payable item template.
        FAIL FAST if template is in use.
        
        Args:
            template_id (int): ID of template to delete
            
        Returns:
            bool: True if deleted
            
        Raises:
            PayableItemBusinessError: If template not found or in use
        """
        # FAIL FAST: Template must exist
        template = PayableItemTemplate.get_by_id(template_id)
        if not template:
            raise PayableItemBusinessError(f"Payable item template with ID {template_id} not found")
        
        # Business rule: Cannot delete if attached to course templates
        if template.course_template_items:
            count = len(template.course_template_items)
            raise PayableItemBusinessError(
                f"Cannot delete payable item '{template.name}' - it is attached to {count} course template(s). "
                f"Remove the attachments first or set is_active=False instead."
            )
        
        # Business rule: Cannot delete if used in any courses
        if template.course_items:
            count = len(template.course_items)
            raise PayableItemBusinessError(
                f"Cannot delete payable item '{template.name}' - it is used in {count} course(s). "
                f"Set is_active=False instead to prevent future use."
            )
        
        db.session.delete(template)
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_all_templates(include_inactive=False):
        """
        Get all payable item templates.
        
        Args:
            include_inactive (bool): Whether to include inactive templates
            
        Returns:
            list[PayableItemTemplate]: List of templates
        """
        query = PayableItemTemplate.query
        
        if not include_inactive:
            query = query.filter_by(is_active=True)
        
        return query.order_by(PayableItemTemplate.name).all()
    
    @staticmethod
    def get_templates_by_type(item_type, include_inactive=False):
        """
        Get payable item templates filtered by type.
        
        Args:
            item_type (str): Item type to filter by
            include_inactive (bool): Whether to include inactive templates
            
        Returns:
            list[PayableItemTemplate]: List of templates
            
        Raises:
            PayableItemValidationError: If item_type invalid
        """
        # FAIL FAST: Validate item type
        item_type_lower = PayableItemLogic.validate_item_type(item_type)
        
        query = PayableItemTemplate.query.filter_by(item_type=item_type_lower)
        
        if not include_inactive:
            query = query.filter_by(is_active=True)
        
        return query.order_by(PayableItemTemplate.name).all()


class CourseTemplatePayableItemLogic:
    """
    Business logic for attaching payable items to course templates.
    Manages the M2M relationship configuration.
    """
    
    @staticmethod
    def attach_item_to_template(course_template_id, payable_item_template_id, is_required=False, display_order=0):
        """
        Attach a payable item to a course template.
        FAIL FAST on validation errors.
        
        Args:
            course_template_id (int): Course template ID
            payable_item_template_id (int): Payable item template ID
            is_required (bool): Whether item is required for enrollment
            display_order (int): Display order for UI
            
        Returns:
            CourseTemplatePayableItem: Created attachment
            
        Raises:
            PayableItemValidationError: If validation fails
            PayableItemBusinessError: If business rules violated
        """
        # FAIL FAST: Course template must exist
        course_template = CourseTemplate.get_by_id(course_template_id)
        if not course_template:
            raise PayableItemBusinessError(f"Course template with ID {course_template_id} not found")
        
        # FAIL FAST: Payable item template must exist and be active
        item_template = PayableItemTemplate.get_by_id(payable_item_template_id)
        if not item_template:
            raise PayableItemBusinessError(f"Payable item template with ID {payable_item_template_id} not found")
        
        if not item_template.is_active:
            raise PayableItemBusinessError(
                f"Cannot attach inactive payable item '{item_template.name}' to course template"
            )
        
        # Business rule: Check for duplicate attachment
        existing = CourseTemplatePayableItem.query.filter_by(
            course_template_id=course_template_id,
            payable_item_template_id=payable_item_template_id
        ).first()
        
        if existing:
            raise PayableItemBusinessError(
                f"Payable item '{item_template.name}' is already attached to course template '{course_template.name}'"
            )
        
        # Create attachment
        attachment = CourseTemplatePayableItem(
            course_template_id=course_template_id,
            payable_item_template_id=payable_item_template_id,
            is_required=bool(is_required),
            display_order=int(display_order)
        )
        
        db.session.add(attachment)
        db.session.commit()
        
        return attachment
    
    @staticmethod
    def detach_item_from_template(course_template_id, payable_item_template_id):
        """
        Remove a payable item from a course template.
        
        Args:
            course_template_id (int): Course template ID
            payable_item_template_id (int): Payable item template ID
            
        Returns:
            bool: True if detached
            
        Raises:
            PayableItemBusinessError: If attachment not found
        """
        # FAIL FAST: Attachment must exist
        attachment = CourseTemplatePayableItem.query.filter_by(
            course_template_id=course_template_id,
            payable_item_template_id=payable_item_template_id
        ).first()
        
        if not attachment:
            raise PayableItemBusinessError(
                f"Payable item attachment not found for course template {course_template_id} "
                f"and item {payable_item_template_id}"
            )
        
        db.session.delete(attachment)
        db.session.commit()
        
        return True
    
    @staticmethod
    def update_attachment(course_template_id, payable_item_template_id, is_required=None, display_order=None):
        """
        Update attachment configuration.
        
        Args:
            course_template_id (int): Course template ID
            payable_item_template_id (int): Payable item template ID
            is_required (bool, optional): New required status
            display_order (int, optional): New display order
            
        Returns:
            CourseTemplatePayableItem: Updated attachment
            
        Raises:
            PayableItemBusinessError: If attachment not found
        """
        # FAIL FAST: Attachment must exist
        attachment = CourseTemplatePayableItem.query.filter_by(
            course_template_id=course_template_id,
            payable_item_template_id=payable_item_template_id
        ).first()
        
        if not attachment:
            raise PayableItemBusinessError(
                f"Payable item attachment not found for course template {course_template_id} "
                f"and item {payable_item_template_id}"
            )
        
        if is_required is not None:
            attachment.is_required = bool(is_required)
        
        if display_order is not None:
            attachment.display_order = int(display_order)
        
        db.session.commit()
        
        return attachment
    
    @staticmethod
    def get_items_for_template(course_template_id):
        """
        Get all payable items attached to a course template.
        
        Args:
            course_template_id (int): Course template ID
            
        Returns:
            list[CourseTemplatePayableItem]: List of attachments ordered by display_order
        """
        return CourseTemplatePayableItem.query.filter_by(
            course_template_id=course_template_id
        ).order_by(CourseTemplatePayableItem.display_order, CourseTemplatePayableItem.id).all()


class CoursePayableItemLogic:
    """
    Business logic for course-specific payable items.
    Handles price snapshots when courses are created.
    """
    
    @staticmethod
    def copy_items_from_template(course_id, course_template_id):
        """
        Copy payable items from course template to course instance.
        Creates CoursePayableItem records with price snapshots.
        Called automatically when a Course is created from a CourseTemplate.
        
        Args:
            course_id (int): New course ID
            course_template_id (int): Source course template ID
            
        Returns:
            list[CoursePayableItem]: Created course payable items
            
        Raises:
            PayableItemBusinessError: If course or template not found
        """
        # FAIL FAST: Course must exist
        course = Course.get_by_id(course_id)
        if not course:
            raise PayableItemBusinessError(f"Course with ID {course_id} not found")
        
        # Get template attachments
        template_items = CourseTemplatePayableItemLogic.get_items_for_template(course_template_id)
        
        if not template_items:
            return []  # No items to copy
        
        created_items = []
        
        for template_item in template_items:
            # Snapshot the price from the template
            item_template = template_item.payable_item_template
            
            course_item = CoursePayableItem(
                course_id=course_id,
                payable_item_template_id=template_item.payable_item_template_id,
                price=item_template.base_price,  # PRICE SNAPSHOT
                is_required=template_item.is_required,
                is_available=True  # Default to available
            )
            
            db.session.add(course_item)
            created_items.append(course_item)
        
        db.session.commit()
        
        return created_items
    
    @staticmethod
    def get_items_for_course(course_id, include_unavailable=False):
        """
        Get all payable items for a specific course.
        
        Args:
            course_id (int): Course ID
            include_unavailable (bool): Whether to include items marked unavailable
            
        Returns:
            list[CoursePayableItem]: List of course payable items
        """
        query = CoursePayableItem.query.filter_by(course_id=course_id)
        
        if not include_unavailable:
            query = query.filter_by(is_available=True)
        
        return query.all()
    
    @staticmethod
    def update_availability(course_payable_item_id, is_available):
        """
        Update availability of a course payable item.
        Allows disabling items for specific courses.
        
        Args:
            course_payable_item_id (int): Course payable item ID
            is_available (bool): New availability status
            
        Returns:
            CoursePayableItem: Updated item
            
        Raises:
            PayableItemBusinessError: If item not found
        """
        # FAIL FAST: Item must exist
        item = CoursePayableItem.get_by_id(course_payable_item_id)
        if not item:
            raise PayableItemBusinessError(f"Course payable item with ID {course_payable_item_id} not found")
        
        item.is_available = bool(is_available)
        db.session.commit()
        
        return item
