"""
Course instance service for course instance business logic.
"""
from datetime import datetime
from src.models.course_folder.course_instances import CourseInstance
from src.models.course_folder.course_templates import CourseTemplate
from src.models.user_folder.instructors import Instructor
from src.models.user_folder.students import Student
from src.models.user_folder.users import User
from src.models.logs import Log


def get_all_course_instances():
    """Get all course instances."""
    return CourseInstance.get_all()


def get_course_instance_by_id(instance_id):
    """
    Get a course instance by ID.
    
    Args:
        instance_id: ID of the course instance
        
    Returns:
        CourseInstance or None
    """
    return CourseInstance.query.get(instance_id)


def create_course_instance(course_template_id, start_date, start_time, duration_days, 
                          location, max_students, c1_instructor_id, c2_instructor_id, 
                          notes, current_user_id):
    """
    Create a new course instance.
    
    Args:
        course_template_id: ID of the course template
        start_date: Start date string (YYYY-MM-DD)
        start_time: Start time string (HH:MM)
        duration_days: Duration in days
        location: Location string
        max_students: Maximum number of students
        c1_instructor_id: C1 instructor ID (optional)
        c2_instructor_id: C2 instructor ID (optional)
        notes: Additional notes
        current_user_id: ID of user creating the instance
        
    Returns:
        CourseInstance: The created instance
        
    Raises:
        ValueError: If validation fails
    """
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        start_time_obj = datetime.strptime(start_time, '%H:%M').time()
    except ValueError as e:
        raise ValueError(f"Invalid date or time format: {str(e)}")
    
    instance = CourseInstance(
        course_template_id=int(course_template_id),
        start_date=start_date_obj,
        start_time=start_time_obj,
        duration_days=int(duration_days),
        location=location,
        max_students=int(max_students),
        c1_instructor_id=int(c1_instructor_id) if c1_instructor_id else None,
        c2_instructor_id=int(c2_instructor_id) if c2_instructor_id else None,
        notes=notes
    )
    instance.save()
    
    # Log the creation
    course_template = CourseTemplate.query.get(instance.course_template_id)
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='create_course_instance',
        description=f'Course instance created: {course_template.name if course_template else "Unknown Course"} on {start_date_obj.strftime("%Y-%m-%d")}',
        user_id=current_user_id,
        target_type='course_instance',
        target_id=instance.id,
        status='success',
        extra_data={
            'course_template_id': instance.course_template_id,
            'course_name': course_template.name if course_template else None,
            'start_date': start_date_obj.isoformat(),
            'start_time': start_time_obj.isoformat(),
            'duration_days': instance.duration_days,
            'location': instance.location,
            'max_students': instance.max_students,
            'c1_instructor_id': instance.c1_instructor_id,
            'c2_instructor_id': instance.c2_instructor_id
        }
    )
    
    return instance


def instructor_signup_for_course(course_instance_id, role, instructor_id, current_user_id):
    """
    Instructor signs up for a course as C1 or C2.
    
    Args:
        course_instance_id: ID of the course instance
        role: 'c1' or 'c2'
        instructor_id: ID of the instructor
        current_user_id: ID of current user
        
    Returns:
        CourseInstance: The updated instance
        
    Raises:
        ValueError: If validation fails or slot is taken
    """
    if role not in ['c1', 'c2']:
        raise ValueError("Invalid role. Must be c1 or c2.")
    
    instance = CourseInstance.query.get(course_instance_id)
    if not instance:
        raise ValueError("Course instance not found")
    
    instructor = Instructor.query.get(instructor_id)
    if not instructor:
        raise ValueError("Instructor record not found")
    
    # Check if slot is available and assign
    if role == 'c1':
        if instance.c1_instructor_id:
            raise ValueError("C1 instructor slot is already taken")
        instance.c1_instructor_id = instructor.id
    else:  # c2
        if instance.c2_instructor_id:
            raise ValueError("C2 instructor slot is already taken")
        instance.c2_instructor_id = instructor.id
    
    instance.save()
    
    # Log the signup
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='course_signup',
        description=f'{instructor.user.first_name} {instructor.user.last_name} signed up as {role.upper()} instructor for {instance.course_template.name}',
        user_id=current_user_id,
        target_type='course_instance',
        target_id=instance.id,
        status='success',
        extra_data={
            'role': role.upper(),
            'course_name': instance.course_template.name,
            'start_date': instance.start_date.isoformat() if instance.start_date else None
        }
    )
    
    return instance


def instructor_withdraw_from_course(course_instance_id, instructor_id, current_user_id):
    """
    Instructor withdraws from a course.
    
    Args:
        course_instance_id: ID of the course instance
        instructor_id: ID of the instructor
        current_user_id: ID of current user
        
    Returns:
        dict: instance and role_dropped
        
    Raises:
        ValueError: If validation fails or instructor not assigned
    """
    instance = CourseInstance.query.get(course_instance_id)
    if not instance:
        raise ValueError("Course instance not found")
    
    instructor = Instructor.query.get(instructor_id)
    if not instructor:
        raise ValueError("Instructor record not found")
    
    # Remove instructor from course
    role_dropped = None
    if instance.c1_instructor_id == instructor.id:
        instance.c1_instructor_id = None
        role_dropped = 'C1'
    elif instance.c2_instructor_id == instructor.id:
        instance.c2_instructor_id = None
        role_dropped = 'C2'
    else:
        raise ValueError("You are not signed up for this course")
    
    instance.save()
    
    # Log the withdrawal
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='course_withdrawal',
        description=f'{instructor.user.first_name} {instructor.user.last_name} withdrew from {role_dropped} instructor position for {instance.course_template.name}',
        user_id=current_user_id,
        target_type='course_instance',
        target_id=instance.id,
        status='success',
        extra_data={
            'role': role_dropped,
            'course_name': instance.course_template.name,
            'start_date': instance.start_date.isoformat() if instance.start_date else None
        }
    )
    
    return {
        'instance': instance,
        'role_dropped': role_dropped
    }


def get_checkout_data(course_instance_id, student_id):
    """
    Get checkout data for a student enrolling in a course.
    
    Args:
        course_instance_id: ID of the course instance
        student_id: ID of the student
        
    Returns:
        dict: course_instance, student, course_name, course_price
        
    Raises:
        ValueError: If course or student not found
    """
    instance = CourseInstance.query.get(course_instance_id)
    if not instance:
        raise ValueError("Course not found")
    
    student = Student.query.get(student_id)
    if not student:
        raise ValueError("Student record not found")
    
    return {
        'course_instance': instance,
        'student': student,
        'course_name': instance.course_template.name if instance.course_template else 'Unknown Course',
        'course_price': instance.get_total_tuition() if instance.course_template else 0.0
    }
