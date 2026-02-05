from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for
from src.models.locations import Location
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required

locations_bp = Blueprint('locations', __name__, url_prefix='/locations')


def _get_current_user():
    """Get current user from session."""
    return Doorman.get_by_token(session['doorman_token']).user


def _success_response(message, data=None, status=200):
    """Create success JSON response."""
    response = {'success': True, 'message': message}
    if data:
        response.update(data)
    return jsonify(response), status


def _error_response(message, status=500):
    """Create error JSON response."""
    return jsonify({'error': message}), status


# =============== ADMIN ROUTES ===============

@locations_bp.route('/admin')
@login_required
@role_required('admin')
def admin_list():
    """List all locations for admin management."""
    status_filter = request.args.get('status', 'active')
    
    if status_filter == 'active':
        locations = Location.get_active_locations()
    elif status_filter == 'deleted':
        locations = Location.query.filter(Location.deleted_at.isnot(None)).order_by(Location.name).all()
    else:  # 'all'
        locations = Location.query.order_by(Location.name).all()
    
    return render_template('private/admins/locations/index.html',
                         current_user=_get_current_user(),
                         locations=locations,
                         status_filter=status_filter)


@locations_bp.route('/admin/create', methods=['POST'])
@login_required
@role_required('admin')
def admin_create():
    """Create a new location."""
    try:
        data = request.get_json() if request.is_json else request.form
        
        name = data.get('name', '').strip()
        location = data.get('location', '').strip()
        tax_rate = data.get('tax_rate', 0)
        additional_notes = data.get('additional_notes', '').strip() or None
        
        # Validation
        if not name:
            return _error_response('Location name is required', 400)
        
        if not location:
            return _error_response('Location address/details are required', 400)
        
        # Validate tax_rate
        try:
            tax_rate = float(tax_rate)
            if tax_rate < 0 or tax_rate > 1:
                return _error_response('Tax rate must be between 0 and 1 (0% to 100%)', 400)
        except (ValueError, TypeError):
            return _error_response('Invalid tax rate', 400)
        
        # Check for duplicate name
        existing = Location.get_by_name(name)
        if existing:
            return _error_response('A location with this name already exists', 400)
        
        # Create location
        new_location = Location.create(
            name=name,
            location=location,
            tax_rate=tax_rate,
            additional_notes=additional_notes
        )
        
        return _success_response(
            'Location created successfully',
            {'location': new_location.to_dict()},
            201
        )
    
    except Exception as e:
        return _error_response(f'Failed to create location: {str(e)}', 500)


@locations_bp.route('/admin/<int:location_id>/update', methods=['PUT', 'POST'])
@login_required
@role_required('admin')
def admin_update(location_id):
    """Update an existing location."""
    try:
        location = Location.query.get_or_404(location_id)
        data = request.get_json() if request.is_json else request.form
        
        name = data.get('name', '').strip()
        location_address = data.get('location', '').strip()
        tax_rate = data.get('tax_rate', 0)
        additional_notes = data.get('additional_notes', '').strip() or None
        
        # Validation
        if not name:
            return _error_response('Location name is required', 400)
        
        if not location_address:
            return _error_response('Location address/details are required', 400)
        
        # Validate tax_rate
        try:
            tax_rate = float(tax_rate)
            if tax_rate < 0 or tax_rate > 1:
                return _error_response('Tax rate must be between 0 and 1 (0% to 100%)', 400)
        except (ValueError, TypeError):
            return _error_response('Invalid tax rate', 400)
        
        # Check for duplicate name (excluding current location)
        existing = Location.get_by_name(name)
        if existing and existing.id != location_id:
            return _error_response('A location with this name already exists', 400)
        
        # Update location
        location.update(
            name=name,
            location=location_address,
            tax_rate=tax_rate,
            additional_notes=additional_notes
        )
        
        return _success_response(
            'Location updated successfully',
            {'location': location.to_dict()}
        )
    
    except Exception as e:
        return _error_response(f'Failed to update location: {str(e)}', 500)


@locations_bp.route('/admin/<int:location_id>/delete', methods=['DELETE', 'POST'])
@login_required
@role_required('admin')
def admin_delete(location_id):
    """Soft delete a location."""
    try:
        location = Location.query.get_or_404(location_id)
        location.soft_delete()
        
        return _success_response('Location deleted successfully')
    
    except Exception as e:
        return _error_response(f'Failed to delete location: {str(e)}', 500)


@locations_bp.route('/admin/<int:location_id>/restore', methods=['POST'])
@login_required
@role_required('admin')
def admin_restore(location_id):
    """Restore a soft-deleted location."""
    try:
        location = Location.query.get_or_404(location_id)
        location.restore()
        
        return _success_response('Location restored successfully')
    
    except Exception as e:
        return _error_response(f'Failed to restore location: {str(e)}', 500)


# =============== PUBLIC/API ROUTES ===============

@locations_bp.route('/api/list')
@login_required
def api_list():
    """API endpoint to get list of active locations."""
    try:
        locations = Location.get_active_locations()
        return jsonify({
            'success': True,
            'locations': [loc.to_dict() for loc in locations]
        })
    except Exception as e:
        return _error_response(f'Failed to fetch locations: {str(e)}', 500)


@locations_bp.route('/api/<int:location_id>')
@login_required
def api_get(location_id):
    """API endpoint to get a specific location."""
    try:
        location = Location.query.get_or_404(location_id)
        return jsonify({
            'success': True,
            'location': location.to_dict()
        })
    except Exception as e:
        return _error_response(f'Failed to fetch location: {str(e)}', 500)
