"""Business logic service for admin operations."""
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from src.models.main import db
from src.models.logs import Log


def get_dashboard_stats():
    """Get dashboard statistics for admin overview."""
    from src.models.user_folder.students import Student
    from src.models.course_folder.course_instances import CourseInstance
    from src.models.course_folder.enrollments import Enrollment
    from src.models.stripe.payments import Payment
    
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    last_month_start = datetime(now.year if now.month > 1 else now.year - 1, 
                                now.month - 1 if now.month > 1 else 12, 1)
    next_week = now + timedelta(days=7)
    
    stats = {
        'total_students': Student.query.count(),
        'active_courses': CourseInstance.query.filter(
            CourseInstance.status.in_(['scheduled', 'active']),
            CourseInstance.start_date >= month_start.date()
        ).count(),
        'pending_enrollments': Enrollment.query.filter_by(status='enrolled').count(),
        'upcoming_courses': CourseInstance.query.filter(
            CourseInstance.status == 'scheduled',
            CourseInstance.start_date >= now.date(),
            CourseInstance.start_date <= next_week.date()
        ).count()
    }
    
    # Calculate revenue
    revenue_this_month = db.session.query(func.sum(Payment.total_cost)).filter(
        Payment.status == 'succeeded',
        extract('year', Payment.created_at) == now.year,
        extract('month', Payment.created_at) == now.month
    ).scalar() or 0
    
    revenue_last_month = db.session.query(func.sum(Payment.total_cost)).filter(
        Payment.status == 'succeeded',
        extract('year', Payment.created_at) == last_month_start.year,
        extract('month', Payment.created_at) == last_month_start.month
    ).scalar() or 0
    
    stats['revenue_this_month'] = revenue_this_month / 100
    stats['revenue_change'] = 0
    if revenue_last_month > 0:
        stats['revenue_change'] = ((revenue_this_month - revenue_last_month) / revenue_last_month) * 100
    
    stats['current_date'] = now
    
    return stats


def grant_admin_privileges(user, granted_by_user_id):
    """Grant admin privileges to a user."""
    from src.models.user_folder.admins import Admin
    
    existing_admin = Admin.query.filter_by(user_id=user.id).first()
    if existing_admin:
        raise ValueError('User is already an admin')
    
    new_admin = Admin.create(user_id=user.id)
    
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='grant_admin',
        description=f'Admin privileges granted to {user.email}',
        user_id=granted_by_user_id,
        target_type='user',
        target_id=user.id,
        status='success',
        extra_data={
            'target_email': user.email,
            'target_user_id': user.id,
            'admin_id': new_admin.id
        }
    )
    
    return new_admin


def revoke_admin_privileges(user, revoked_by_user_id):
    """Revoke admin privileges from a user."""
    from src.models.user_folder.admins import Admin
    
    existing_admin = Admin.query.filter_by(user_id=user.id).first()
    if not existing_admin:
        raise ValueError('User is not an admin')
    
    existing_admin.delete()
    
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='revoke_admin',
        description=f'Admin privileges revoked from {user.email}',
        user_id=revoked_by_user_id,
        target_type='user',
        target_id=user.id,
        status='success',
        extra_data={
            'target_email': user.email,
            'target_user_id': user.id
        }
    )


def get_filtered_students(search='', status='', enrollments='', limit='50'):
    """Get filtered list of students based on criteria."""
    from src.models.user_folder.students import Student
    from src.models.user_folder.users import User
    
    query = Student.query.join(User).order_by(Student.id.desc())
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Student.first_name.ilike(search_pattern)) |
            (Student.last_name.ilike(search_pattern)) |
            (User.email.ilike(search_pattern))
        )
    
    if status == 'active':
        query = query.filter(Student.created_by_student_id.is_(None))
    elif status == 'guest':
        query = query.filter(Student.created_by_student_id.isnot(None))
    
    filtered_students = query.all()
    
    if enrollments == 'has':
        filtered_students = [s for s in filtered_students if s.enrollments.count() > 0]
    elif enrollments == 'none':
        filtered_students = [s for s in filtered_students if s.enrollments.count() == 0]
    
    if limit != 'all':
        try:
            limit_num = int(limit)
            filtered_students = filtered_students[:limit_num]
        except ValueError:
            filtered_students = filtered_students[:50]
    
    return filtered_students


def get_student_counts():
    """Get counts of students by category."""
    from src.models.user_folder.students import Student
    
    total = Student.query.count()
    active = Student.query.filter(Student.created_by_student_id.is_(None)).count()
    guest = Student.query.filter(Student.created_by_student_id.isnot(None)).count()
    enrolled = sum(1 for s in Student.query.all() if s.enrollments.count() > 0)
    
    return {
        'total_count': total,
        'active_count': active,
        'guest_count': guest,
        'enrolled_count': enrolled
    }


def export_students_to_csv(students):
    """Export students to CSV format."""
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Type', 'Relationship', 'Enrollments', 'Registered'])
    
    for student in students:
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
    
    return output.getvalue()


def toggle_student_active_status(student, toggled_by_user_id):
    """Toggle a student's active status."""
    if not student.user:
        raise ValueError('Student has no associated user account')
    
    student.user.is_active = not student.user.is_active
    student.user.save()
    
    student.is_active = student.user.is_active
    student.save()
    
    status_text = 'activated' if student.user.is_active else 'deactivated'
    
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='toggle_account_status',
        description=f'Student account {status_text}: {student.user.email}',
        user_id=toggled_by_user_id,
        target_type='student',
        target_id=student.id,
        status='success',
        extra_data={
            'student_email': student.user.email,
            'new_status': 'active' if student.user.is_active else 'inactive',
            'action_type': status_text
        }
    )
    
    return status_text


def get_filtered_logs(page=1, per_page=50, log_type='', status='', purpose='', action='', user_id=''):
    """Get filtered activity logs."""
    from src.models.logs import Log
    
    query = Log.query
    
    if log_type:
        query = query.filter_by(log_type=log_type)
    if status:
        query = query.filter_by(status=status)
    if purpose:
        query = query.filter_by(purpose=purpose)
    if action:
        query = query.filter_by(action=action)
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    query = query.order_by(Log.created_at.desc())
    
    return query.paginate(page=page, per_page=per_page, error_out=False)


def get_log_filter_options():
    """Get unique values for log filtering."""
    from src.models.logs import Log
    from src.models.user_folder.users import User
    
    purposes = db.session.query(Log.purpose).filter(Log.log_type == Log.TYPE_EMAIL).distinct().all()
    purposes = [p[0] for p in purposes if p[0]]
    
    log_types = db.session.query(Log.log_type).distinct().all()
    log_types = [lt[0] for lt in log_types if lt[0]]
    
    actions = db.session.query(Log.action).distinct().all()
    actions = [a[0] for a in actions if a[0]]
    
    user_ids = db.session.query(Log.user_id).filter(Log.user_id.isnot(None)).distinct().all()
    users_with_logs = User.query.filter(User.id.in_([uid[0] for uid in user_ids])).all()
    
    statuses = ['pending', 'sent', 'success', 'failed']
    
    return {
        'purposes': purposes,
        'log_types': log_types,
        'actions': actions,
        'users_with_logs': users_with_logs,
        'statuses': statuses
    }
