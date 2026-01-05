from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from datetime import datetime
from src.models.user_folder.users import User
from src.models.user_folder.students import Student
from src.models.doorman import Doorman
from src.models.flask_mail.email_logs import Log
from src.utils.custom_decorators import login_required

# Create blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login-reg')
def loginReg():
    """Login page route."""
    context = {
        'all_users': User.query.all()
    }
    return render_template('public/auth/loginReg.html', **context)

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard redirect route based on user role."""
    if 'doorman_token' not in session:
        return redirect(url_for('auth.loginReg'))

    doorman = Doorman.get_by_token(session['doorman_token'])
    if not doorman:
        return redirect(url_for('auth.loginReg'))

    user = doorman.user

    if user.is_superuser:
        return redirect(url_for('superuser.dashboard'))
    elif user.is_admin:
        return redirect(url_for('admin.dashboard'))
    elif user.is_instructor:
        return redirect(url_for('instructor.dashboard'))
    else:
        return redirect(url_for('student.dashboard'))

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login form submission route."""
    # Logic for handling login form submission will go here
    from src.utils.password_management import verify_hash
    data = {**request.form}
    
    # get user
    user = User.query.filter_by(email=data.get('email')).first()

    if user and verify_hash(user.password_hash, data.get('password')):
        # create doorman session
        doorman_session = Doorman.create(user_id=user.id, ip_address=request.remote_addr,
                             user_agent=request.headers.get('User-Agent'))
        
        session['doorman_token'] = doorman_session.session_token
        
        # Log the login activity
        Log.create_log(
            log_type=Log.TYPE_AUTH,
            action='login',
            description=f'{user.first_name} {user.last_name} logged in',
            user_id=user.id,
            status='success',
            extra_data={'ip_address': request.remote_addr, 'user_agent': request.headers.get('User-Agent')}
        )

        # check to see if user is superuser, admin, instructor, or student and redirect accordingly
        if user.is_superuser:
            return redirect(url_for('superuser.dashboard'))
        elif user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif user.is_instructor:
            return redirect(url_for('instructor.dashboard'))
        else:
            return redirect(url_for('student.dashboard'))

    flash('Invalid email or password.', 'danger')
    return redirect(url_for('auth.loginReg'))

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registration form submission route."""
    from src.utils.password_management import generate_random_password

    data = {**request.form}
    course_id = data.get('course_id')  # Get course ID if provided

    password_generation = generate_random_password()
    # password_generation = 'Pass123!!'
    new_user = User.create(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        email=data.get('email'),
        password=password_generation,  # Pass plain password, User.set_password() will hash it
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # create a student account
    new_student = Student(
        user_id=new_user.id,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone_number=data.get('phone_number'),
        student_id=data.get('student_id')
    )
    new_student.save()
    
    # Log the registration activity
    Log.create_log(
        log_type=Log.TYPE_AUTH,
        action='register',
        description=f'New user registered: {new_user.first_name} {new_user.last_name}',
        user_id=new_user.id,
        target_type='user',
        target_id=new_user.id,
        status='success',
        extra_data={'email': new_user.email, 'ip_address': request.remote_addr}
    )
    
    # Need to send an email with temporary password and verification link here
    from src.services.flask_mail.email_service import send_email
    send_email(
        purpose='new_user',
        to_address=new_user.email,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        temp_password=password_generation,
        login_link=url_for('auth.loginReg', _external=True),
    )


    doorman_session = Doorman.create(user_id=new_user.id, ip_address=request.remote_addr,
                         user_agent=request.headers.get('User-Agent'))
    
    session['doorman_token'] = doorman_session.session_token

    if 'doorman_token' in session:
        # If course_id is provided, redirect to checkout
        if course_id:
            return redirect(url_for('student.checkout', course_instance_id=course_id))
        return redirect(url_for('student.dashboard'))

    return redirect(url_for('auth.loginReg'))

@auth_bp.route('/logout')
def logout():
    """Logout route."""
    if 'doorman_token' in session:
        doorman = Doorman.get_by_token(session['doorman_token'])
        if doorman:
            user = doorman.user
            # Log the logout activity
            Log.create_log(
                log_type=Log.TYPE_AUTH,
                action='logout',
                description=f'{user.first_name} {user.last_name} logged out',
                user_id=user.id,
                status='success',
                extra_data={'ip_address': request.remote_addr}
            )
            doorman.sign_out()
        session.pop('doorman_token', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.loginReg'))


@auth_bp.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """Delete a user and their related records."""
    from src.models.user_folder.students import Student
    from src.models.user_folder.instructors import Instructor
    from src.models.user_folder.admins import Admin
    from src.models.user_folder.superusers import Superuser
    
    try:
        user = User.query.get_or_404(user_id)
        user_name = f"{user.first_name} {user.last_name}"
        
        # Log the deletion activity before deleting
        Log.create_log(
            log_type=Log.TYPE_USER_ACTION,
            action='delete',
            description=f'User account deleted: {user_name}',
            user_id=user_id,
            target_type='user',
            target_id=user_id,
            status='success',
            extra_data={'email': user.email, 'deleted_by': 'self'}
        )
        
        # Delete related records in order to avoid foreign key constraints
        Doorman.query.filter_by(user_id=user_id).delete()
        Student.query.filter_by(user_id=user_id).delete()
        Instructor.query.filter_by(user_id=user_id).delete()
        Admin.query.filter_by(user_id=user_id).delete()
        Superuser.query.filter_by(user_id=user_id).delete()
        
        # Delete the user
        user.delete()
        
        flash(f'User {user_name} has been deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('auth.loginReg'))
