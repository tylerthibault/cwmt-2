from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, session
from src.models.user_folder import admins, users
from src.models.doorman import Doorman
from src.models.main import db
from src.models.flask_mail.email_logs import Log
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

        # Log the action
        current_user = Doorman.get_by_token(session['doorman_token']).user
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='grant_admin',
            description=f'Admin privileges granted to {user.email}',
            user_id=current_user.id,
            target_type='user',
            target_id=user.id,
            status='success',
            extra_data={
                'target_email': user.email,
                'target_user_id': user.id,
                'admin_id': new_admin.id
            }
        )

        return redirect(url_for('admin.dashboard'))

    if status == 'remove':
        # Find the admin entry
        existing_admin = admins.Admin.query.filter_by(user_id=user.id).first()
        if not existing_admin:
            return "User is not an admin", 400

        # Delete the admin entry
        existing_admin.delete()

        # Log the action
        current_user = Doorman.get_by_token(session['doorman_token']).user
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='revoke_admin',
            description=f'Admin privileges revoked from {user.email}',
            user_id=current_user.id,
            target_type='user',
            target_id=user.id,
            status='success',
            extra_data={
                'target_email': user.email,
                'target_user_id': user.id
            }
        )

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

@admin_bp.route('/students/<int:student_id>/toggle-status', methods=['POST'])
@login_required
@role_required('admin')
def toggle_student_status(student_id):
    """Route to activate or deactivate a student account."""
    from flask import flash
    from src.models.user_folder.students import Student
    
    student = Student.query.get(student_id)
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('admin.students'))
    
    if not student.user:
        flash('Student has no associated user account.', 'danger')
        return redirect(url_for('admin.view_student', student_id=student_id))
    
    try:
        # Toggle the is_active status
        student.user.is_active = not student.user.is_active
        student.user.save()
        
        # Also update the student record
        student.is_active = student.user.is_active
        student.save()
        
        status_text = 'activated' if student.user.is_active else 'deactivated'
        flash(f'Student account has been {status_text} successfully.', 'success')
        
        # Log the action
        current_user = Doorman.get_by_token(session['doorman_token']).user
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='toggle_account_status',
            description=f'Student account {status_text}: {student.user.email}',
            user_id=current_user.id,
            target_type='student',
            target_id=student.id,
            status='success',
            extra_data={
                'student_email': student.user.email,
                'new_status': 'active' if student.user.is_active else 'inactive',
                'action_type': status_text
            }
        )
        
    except Exception as e:
        flash(f'Error updating student status: {str(e)}', 'danger')
    
    return redirect(url_for('admin.view_student', student_id=student_id))

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
        
        # Log the refund
        current_user = Doorman.get_by_token(session['doorman_token']).user
        Log.create_log(
            log_type=Log.TYPE_PAYMENT,
            action='issue_refund',
            description=f'Refund of ${amount/100:.2f} issued for payment #{payment_id}',
            user_id=current_user.id,
            target_type='payment',
            target_id=payment_id,
            status='success',
            extra_data={
                'refund_id': refund.id,
                'amount': amount,
                'reason': reason,
                'student_email': payment.student.user.email if payment.student and payment.student.user else None,
                'line_item_id': line_item_id,
                'full_refund': full_refund
            }
        )
        
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


# Unenrollment Requests
@admin_bp.route('/unenrollment-requests')
@login_required
@role_required('admin')
def unenrollment_requests():
    """View all unenrollment requests."""
    from src.models.course_folder.enrollments import Enrollment
    
    status_filter = request.args.get('status', 'pending')
    
    if status_filter == 'pending':
        enrollments = Enrollment.get_pending_unenrollments()
    elif status_filter == 'processed':
        enrollments = Enrollment.query.filter(
            Enrollment.unenrollment_requested == True,
            Enrollment.unenrollment_processed_at.isnot(None)
        ).order_by(Enrollment.unenrollment_processed_at.desc()).all()
    else:  # all
        enrollments = Enrollment.query.filter_by(unenrollment_requested=True).order_by(Enrollment.unenrollment_requested_at.desc()).all()
    
    # Count by status
    pending_count = Enrollment.query.filter_by(unenrollment_requested=True, status='enrolled').count()
    processed_count = Enrollment.query.filter(
        Enrollment.unenrollment_requested == True,
        Enrollment.unenrollment_processed_at.isnot(None)
    ).count()
    
    context = {
        'current_user': Doorman.get_by_token(session['doorman_token']).user,
        'enrollments': enrollments,
        'status_filter': status_filter,
        'pending_count': pending_count,
        'processed_count': processed_count
    }
    return render_template('private/admins/unenrollment_requests/index.html', **context)


