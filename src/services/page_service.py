"""Business logic service for CMS page and section operations."""
from src.models.pages_folder.pages import Page
from src.models.pages_folder.page_sections import PageSection
from src.models.logs import Log


# ─── Pages ──────────────────────────────────────────────────────────────────

def get_all_pages():
    return Page.get_all_active()


def get_page_by_id(page_id):
    page = Page.query.filter_by(id=page_id, deleted_at=None).first()
    if not page:
        raise ValueError('Page not found')
    return page


def get_page_by_slug(slug):
    page = Page.query.filter_by(slug=slug, deleted_at=None).first()
    if not page:
        raise ValueError('Page not found')
    return page


def create_page(title, slug, meta_description='', user_id=None):
    slug = _normalise_slug(slug)
    if Page.query.filter_by(slug=slug, deleted_at=None).first():
        raise ValueError(f'A page with slug "{slug}" already exists')

    page = Page(
        title=title.strip(),
        slug=slug,
        meta_description=(meta_description or '').strip(),
        is_published=False,
        created_by=user_id,
    )
    page.save()

    _log('create_page', f'Page "{page.title}" created', user_id,
         extra={'page_id': page.id, 'slug': page.slug})
    return page


def update_page(page_id, title, slug, meta_description='', user_id=None):
    page = get_page_by_id(page_id)
    new_slug = _normalise_slug(slug)

    # Check slug uniqueness (excluding this page)
    conflict = Page.query.filter(
        Page.slug == new_slug,
        Page.id != page_id,
        Page.deleted_at == None  # noqa: E711
    ).first()
    if conflict:
        raise ValueError(f'A page with slug "{new_slug}" already exists')

    page.title = title.strip()
    page.slug = new_slug
    page.meta_description = (meta_description or '').strip()
    page.save()

    _log('update_page', f'Page "{page.title}" updated', user_id,
         extra={'page_id': page.id})
    return page


def delete_page(page_id, user_id=None):
    page = get_page_by_id(page_id)
    if page.is_protected:
        raise ValueError('This page is protected and cannot be deleted')
    page.soft_delete()
    _log('delete_page', f'Page "{page.title}" deleted', user_id,
         extra={'page_id': page.id})


def toggle_publish(page_id, user_id=None):
    page = get_page_by_id(page_id)
    if page.is_published:
        page.unpublish()
        action = 'unpublished'
    else:
        page.publish()
        action = 'published'
    _log('toggle_publish_page', f'Page "{page.title}" {action}', user_id,
         extra={'page_id': page.id, 'is_published': page.is_published})
    return page


# ─── Sections ────────────────────────────────────────────────────────────────

def get_section(section_id):
    section = PageSection.query.get(section_id)
    if not section:
        raise ValueError('Section not found')
    return section


def create_section(page_id, section_type, title='', content='',
                   image_url='', image_alt='', image_position='left',
                   button_text='', button_url='', button_style='primary',
                   video_url='', user_id=None):
    page = get_page_by_id(page_id)

    # Place new section at end
    max_order = (PageSection.query
                 .filter_by(page_id=page_id)
                 .count())

    section = PageSection(
        page_id=page_id,
        section_type=section_type,
        title=(title or '').strip(),
        content=content or '',
        image_url=(image_url or '').strip(),
        image_alt=(image_alt or '').strip(),
        image_position=image_position or 'left',
        button_text=(button_text or '').strip(),
        button_url=(button_url or '').strip(),
        button_style=button_style or 'primary',
        video_url=(video_url or '').strip(),
        display_order=max_order,
        is_active=True,
    )
    section.save()

    _log('create_section', f'Section added to page "{page.title}"', user_id,
         extra={'page_id': page_id, 'section_id': section.id, 'type': section_type})
    return section


def update_section(section_id, title='', content='',
                   image_url='', image_alt='', image_position='left',
                   button_text='', button_url='', button_style='primary',
                   video_url='', user_id=None):
    section = get_section(section_id)

    section.title = (title or '').strip()
    section.content = content or ''
    section.image_url = (image_url or '').strip()
    section.image_alt = (image_alt or '').strip()
    section.image_position = image_position or 'left'
    section.button_text = (button_text or '').strip()
    section.button_url = (button_url or '').strip()
    section.button_style = button_style or 'primary'
    section.video_url = (video_url or '').strip()
    section.save()

    _log('update_section', f'Section #{section.id} updated', user_id,
         extra={'section_id': section.id})
    return section


def delete_section(section_id, user_id=None):
    section = get_section(section_id)
    page_id = section.page_id
    section.delete()
    _renumber_sections(page_id)
    _log('delete_section', f'Section #{section_id} deleted', user_id,
         extra={'section_id': section_id})


def reorder_sections(page_id, ordered_ids, user_id=None):
    """Accept list of section IDs in desired order and update display_order."""
    for idx, sid in enumerate(ordered_ids):
        section = PageSection.query.filter_by(id=sid, page_id=page_id).first()
        if section:
            section.display_order = idx
            section.save(commit=False)
    from src.models.main import db
    db.session.commit()
    _log('reorder_sections', f'Sections reordered on page {page_id}', user_id,
         extra={'page_id': page_id})


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _normalise_slug(slug):
    import re
    slug = slug.strip().lower()
    slug = re.sub(r'[^a-z0-9-]+', '-', slug)
    slug = re.sub(r'-{2,}', '-', slug).strip('-')
    return slug


def _renumber_sections(page_id):
    sections = (PageSection.query
                .filter_by(page_id=page_id)
                .order_by(PageSection.display_order)
                .all())
    for idx, s in enumerate(sections):
        s.display_order = idx
        s.save(commit=False)
    from src.models.main import db
    db.session.commit()


def _log(action, description, user_id, extra=None):
    try:
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action=action,
            description=description,
            user_id=user_id,
            status='success',
            extra_data=extra or {},
        )
    except Exception:
        pass
