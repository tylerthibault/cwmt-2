from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, session
from src.models.user_folder import admins, users
from src.models.doorman import Doorman
from src.utils.custom_decorators import login_required, role_required

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    """admin dashboard route."""
    context = {
        'current_user': Doorman.get_by_token(session['doorman_token']).user
    }
    return render_template('private/admins/dashboard/index.html', **context)


@admin_bp.route('/set-admin/<int:user_id>/<status>', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'superuser')
def admin_status(user_id, status='add'):
    """
        Route to set a user as an admin.
    """
    user = users.User.query.get(user_id)
    if not user:
        return "User not found", 404

    if status == 'add':
        # Check if the user is already an admin
        existing_admin = admins.Admin.query.filter_by(user_id=user.id).first()
        if existing_admin:
            return "User is already an admin", 400

        # Create a new Admin entry
        new_admin = admins.Admin.create(user_id=user.id)

        return redirect(url_for('admin.dashboard'))

    if status == 'remove':
        # Find the admin entry
        existing_admin = admins.Admin.query.filter_by(user_id=user.id).first()
        if not existing_admin:
            return "User is not an admin", 400

        # Delete the admin entry
        existing_admin.delete()

        return redirect(url_for('auth.login'))
    

# All Students Route
@admin_bp.route('/students')
@login_required
@role_required('admin')
def students():
    """Route to view all students with filtering."""
    from src.models.user_folder.students import Student
    from src.models.user_folder.users import User
    from flask import make_response
    import csv
    from io import StringIO
    
    # Get filter parameters
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')
    enrollments = request.args.get('enrollments', '')
    limit = request.args.get('limit', '50')
    export = request.args.get('export', '')
    
    # Base query with eager loading
    query = Student.query.join(User).order_by(Student.id.desc())
    
    # Apply search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Student.first_name.ilike(search_pattern)) |
            (Student.last_name.ilike(search_pattern)) |
            (User.email.ilike(search_pattern))
        )
    
    # Apply status filter
    if status == 'active':
        query = query.filter(Student.created_by_student_id.is_(None))
    elif status == 'guest':
        query = query.filter(Student.created_by_student_id.isnot(None))
    
    # Calculate total before enrollment filter
    total_count = Student.query.count()
    active_count = Student.query.filter(Student.created_by_student_id.is_(None)).count()
    guest_count = Student.query.filter(Student.created_by_student_id.isnot(None)).count()
    
    # Get filtered students for enrollment filter
    filtered_students = query.all()
    
    # Apply enrollment filter
    if enrollments == 'has':
        filtered_students = [s for s in filtered_students if s.enrollments.count() > 0]
    elif enrollments == 'none':
        filtered_students = [s for s in filtered_students if s.enrollments.count() == 0]
    
    # Calculate enrolled count
    enrolled_count = sum(1 for s in Student.query.all() if s.enrollments.count() > 0)
    
    # Apply limit
    if limit != 'all':
        try:
            limit_num = int(limit)
            filtered_students = filtered_students[:limit_num]
        except ValueError:
            filtered_students = filtered_students[:50]
    
    # Handle CSV export
    if export == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Type', 'Relationship', 'Enrollments', 'Registered'])
        
        for student in filtered_students:
            account_type = 'Guest Account' if student.created_by_student_id else 'Primary Account'
            relationship = student.relationship if student.relationship else ''
            enrollment_count = student.enrollments.count()
            registered = student.user.created_at.strftime('%Y-%m-%d') if student.user else 'N/A'
            
            writer.writerow([
                student.id,
                f"{student.first_name} {student.last_name}",
                student.user.email if student.user else 'N/A',
                student.user.phone_number if student.user and student.user.phone_number else 'N/A',
                account_type,
                relationship,
                enrollment_count,
                registered
            ])
        
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=students_{datetime.now().strftime("%Y%m%d")}.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response
    
    context = {
        'current_user': Doorman.get_by_token(session['doorman_token']).user,
        'students': filtered_students,
        'total_count': total_count,
        'active_count': active_count,
        'guest_count': guest_count,
        'enrolled_count': enrolled_count
    }
    return render_template('private/admins/students/index.html', **context)

