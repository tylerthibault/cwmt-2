"""
Seed payable item templates and attach them to course templates
Run this after course templates are seeded
"""
from decimal import Decimal
from src.models import db
from src.models.payable_item_model import PayableItemTemplate, CourseTemplatePayableItem
from src.models.courses_model import CourseTemplate
from src.logic.payable_item_logic import PayableItemLogic, CourseTemplatePayableItemLogic


def seed_payable_items(app):
    """
    Seed default payable item templates if they don't exist.
    Then attach them to appropriate course templates.
    
    Args:
        app: Flask application instance with app context
    """
    with app.app_context():
        app.looger.info("Seeding payable item templates...")
        
        # Define default payable items
        default_items = [
            # Tuition items
            {
                'name': 'Basic Rider Course Tuition',
                'description': '3-day comprehensive basic rider training course',
                'base_price': Decimal('350.00'),
                'item_type': 'tuition',
                'is_taxable': False,
                'is_active': True
            },
            {
                'name': 'Get Riding Course Tuition',
                'description': '2-day beginner motorcycle riding course',
                'base_price': Decimal('295.00'),
                'item_type': 'tuition',
                'is_taxable': False,
                'is_active': True
            },
            {
                'name': 'Advanced Rider Course Tuition',
                'description': '1-day advanced riding skills course',
                'base_price': Decimal('150.00'),
                'item_type': 'tuition',
                'is_taxable': False,
                'is_active': True
            },
            {
                'name': 'Street Smart Course Tuition',
                'description': '1-day urban riding awareness course',
                'base_price': Decimal('125.00'),
                'item_type': 'tuition',
                'is_taxable': False,
                'is_active': True
            },
            {
                'name': 'Track Day Experience Tuition',
                'description': 'Full day track riding experience',
                'base_price': Decimal('450.00'),
                'item_type': 'tuition',
                'is_taxable': False,
                'is_active': True
            },
            
            # Rental equipment
            {
                'name': 'Motorcycle Rental',
                'description': 'Full course motorcycle rental (125cc - 500cc)',
                'base_price': Decimal('75.00'),
                'item_type': 'rental',
                'is_taxable': True,
                'is_active': True
            },
            {
                'name': 'Helmet Rental',
                'description': 'DOT-approved helmet for course duration',
                'base_price': Decimal('15.00'),
                'item_type': 'rental',
                'is_taxable': True,
                'is_active': True
            },
            {
                'name': 'Gloves Rental',
                'description': 'Riding gloves for course duration',
                'base_price': Decimal('10.00'),
                'item_type': 'rental',
                'is_taxable': True,
                'is_active': True
            },
            {
                'name': 'Jacket Rental',
                'description': 'Protective riding jacket for course duration',
                'base_price': Decimal('20.00'),
                'item_type': 'rental',
                'is_taxable': True,
                'is_active': True
            },
            
            # Equipment to purchase
            {
                'name': 'Course Workbook',
                'description': 'Official course study materials and workbook',
                'base_price': Decimal('25.00'),
                'item_type': 'equipment',
                'is_taxable': True,
                'is_active': True
            },
            {
                'name': 'Safety Vest',
                'description': 'High-visibility safety vest (keep after course)',
                'base_price': Decimal('12.00'),
                'item_type': 'equipment',
                'is_taxable': True,
                'is_active': True
            },
            
            # Misc fees
            {
                'name': 'Late Registration Fee',
                'description': 'Fee for registrations within 48 hours of course start',
                'base_price': Decimal('35.00'),
                'item_type': 'misc',
                'is_taxable': False,
                'is_active': True
            },
            {
                'name': 'Rescheduling Fee',
                'description': 'Fee for changing course date after registration',
                'base_price': Decimal('25.00'),
                'item_type': 'misc',
                'is_taxable': False,
                'is_active': True
            },
            {
                'name': 'DMV Certificate Processing',
                'description': 'Processing fee for DMV completion certificate',
                'base_price': Decimal('15.00'),
                'item_type': 'misc',
                'is_taxable': False,
                'is_active': True
            }
        ]
        
        created_items = []
        
        for item_data in default_items:
            # Check if item already exists
            existing = PayableItemTemplate.query.filter(
                db.func.lower(PayableItemTemplate.name) == item_data['name'].lower()
            ).first()
            
            if not existing:
                try:
                    item = PayableItemLogic.create_template(item_data)
                    created_items.append(item)
                    app.looger.info(f"  ✓ Created payable item: {item.name} (${item.base_price})")
                except Exception as e:
                    app.looger.error(f"  ✗ Failed to create payable item '{item_data['name']}': {e}")
            else:
                app.looger.info(f"  - Payable item already exists: {existing.name}")
        
        if created_items:
            app.looger.info(f"Created {len(created_items)} payable item templates")
        
        # Now attach items to course templates
        app.looger.info("\nAttaching payable items to course templates...")
        _attach_items_to_templates(app)


