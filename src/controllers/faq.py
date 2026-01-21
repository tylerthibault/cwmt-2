"""
FAQ controller for managing frequently asked questions.
"""
from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required
from src.services import faq_service

faq_bp = Blueprint('faq', __name__)


def _get_current_user():
    """Get current user from session."""
    return Doorman.get_by_token(session['doorman_token']).user


@faq_bp.route('/manage')
@login_required
@role_required('superuser')
def manage_faqs():
    """List all FAQs for management."""
    faqs = faq_service.get_all_faqs()
    categories = faq_service.get_all_categories()
    
    return render_template('private/superusers/faqs/index.html',
                         current_user=_get_current_user(),
                         faqs=faqs,
                         categories=categories)


@faq_bp.route('/create', methods=['POST'])
@login_required
@role_required('superuser')
def create_faq():
    """Create a new FAQ."""
    try:
        faq_service.create_faq(
            question=request.form.get('question'),
            answer=request.form.get('answer'),
            category=request.form.get('category'),
            display_order=request.form.get('display_order', 0),
            user_id=_get_current_user().id
        )
        flash('FAQ created successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('faq.manage_faqs'))


@faq_bp.route('/update/<int:faq_id>', methods=['POST'])
@login_required
@role_required('superuser')
def update_faq(faq_id):
    """Update an existing FAQ."""
    try:
        faq_service.update_faq(
            faq_id=faq_id,
            question=request.form.get('question'),
            answer=request.form.get('answer'),
            category=request.form.get('category'),
            display_order=request.form.get('display_order'),
            user_id=_get_current_user().id
        )
        flash('FAQ updated successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('faq.manage_faqs'))


@faq_bp.route('/toggle/<int:faq_id>', methods=['POST'])
@login_required
@role_required('superuser')
def toggle_faq(faq_id):
    """Toggle FAQ active status."""
    try:
        faq = faq_service.toggle_faq_status(faq_id, user_id=_get_current_user().id)
        status = 'activated' if faq.is_active else 'deactivated'
        flash(f'FAQ {status} successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('faq.manage_faqs'))


@faq_bp.route('/delete/<int:faq_id>', methods=['POST'])
@login_required
@role_required('superuser')
def delete_faq(faq_id):
    """Delete an FAQ."""
    try:
        faq_service.delete_faq(faq_id, user_id=_get_current_user().id)
        flash('FAQ deleted successfully!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    
    return redirect(url_for('faq.manage_faqs'))


@faq_bp.route('/reorder', methods=['POST'])
@login_required
@role_required('superuser')
def reorder_faqs():
    """Reorder FAQs based on display order."""
    try:
        faq_order = request.json.get('order', [])
        faq_service.reorder_faqs(faq_order, user_id=_get_current_user().id)
        return jsonify({'success': True, 'message': 'FAQs reordered successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@faq_bp.route('/get/<int:faq_id>')
@login_required
@role_required('superuser')
def get_faq_json(faq_id):
    """Get FAQ data as JSON for editing."""
    try:
        faq = faq_service.get_faq_by_id(faq_id)
        if not faq:
            return jsonify({'error': 'FAQ not found'}), 404
        
        return jsonify({
            'id': faq.id,
            'question': faq.question,
            'answer': faq.answer,
            'category': faq.category or '',
            'display_order': faq.display_order,
            'is_active': faq.is_active
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
