"""
Instructor service for instructor-related business logic.
"""
from datetime import datetime
from src.models.user_folder.instructors import Instructor
from src.models.user_folder.users import User
from src.models.course_folder.course_instances import CourseInstance


def get_instructor_by_user_id(user_id):
    """Get instructor record by user ID."""
    return Instructor.query.filter_by(user_id=user_id).first()


def get_all_instructors():
    """Get all instructor records."""
    return Instructor.get_all()


def get_instructor_dashboard_data(current_user):
    """
    Get all data needed for instructor dashboard.
    
    Returns:
        dict: Dashboard data including course instances, instructors, and current instructor ID
    """
    current_instructor = get_instructor_by_user_id(current_user.id)
    course_instances = CourseInstance.get_all()
    instructors = get_all_instructors()
    
    return {
        'current_instructor_id': current_instructor.id if current_instructor else None,
        'course_instances': course_instances,
        'instructors': instructors
    }


def create_instructor(user_id):
    """
    Create a new instructor record for a user.
    
    Args:
        user_id: ID of the user to make an instructor
        
    Returns:
        Instructor: The created instructor record
        
    Raises:
        ValueError: If user doesn't exist or is already an instructor
    """
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")
    
    existing_instructor = Instructor.query.filter_by(user_id=user_id).first()
    if existing_instructor:
        raise ValueError("User is already an instructor")
    
    new_instructor = Instructor.create(
        user_id=user_id,
        is_active=True,
        status_change_date=datetime.utcnow()
    )
    
    return new_instructor


def deactivate_instructor(user_id):
    """
    Deactivate an instructor (soft delete).
    
    Args:
        user_id: ID of the user instructor to deactivate
        
    Returns:
        Instructor: The deactivated instructor record
        
    Raises:
        ValueError: If user is not an instructor
    """
    instructor = Instructor.query.filter_by(user_id=user_id).first()
    if not instructor:
        raise ValueError("User is not an instructor")
    
    instructor.is_active = False
    instructor.status_change_date = datetime.utcnow()
    instructor.save()
    
    return instructor
