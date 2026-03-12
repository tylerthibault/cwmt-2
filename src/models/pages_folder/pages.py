from datetime import datetime
from src.models.main import db, CRUDMixin


class Page(db.Model, CRUDMixin):
    """CMS page model. Each page has a unique slug and an ordered list of sections."""

    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(200), nullable=False, unique=True, index=True)
    title = db.Column(db.String(255), nullable=False)
    meta_description = db.Column(db.String(500), nullable=True)

    is_published = db.Column(db.Boolean, default=False, nullable=False, index=True)
    # Protected pages cannot be deleted (e.g. home, about, contact)
    is_protected = db.Column(db.Boolean, default=False, nullable=False)

    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    creator = db.relationship('User', backref=db.backref('pages_created', lazy='dynamic'))
    sections = db.relationship(
        'PageSection',
        backref='page',
        lazy='dynamic',
        order_by='PageSection.display_order',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<Page {self.slug!r}>'

    @classmethod
    def get_published(cls, slug):
        """Return a published, non-deleted page by slug, or None."""
        return cls.query.filter_by(slug=slug, is_published=True, deleted_at=None).first()

    @classmethod
    def get_all_active(cls):
        """Return all non-deleted pages ordered by title."""
        return cls.query.filter_by(deleted_at=None).order_by(cls.title).all()

    def ordered_sections(self):
        """Return active sections sorted by display_order."""
        from src.models.pages_folder.page_sections import PageSection
        return (PageSection.query
                .filter_by(page_id=self.id, is_active=True)
                .order_by(PageSection.display_order)
                .all())

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()
        self.save()

    def publish(self):
        self.is_published = True
        self.save()

    def unpublish(self):
        self.is_published = False
        self.save()
