from src.models.main import db, CRUDMixin


SECTION_TYPES = ['text', 'image_text', 'image', 'cta', 'video']


class PageSection(db.Model, CRUDMixin):
    """A single content block belonging to a Page."""

    __tablename__ = 'page_sections'

    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'), nullable=False, index=True)

    # One of: text | image_text | image | cta | video
    section_type = db.Column(db.String(20), nullable=False, default='text')

    # Shared
    title = db.Column(db.String(255), nullable=True)
    display_order = db.Column(db.Integer, default=0, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Rich HTML content (used by text, image_text, cta)
    content = db.Column(db.Text, nullable=True)

    # Image fields (used by image, image_text)
    image_url = db.Column(db.String(500), nullable=True)
    image_alt = db.Column(db.String(255), nullable=True)
    # 'left' or 'right' — which side the image sits on in image_text layout
    image_position = db.Column(db.String(10), nullable=True, default='left')

    # CTA fields
    button_text = db.Column(db.String(100), nullable=True)
    button_url = db.Column(db.String(500), nullable=True)
    # Bootstrap button variant, e.g. 'primary', 'secondary', 'outline-primary'
    button_style = db.Column(db.String(50), nullable=True, default='primary')

    # Video embed URL (YouTube share/embed URL)
    video_url = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f'<PageSection {self.section_type} order={self.display_order}>'

    def to_dict(self):
        return {
            'id': self.id,
            'page_id': self.page_id,
            'section_type': self.section_type,
            'title': self.title or '',
            'content': self.content or '',
            'image_url': self.image_url or '',
            'image_alt': self.image_alt or '',
            'image_position': self.image_position or 'left',
            'button_text': self.button_text or '',
            'button_url': self.button_url or '',
            'button_style': self.button_style or 'primary',
            'video_url': self.video_url or '',
            'display_order': self.display_order,
            'is_active': self.is_active,
        }
