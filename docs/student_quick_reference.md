# Student System - Quick Reference

## Quick Import
```python
from src.logic.student_logic import StudentLogic
```

## Common Operations

### Create Student Profile
```python
profile = StudentLogic.create_student_profile(
    user_id=1,
    student_data={
        'student_number': 'STU12345',
        'grade_level': 'Beginner'
    }
)
```

### Enroll in Course
```python
# With motorcycle
enrollment = StudentLogic.enroll_in_course(
    student_id=profile.id,
    course_id=1,
    enrollment_data={
        'brings_motorcycle': True,
        'motorcycle_make': 'Honda',
        'motorcycle_model': 'CBR500R',
        'motorcycle_year': 2022,
        'motorcycle_license_plate': 'MC123'
    }
)

# With car
enrollment = StudentLogic.enroll_in_course(
    student_id=profile.id,
    course_id=2,
    enrollment_data={
        'brings_car': True,
        'car_make': 'Toyota',
        'car_model': 'Corolla',
        'car_year': 2020,
        'car_license_plate': 'CAR456'
    }
)
```

### Update Score
```python
StudentLogic.update_course_score(enrollment_id=1, score=92.5)
```

### Complete Course
```python
StudentLogic.complete_course(enrollment_id=1, final_score=95.0)
```

### Get Student's Courses
```python
# All courses
courses = StudentLogic.get_student_courses(student_id=1)

# Only active
active = StudentLogic.get_student_courses(student_id=1, status='active')

# Only completed
completed = StudentLogic.get_student_courses(student_id=1, status='completed')
```

### Get Course's Students
```python
# All students
students = StudentLogic.get_course_students(course_id=1)

# Only active
active = StudentLogic.get_course_students(course_id=1, status='active')
```

### Calculate GPA
```python
gpa = StudentLogic.calculate_student_gpa(student_id=1)
```

## Status Values
- `'active'` - Currently enrolled
- `'completed'` - Finished course
- `'withdrawn'` - Dropped course
- `'failed'` - Did not pass

## Common Queries

### Get Student Profile from User
```python
profile = StudentLogic.get_student_profile(user_id=1)
```

### Get Enrollment
```python
# By ID
enrollment = StudentLogic.get_enrollment(enrollment_id=1)

# By student and course
enrollment = StudentLogic.get_enrollment_by_student_and_course(
    student_id=1,
    course_id=1
)
```

### Update Enrollment
```python
StudentLogic.update_enrollment(
    enrollment_id=1,
    update_data={
        'notes': 'Updated notes',
        'attendance_percentage': 95.0
    }
)
```

### Unenroll (Soft Delete)
```python
StudentLogic.unenroll_from_course(enrollment_id=1)
# Sets status to 'withdrawn'
```

## Direct Model Access (Read-Only)

```python
from src.models.student_profile import StudentProfile
from src.models.course_enrollment import CourseEnrollment

# Query student
student = StudentProfile.query.get(1)
print(student.overall_score)
print(student.student_number)

# Query enrollment
enrollment = CourseEnrollment.query.get(1)
print(enrollment.course_score)
print(enrollment.brings_motorcycle)

# Access relationships
for enrollment in student.course_enrollments:
    print(f"Course: {enrollment.course_id}")
    print(f"Score: {enrollment.course_score}")
```

## Seeding

```bash
# Seed all including students
python seeds/run_seeds.py --all

# Seed only students
python seeds/run_seeds.py --students
```

## Error Handling

```python
try:
    enrollment = StudentLogic.enroll_in_course(student_id, course_id, data)
except ValueError as e:
    # Validation error (student not found, already enrolled, etc.)
    print(f"Validation error: {e}")
except Exception as e:
    # Database error
    print(f"Database error: {e}")
```

## Common Validations

- Student must exist
- Course must exist
- Course must not be full
- Student cannot enroll twice in same course
- Scores must be 0-100
- Vehicle info required if brings_vehicle flag is True
