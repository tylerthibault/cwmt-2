# Student Profile and Course Enrollment System

## Overview

This document describes the student profile and course enrollment system implemented following the constitutional principle of **thin models** and **thick logic**.

## Architecture

### Models (THIN - Database Schema Only)

#### 1. StudentProfile (`src/models/student_profile.py`)

Extends User with student-specific data in a one-to-one relationship.

**Fields:**
- `user_id` - Foreign key to User (one-to-one)
- `student_number` - Unique student identifier
- `overall_score` - Average score across all completed courses (0-100)
- `grade_level` - Student level (e.g., 'Beginner', 'Intermediate', 'Advanced')
- `emergency_contact_name` - Emergency contact information
- `emergency_contact_phone` - Emergency contact phone

**Relationships:**
- `user` - One-to-one relationship with User
- `course_enrollments` - One-to-many with CourseEnrollment

#### 2. CourseEnrollment (`src/models/course_enrollment.py`)

Tracks student enrollment in specific courses with course-specific data.

**Fields:**
- `student_id` - Foreign key to StudentProfile
- `course_id` - Foreign key to Course
- `status` - Enrollment status ('active', 'completed', 'withdrawn', 'failed')
- `enrollment_date` - When student enrolled
- `completion_date` - When course was completed (if applicable)
- `course_score` - Score for this specific course (0-100)
- `attendance_percentage` - Attendance percentage (0-100)

**Vehicle Information (per course):**
- `brings_motorcycle` - Boolean flag
- `motorcycle_make` - Make of motorcycle
- `motorcycle_model` - Model of motorcycle
- `motorcycle_year` - Year of motorcycle
- `motorcycle_license_plate` - License plate number
- `brings_car` - Boolean flag
- `car_make` - Make of car
- `car_model` - Model of car
- `car_year` - Year of car
- `car_license_plate` - License plate number
- `notes` - Additional course-specific notes

**Relationships:**
- `student` - Many-to-one with StudentProfile
- `course` - Many-to-one with Course

**Constraints:**
- Unique constraint on (student_id, course_id) - student can only enroll once per course

#### 3. Course Model Updates (`src/models/courses_model.py`)

**Updated Relationships:**
- Removed simple `students` many-to-many relationship
- Added `enrollments` - One-to-many with CourseEnrollment

**Updated Methods:**
- `to_dict()` - Now uses `enrollments` instead of `students`
- `get_available_slots()` - Uses `len(enrollments)`
- `is_full()` - Uses `len(enrollments)`

### Logic Layer (THICK - All Business Logic)

#### StudentLogic (`src/logic/student_logic.py`)

All business operations for students and enrollments.

**Student Profile Operations:**

```python
# Create student profile
StudentLogic.create_student_profile(user_id, student_data)

# Get student profile
StudentLogic.get_student_profile(user_id)
StudentLogic.get_student_profile_by_id(student_id)

# Update student profile
StudentLogic.update_student_profile(student_id, update_data)
```

**Enrollment Operations:**

```python
# Enroll student in course
StudentLogic.enroll_in_course(student_id, course_id, enrollment_data)

# Unenroll (soft delete - sets status to withdrawn)
StudentLogic.unenroll_from_course(enrollment_id)

# Update enrollment details
StudentLogic.update_enrollment(enrollment_id, update_data)

# Get enrollments
StudentLogic.get_student_courses(student_id, status=None)
StudentLogic.get_course_students(course_id, status=None)
StudentLogic.get_enrollment(enrollment_id)
StudentLogic.get_enrollment_by_student_and_course(student_id, course_id)
```

**Scoring Operations:**

```python
# Update course score
StudentLogic.update_course_score(enrollment_id, score)

# Complete course with optional final score
StudentLogic.complete_course(enrollment_id, final_score=None)

# Calculate GPA
StudentLogic.calculate_student_gpa(student_id)
```

**Business Rules Implemented:**

1. **Validation:**
   - Student must exist before enrolling
   - Course must exist and not be full
   - No duplicate enrollments
   - Vehicle info required if vehicle flags set
   - Scores must be 0-100

2. **Auto-calculations:**
   - Overall score auto-updates when courses completed
   - GPA calculated from completed courses
   - Attendance tracking per course

3. **Soft Deletes:**
   - Unenrollment sets status to 'withdrawn' (preserves history)

## Usage Examples

### Creating a Student Profile

```python
from src.logic.student_logic import StudentLogic

# Create student profile for user
student_data = {
    'student_number': 'STU12345',
    'grade_level': 'Beginner',
    'emergency_contact_name': 'John Doe',
    'emergency_contact_phone': '555-0100'
}

profile = StudentLogic.create_student_profile(user_id=1, student_data=student_data)
```

### Enrolling in a Course with Vehicle Info