def _attach_items_to_templates(app):
    """
    Attach payable items to course templates with proper configuration.
    """
    # Get all templates and items
    templates = {t.name: t for t in CourseTemplate.query.all()}
    items = {i.name: i for i in PayableItemTemplate.query.all()}
    
    # Define which items go with which courses
    attachments = [
        # Basic Rider Course
        {
            'template': 'Basic Rider Course',
            'items': [
                {'item': 'Basic Rider Course Tuition', 'required': True, 'order': 1},
                {'item': 'Motorcycle Rental', 'required': False, 'order': 2},
                {'item': 'Helmet Rental', 'required': False, 'order': 3},
                {'item': 'Gloves Rental', 'required': False, 'order': 4},
                {'item': 'Jacket Rental', 'required': False, 'order': 5},
                {'item': 'Course Workbook', 'required': True, 'order': 6},
                {'item': 'Safety Vest', 'required': False, 'order': 7},
            ]
        },
        # Get Riding
        {
            'template': 'Get Riding',
            'items': [
                {'item': 'Get Riding Course Tuition', 'required': True, 'order': 1},
                {'item': 'Motorcycle Rental', 'required': False, 'order': 2},
                {'item': 'Helmet Rental', 'required': False, 'order': 3},
                {'item': 'Gloves Rental', 'required': False, 'order': 4},
                {'item': 'Jacket Rental', 'required': False, 'order': 5},
                {'item': 'Safety Vest', 'required': False, 'order': 6},
            ]
        },
        # Advanced Rider Course
        {
            'template': 'Advanced Rider Course',
            'items': [
                {'item': 'Advanced Rider Course Tuition', 'required': True, 'order': 1},
                {'item': 'Course Workbook', 'required': True, 'order': 2},
            ]
        },
        # Street Smart
        {
            'template': 'Street Smart',
            'items': [
                {'item': 'Street Smart Course Tuition', 'required': True, 'order': 1},
            ]
        },
        # Track Day Experience
        {
            'template': 'Track Day Experience',
            'items': [
                {'item': 'Track Day Experience Tuition', 'required': True, 'order': 1},
                {'item': 'Helmet Rental', 'required': False, 'order': 2},
                {'item': 'Gloves Rental', 'required': False, 'order': 3},
                {'item': 'Jacket Rental', 'required': False, 'order': 4},
            ]
        },
    ]
    
    for attachment_config in attachments:
        template_name = attachment_config['template']
        
        if template_name not in templates:
            app.looger.warning(f"  ⚠ Template '{template_name}' not found")
            continue
        
        template = templates[template_name]
        
        for item_config in attachment_config['items']:
            item_name = item_config['item']
            
            if item_name not in items:
                app.looger.warning(f"  ⚠ Item '{item_name}' not found")
                continue
            
            item = items[item_name]
            
            # Check if already attached
            existing = CourseTemplatePayableItem.query.filter_by(
                course_template_id=template.id,
                payable_item_template_id=item.id
            ).first()
            
            if not existing:
                try:
                    CourseTemplatePayableItemLogic.attach_item_to_template(
                        course_template_id=template.id,
                        payable_item_template_id=item.id,
                        is_required=item_config['required'],
                        display_order=item_config['order']
                    )
                    required_str = "REQUIRED" if item_config['required'] else "optional"
                    app.looger.info(f"  ✓ Attached '{item.name}' to '{template.name}' ({required_str})")
                except Exception as e:
                    app.looger.error(f"  ✗ Failed to attach '{item.name}' to '{template.name}': {e}")
            else:
                app.looger.info(f"  - Item '{item.name}' already attached to '{template.name}'")
    
    app.looger.info("Payable item seeding complete!")


def seed_default_payable_items(app):
    """
    Main entry point for seeding payable items.
    Called from AUTO_SEED or manual seeding.
    
    Args:
        app: Flask application instance
    """
    seed_payable_items(app)
