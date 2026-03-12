"""
CMS Pages controller — admin management + public rendering.
"""
from flask import (Blueprint, render_template, redirect, url_for,
                   request, session, flash, jsonify, abort)
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required
from src.services import page_service
from src.models.pages_folder.page_sections import SECTION_TYPES

pages_bp = Blueprint('pages', __name__)


def _get_current_user():
    return Doorman.get_by_token(session['doorman_token']).user


def _ok(message, data=None, status=200):
    resp = {'success': True, 'message': message}
    if data:
        resp.update(data)
    return jsonify(resp), status


def _err(message, status=400):
    return jsonify({'success': False, 'error': message}), status


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN — Pages list
# ═══════════════════════════════════════════════════════════════════════════════

@pages_bp.route('/admin/pages')
@login_required
@role_required('admin', 'superuser')
def admin_list():
    pages = page_service.get_all_pages()
    return render_template('private/admins/pages/index.html',
                           current_user=_get_current_user(),
                           pages=pages)


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN — Create page
# ═══════════════════════════════════════════════════════════════════════════════

@pages_bp.route('/admin/pages/create', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'superuser')
def admin_create():
    if request.method == 'POST':
        try:
            page = page_service.create_page(
                title=request.form.get('title', ''),
                slug=request.form.get('slug', ''),
                meta_description=request.form.get('meta_description', ''),
                user_id=_get_current_user().id,
            )
            flash(f'Page "{page.title}" created.', 'success')
            return redirect(url_for('pages.admin_editor', page_id=page.id))
        except ValueError as e:
            flash(str(e), 'danger')

    return render_template('private/admins/pages/create.html',
                           current_user=_get_current_user())


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN — Page editor
# ═══════════════════════════════════════════════════════════════════════════════

@pages_bp.route('/admin/pages/<int:page_id>/edit')
@login_required
@role_required('admin', 'superuser')
def admin_editor(page_id):
    try:
        page = page_service.get_page_by_id(page_id)
    except ValueError:
        abort(404)
    sections = page.ordered_sections()
    return render_template('private/admins/pages/editor.html',
                           current_user=_get_current_user(),
                           page=page,
                           sections=sections,
                           section_types=SECTION_TYPES)


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN — Update page metadata
# ═══════════════════════════════════════════════════════════════════════════════

@pages_bp.route('/admin/pages/<int:page_id>/update', methods=['POST'])
@login_required
@role_required('admin', 'superuser')
def admin_update(page_id):
    try:
        page_service.update_page(
            page_id=page_id,
            title=request.form.get('title', ''),
            slug=request.form.get('slug', ''),
            meta_description=request.form.get('meta_description', ''),
            user_id=_get_current_user().id,
        )
        flash('Page settings saved.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('pages.admin_editor', page_id=page_id))


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN — Delete page
# ═══════════════════════════════════════════════════════════════════════════════

@pages_bp.route('/admin/pages/<int:page_id>/delete', methods=['POST'])
@login_required
@role_required('admin', 'superuser')
def admin_delete(page_id):
    try:
        page_service.delete_page(page_id, user_id=_get_current_user().id)
        flash('Page deleted.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('pages.admin_list'))


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN — Toggle publish
# ═══════════════════════════════════════════════════════════════════════════════

@pages_bp.route('/admin/pages/<int:page_id>/toggle-publish', methods=['POST'])
@login_required
@role_required('admin', 'superuser')
def admin_toggle_publish(page_id):
    try:
        page = page_service.toggle_publish(page_id, user_id=_get_current_user().id)
        status = 'published' if page.is_published else 'unpublished'
        flash(f'Page {status}.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('pages.admin_editor', page_id=page_id))


# ═══════════════════════════════════════════════════════════════════════════════
# ADMIN — Sections CRUD
# ═══════════════════════════════════════════════════════════════════════════════

@pages_bp.route('/admin/pages/<int:page_id>/sections/create', methods=['POST'])
@login_required
@role_required('admin', 'superuser')
def admin_section_create(page_id):
    try:
        section = page_service.create_section(
            page_id=page_id,
            section_type=request.form.get('section_type', 'text'),
            title=request.form.get('title', ''),
            content=request.form.get('content', ''),
            image_url=request.form.get('image_url', ''),
            image_alt=request.form.get('image_alt', ''),
            image_position=request.form.get('image_position', 'left'),
            button_text=request.form.get('button_text', ''),
            button_url=request.form.get('button_url', ''),
            button_style=request.form.get('button_style', 'primary'),
            video_url=request.form.get('video_url', ''),
            user_id=_get_current_user().id,
        )
        flash('Section added.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('pages.admin_editor', page_id=page_id))


@pages_bp.route('/admin/pages/<int:page_id>/sections/<int:section_id>/update', methods=['POST'])
@login_required
@role_required('admin', 'superuser')
def admin_section_update(page_id, section_id):
    try:
        page_service.update_section(
            section_id=section_id,
            title=request.form.get('title', ''),
            content=request.form.get('content', ''),
            image_url=request.form.get('image_url', ''),
            image_alt=request.form.get('image_alt', ''),
            image_position=request.form.get('image_position', 'left'),
            button_text=request.form.get('button_text', ''),
            button_url=request.form.get('button_url', ''),
            button_style=request.form.get('button_style', 'primary'),
            video_url=request.form.get('video_url', ''),
            user_id=_get_current_user().id,
        )
        flash('Section updated.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('pages.admin_editor', page_id=page_id))


@pages_bp.route('/admin/pages/<int:page_id>/sections/<int:section_id>/delete', methods=['POST'])
@login_required
@role_required('admin', 'superuser')
def admin_section_delete(page_id, section_id):
    try:
        page_service.delete_section(section_id, user_id=_get_current_user().id)
        flash('Section removed.', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    return redirect(url_for('pages.admin_editor', page_id=page_id))


@pages_bp.route('/admin/pages/<int:page_id>/sections/<int:section_id>', methods=['GET'])
@login_required
@role_required('admin', 'superuser')
def admin_section_get(page_id, section_id):
    """Return section data as JSON so the edit modal can pre-fill."""
    try:
        section = page_service.get_section(section_id)
        if section.page_id != page_id:
            return _err('Not found', 404)
        return _ok('ok', {'section': section.to_dict()})
    except ValueError as e:
        return _err(str(e), 404)


@pages_bp.route('/admin/pages/<int:page_id>/sections/reorder', methods=['POST'])
@login_required
@role_required('admin', 'superuser')
def admin_section_reorder(page_id):
    """Accept JSON body {"order": [id, id, ...]} and persist new display_order."""
    try:
        data = request.get_json(force=True) or {}
        ordered_ids = [int(i) for i in data.get('order', [])]
        page_service.reorder_sections(page_id, ordered_ids, user_id=_get_current_user().id)
        return _ok('Order saved')
    except Exception as e:
        return _err(str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC — Render page
# ═══════════════════════════════════════════════════════════════════════════════

@pages_bp.route('/p/<slug>')
def public_page(slug):
    from src.models.pages_folder.pages import Page as PageModel
    page = PageModel.get_published(slug)
    if not page:
        abort(404)
    sections = page.ordered_sections()
    return render_template('public/pages/page.html',
                           page=page,
                           sections=sections)