@admin_bp.route('/api/enrollments/<int:enrollment_id>/approve-unenrollment', methods=['POST'])
@login_required
@role_required('admin')
def approve_unenrollment(enrollment_id):
    """Approve an unenrollment request and process refund."""
    import stripe
    import os
    from flask import jsonify
    from src.models.course_folder.enrollments import Enrollment
    from src.models.stripe.payments import Payment
    from src.models.stripe.payment_line_items import PaymentLineItem
    from src.models.course_folder.payable_templates import PayableTemplate
    
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    try:
        data = request.get_json()
        enrollment = Enrollment.query.get(enrollment_id)
        
        if not enrollment:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        if not enrollment.unenrollment_requested:
            return jsonify({'error': 'No unenrollment request found'}), 400
        
        if enrollment.status != 'enrolled':
            return jsonify({'error': 'Enrollment is not active'}), 400
        
        # Get refund percentage from request data or use default
        refund_percentage = data.get('refund_percentage', enrollment.refund_percentage)
        admin_notes = data.get('admin_notes', '')
        
        # Get current user
        current_user = Doorman.get_by_token(session['doorman_token']).user
        
        # Get payment for this enrollment
        payment = enrollment.get_payment()
        
        refund_amount = 0
        if payment and payment.status == 'succeeded' and payment.stripe_charge_id:
            # Calculate refund amount (e.g., 80% of total)
            refund_amount = int((payment.total_cost * refund_percentage) / 100)
            
            if refund_amount > 0:
                # Check actual Stripe refund status
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
                
                # Check if there's enough remaining to refund
                remaining_refundable = payment.total_cost - max(total_refunded, actual_stripe_refunded)
                
                if refund_amount > remaining_refundable:
                    refund_amount = remaining_refundable
                
                if refund_amount > 0:
                    # Create Stripe refund
                    refund = stripe.Refund.create(
                        charge=payment.stripe_charge_id,
                        amount=refund_amount,
                        reason='requested_by_customer',
                        metadata={
                            'payment_id': payment.id,
                            'enrollment_id': enrollment_id,
                            'refund_percentage': refund_percentage
                        }
                    )
                    
                    # Create "Unenrollment Refund" line item
                    unenroll_template = PayableTemplate.query.filter_by(name='Unenrollment Refund').first()
                    if not unenroll_template:
                        unenroll_template = PayableTemplate(
                            name='Unenrollment Refund',
                            description=f'Refund for unenrollment ({refund_percentage}% of payment)',
                            amount=0,
                            is_required=False
                        )
                        unenroll_template.save()
                    
                    # Create line item for this refund
                    refund_line_item = PaymentLineItem(
                        payment_id=payment.id,
                        payable_template_id=unenroll_template.id,
                        cost_of_item=refund_amount,
                        quantity=1
                    )
                    refund_line_item.amount_refunded = refund_amount
                    refund_line_item.save()
                    
                    # Update payment status if fully refunded
                    new_total_refunded = total_refunded + refund_amount
                    if new_total_refunded >= payment.total_cost:
                        payment.status = 'refunded'
                        payment.save()
        
        # Update enrollment - approve unenrollment
        enrollment.refund_percentage = refund_percentage
        enrollment.approve_unenrollment(current_user.id, admin_notes)
        
        # Log the approval
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='approve_unenrollment',
            description=f'Unenrollment approved for {enrollment.student.user.email} from {enrollment.course_instance.course_template.name}',
            user_id=current_user.id,
            target_type='enrollment',
            target_id=enrollment_id,
            status='success',
            extra_data={
                'student_email': enrollment.student.user.email,
                'course_name': enrollment.course_instance.course_template.name,
                'refund_percentage': refund_percentage,
                'refund_amount': refund_amount,
                'admin_notes': admin_notes,
                'payment_id': payment.id if payment else None
            }
        )
        
        return jsonify({
            'success': True,
            'message': f'Unenrollment approved and {refund_percentage}% refund issued',
            'refund_amount': refund_amount
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': f'Stripe error: {str(e)}'}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@admin_bp.route('/logs')
@login_required
@role_required('admin')
def activity_logs():
    """Route to view activity logs including email logs."""
    from flask import flash
    from src.models.flask_mail.email_logs import Log
    from src.models.user_folder.users import User
    
    # Get filter parameters
    page = request.args.get('page', 1, type=int)
    per_page = 50
    log_type_filter = request.args.get('log_type', '')
    status_filter = request.args.get('status', '')
    purpose_filter = request.args.get('purpose', '')
    action_filter = request.args.get('action', '')
    user_filter = request.args.get('user_id', '')
    
    # Build query
    query = Log.query
    
    # Filter by log type (show all types by default)
    if log_type_filter:
        query = query.filter_by(log_type=log_type_filter)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if purpose_filter:
        query = query.filter_by(purpose=purpose_filter)
    
    if action_filter:
        query = query.filter_by(action=action_filter)
    
    if user_filter:
        query = query.filter_by(user_id=user_filter)
    
    # Order by most recent first
    query = query.order_by(Log.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    logs = pagination.items
    
    # Get unique values for filters
    purposes = db.session.query(Log.purpose).filter(Log.log_type == Log.TYPE_EMAIL).distinct().all()
    purposes = [p[0] for p in purposes if p[0]]
    
    log_types = db.session.query(Log.log_type).distinct().all()
    log_types = [lt[0] for lt in log_types if lt[0]]
    
    actions = db.session.query(Log.action).distinct().all()
    actions = [a[0] for a in actions if a[0]]
    
    # Get users who have logs
    user_ids = db.session.query(Log.user_id).filter(Log.user_id.isnot(None)).distinct().all()
    users_with_logs = User.query.filter(User.id.in_([uid[0] for uid in user_ids])).all()
    
    statuses = ['pending', 'sent', 'success', 'failed']
    
    context = {
        'current_user': Doorman.get_by_token(session['doorman_token']).user,
        'logs': logs,
        'pagination': pagination,
        'purposes': purposes,
        'statuses': statuses,
        'log_types': log_types,
        'actions': actions,
        'users_with_logs': users_with_logs,
        'current_log_type': log_type_filter,
        'current_status': status_filter,
        'current_purpose': purpose_filter,
        'current_action': action_filter,
        'current_user_id': user_filter
    }
    return render_template('private/admins/logs/index.html', **context)


@admin_bp.route('/api/enrollments/<int:enrollment_id>/deny-unenrollment', methods=['POST'])
@login_required
@role_required('admin')
def deny_unenrollment(enrollment_id):
    """Deny an unenrollment request."""
    from flask import jsonify
    from src.models.course_folder.enrollments import Enrollment
    
    try:
        data = request.get_json()
        enrollment = Enrollment.query.get(enrollment_id)
        
        if not enrollment:
            return jsonify({'error': 'Enrollment not found'}), 404
        
        if not enrollment.unenrollment_requested:
            return jsonify({'error': 'No unenrollment request found'}), 400
        
        admin_notes = data.get('admin_notes', '')
        
        # Get current user
        current_user = Doorman.get_by_token(session['doorman_token']).user
        
        # Deny unenrollment
        enrollment.deny_unenrollment(current_user.id, admin_notes)
        
        # Log the denial
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='deny_unenrollment',
            description=f'Unenrollment denied for {enrollment.student.user.email} from {enrollment.course_instance.course_template.name}',
            user_id=current_user.id,
            target_type='enrollment',
            target_id=enrollment_id,
            status='success',
            extra_data={
                'student_email': enrollment.student.user.email,
                'course_name': enrollment.course_instance.course_template.name,
                'admin_notes': admin_notes
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Unenrollment request denied'
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@admin_bp.route('/enroll-student')
@login_required
@role_required('admin')
def enroll_student_form():
    """Show form to manually enroll a student in a course."""
    from src.models.user_folder.students import Student
    from src.models.course_folder.course_instances import CourseInstance
    
    # Get all students and course instances
    students = Student.query.join(users.User).order_by(users.User.email).all()
    courses = CourseInstance.query.order_by(CourseInstance.start_date.desc()).all()
    
    context = {
        'current_user': Doorman.get_by_token(session['doorman_token']).user,
        'students': students,
        'courses': courses
    }
    return render_template('private/admins/enrollments/create.html', **context)


@admin_bp.route('/api/enroll-student', methods=['POST'])
@login_required
@role_required('admin')
def enroll_student():
    """Manually enroll a student in a course (with or without creating account)."""
    from flask import jsonify
    from src.models.user_folder.students import Student
    from src.models.course_folder.course_instances import CourseInstance
    from src.models.course_folder.enrollments import Enrollment
    from src.models.stripe.payments import Payment
    from src.models.stripe.payment_line_items import PaymentLineItem
    from src.utils.password_management import generate_random_password
    
    try:
        data = request.get_json()
        course_instance_id = data.get('course_instance_id')
        student_id = data.get('student_id')  # If existing student
        create_new = data.get('create_new', False)  # If creating new student
        
        # New student data (if creating)
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        
        # Enrollment options
        waive_payment = data.get('waive_payment', False)
        admin_notes = data.get('admin_notes', '')
        
        if not course_instance_id:
            return jsonify({'error': 'Course instance ID is required'}), 400
        
        # Get course instance
        course_instance = CourseInstance.query.get(course_instance_id)
        if not course_instance:
            return jsonify({'error': 'Course not found'}), 404
        
        # Get or create student
        if create_new:
            # Validate new student data
            if not first_name or not last_name or not email:
                return jsonify({'error': 'First name, last name, and email are required'}), 400
            
            # Check if email already exists
            existing_user = users.User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'error': 'A user with this email already exists'}), 400
            
            # Create new user account
            temp_password = generate_random_password()
            new_user = users.User(
                email=email,
                password=temp_password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone if phone else None,
                is_active=True
            )
            new_user.save()
            
            # Create student record
            student = Student(
                user_id=new_user.id,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            student.save()
            
            student_created = True
            temp_password_for_log = temp_password
        else:
            # Use existing student
            if not student_id:
                return jsonify({'error': 'Student ID is required'}), 400
            
            student = Student.query.get(student_id)
            if not student:
                return jsonify({'error': 'Student not found'}), 404
            
            student_created = False
            temp_password_for_log = None
        
        # Check if already enrolled
        if Enrollment.enrollment_exists(student.id, course_instance_id):
            return jsonify({'error': 'Student is already enrolled in this course'}), 400
        
        # Check if course is full
        current_enrollments = Enrollment.count_active_enrollments_for_course(course_instance_id)
        if current_enrollments >= course_instance.max_students:
            return jsonify({'error': 'Course is full'}), 400
        
        # Create enrollment
        enrollment = Enrollment(
            student_id=student.id,
            course_instance_id=course_instance_id,
            status='enrolled'
        )
        enrollment.save()
        
        # Create payment record if not waived
        payment = None
        if not waive_payment and course_instance.course_template:
            # Calculate total cost
            total_cost = 0
            line_items_data = []
            
            for payable_template in course_instance.course_template.payable_templates.all():
                if payable_template.is_required:
                    amount_in_cents = int(payable_template.amount * 100)
                    total_cost += amount_in_cents
                    line_items_data.append({
                        'payable_template_id': payable_template.id,
                        'amount': amount_in_cents
                    })
            
            if total_cost > 0:
                # Create payment record (marked as admin-enrolled)
                payment = Payment(
                    student_id=student.id,
                    course_instance_id=course_instance_id,
                    total_cost=total_cost,
                    customer_email=student.user.email if student.user else email,
                    status='succeeded',  # Mark as succeeded since admin enrolled
                    stripe_payment_intent_id=f'admin_enrolled_{enrollment.id}'
                )
                payment.save()
                
                # Create line items
                for item_data in line_items_data:
                    line_item = PaymentLineItem(
                        payment_id=payment.id,
                        payable_template_id=item_data['payable_template_id'],
                        cost_of_item=item_data['amount'],
                        quantity=1
                    )
                    line_item.save()
                
                # Link payment to enrollment
                enrollment.payment_id = payment.id
                enrollment.save()
        
        # Log the manual enrollment
        current_user = Doorman.get_by_token(session['doorman_token']).user
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='admin_enroll_student',
            description=f'Admin manually enrolled {student.user.email if student.user else email} in {course_instance.course_template.name if course_instance.course_template else "course"}',
            user_id=current_user.id,
            target_type='enrollment',
            target_id=enrollment.id,
            status='success',
            extra_data={
                'student_id': student.id,
                'student_email': student.user.email if student.user else email,
                'course_instance_id': course_instance_id,
                'course_name': course_instance.course_template.name if course_instance.course_template else None,
                'student_created': student_created,
                'waive_payment': waive_payment,
                'admin_notes': admin_notes,
                'temp_password': temp_password_for_log if student_created else None,
                'payment_id': payment.id if payment else None
            }
        )
        
        response_data = {
            'success': True,
            'message': 'Student enrolled successfully',
            'enrollment_id': enrollment.id,
            'student_id': student.id
        }
        
        if student_created:
            response_data['new_account'] = True
            response_data['temp_password'] = temp_password_for_log
            response_data['email'] = email
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500