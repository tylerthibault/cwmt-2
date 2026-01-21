from datetime import datetime
from src.models.main import db, CRUDMixin


class FAQ(db.Model, CRUDMixin):
    """FAQ model for frequently asked questions."""
    
    __tablename__ = 'faqs'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # FAQ Content
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    
    # Organization
    category = db.Column(db.String(100), nullable=True, index=True)  # e.g., "Enrollment", "Courses", "Payment"
    display_order = db.Column(db.Integer, default=0, nullable=False)  # For controlling display order
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<FAQ {self.id}: {self.question[:50]}...>'
    
    @classmethod
    def get_active_faqs(cls):
        """Get all active FAQs ordered by display order and creation date."""
        return cls.query.filter_by(is_active=True).order_by(cls.display_order, cls.created_at).all()
    
    @classmethod
    def get_by_category(cls, category):
        """Get all active FAQs for a specific category."""
        return cls.query.filter_by(is_active=True, category=category).order_by(cls.display_order, cls.created_at).all()
    
    @classmethod
    def get_all_categories(cls):
        """Get all unique categories from active FAQs."""
        categories = db.session.query(cls.category).filter(
            cls.is_active == True,
            cls.category.isnot(None)
        ).distinct().order_by(cls.category).all()
        return [cat[0] for cat in categories]
    
    @classmethod
    def get_grouped_faqs(cls):
        """Get all active FAQs grouped by category."""
        faqs = cls.get_active_faqs()
        grouped = {}
        uncategorized = []
        
        for faq in faqs:
            if faq.category:
                if faq.category not in grouped:
                    grouped[faq.category] = []
                grouped[faq.category].append(faq)
            else:
                uncategorized.append(faq)
        
        # Add uncategorized at the end if any exist
        if uncategorized:
            grouped['General'] = uncategorized
            
        return grouped
    
    def deactivate(self):
        """Deactivate the FAQ."""
        self.is_active = False
        self.save()
    
    def activate(self):
        """Activate the FAQ."""
        self.is_active = True
        self.save()
