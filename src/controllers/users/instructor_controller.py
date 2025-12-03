"""
Instructor Controller
Handles instructor-specific routes for course schedule management
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps

from src.controllers.auth_controller import login_required
from src.models.courses_model import Course
from src.models.user import User
from src.models.roles import Role
from src.models.logbook import Logbook
from src.logic.course_logic import CourseLogic, CourseLogicError
from src.models import db
from datetime import datetime, date, timedelta

# Create blueprint for instructor routes
instructor_bp = Blueprint('instructor', __name__, url_prefix='/instructor')


def get_current_user():
    """Get the current logged-in user from session"""
    token = session.get('token')
    if not token:
        return None
    
    logbook_entry = Logbook.query.filter_by(token=token, has_logged_out=False).first()
    if not logbook_entry:
        return None
    
    return User.query.get(logbook_entry.user_id)


def instructor_required(f):
    """Decorator to require instructor role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Check if user has instructor role
        instructor_role = Role.query.filter_by(name='instructor').first()
        if instructor_role not in user.role_list:
            flash('You must be an instructor to access this page.', 'danger')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    return decorated_function


@instructor_bp.route('/')
@instructor_bp.route('/dashboard')
@login_required
@instructor_required
def dashboard():
    """
    Instructor dashboard - main landing page for instructors.
    Shows upcoming courses and instructor schedule overview.
    """
    try:
        current_user = get_current_user()
        
        # Get instructor's assigned courses
        today = date.today()
        my_courses = Course.query.filter(
            db.or_(
                Course.instructor1_id == current_user.id,
                Course.instructor2_id == current_user.id
            ),
            Course.course_date >= today
        ).order_by(
            Course.course_date,
            Course.course_time
        ).limit(5).all()
        
        # Get available courses (no instructor assigned yet)
        available_courses = Course.query.filter(
            Course.instructor1_id == None,
            Course.course_date >= today,
            Course.status == 'scheduled'
        ).order_by(
            Course.course_date,
            Course.course_time
        ).limit(5).all()
        
        return render_template(
            'private/instructor/dashboard/index.html',
            my_courses=my_courses,
            available_courses=available_courses,
            current_user=current_user,
            user=current_user,
            current_role='instructor'
        )
        
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        current_user = get_current_user()
        return render_template(
            'private/instructor/dashboard/index.html',
            my_courses=[],
            available_courses=[],
            current_user=current_user,
            user=current_user,
            current_role='instructor'
        )


@instructor_bp.route('/schedule')
@login_required
@instructor_required
def schedule():
    """
    Display the instructor schedule page with upcoming courses.
    Shows all scheduled courses and allows instructors to sign up.
    """
    try:
        current_user = get_current_user()
        
        # Get all upcoming courses (scheduled status, future dates)
        today = date.today()
        upcoming_courses = Course.query.filter(
            Course.course_date >= today,
            Course.status == 'scheduled'
        ).order_by(
            Course.course_date,
            Course.course_time
        ).all()
        
        # Convert to dicts with relationships
        courses_data = []
        for course in upcoming_courses:
            course_dict = course.to_dict(include_enrollments=True, include_template=True)
            courses_data.append(course)
        
        return render_template(
            'private/instructor/shedule/index.html',
            courses=courses_data,
            current_user=current_user,
            user=current_user,
            current_role='instructor'
        )
        
    except Exception as e:
        flash(f'Error loading schedule: {str(e)}', 'danger')
        current_user = get_current_user()
        return render_template(
            'private/instructor/shedule/index.html',
            courses=[],
            current_user=current_user,
            user=current_user,
            current_role='instructor'
        )


