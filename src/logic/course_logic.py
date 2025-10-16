"""
Course Logic Layer - THICK logic following constitutional principles
Contains ALL business logic for course and course template management
"""
from datetime import date, time, datetime, timedelta
from src.models import db
from src.models.courses_model import Course, CourseTemplate
from src.models.user import User
from src.models.roles import Role


class CourseLogicError(Exception):
    """Base exception for course logic errors"""
    pass


class CourseValidationError(CourseLogicError):
    """Exception for validation errors"""
    pass


class CourseBusinessError(CourseLogicError):
    """Exception for business rule violations"""
    pass


class CourseTemplateLogic:
    """
    Business logic for course template management.
    All validation, business rules, and complex operations for templates.
    """
    
    VALID_EXPERIENCE_LEVELS = ['beginner', 'intermediate', 'advanced']
    
    @staticmethod
    def create_template(data):
        """
        Create a new course template with full validation.
        
        Args:
            data (dict): Template data including name, description, duration_days, experience_level
            
        Returns:
            CourseTemplate: Created template instance
            
        Raises:
            CourseValidationError: If validation fails
            CourseBusinessError: If business rules violated
        """
        # Validation
        if not data.get('name'):
            raise CourseValidationError("Template name is required")
        
        if not data.get('duration_days') or data['duration_days'] < 1:
            raise CourseValidationError("Duration must be at least 1 day")
        
        if data.get('experience_level') not in CourseTemplateLogic.VALID_EXPERIENCE_LEVELS:
            raise CourseValidationError(
                f"Experience level must be one of: {', '.join(CourseTemplateLogic.VALID_EXPERIENCE_LEVELS)}"
            )
        
        # Business rule: Check for duplicate template names
        existing = CourseTemplate.query.filter_by(name=data['name']).first()
        if existing:
            raise CourseBusinessError(f"Course template with name '{data['name']}' already exists")
        
        # Create template
        template = CourseTemplate(
            name=data['name'],
            description=data.get('description', ''),
            duration_days=data['duration_days'],
            experience_level=data['experience_level'],
            is_active=data.get('is_active', True)
        )
        
        db.session.add(template)
        db.session.commit()
        
        return template
    
    @staticmethod
    def update_template(template_id, data):
        """
        Update an existing course template.
        
        Args:
            template_id (int): ID of template to update
            data (dict): Updated template data
            
        Returns:
            CourseTemplate: Updated template instance
            
        Raises:
            CourseValidationError: If validation fails
            CourseBusinessError: If template not found or business rules violated
        """
        template = CourseTemplate.query.get(template_id)
        if not template:
            raise CourseBusinessError(f"Course template with ID {template_id} not found")
        
        # Validate experience level if provided
        if 'experience_level' in data and data['experience_level'] not in CourseTemplateLogic.VALID_EXPERIENCE_LEVELS:
            raise CourseValidationError(
                f"Experience level must be one of: {', '.join(CourseTemplateLogic.VALID_EXPERIENCE_LEVELS)}"
            )
        
        # Validate duration if provided
        if 'duration_days' in data and data['duration_days'] < 1:
            raise CourseValidationError("Duration must be at least 1 day")
        
        # Check for duplicate name if changing name
        if 'name' in data and data['name'] != template.name:
            existing = CourseTemplate.query.filter_by(name=data['name']).first()
            if existing:
                raise CourseBusinessError(f"Course template with name '{data['name']}' already exists")
        
        # Update template
        template.from_dict(data)
        db.session.commit()
        
        return template
    
    @staticmethod
    def get_template(template_id):
        """Get a course template by ID"""
        template = CourseTemplate.query.get(template_id)
        if not template:
            raise CourseBusinessError(f"Course template with ID {template_id} not found")
        return template
    
    @staticmethod
    def get_all_templates(active_only=False):
        """
        Get all course templates.
        
        Args:
            active_only (bool): If True, return only active templates
            
        Returns:
            list: List of CourseTemplate instances
        """
        query = CourseTemplate.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.all()
    
    @staticmethod
    def deactivate_template(template_id):
        """
        Deactivate a course template (soft delete).
        
        Args:
            template_id (int): ID of template to deactivate
            
        Returns:
            CourseTemplate: Deactivated template
        """
        template = CourseTemplateLogic.get_template(template_id)
        template.is_active = False
        db.session.commit()
        return template


