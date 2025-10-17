# Max Students Implementation

## Overview
Implemented a maximum student capacity system for courses with different enrollment rules for students vs super-users.

## Business Rules
1. **Course Templates** have a `max_students` field (default: 1)
2. **Courses** can override the template's `max_students` with their own value
3. **Students** cannot enroll in full courses (hard limit enforced in backend)
4. **Super-users/Admins** can enroll students even if the course is full (override capability)
5. The system tracks whether an enrollment was done by an admin

## Database Changes

### CourseTemplate Model
- Added `max_students` column (Integer, default=1, not null)
- Updated `to_dict()` to include `max_students`

### Course Model
- **Breaking Change**: Changed from single student to many-to-many relationship
- Removed `student_id` column
- Added `max_students` column (Integer, nullable=True) - overrides template if set
- Created `course_enrollments` association table with:
  - `course_id`
  - `student_id`
  - `enrolled_at` (timestamp)
  - `enrolled_by_admin` (Boolean) - tracks admin enrollments
  - Unique constraint on (course_id, student_id)
- Changed `student` relationship to `students` (many-to-many)
- Added helper methods:
  - `get_max_students()` - returns effective max (course override or template value)
  - `get_available_slots()` - calculates remaining capacity
  - `is_full()` - checks if at/over capacity

## Logic Layer Changes

### CourseTemplateLogic
- Updated `create_template()` to accept and validate `max_students`
- Validates `max_students >= 1`

### CourseLogic
- **Updated `enroll_student()`**:
  - Added `is_admin_override` parameter (default: False)
  - Validates student isn't already enrolled
  - Checks capacity UNLESS `is_admin_override=True`
  - Throws `CourseBusinessError` if full (for students)
  - Allows admin enrollment even when full
  - Updates `enrolled_by_admin` flag in enrollment table
  
- **Updated `get_available_courses()`**:
  - Added `include_full` parameter (default: False)
  - Filters out full courses by default (for student view)
  - Uses eager loading for better performance
  - Admins can set `include_full=True` to see all courses

## UI Changes

### Student Dashboard Template
- Shows enrollment count: "X/Y enrolled" under course name
- Three states for enroll button:
  1. **Location TBD**: Gray "TBD" button (disabled)
  2. **Class Full**: Yellow "Full" button (disabled)
  3. **Available**: Blue "Enroll" button (enabled)
- Tooltips explain why button is disabled

## Migration Required

You'll need to create a migration to:
1. Add `max_students` to `course_templates` table
2. Add `max_students` to `courses` table
3. Create `course_enrollments` association table
4. Migrate existing `student_id` data to `course_enrollments`
5. Drop `student_id` column from `courses` table

## Usage Examples

### For Students (Strict Capacity Check)
```python
try:
    CourseLogic.enroll_student(
        course_id=123,
        student_id=456,
        is_admin_override=False  # Enforces capacity
    )
except CourseBusinessError as e:
    # "Course is full. Maximum capacity is 12 students..."
    flash(str(e), 'error')
```

### For Super-Users (Bypass Capacity)
```python
# Admin can enroll even if full
CourseLogic.enroll_student(
    course_id=123,
    student_id=456,
    is_admin_override=True  # Bypasses capacity check
)
```

### Check Available Courses
```python
# For students - excludes full courses
available = CourseLogic.get_available_courses(include_full=False)

# For admins - includes all courses
all_courses = CourseLogic.get_available_courses(include_full=True)
```

## Security
- Backend validation prevents students from bypassing capacity limits
- Even if a student manipulates the frontend, the `enroll_student()` method will reject enrollment if course is full (unless called with `is_admin_override=True`)
- Admin override is only available to super-user controllers, not student-facing endpoints

## Future Enhancements
- Add waiting list functionality
- Send notifications when spots become available
- Show enrollment history/audit trail
- Add capacity warnings at 80%, 90% full
