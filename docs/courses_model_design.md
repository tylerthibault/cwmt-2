# Courses Model Design Documentation

## Overview
This document describes the database schema for the courses system, which includes course templates and course instances.

## Database Tables

### 1. CourseTemplate Table (`course_templates`)

**Purpose:** Stores reusable course templates/blueprints that define the configuration for courses.

**Columns:**
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | Integer | No | Primary key (inherited from BaseModel) |
| name | String(120) | No | Name of the course template |
| description | Text | Yes | Detailed description of the course |
| duration_days | Integer | No | Length of the course in days |
| experience_level | String(50) | No | Required experience level (e.g., 'beginner', 'intermediate', 'advanced') |
| is_active | Boolean | No | Whether this template is active (default: True) |
| created_at | DateTime | No | When the template was created (inherited from BaseModel) |
| updated_at | DateTime | No | When the template was last updated (inherited from BaseModel) |

**Relationships:**
- `courses` - One-to-Many relationship with Course model (a template can have many course instances)

**Methods:**
- `to_dict()` - Serializes the template to a dictionary

### 2. Course Table (`courses`)

**Purpose:** Stores individual course instances scheduled at specific dates/times with assigned users.

**Columns:**
| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | Integer | No | Primary key (inherited from BaseModel) |
| course_template_id | Integer | No | Foreign key to course_templates table |
| course_date | Date | No | Date when the course is scheduled |
| course_time | Time | No | Time when the course starts |
| status | String(50) | No | Current status of the course (default: 'scheduled') |
| student_id | Integer | Yes | Foreign key to users table (the enrolled student) |
| instructor1_id | Integer | Yes | Foreign key to users table (first instructor) |
| instructor2_id | Integer | Yes | Foreign key to users table (second instructor) |
| created_at | DateTime | No | When the course was created (inherited from BaseModel) |
| updated_at | DateTime | No | When the course was last updated (inherited from BaseModel) |

**Status Values:**
- `scheduled` - Course is scheduled but hasn't started
- `in_progress` - Course is currently running
- `completed` - Course has been completed
- `cancelled` - Course was cancelled

**Relationships:**
- `template` - Many-to-One relationship with CourseTemplate (each course is based on one template)
- `student` - Many-to-One relationship with User (one student per course)
- `instructor1` - Many-to-One relationship with User (first instructor)
- `instructor2` - Many-to-One relationship with User (second instructor)

**Methods:**
- `to_dict(include_users=False, include_template=False)` - Serializes the course to a dictionary with optional user and template details

## Relationships Diagram

```
CourseTemplate (1) ────< (Many) Course
                              ├─> (1) User (student)
                              ├─> (1) User (instructor1)
                              └─> (1) User (instructor2)
```

## Usage Examples

### Creating a Course Template

```python
from src.models.courses_model import CourseTemplate
from src.models import db

# In your logic layer (e.g., src/logic/course_logic.py)
template = CourseTemplate(
    name="Advanced Wilderness Survival",
    description="A comprehensive course on wilderness survival techniques",
    duration_days=5,
    experience_level="advanced",
    is_active=True
)
db.session.add(template)
db.session.commit()
```

### Creating a Course Instance

```python
from src.models.courses_model import Course
from datetime import date, time

# In your logic layer
course = Course(
    course_template_id=1,
    course_date=date(2025, 11, 1),
    course_time=time(9, 0),
    status="scheduled",
    student_id=5,  # User ID of the student
    instructor1_id=2,  # User ID of first instructor
    instructor2_id=3   # User ID of second instructor
)
db.session.add(course)
db.session.commit()
```

### Querying Courses

```python
# Get all courses for a specific template
template = CourseTemplate.query.get(1)
courses = template.courses

# Get all courses for a student
from src.models.user import User
student = User.query.get(5)
student_courses = student.enrolled_courses

# Get all courses where a user is an instructor
instructor_courses = user.courses_as_instructor1 + user.courses_as_instructor2

# Get courses by date range
from datetime import date
courses = Course.query.filter(
    Course.course_date >= date(2025, 11, 1),
    Course.course_date <= date(2025, 11, 30)
).all()
```

## Next Steps

1. **Create Logic Layer** (`src/logic/course_logic.py`):
   - Business logic for creating/updating courses and templates
   - Validation (e.g., ensuring instructors have proper roles)
   - Enrollment logic
   - Course status management

2. **Create Controller Routes** (`src/controllers/course_controller.py`):
   - REST API endpoints for CRUD operations
   - Course enrollment endpoints
   - Course schedule management

3. **Add Constraints** (if needed):
   - Unique constraints on course scheduling
   - Check constraints for valid status transitions
   - Validation that instructors have instructor role

4. **Create Seed Data** (`src/utils/seed_courses.py`):
   - Sample course templates
   - Sample scheduled courses

## Model Architecture Compliance

These models follow the **THIN MODEL** pattern as defined in the project constitution:

✅ **Contains:**
- Database schema (columns, relationships, constraints)
- Simple serialization methods (`to_dict()`)
- Basic model structure

❌ **Does NOT contain:**
- Business logic (belongs in `src/logic/course_logic.py`)
- Validation rules (belongs in logic layer)
- Complex calculations (belongs in logic layer)
- External service calls (belongs in logic layer)

All business logic for course management should be implemented in a dedicated logic layer module.
