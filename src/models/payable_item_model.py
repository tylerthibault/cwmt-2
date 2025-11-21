"""
Payable Item models - THIN models following constitutional principles
Contains ONLY database schema and simple serialization
"""
from decimal import Decimal
from src.models import db
from src.models.base_model import BaseModel


class PayableItemTemplate(BaseModel):
    """
    PayableItemTemplate database model - THIN model pattern.
    
    Master catalog of items that can be charged to students.
    Examples: tuition, helmet rental, equipment fees, misc charges.
    
    Contains ONLY:
    - Database schema (columns, relationships, constraints)
    - Simple serialization methods (to_dict, from_dict)
    
    Does NOT contain:
    - Business logic (belongs in src/logic/payable_item_logic.py)
    - Validation (belongs in logic layer)
    - Price calculations (belongs in logic layer)
    """
    __tablename__ = 'payable_item_templates'
    
    # Core fields
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)  # Use Numeric for money - NO floats
    item_type = db.Column(db.String(50), nullable=False)  # 'tuition', 'rental', 'equipment', 'misc'
    is_taxable = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    course_template_items = db.relationship(
        'CourseTemplatePayableItem',
        back_populates='payable_item_template',
        cascade='all, delete-orphan'
    )
    course_items = db.relationship(
        'CoursePayableItem',
        back_populates='payable_item_template',
        cascade='all, delete-orphan'
    )
    
    # Indexes defined in migration
    __table_args__ = (
        db.Index('idx_item_type', 'item_type'),
        db.Index('idx_is_active', 'is_active'),
    )
    
    def to_dict(self):
        """
        Serialize payable item template to dictionary.
        Simple serialization only - NO business logic.
        
        Returns:
            dict: PayableItemTemplate data as dictionary
        """
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'description': self.description,
            'base_price': float(self.base_price) if self.base_price else 0.0,
            'item_type': self.item_type,
            'is_taxable': self.is_taxable,
            'is_active': self.is_active
        })
        return base_dict
    
    def __repr__(self):
        """String representation of payable item template"""
        return f'<PayableItemTemplate {self.name} (${self.base_price})>'


class CourseTemplatePayableItem(BaseModel):
    """
    CourseTemplatePayableItem join table - THIN model pattern.
    
    Many-to-many relationship: Links course templates to payable item templates.
    Defines which items are available for courses created from this template.
    
    Contains ONLY:
    - Database schema (columns, relationships, constraints)
    - Simple serialization methods (to_dict, from_dict)
    
    Does NOT contain:
    - Business logic (belongs in src/logic/payable_item_logic.py)
    - Validation (belongs in logic layer)
    """
    __tablename__ = 'course_template_payable_items'
    
    # Foreign keys
    course_template_id = db.Column(
        db.Integer,
        db.ForeignKey('course_templates.id', ondelete='CASCADE'),
        nullable=False
    )
    payable_item_template_id = db.Column(
        db.Integer,
        db.ForeignKey('payable_item_templates.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Configuration fields
    is_required = db.Column(db.Boolean, default=False, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    
    # Relationships
    course_template = db.relationship('CourseTemplate', backref='payable_items')
    payable_item_template = db.relationship('PayableItemTemplate', back_populates='course_template_items')
    
    # Constraints defined in migration
    __table_args__ = (
        db.UniqueConstraint(
            'course_template_id',
            'payable_item_template_id',
            name='uq_course_template_payable_item'
        ),
        db.Index('idx_display_order', 'display_order'),
    )
    
    def to_dict(self):
        """
        Serialize course template payable item to dictionary.
        Simple serialization only - NO business logic.
        
        Returns:
            dict: CourseTemplatePayableItem data as dictionary
        """
        base_dict = super().to_dict()
        base_dict.update({
            'course_template_id': self.course_template_id,
            'payable_item_template_id': self.payable_item_template_id,
            'is_required': self.is_required,
            'display_order': self.display_order
        })
        return base_dict
    
    def __repr__(self):
        """String representation"""
        return f'<CourseTemplatePayableItem template={self.course_template_id} item={self.payable_item_template_id}>'


class CoursePayableItem(BaseModel):
    """
    CoursePayableItem database model - THIN model pattern.
    
    Per-course instance of a payable item with price snapshot.
    Created when a Course is instantiated from a CourseTemplate.
    Captures the price at course creation time (snapshot pattern).
    
    Contains ONLY:
    - Database schema (columns, relationships, constraints)
    - Simple serialization methods (to_dict, from_dict)
    
    Does NOT contain:
    - Business logic (belongs in src/logic/payable_item_logic.py)
    - Validation (belongs in logic layer)
    - Price calculations (belongs in logic layer)
    """
    __tablename__ = 'course_payable_items'
    
    # Foreign keys
    course_id = db.Column(
        db.Integer,
        db.ForeignKey('courses.id', ondelete='CASCADE'),
        nullable=False
    )
    payable_item_template_id = db.Column(
        db.Integer,
        db.ForeignKey('payable_item_templates.id', ondelete='RESTRICT'),
        nullable=False
    )
    
    # Price snapshot - captured at course creation
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Copied from template's base_price
    
    # Configuration fields - copied from template configuration
    is_required = db.Column(db.Boolean, default=False, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)  # Can be disabled per course
    
    # Relationships
    course = db.relationship('Course', backref='payable_items')
    payable_item_template = db.relationship('PayableItemTemplate', back_populates='course_items')
    # enrollment_line_items relationship will be added in Phase 2 when EnrollmentLineItem model is created
    # enrollment_line_items = db.relationship(
    #     'EnrollmentLineItem',
    #     back_populates='course_payable_item',
    #     cascade='all, delete-orphan'
    # )
    
    # Indexes defined in migration
    __table_args__ = (
        db.Index('idx_course_id', 'course_id'),
        db.Index('idx_course_payable_item', 'course_id', 'payable_item_template_id'),
    )
    
    def to_dict(self):
        """
        Serialize course payable item to dictionary.
        Simple serialization only - NO business logic.
        
        Returns:
            dict: CoursePayableItem data as dictionary
        """
        base_dict = super().to_dict()
        base_dict.update({
            'course_id': self.course_id,
            'payable_item_template_id': self.payable_item_template_id,
            'price': float(self.price) if self.price else 0.0,
            'is_required': self.is_required,
            'is_available': self.is_available
        })
        return base_dict
    
    def __repr__(self):
        """String representation"""
        return f'<CoursePayableItem course={self.course_id} item={self.payable_item_template_id} price=${self.price}>'
