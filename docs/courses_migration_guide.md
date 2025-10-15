# Course System Database Migration Guide

## Overview
This guide helps you add the new course tables to your existing database.

## Option 1: Fresh Database (Recommended for Development)

If you're in development and can reset your database:

1. **Backup your current database** (if needed):
   ```bash
   cp instance/your_database.db instance/your_database.backup.db
   ```

2. **Delete the existing database**:
   ```bash
   rm instance/your_database.db
   ```

3. **Restart your Flask application**:
   ```bash
   python run.py
   ```

The database will be recreated with all tables including the new course tables, and default course templates will be seeded automatically.

## Option 2: Add Tables to Existing Database

If you want to keep your existing data:

### Manual Migration (SQL)

1. **Connect to your database** and run:

```sql
-- Create course_templates table
CREATE TABLE IF NOT EXISTS course_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL,
    description TEXT,
    duration_days INTEGER NOT NULL,
    experience_level VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create courses table
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_template_id INTEGER NOT NULL,
    course_date DATE NOT NULL,
    course_time TIME NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'scheduled',
    student_id INTEGER,
    instructor1_id INTEGER,
    instructor2_id INTEGER,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_template_id) REFERENCES course_templates (id),
    FOREIGN KEY (student_id) REFERENCES users (id),
    FOREIGN KEY (instructor1_id) REFERENCES users (id),
    FOREIGN KEY (instructor2_id) REFERENCES users (id)
);
```

2. **Seed default course templates**:

```bash
python -c "from src import create_app; from src.utils.seed_courses import seed_default_course_templates; app = create_app(); app.app_context().push(); seed_default_course_templates(app)"
```

### Using Flask-Migrate (If Installed)

If you're using Flask-Migrate (Alembic):

1. **Generate migration**:
   ```bash
   flask db migrate -m "Add course and course_template tables"
   ```

2. **Review the migration file** in `migrations/versions/`

3. **Apply migration**:
   ```bash
   flask db upgrade
   ```

4. **Seed course templates**:
   ```bash
   python src/utils/seed_courses.py
   ```

## Verify Installation

After migration, verify the tables exist:

```python
from src import create_app
from src.models.courses_model import Course, CourseTemplate

app = create_app()
with app.app_context():
    # Check templates
    templates = CourseTemplate.query.all()
    print(f"Found {len(templates)} course templates")
    
    # Check courses
    courses = Course.query.all()
    print(f"Found {len(courses)} courses")
```

## Test the Implementation

Create a test course:

```python
from src import create_app
from src.logic.course_logic import CourseTemplateLogic, CourseLogic
from datetime import date, time

app = create_app()
with app.app_context():
    # Create a custom template
    template = CourseTemplateLogic.create_template({
        'name': 'Test Course',
        'description': 'A test course',
        'duration_days': 3,
        'experience_level': 'beginner'
    })
    print(f"Created template: {template.to_dict()}")
    
    # Create a course (requires existing users with student and instructor roles)
    # You'll need to replace these IDs with actual user IDs from your database
    try:
        course = CourseLogic.create_course({
            'course_template_id': template.id,
            'course_date': date(2025, 12, 1),
            'course_time': time(9, 0),
            'student_id': 1,  # Replace with actual student user ID
            'instructor1_id': 2,  # Replace with actual instructor user ID
            'instructor2_id': 3   # Replace with actual instructor user ID
        })
        print(f"Created course: {course.to_dict()}")
    except Exception as e:
        print(f"Note: {e}")
        print("You'll need users with student and instructor roles to create courses")
```

## Troubleshooting

### "Role 'student' or 'instructor' not found"
Make sure you have the roles seeded:
```python
from src.utils.seed_roles import seed_default_roles
seed_default_roles(app)
```

### "Table already exists" error
This means the tables were already created. You can skip table creation and just seed the templates.

### Foreign key constraint errors
Make sure your users table exists before creating courses with student/instructor references.

## Next Steps

Once the tables are created and verified:

1. ✅ Create some test users with 'student' and 'instructor' roles
2. ✅ Create course instances using the logic layer
3. ✅ Build controller endpoints for the API
4. ✅ Create frontend templates for course management
5. ✅ Add unit tests for the logic layer

## Rollback (If Needed)

If you need to remove the course tables:

```sql
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS course_templates;
```

Then restart your application.
