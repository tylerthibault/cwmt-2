"""
Course template service for course template business logic.
"""
from src.models.course_folder.course_templates import CourseTemplate
from src.models.course_folder.payable_templates import PayableTemplate
from src.models.logs import Log


def get_all_course_templates_with_payables():
    """
    Get all course templates with their associated payables.
    
    Returns:
        dict: course_templates and payable_templates lists
    """
    return {
        'course_templates': CourseTemplate.get_all(),
        'payable_templates': PayableTemplate.get_all()
    }


def create_course_template(name, experience_level, duration_days, max_students, tuition, color, current_user_id, description=None, short_blurb=None, is_featured=False, is_taxable=True):
    """
    Create a new course template with associated tuition payable.
    
    Args:
        name: Name of the course
        experience_level: Experience level (beginner, intermediate, advanced)
        duration_days: Duration in days
        max_students: Maximum number of students
        tuition: Tuition amount
        color: Color for calendar display
        current_user_id: ID of user creating the template
        description: Full course description (optional)
        short_blurb: Short description for cards (optional)
        is_featured: Whether to show on landing page (optional)
        is_test_session: Whether this is a test session (tax exempt) (optional)
        
    Returns:
        CourseTemplate: The created template
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    if not all([name, experience_level, duration_days, max_students, tuition]):
        raise ValueError("All fields are required")
    
    try:
        duration_int = int(duration_days)
        max_students_int = int(max_students)
        tuition_float = float(tuition)
    except (ValueError, TypeError):
        raise ValueError("Duration, max students, and tuition must be valid numbers")
    
    # Create course template
    new_template = CourseTemplate(
        name=name,
        experience_level=experience_level,
        duration_days=duration_int,
        max_students=max_students_int,
        color=color or '#0d6efd'
    )
    new_template.description = description
    new_template.short_blurb = short_blurb
    new_template.is_featured = is_featured
    new_template.is_taxable = is_taxable
    new_template.save()
    
    # Create tuition payable template
    tuition_payable = PayableTemplate(
        name=f"{name} Tuition",
        amount=tuition_float,
        description=f"Tuition for {name}",
        is_required=True
    )
    tuition_payable.save()
    
    # Attach tuition to course template
    new_template.payable_templates.append(tuition_payable)
    new_template.save()
    
    # Log the creation
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='create_course_template',
        description=f'Course template created: {new_template.name}',
        user_id=current_user_id,
        target_type='course_template',
        target_id=new_template.id,
        status='success',
        extra_data={
            'template_name': new_template.name,
            'experience_level': new_template.experience_level,
            'duration_days': new_template.duration_days,
            'max_students': new_template.max_students,
            'tuition': tuition_float,
            'color': new_template.color,
            'tuition_payable_id': tuition_payable.id
        }
    )
    
    return new_template


def update_course_template(template_id, name, experience_level, duration_days, max_students, tuition, color, current_user_id, description=None, short_blurb=None, is_featured=False, is_taxable=True):
    """
    Update an existing course template and its tuition payable.
    
    Args:
        template_id: ID of template to update
        name: Updated name
        experience_level: Updated experience level
        duration_days: Updated duration
        max_students: Updated max students
        tuition: Updated tuition amount
        color: Updated color
        current_user_id: ID of user making the update
        description: Full course description (optional)
        short_blurb: Short description for cards (optional)
        is_featured: Whether to show on landing page (optional)
        is_test_session: Whether this is a test session (tax exempt) (optional)
        
    Returns:
        CourseTemplate: The updated template
        
    Raises:
        ValueError: If template not found or invalid data
    """
    template = CourseTemplate.query.get(template_id)
    if not template:
        raise ValueError("Course template not found")
    
    if not all([name, experience_level, duration_days, max_students, tuition]):
        raise ValueError("All fields are required")
    
    try:
        duration_int = int(duration_days)
        max_students_int = int(max_students)
        tuition_float = float(tuition)
    except (ValueError, TypeError):
        raise ValueError("Duration, max students, and tuition must be valid numbers")
    
    old_name = template.name
    
    # Update template fields
    template.name = name
    template.description = description
    template.short_blurb = short_blurb
    template.experience_level = experience_level
    template.duration_days = duration_int
    template.max_students = max_students_int
    template.color = color or '#0d6efd'
    template.is_featured = is_featured
    template.is_taxable = is_taxable
    template.save()
    
    # Find and update tuition payable
    tuition_payable = None
    for payable in template.payable_templates:
        if payable.name == f"{old_name} Tuition" or "Tuition" in payable.name:
            tuition_payable = payable
            break
    
    if tuition_payable:
        tuition_payable.name = f"{name} Tuition"
        tuition_payable.amount = tuition_float
        tuition_payable.description = f"Tuition for {name}"
        tuition_payable.save()
    else:
        # Create new tuition payable if it doesn't exist
        tuition_payable = PayableTemplate(
            name=f"{name} Tuition",
            amount=tuition_float,
            description=f"Tuition for {name}",
            is_required=True
        )
        tuition_payable.save()
        template.payable_templates.append(tuition_payable)
        template.save()
    
    # Log the update
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='update_course_template',
        description=f'Course template updated: {template.name}',
        user_id=current_user_id,
        target_type='course_template',
        target_id=template.id,
        status='success',
        extra_data={
            'template_name': template.name,
            'old_name': old_name,
            'experience_level': template.experience_level,
            'duration_days': template.duration_days,
            'max_students': template.max_students,
            'tuition': tuition_float,
            'color': template.color
        }
    )
    
    return template


def add_payable_to_course(course_template_id, payable_template_id, current_user_id):
    """
    Add a payable template to a course template.
    
    Args:
        course_template_id: ID of course template
        payable_template_id: ID of payable template
        current_user_id: ID of user performing the action
        
    Returns:
        dict: course_template and payable_template
        
    Raises:
        ValueError: If templates not found or payable already associated
    """
    course_template = CourseTemplate.query.get(course_template_id)
    payable_template = PayableTemplate.query.get(payable_template_id)
    
    if not course_template or not payable_template:
        raise ValueError("Invalid course or payable template")
    
    if course_template.payable_templates.filter_by(id=payable_template.id).first():
        raise ValueError("Payable template already associated with this course template")
    
    course_template.payable_templates.append(payable_template)
    course_template.save()
    
    # Log the addition
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='add_payable_to_course',
        description=f'Payable "{payable_template.name}" added to course template "{course_template.name}"',
        user_id=current_user_id,
        target_type='course_template',
        target_id=course_template.id,
        status='success',
        extra_data={
            'course_template_name': course_template.name,
            'payable_template_name': payable_template.name,
            'payable_template_id': payable_template.id,
            'payable_amount': float(payable_template.amount),
            'is_required': payable_template.is_required
        }
    )
    
    return {
        'course_template': course_template,
        'payable_template': payable_template
    }


def remove_payable_from_course(course_template_id, payable_template_id, current_user_id):
    """
    Remove a payable template from a course template.
    
    Args:
        course_template_id: ID of course template
        payable_template_id: ID of payable template
        current_user_id: ID of user performing the action
        
    Returns:
        dict: course_template and payable_template
        
    Raises:
        ValueError: If templates not found or payable not associated
    """
    course_template = CourseTemplate.query.get(course_template_id)
    payable_template = PayableTemplate.query.get(payable_template_id)
    
    if not course_template or not payable_template:
        raise ValueError("Invalid course or payable template")
    
    if not course_template.payable_templates.filter_by(id=payable_template.id).first():
        raise ValueError("Payable template not associated with this course template")
    
    course_template.payable_templates.remove(payable_template)
    course_template.save()
    
    # Log the removal
    Log.create_log(
        log_type=Log.TYPE_USER_ACTION,
        action='remove_payable_from_course',
        description=f'Payable "{payable_template.name}" removed from course template "{course_template.name}"',
        user_id=current_user_id,
        target_type='course_template',
        target_id=course_template.id,
        status='success',
        extra_data={
            'course_template_name': course_template.name,
            'payable_template_name': payable_template.name,
            'payable_template_id': payable_template.id
        }
    )
    
    return {
        'course_template': course_template,
        'payable_template': payable_template
    }
