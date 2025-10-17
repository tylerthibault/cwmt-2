# Course Management Updates - Max Students

## Summary
Updated the course management system to include the `max_students` field in both the UI and seed data.

## Changes Made

### 1. Seed File (`seeds/seed_courses.py`)
- ✅ Added `max_students` field to all 38 course templates
- Values set based on experience level and course type:
  - **Beginner courses**: 8-12 students
  - **Intermediate courses**: 10-15 students  
  - **Advanced courses**: 6-10 students
  - **Specialized/Skills courses**: 6-12 students

### 2. Course Management Page (`src/templates/private/super_user/course_management/index.html`)

#### Create Template Form
- Added "Max Students" input field
- Default value: 12
- Min value: 1
- Required field

#### Sidebar Course Cards
- Added `max_students` badge showing "Max: X"
- Color: Warning (yellow/orange)
- Wraps with other badges for responsive layout

#### Course Details Header
- Added `max_students` badge: "Max: X students"
- Positioned between duration and experience level badges

#### Course Information Card
- Added "Max Students" field showing count with proper pluralization
- Reorganized layout:
  - Row 1: Duration, Max Students, Experience Level, Status
  - Row 2: Courses Created (standalone)

#### Edit Template Form
- Added "Max Students" input field
- Bound to existing course value
- Min value: 1
- Required field

## UI Display Examples

### Sidebar Badge
```
Get Riding
[2 days] [Beginner] [Max: 12]
```

### Header Badges
```
Get Riding
[2 days] [Max: 12 students] [Beginner] [Active]
```

### Course Info Section
```
Duration: 2 days
Max Students: 12 students
Experience Level: Beginner
Status: Active

Courses Created: 5 courses
```

## Form Fields

### Create Form
- Course Name (text, required)
- Description (textarea, optional)
- Duration (number, min 1, required)
- **Max Students (number, min 1, required, default: 12)** ← NEW
- Experience Level (select, required)

### Edit Form
Same fields as create form, pre-populated with existing values

## Database Impact
- The `max_students` column already exists in both `course_templates` and `courses` tables
- Seed data now properly populates this field
- All new templates will require this field

## Testing Checklist
- [ ] Create new course template with max_students
- [ ] Edit existing template max_students value
- [ ] Verify badges display correctly on sidebar
- [ ] Verify badges display correctly on header
- [ ] Verify course info section shows max_students
- [ ] Run seed file to populate with max_students values
- [ ] Verify student enrollment respects max_students limit
- [ ] Verify admin can override max_students limit

## Notes
- The UI properly handles singular/plural forms ("1 student" vs "2 students")
- All fields are required to prevent null values
- The max_students field is prominently displayed to help admins manage capacity