```python
# Student brings motorcycle to course
enrollment_data = {
    'brings_motorcycle': True,
    'motorcycle_make': 'Honda',
    'motorcycle_model': 'CBR500R',
    'motorcycle_year': 2022,
    'motorcycle_license_plate': 'MC12345',
    'notes': 'Student has own gear'
}

enrollment = StudentLogic.enroll_in_course(
    student_id=profile.id,
    course_id=1,
    enrollment_data=enrollment_data
)
```

### Different Vehicle for Different Course

```python
# Same student brings car to different course
enrollment_data = {
    'brings_car': True,
    'car_make': 'Toyota',
    'car_model': 'Corolla',
    'car_year': 2020,
    'car_license_plate': 'CAR789',
    'notes': 'Defensive driving course'
}

enrollment2 = StudentLogic.enroll_in_course(
    student_id=profile.id,
    course_id=2,
    enrollment_data=enrollment_data
)
```

### Completing a Course with Score

```python
# Complete course and set final score
enrollment = StudentLogic.complete_course(
    enrollment_id=enrollment.id,
    final_score=92.5
)

# Overall score automatically updated in student profile
student = StudentLogic.get_student_profile_by_id(profile.id)
print(f"Overall Score: {student.overall_score}")
```

### Querying Student Courses

```python
# Get all courses for student
all_courses = StudentLogic.get_student_courses(student_id=profile.id)

# Get only active enrollments
active_courses = StudentLogic.get_student_courses(
    student_id=profile.id,
    status='active'
)

# Get completed courses
completed_courses = StudentLogic.get_student_courses(
    student_id=profile.id,
    status='completed'
)
```

### Querying Course Students

```python
# Get all students in a course
students = StudentLogic.get_course_students(course_id=1)

# Get only active students
active_students = StudentLogic.get_course_students(
    course_id=1,
    status='active'
)

# Check vehicle info for course
for enrollment in active_students:
    if enrollment.brings_motorcycle:
        print(f"Student brings {enrollment.motorcycle_make} {enrollment.motorcycle_model}")
```

## Database Schema

### StudentProfile Table
```sql
CREATE TABLE student_profiles (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    student_number VARCHAR(50) UNIQUE,
    overall_score FLOAT DEFAULT 0.0,
    grade_level VARCHAR(20),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### CourseEnrollment Table
```sql
CREATE TABLE course_enrollments (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    enrollment_date DATETIME NOT NULL,
    completion_date DATETIME,
    course_score FLOAT DEFAULT 0.0,
    attendance_percentage FLOAT DEFAULT 0.0,
    brings_motorcycle BOOLEAN DEFAULT FALSE,
    motorcycle_make VARCHAR(50),
    motorcycle_model VARCHAR(50),
    motorcycle_year INTEGER,
    motorcycle_license_plate VARCHAR(20),
    brings_car BOOLEAN DEFAULT FALSE,
    car_make VARCHAR(50),
    car_model VARCHAR(50),
    car_year INTEGER,
    car_license_plate VARCHAR(20),
    notes TEXT,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (student_id) REFERENCES student_profiles(id),
    FOREIGN KEY (course_id) REFERENCES courses(id),
    UNIQUE (student_id, course_id)
);
```

## Seeding

Run the seed files to create sample data:

```bash
# Seed all data including students
python seeds/run_seeds.py --all

# Or seed only students (requires users and courses to exist first)
python seeds/run_seeds.py --students
```

The student seeder creates:
1. Student profiles for all non-admin users
2. Sample course enrollments with various vehicle configurations
3. Some completed courses with scores for testing

## Benefits of This Architecture

1. **Separation of Concerns**
   - User authentication stays in User model
   - Student-specific data in StudentProfile
   - Course-specific student data in CourseEnrollment

2. **Flexibility**
   - Track different vehicles per course
   - Track different scores per course
   - Easy to add instructor profiles, admin profiles, etc.

3. **Data Integrity**
   - Unique constraints prevent duplicate enrollments
   - Foreign keys ensure referential integrity
   - Soft deletes preserve history

4. **Constitutional Compliance**
   - Models are THIN (schema only)
   - Logic is THICK (all business rules)
   - Easy to test and maintain

5. **Scalability**
   - Easy to add new fields to enrollments
   - Easy to add new student profile fields
   - Easy to add new business rules in logic layer

## Future Enhancements

Possible additions while maintaining architecture:

1. **Additional Enrollment Fields:**
   - Certification number
   - Payment status
   - Special accommodations
   - Equipment rental details

2. **Student Profile Fields:**
   - Date of birth
   - Address information
   - Medical conditions
   - Photo URL

3. **Business Logic:**
   - Waitlist management
   - Prerequisites checking
   - Certification tracking
   - Payment processing

4. **Reports:**
   - Student progress reports
   - Course completion rates
   - Vehicle usage statistics
   - Attendance reports