@instructor_bp.route('/schedule/signup/<int:course_id>', methods=['POST'])
@login_required
@instructor_required
def signup_for_course(course_id):
    """
    Sign up the current instructor for a course.
    Assigns them to the first available instructor slot.
    """
    try:
        current_user = get_current_user()
        
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Check if course is in the past
        if course.course_date < date.today():
            return jsonify({'error': 'Cannot sign up for past courses'}), 400
        
        # Check if course is not scheduled
        if course.status != 'scheduled':
            return jsonify({'error': f'Cannot sign up for {course.status} courses'}), 400
        
        # Check if user is already assigned
        if course.instructor1_id == current_user.id or course.instructor2_id == current_user.id:
            return jsonify({'error': 'You are already assigned to this course'}), 400
        
        # Assign to first available slot
        if not course.instructor1_id:
            course.instructor1_id = current_user.id
            slot = 'Instructor 1'
        elif not course.instructor2_id:
            course.instructor2_id = current_user.id
            slot = 'Instructor 2'
        else:
            return jsonify({'error': 'Course is already fully staffed'}), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully signed up as {slot}',
            'course_id': course_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@instructor_bp.route('/schedule/remove/<int:course_id>', methods=['POST'])
@login_required
@instructor_required
def remove_from_course(course_id):
    """
    Remove the current instructor from a course.
    """
    try:
        current_user = get_current_user()
        
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Check if user is assigned to this course
        if course.instructor1_id != current_user.id and course.instructor2_id != current_user.id:
            return jsonify({'error': 'You are not assigned to this course'}), 400
        
        # Check if course is in the past
        if course.course_date < date.today():
            return jsonify({'error': 'Cannot remove yourself from past courses'}), 400
        
        # Check if course is not scheduled
        if course.status != 'scheduled':
            return jsonify({'error': f'Cannot remove yourself from {course.status} courses'}), 400
        
        # Remove user from appropriate slot
        if course.instructor1_id == current_user.id:
            course.instructor1_id = None
            slot = 'Instructor 1'
        else:
            course.instructor2_id = None
            slot = 'Instructor 2'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully removed from {slot} slot',
            'course_id': course_id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@instructor_bp.route('/my-courses')
@login_required
@instructor_required
def my_courses():
    """
    Display courses where the current user is assigned as an instructor.
    """
    try:
        current_user = get_current_user()
        courses = CourseLogic.get_courses_for_instructor(current_user.id)
        
        return render_template(
            'private/instructor/my_courses.html',
            courses=courses,
            current_user=current_user,
            user=current_user,
            current_role='instructor'
        )
        
    except Exception as e:
        flash(f'Error loading your courses: {str(e)}', 'danger')
        return redirect(url_for('instructor.schedule'))


# ============================================================================
# STUDENT VIEWING ROUTES (Instructor Access)
# ============================================================================

@instructor_bp.route('/students/<int:student_id>')
@instructor_required
def view_student(student_id):
    """
    View student details (instructor can view students in their courses).
    
    Args:
        student_id: StudentProfile ID (not User ID)
    """
    from src.logic.student_logic import StudentLogic
    from src.models.student_profile import StudentProfile
    
    current_user = get_current_user()
    
    # Get student profile
    student = StudentProfile.query.get_or_404(student_id)
    
    # Get all enrollments for this student
    enrollments = StudentLogic.get_student_courses(student_id)
    
    # Calculate GPA
    gpa = StudentLogic.calculate_student_gpa(student_id)
    
    return render_template(
        'private/instructor/students/detail.html',
        student=student,
        enrollments=enrollments,
        gpa=gpa,
        current_user=current_user,
        user=current_user,
        current_role='instructor',
        page_title=f'Student: {student.user.first_name} {student.user.last_name}'
    )


@instructor_bp.route('/course/<int:course_id>/students')
@instructor_required
def course_students(course_id):
    """
    View all students enrolled in a specific course.
    Only accessible if the instructor is assigned to the course.
    
    Args:
        course_id: Course ID
    """
    from src.logic.student_logic import StudentLogic
    
    current_user = get_current_user()
    course = Course.query.get_or_404(course_id)
    
    # Verify instructor is assigned to this course
    if course.instructor1_id != current_user.id and course.instructor2_id != current_user.id:
        flash('You do not have access to this course', 'error')
        return redirect(url_for('instructor.schedule'))
    
    # Get all students in this course
    enrollments = StudentLogic.get_course_students(course_id, status='active')
    
    return render_template(
        'private/instructor/students/course_roster.html',
        course=course,
        enrollments=enrollments,
        current_user=current_user,
        user=current_user,
        current_role='instructor',
        page_title=f'Students in {course.template.name if course.template else "Course"}'
    )