@admin_bp.route('/students/<int:student_id>')
@login_required
@role_required('admin')
def view_student(student_id):
    """Route to view a specific student's details."""
    from src.models.user_folder.students import Student
    from src.models.stripe.payments import Payment
    
    student = Student.query.get(student_id)
    if not student:
        return "Student not found", 404
    
    # Get all payments for this student
    payments = Payment.query.filter_by(student_id=student_id).order_by(Payment.created_at.desc()).all()
    
    context = {
        'current_user': Doorman.get_by_token(session['doorman_token']).user,
        'student': student,
        'payments': payments
    }
    return render_template('private/admins/students/details.html', **context)

@admin_bp.route('/payments/<int:payment_id>')
@login_required
@role_required('admin')
def view_payment(payment_id):
    """Route to view a specific payment's details with itemized breakdown."""
    from src.models.stripe.payments import Payment
    
    payment = Payment.query.get(payment_id)
    if not payment:
        return "Payment not found", 404
    
    context = {
        'current_user': Doorman.get_by_token(session['doorman_token']).user,
        'payment': payment
    }
    return render_template('private/admins/payments/details.html', **context)

# ------------------------------------------------------
# --------------------- API ROUTES ---------------------
# ------------------------------------------------------

@admin_bp.route('/api/payments/<int:payment_id>/sync-stripe', methods=['POST'])
@login_required
@role_required('admin')
def sync_payment_with_stripe(payment_id):
    """Sync payment refund status with Stripe."""
    import stripe
    import os
    from flask import jsonify
    from src.models.stripe.payments import Payment
    from src.models.stripe.payment_line_items import PaymentLineItem
    from src.models.course_folder.payable_templates import PayableTemplate
    
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    try:
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        if not payment.stripe_charge_id:
            return jsonify({'error': 'No Stripe charge ID found'}), 400
        
        # Retrieve charge from Stripe
        stripe_charge = stripe.Charge.retrieve(payment.stripe_charge_id)
        actual_stripe_refunded = stripe_charge.amount_refunded
        
        # Calculate total already refunded in our database
        total_refunded = sum(
            item.amount_refunded if item.amount_refunded else 0 
            for item in payment.line_items.all()
        )
        
        if actual_stripe_refunded <= total_refunded:
            return jsonify({
                'success': True,
                'message': 'Database is already in sync with Stripe',
                'stripe_refunded': actual_stripe_refunded,
                'db_refunded': total_refunded
            }), 200
        
        # There's a discrepancy - Stripe has more refunded
        difference = actual_stripe_refunded - total_refunded
        
        # Create a "Stripe Sync Adjustment" line item for the difference
        sync_template = PayableTemplate.query.filter_by(name='Stripe Sync Adjustment').first()
        if not sync_template:
            sync_template = PayableTemplate(
                name='Stripe Sync Adjustment',
                description='Automatic sync adjustment to match Stripe records',
                amount=0,
                is_required=False
            )
            sync_template.save()
        
        # Create line item for the missing refund amount
        sync_line_item = PaymentLineItem(
            payment_id=payment_id,
            payable_template_id=sync_template.id,
            cost_of_item=difference,
            quantity=1
        )
        sync_line_item.amount_refunded = difference
        sync_line_item.save()
        
        # Update payment status if now fully refunded
        new_total_refunded = total_refunded + difference
        if new_total_refunded >= payment.total_cost:
            payment.status = 'refunded'
            payment.save()
        
        return jsonify({
            'success': True,
            'message': f'Synced ${difference/100:.2f} from Stripe',
            'stripe_refunded': actual_stripe_refunded,
            'db_refunded_before': total_refunded,
            'db_refunded_after': new_total_refunded
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': f'Stripe error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@admin_bp.route('/api/payments/<int:payment_id>/refund', methods=['POST'])
@login_required
@role_required('admin')
def refund_payment(payment_id):
    """Issue a refund for a payment or specific line item."""
    import stripe
    import os
    from flask import jsonify
    from src.models.stripe.payments import Payment
    from src.models.stripe.payment_line_items import PaymentLineItem
    
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    try:
        data = request.get_json()
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        if payment.status != 'succeeded':
            return jsonify({'error': 'Can only refund succeeded payments'}), 400
        
        if not payment.stripe_charge_id:
            return jsonify({'error': 'No Stripe charge ID found'}), 400
        
        # Check actual refund status from Stripe
        try:
            stripe_charge = stripe.Charge.retrieve(payment.stripe_charge_id)
            actual_stripe_refunded = stripe_charge.amount_refunded
        except stripe.error.StripeError:
            actual_stripe_refunded = 0
        
        # Calculate total already refunded in our database
        total_refunded = sum(
            item.amount_refunded if item.amount_refunded else 0 
            for item in payment.line_items.all()
        )
        
        # Sync with Stripe if there's a discrepancy
        if actual_stripe_refunded > total_refunded:
            return jsonify({
                'error': f'Database out of sync with Stripe. Stripe shows ${actual_stripe_refunded/100:.2f} refunded, but database shows ${total_refunded/100:.2f}. Please contact support to sync records before issuing additional refunds.'
            }), 409
        
        # Check if payment is already fully refunded
        if total_refunded >= payment.total_cost or actual_stripe_refunded >= payment.total_cost:
            return jsonify({'error': 'Payment has already been fully refunded. To issue additional compensation, use a store credit or manual payment system.'}), 400
        
        # Determine refund amount
        line_item_id = data.get('line_item_id')
        amount = data.get('amount')  # in cents
        reason = data.get('reason')
        full_refund = data.get('full_refund', False)
        
        if not amount or amount <= 0:
            return jsonify({'error': 'Invalid refund amount'}), 400
        
        # Calculate remaining refundable amount
        remaining_refundable = payment.total_cost - total_refunded
        
        # Validate amount doesn't exceed remaining refundable
        if amount > remaining_refundable:
            return jsonify({'error': f'Refund amount exceeds remaining refundable amount (${remaining_refundable/100:.2f})'}), 400
        
        # Create Stripe refund
        refund = stripe.Refund.create(
            charge=payment.stripe_charge_id,
            amount=amount,
            reason='requested_by_customer',
            metadata={
                'payment_id': payment_id,
                'line_item_id': line_item_id if line_item_id else None,
                'admin_reason': reason if reason else None
            }
        )
        
        # Update line item refunded amount if specific line item
        if line_item_id:
            line_item = PaymentLineItem.query.get(line_item_id)
            if line_item and line_item.payment_id == payment_id:
                current_refunded = line_item.amount_refunded if line_item.amount_refunded else 0
                line_item.amount_refunded = current_refunded + amount
                line_item.save()
        else:
            # For custom refunds without a specific line item, create a special line item
            from src.models.course_folder.payable_templates import PayableTemplate
            
            # Check if "Custom Refund" payable template exists, if not create it
            custom_template = PayableTemplate.query.filter_by(name='Custom Refund').first()
            if not custom_template:
                custom_template = PayableTemplate(
                    name='Custom Refund',
                    description='Administrative custom refund',
                    amount=0,  # Amount varies
                    is_required=False
                )
                custom_template.save()
            
            # Create a line item for this custom refund
            custom_line_item = PaymentLineItem(
                payment_id=payment_id,
                payable_template_id=custom_template.id,
                cost_of_item=amount,
                quantity=1
            )
            custom_line_item.amount_refunded = amount
            custom_line_item.save()
        
        # Update payment status if fully refunded
        # Recalculate after adding the new refund
        new_total_refunded = total_refunded + amount
        
        if new_total_refunded >= payment.total_cost:
            payment.status = 'refunded'
            payment.save()
        
        return jsonify({
            'success': True,
            'refund_id': refund.id,
            'amount': amount,
            'message': 'Refund issued successfully'
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': f'Stripe error: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500