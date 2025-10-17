# Course Instance Creation Fix

## Issue
When trying to create a course instance, the system was failing because the code was still trying to assign `student_id` directly to the Course model, but we had changed the model to use a many-to-many relationship with `students` instead.

## Root Cause
The Course model was updated to support multiple students through a `course_enrollments` association table, but the course creation logic in `CourseLogic.create_course()` was still using the old `student_id` field.

## Changes Made

### 1. `src/logic/course_logic.py` - `create_course()` method

**Before:**
```python
course = Course(
    ...
    student_id=student_id,  # ❌ This field no longer exists
    ...
)
```

**After:**
```python
course = Course(
    ...
    max_students=max_students_override,  # ✅ Added max_students support
    ...
    # No student_id field
)
db.session.add(course)
db.session.commit()

# Enroll student separately if provided (backward compatibility)
if student_id:
    try:
        CourseLogic.enroll_student(course.id, student_id, is_admin_override=True)
    except Exception as e:
        db.session.rollback()
        raise CourseBusinessError(f"Course created but failed to enroll student: {str(e)}")
```

### 2. `src/logic/course_logic.py` - `update_course_instance()` method

**Updated to:**
- Support `max_students` override field
- Handle student enrollment through the many-to-many relationship
- Maintain backward compatibility by converting `student_id` to enrollment
- Use `course.students.append(student)` instead of `course.student_id = student_id`

**Key changes:**
```python
# Added max_students support
if 'max_students' in data:
    max_students = data['max_students']
    if max_students is not None and max_students != '':
        max_students = int(max_students)
        if max_students < 1:
            raise CourseValidationError("Max students must be at least 1")
        course.max_students = max_students
    else:
        course.max_students = None

# Updated student assignment
if 'student_id' in data:
    student_id = data['student_id'] if data['student_id'] not in ['', None] else None
    if student_id:
        CourseLogic._validate_student(student_id)
        from src.models.user import User
        student = User.query.get(student_id)
        if student and student not in course.students:
            course.students.append(student)  # ✅ Use many-to-many relationship
```

### 3. `seeds/seed_courses.py` - `seed_sample_courses()` function

**Updated to:**
- Remove `student_id` from course creation data
- Create course first without student
- Enroll student separately using the relationship
- Added `location` field to sample data

**Changes:**
```python
# Remove student_id from course_data
student_to_enroll = None
if 'student_id' in course_data:
    student_to_enroll = course_data.pop('student_id')

# Create the course without student
course = Course(**course_data)
db.session.add(course)
db.session.flush()  # Get the course ID

# Enroll student if specified
if student_to_enroll:
    student = User.query.get(student_to_enroll)
    if student:
        course.students.append(student)  # ✅ Use many-to-many relationship
```

## Benefits

1. **Backward Compatibility**: Forms that still send `student_id` will work - the system converts it to an enrollment
2. **Multi-Student Support**: Courses can now have multiple students enrolled
3. **Max Students**: Course instances can override the template's max_students value
4. **Proper Separation**: Course creation and student enrollment are now separate concerns
5. **Admin Override**: When enrolling during course creation, `is_admin_override=True` is used, allowing enrollment even if capacity is reached

## Migration Notes

### Database Changes Required
You'll need to run a migration to:
1. Create the `course_enrollments` table if it doesn't exist
2. Migrate existing `student_id` data to `course_enrollments` table
3. Drop the `student_id` column from `courses` table

### Sample Migration Data
If you have existing courses with `student_id`, you need to migrate them:
```sql
-- Insert into course_enrollments from existing student_id
INSERT INTO course_enrollments (course_id, student_id, enrolled_at, enrolled_by_admin)
SELECT id, student_id, created_at, true
FROM courses
WHERE student_id IS NOT NULL;

-- Then drop the column
ALTER TABLE courses DROP COLUMN student_id;
```

## Testing Checklist

- [x] Create course without student
- [x] Create course with student (backward compatibility)
- [x] Update course max_students
- [x] Enroll multiple students in a course
- [x] Verify capacity limits work
- [x] Seed sample courses successfully
- [ ] Run full integration tests
- [ ] Test admin course creation UI
- [ ] Test student enrollment from student portal

## API Examples

### Create Course (No Student)
```python
course_data = {
    'course_template_id': 1,
    'course_date': '2025-12-01',
    'course_time': '09:00',
    'location': 'Seattle',
    'instructor1_id': 5,
    'instructor2_id': 6
}
course = CourseLogic.create_course(course_data)
```

### Create Course with Student (Backward Compatible)
```python
course_data = {
    'course_template_id': 1,
    'course_date': '2025-12-01',
    'course_time': '09:00',
    'location': 'Seattle',
    'student_id': 10,  # Will be enrolled automatically
    'instructor1_id': 5,
    'instructor2_id': 6
}
course = CourseLogic.create_course(course_data)
```

### Enroll Additional Students
```python
# Course already created, enroll more students
CourseLogic.enroll_student(course_id=1, student_id=11, is_admin_override=False)
CourseLogic.enroll_student(course_id=1, student_id=12, is_admin_override=False)
```
