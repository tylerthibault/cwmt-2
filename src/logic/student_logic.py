"""
Student business logic - THICK logic layer following constitutional principles
Contains ALL business logic for student operations
"""
from datetime import datetime
from src.models import db
from src.models.user import User
from src.models.student_profile import StudentProfile
from src.models.course_enrollment import CourseEnrollment
from src.models.courses_model import Course


class StudentLogic:
    """
    Student business logic layer.
    
    ALL validation, business rules, and complex operations go here.
    Models remain thin - this layer is THICK with logic.
    """
    
    @staticmethod
    def create_student_profile(user_id, student_data=None):
        """
        Create student profile for a user.
        
        Args:
            user_id (int): ID of the user
            student_data (dict, optional): Student profile data
            
        Returns:
            StudentProfile: Created student profile
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        if student_data is None:
            student_data = {}
            
        # Validate user exists
        user = User.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Check if student profile already exists
        existing = StudentProfile.query.filter_by(user_id=user_id).first()
        if existing:
            raise ValueError(f"Student profile already exists for user {user_id}")
        
        # Validate student data
        StudentLogic._validate_student_data(student_data)
        
        # Create profile
        try:
            profile = StudentProfile(user_id=user_id, **student_data)
            db.session.add(profile)
            db.session.commit()
            return profile
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create student profile: {str(e)}")
    
    @staticmethod
    def get_student_profile(user_id):
        """
        Get student profile for a user.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            StudentProfile: Student profile or None
        """
        return StudentProfile.query.filter_by(user_id=user_id).first()
    
    @staticmethod
    def get_student_profile_by_id(student_id):
        """
        Get student profile by student profile ID.
        
        Args:
            student_id (int): ID of the student profile
            
        Returns:
            StudentProfile: Student profile or None
        """
        return StudentProfile.query.get(student_id)
    
    @staticmethod
    def update_student_profile(student_id, update_data):
        """
        Update student profile.
        
        Args:
            student_id (int): Student profile ID
            update_data (dict): Data to update
            
        Returns:
            StudentProfile: Updated student profile
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        profile = StudentProfile.query.get(student_id)
        if not profile:
            raise ValueError(f"Student profile {student_id} not found")
        
        # Validate update data
        StudentLogic._validate_student_data(update_data)
        
        try:
            for key, value in update_data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            db.session.commit()
            return profile
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update student profile: {str(e)}")
    
    @staticmethod
    def enroll_in_course(student_id, course_id, enrollment_data=None):
        """
        Enroll student in a course with specific details.
        
        Args:
            student_id (int): Student profile ID
            course_id (int): Course ID
            enrollment_data (dict, optional): Enrollment details (vehicle info, etc.)
            
        Returns:
            CourseEnrollment: Created enrollment
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        if enrollment_data is None:
            enrollment_data = {}
            
        # Validate student exists
        student = StudentProfile.query.get(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # Validate course exists
        course = Course.query.get(course_id)
        if not course:
            raise ValueError(f"Course {course_id} not found")
        
        # Check if already enrolled
        existing = CourseEnrollment.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        
        if existing:
            raise ValueError("Student already enrolled in this course")
        
        # Check if course is full
        if course.is_full():
            raise ValueError("Course is full")
        
        # Validate enrollment data
        StudentLogic._validate_enrollment_data(enrollment_data)
        
        # Create enrollment
        try:
            enrollment = CourseEnrollment(
                student_id=student_id,
                course_id=course_id,
                enrollment_date=datetime.utcnow(),
                status='active',
                **enrollment_data
            )
            db.session.add(enrollment)
            db.session.commit()
            return enrollment
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to enroll student: {str(e)}")
    
    @staticmethod
    def unenroll_from_course(enrollment_id):
        """
        Unenroll student from a course (soft delete - sets status to withdrawn).
        
        Args:
            enrollment_id (int): Enrollment ID
            
        Returns:
            CourseEnrollment: Updated enrollment
            
        Raises:
            ValueError: If enrollment not found
            Exception: If database operation fails
        """
        enrollment = CourseEnrollment.query.get(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment {enrollment_id} not found")
        
        try:
            enrollment.status = 'withdrawn'
            db.session.commit()
            return enrollment
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to unenroll student: {str(e)}")
    
    @staticmethod
    def update_enrollment(enrollment_id, update_data):
        """
        Update enrollment details (vehicle info, notes, etc.).
        
        Args:
            enrollment_id (int): Enrollment ID
            update_data (dict): Data to update
            
        Returns:
            CourseEnrollment: Updated enrollment
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        enrollment = CourseEnrollment.query.get(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment {enrollment_id} not found")
        
        # Validate enrollment data
        StudentLogic._validate_enrollment_data(update_data)
        
        try:
            for key, value in update_data.items():
                if hasattr(enrollment, key):
                    # Convert empty strings to None for cleaner database storage
                    if isinstance(value, str) and value.strip() == '':
                        value = None
                    setattr(enrollment, key, value)
            db.session.commit()
            return enrollment
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update enrollment: {str(e)}")
    
    @staticmethod
    def update_course_score(enrollment_id, score):
        """
        Update student's score for a specific course.
        
        Args:
            enrollment_id (int): Enrollment ID
            score (float): New score (0-100)
            
        Returns:
            CourseEnrollment: Updated enrollment
            
        Raises:
            ValueError: If score is invalid or enrollment not found
            Exception: If database operation fails
        """
        if not 0 <= score <= 100:
            raise ValueError("Score must be between 0 and 100")
        
        enrollment = CourseEnrollment.query.get(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment {enrollment_id} not found")
        
        try:
            enrollment.course_score = score
            
            # Update overall student score (business logic)
            StudentLogic._update_overall_score(enrollment.student_id)
            
            db.session.commit()
            return enrollment
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update score: {str(e)}")
    
    @staticmethod
    def complete_course(enrollment_id, final_score=None):
        """
        Mark course as completed for a student.
        
        Args:
            enrollment_id (int): Enrollment ID
            final_score (float, optional): Final score for the course
            
        Returns:
            CourseEnrollment: Updated enrollment
            
        Raises:
            ValueError: If validation fails
            Exception: If database operation fails
        """
        enrollment = CourseEnrollment.query.get(enrollment_id)
        if not enrollment:
            raise ValueError(f"Enrollment {enrollment_id} not found")
        
        try:
            enrollment.status = 'completed'
            enrollment.completion_date = datetime.utcnow()
            
            if final_score is not None:
                if not 0 <= final_score <= 100:
                    raise ValueError("Score must be between 0 and 100")
                enrollment.course_score = final_score
            
            # Update overall student score
            StudentLogic._update_overall_score(enrollment.student_id)
            
            db.session.commit()
            return enrollment
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to complete course: {str(e)}")
    
    @staticmethod
    def get_student_courses(student_id, status=None):
        """
        Get all courses for a student.
        
        Args:
            student_id (int): Student profile ID
            status (str, optional): Filter by enrollment status
            
        Returns:
            list: List of course enrollments
        """
        query = CourseEnrollment.query.filter_by(student_id=student_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.all()
    
    @staticmethod
    def get_course_students(course_id, status=None):
        """
        Get all students enrolled in a course.
        
        Args:
            course_id (int): Course ID
            status (str, optional): Filter by enrollment status
            
        Returns:
            list: List of course enrollments
        """
        query = CourseEnrollment.query.filter_by(course_id=course_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.all()
    
    @staticmethod
    def get_enrollment(enrollment_id):
        """
        Get enrollment by ID.
        
        Args:
            enrollment_id (int): Enrollment ID
            
        Returns:
            CourseEnrollment: Enrollment or None
        """
        return CourseEnrollment.query.get(enrollment_id)
    
    @staticmethod
    def get_enrollment_by_student_and_course(student_id, course_id):
        """
        Get enrollment by student and course.
        
        Args:
            student_id (int): Student profile ID
            course_id (int): Course ID
            
        Returns:
            CourseEnrollment: Enrollment or None
        """
        return CourseEnrollment.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
    
    @staticmethod
    def calculate_student_gpa(student_id):
        """
        Calculate GPA for a student based on completed courses.
        
        Args:
            student_id (int): Student profile ID
            
        Returns:
            float: GPA (0.0-4.0 scale)
        """
        enrollments = CourseEnrollment.query.filter_by(
            student_id=student_id,
            status='completed'
        ).all()
        
        if not enrollments:
            return 0.0
        
        # Convert percentage scores to GPA scale (0-4.0)
        total_gpa = 0.0
        for enrollment in enrollments:
            score = enrollment.course_score
            if score >= 90:
                gpa = 4.0
            elif score >= 80:
                gpa = 3.0
            elif score >= 70:
                gpa = 2.0
            elif score >= 60:
                gpa = 1.0
            else:
                gpa = 0.0
            total_gpa += gpa
        
        return total_gpa / len(enrollments)
    
    @staticmethod
    def _validate_student_data(data):
        """
        Validate student profile data.
        
        Args:
            data (dict): Student data to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Validate overall_score if provided
        if 'overall_score' in data:
            score = data['overall_score']
            if not isinstance(score, (int, float)) or not 0 <= score <= 100:
                raise ValueError("Overall score must be between 0 and 100")
        
        # Validate student_number format if provided
        if 'student_number' in data and data['student_number']:
            student_num = data['student_number']
            if not isinstance(student_num, str) or len(student_num) > 50:
                raise ValueError("Student number must be a string with max 50 characters")
    
    @staticmethod
    def _validate_enrollment_data(data):
        """
        Validate enrollment data.
        
        Args:
            data (dict): Enrollment data to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Ensure vehicle info is provided if brings_motorcycle is True
        if data.get('brings_motorcycle') and not data.get('motorcycle_make'):
            raise ValueError("Motorcycle make required when bringing motorcycle")
        
        # Validate scores if provided
        if 'course_score' in data:
            score = data['course_score']
            if not isinstance(score, (int, float)) or not 0 <= score <= 100:
                raise ValueError("Course score must be between 0 and 100")
        
        if 'attendance_percentage' in data:
            attendance = data['attendance_percentage']
            if not isinstance(attendance, (int, float)) or not 0 <= attendance <= 100:
                raise ValueError("Attendance percentage must be between 0 and 100")
    
    @staticmethod
    def _update_overall_score(student_id):
        """
        Calculate and update overall student score across all completed courses.
        
        Args:
            student_id (int): Student profile ID
        """
        enrollments = CourseEnrollment.query.filter_by(
            student_id=student_id,
            status='completed'
        ).all()
        
        student = StudentProfile.query.get(student_id)
        if not student:
            return
        
        if enrollments:
            avg_score = sum(e.course_score for e in enrollments) / len(enrollments)
            student.overall_score = round(avg_score, 2)
        else:
            student.overall_score = 0.0