class CourseLogic:
    """
    Business logic for course instance management.
    All validation, business rules, and complex operations for courses.
    """
    
    VALID_STATUSES = ['scheduled', 'in_progress', 'completed', 'cancelled']
    
    @staticmethod
    def create_course(data):
        """
        Create a new course instance with full validation.
        
        Args:
            data (dict): Course data including template_id, date, time, student_id, instructor IDs
            
        Returns:
            Course: Created course instance
            
        Raises:
            CourseValidationError: If validation fails
            CourseBusinessError: If business rules violated
        """
        # Validation
        if not data.get('course_template_id'):
            raise CourseValidationError("Course template ID is required")
        
        # Validate template exists
        template = CourseTemplate.query.get(data['course_template_id'])
        if not template:
            raise CourseBusinessError(f"Course template with ID {data['course_template_id']} not found")
        
        if not template.is_active:
            raise CourseBusinessError("Cannot create course from inactive template")
        
        # Validate date and time
        if not data.get('course_date'):
            raise CourseValidationError("Course date is required")
        
        if not data.get('course_time'):
            raise CourseValidationError("Course time is required")
        
        # Convert string dates/times if needed
        course_date = data['course_date']
        if isinstance(course_date, str):
            try:
                course_date = datetime.strptime(course_date, '%Y-%m-%d').date()
            except ValueError:
                raise CourseValidationError("Invalid date format. Use YYYY-MM-DD")
        
        course_time = data['course_time']
        if isinstance(course_time, str):
            try:
                course_time = datetime.strptime(course_time, '%H:%M').time()
            except ValueError:
                raise CourseValidationError("Invalid time format. Use HH:MM")
        
        # Business rule: Course date must be in the future
        if course_date < date.today():
            raise CourseBusinessError("Course date must be in the future")
        
        # Validate and assign users (convert empty strings to None)
        student_id = data.get('student_id') or None
        instructor1_id = data.get('instructor1_id') or None
        instructor2_id = data.get('instructor2_id') or None
        location = data.get('location') or None
        
        # Convert empty strings to None for integer fields
        if student_id == '':
            student_id = None
        if instructor1_id == '':
            instructor1_id = None
        if instructor2_id == '':
            instructor2_id = None
        
        if student_id:
            CourseLogic._validate_student(student_id)
        
        if instructor1_id:
            CourseLogic._validate_instructor(instructor1_id)
        
        if instructor2_id:
            CourseLogic._validate_instructor(instructor2_id)
        
        # Business rule: Two instructors must be different people
        if instructor1_id and instructor2_id and instructor1_id == instructor2_id:
            raise CourseBusinessError("Cannot assign the same instructor twice")
        
        # Create course
        course = Course(
            course_template_id=data['course_template_id'],
            course_date=course_date,
            course_time=course_time,
            status=data.get('status', 'scheduled'),
            location=location,
            student_id=student_id,
            instructor1_id=instructor1_id,
            instructor2_id=instructor2_id
        )
        
        db.session.add(course)
        db.session.commit()
        
        return course
    
    @staticmethod
    def _validate_student(user_id):
        """Validate that a user exists and has student role"""
        user = User.query.get(user_id)
        if not user:
            raise CourseBusinessError(f"User with ID {user_id} not found")
        
        # Check if user has student role
        student_role = Role.query.filter_by(name='student').first()
        if student_role not in user.role_list:
            raise CourseBusinessError(f"User {user.username} does not have student role")
        
        return user
    
    @staticmethod
    def _validate_instructor(user_id):
        """Validate that a user exists and has instructor role"""
        user = User.query.get(user_id)
        if not user:
            raise CourseBusinessError(f"User with ID {user_id} not found")
        
        # Check if user has instructor role
        instructor_role = Role.query.filter_by(name='instructor').first()
        if instructor_role not in user.role_list:
            raise CourseBusinessError(f"User {user.username} does not have instructor role")
        
        return user
    
    @staticmethod
    def enroll_student(course_id, student_id):
        """
        Enroll a student in a course.
        
        Args:
            course_id (int): ID of the course
            student_id (int): ID of the student to enroll
            
        Returns:
            Course: Updated course instance
        """
        course = Course.query.get(course_id)
        if not course:
            raise CourseBusinessError(f"Course with ID {course_id} not found")
        
        # Business rule: Cannot enroll in cancelled or completed courses
        if course.status in ['cancelled', 'completed']:
            raise CourseBusinessError(f"Cannot enroll in {course.status} course")
        
        # Business rule: Cannot replace existing student (use different method)
        if course.student_id:
            raise CourseBusinessError("Course already has a student enrolled. Use replace_student method instead.")
        
        # Validate student
        CourseLogic._validate_student(student_id)
        
        course.student_id = student_id
        db.session.commit()
        
        return course
    
    @staticmethod
    def assign_instructor(course_id, instructor_id, position=1):
        """
        Assign an instructor to a course.
        
        Args:
            course_id (int): ID of the course
            instructor_id (int): ID of the instructor to assign
            position (int): Position (1 or 2) for the instructor
            
        Returns:
            Course: Updated course instance
        """
        course = Course.query.get(course_id)
        if not course:
            raise CourseBusinessError(f"Course with ID {course_id} not found")
        
        if position not in [1, 2]:
            raise CourseValidationError("Instructor position must be 1 or 2")
        
        # Validate instructor
        CourseLogic._validate_instructor(instructor_id)
        
        # Business rule: Same instructor cannot fill both positions
        if position == 1 and course.instructor2_id == instructor_id:
            raise CourseBusinessError("This instructor is already assigned as instructor 2")
        if position == 2 and course.instructor1_id == instructor_id:
            raise CourseBusinessError("This instructor is already assigned as instructor 1")
        
        # Assign instructor
        if position == 1:
            course.instructor1_id = instructor_id
        else:
            course.instructor2_id = instructor_id
        
        db.session.commit()
        
        return course
    
    @staticmethod
    def update_status(course_id, new_status):
        """
        Update course status with validation.
        
        Args:
            course_id (int): ID of the course
            new_status (str): New status value
            
        Returns:
            Course: Updated course instance
        """
        if new_status not in CourseLogic.VALID_STATUSES:
            raise CourseValidationError(
                f"Status must be one of: {', '.join(CourseLogic.VALID_STATUSES)}"
            )
        
        course = Course.query.get(course_id)
        if not course:
            raise CourseBusinessError(f"Course with ID {course_id} not found")
        
        # Business rules for status transitions
        if course.status == 'completed' and new_status != 'completed':
            raise CourseBusinessError("Cannot change status of completed course")
        
        if course.status == 'cancelled' and new_status != 'cancelled':
            raise CourseBusinessError("Cannot change status of cancelled course")
        
        course.status = new_status
        db.session.commit()
        
        return course
    
    @staticmethod
    def get_course(course_id):
        """Get a course by ID"""
        course = Course.query.get(course_id)
        if not course:
            raise CourseBusinessError(f"Course with ID {course_id} not found")
        return course
    
    @staticmethod
    def get_courses_by_date_range(start_date, end_date):
        """Get all courses within a date range"""
        return Course.query.filter(
            Course.course_date >= start_date,
            Course.course_date <= end_date
        ).order_by(Course.course_date, Course.course_time).all()
    
    @staticmethod
    def get_courses_for_student(student_id):
        """Get all courses for a specific student"""
        return Course.query.filter_by(student_id=student_id).order_by(
            Course.course_date, Course.course_time
        ).all()
    
    @staticmethod
    def get_courses_for_instructor(instructor_id):
        """Get all courses where user is an instructor"""
        return Course.query.filter(
            db.or_(
                Course.instructor1_id == instructor_id,
                Course.instructor2_id == instructor_id
            )
        ).order_by(Course.course_date, Course.course_time).all()
    
    @staticmethod
    def create_course_instance(data):
        """
        Alias for create_course for admin controller compatibility.
        Create a new course instance on the schedule.
        
        Args:
            data (dict): Course data from admin form
            
        Returns:
            Course: Created course instance
        """
        return CourseLogic.create_course(data)
    
    @staticmethod
    def update_course_instance(course_id, data):
        """
        Update an existing course instance.
        
        Args:
            course_id (int): ID of course to update
            data (dict): Updated course data
            
        Returns:
            Course: Updated course instance
        """
        course = Course.query.get(course_id)
        if not course:
            raise CourseBusinessError(f"Course with ID {course_id} not found")
        
        # Validate template if changing
        if 'course_template_id' in data:
            template = CourseTemplate.query.get(data['course_template_id'])
            if not template:
                raise CourseBusinessError(f"Course template with ID {data['course_template_id']} not found")
            if not template.is_active:
                raise CourseBusinessError("Cannot assign inactive template")
            course.course_template_id = data['course_template_id']
        
        # Update date if provided
        if 'course_date' in data:
            course_date = data['course_date']
            if isinstance(course_date, str):
                try:
                    course_date = datetime.strptime(course_date, '%Y-%m-%d').date()
                except ValueError:
                    raise CourseValidationError("Invalid date format. Use YYYY-MM-DD")
            
            # Business rule: Course date must be in the future (only for upcoming courses)
            if course.status == 'scheduled' and course_date < date.today():
                raise CourseBusinessError("Course date must be in the future")
            
            course.course_date = course_date
        
        # Update time if provided
        if 'course_time' in data:
            course_time = data['course_time']
            if isinstance(course_time, str):
                try:
                    course_time = datetime.strptime(course_time, '%H:%M').time()
                except ValueError:
                    raise CourseValidationError("Invalid time format. Use HH:MM")
            course.course_time = course_time
        
        # Update location if provided
        if 'location' in data:
            course.location = data['location'] or None
        
        # Update status if provided
        if 'status' in data:
            if data['status'] not in CourseLogic.VALID_STATUSES:
                raise CourseValidationError(
                    f"Status must be one of: {', '.join(CourseLogic.VALID_STATUSES)}"
                )
            # Apply status transition business rules
            if course.status == 'completed' and data['status'] != 'completed':
                raise CourseBusinessError("Cannot change status of completed course")
            if course.status == 'cancelled' and data['status'] != 'cancelled':
                raise CourseBusinessError("Cannot change status of cancelled course")
            course.status = data['status']
        
        # Update student if provided
        if 'student_id' in data:
            student_id = data['student_id'] if data['student_id'] not in ['', None] else None
            if student_id:
                CourseLogic._validate_student(student_id)
            course.student_id = student_id
        
        # Update instructors if provided
        if 'instructor1_id' in data:
            instructor1_id = data['instructor1_id'] if data['instructor1_id'] not in ['', None] else None
            if instructor1_id:
                CourseLogic._validate_instructor(instructor1_id)
                # Check not same as instructor 2
                if course.instructor2_id and instructor1_id == course.instructor2_id:
                    raise CourseBusinessError("Cannot assign the same instructor twice")
            course.instructor1_id = instructor1_id
        
        if 'instructor2_id' in data:
            instructor2_id = data['instructor2_id'] if data['instructor2_id'] not in ['', None] else None
            if instructor2_id:
                CourseLogic._validate_instructor(instructor2_id)
                # Check not same as instructor 1
                if course.instructor1_id and instructor2_id == course.instructor1_id:
                    raise CourseBusinessError("Cannot assign the same instructor twice")
            course.instructor2_id = instructor2_id
        
        db.session.commit()
        return course
    
    @staticmethod
    def delete_course_instance(course_id):
        """
        Delete a course instance from the schedule.
        
        Args:
            course_id (int): ID of course to delete
            
        Raises:
            CourseBusinessError: If course not found or cannot be deleted
        """
        course = Course.query.get(course_id)
        if not course:
            raise CourseBusinessError(f"Course with ID {course_id} not found")
        
        # Business rule: Can only delete scheduled courses (not in progress or completed)
        if course.status in ['in_progress', 'completed']:
            raise CourseBusinessError(f"Cannot delete {course.status} course. Cancel it instead.")
        
        db.session.delete(course)
        db.session.commit()
