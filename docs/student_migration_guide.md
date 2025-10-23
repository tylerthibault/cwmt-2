# Student Profile System - Migration Guide

## Database Migration

This guide helps you migrate from the old course enrollment system to the new StudentProfile and CourseEnrollment system.

## What Changed

### Old System
- Simple many-to-many table: `course_enrollments` (just course_id and student_id)
- Students were directly linked to courses via User model
- No course-specific student data
- No vehicle tracking per course

### New System
- `StudentProfile` model: One-to-one with User for student-specific data
- `CourseEnrollment` model: Full-featured enrollment with vehicle info, scores, notes
- Course-specific tracking: Different vehicles, scores, and data per course
- Enrollment status tracking: active, completed, withdrawn, failed

## Migration Steps

### Option 1: Fresh Database (Recommended for Development)

If you're in development and can start fresh:

1. **Backup your current database** (if needed):
   ```bash
   cp instance/app.db instance/app.db.backup
   ```

2. **Delete the old database**:
   ```bash
   rm instance/app.db
   ```

3. **Run the application** (will create new tables):
   ```bash
   python run.py
   ```
   
   The `init_db()` function will automatically create all tables.

4. **Run seeds** to populate with test data:
   ```bash
   python seeds/run_seeds.py --all
   ```

### Option 2: Preserve Existing Data

If you have production data to preserve:

1. **Export existing enrollments** (before migration):
   ```python
   from src import create_app
   from src.models import db
   
   app = create_app()
   with app.app_context():
       # Query old course_enrollments table
       result = db.engine.execute("SELECT * FROM course_enrollments")
       enrollments = [dict(row) for row in result]
       
       # Save to file
       import json
       with open('enrollments_backup.json', 'w') as f:
           json.dump(enrollments, f)
   ```

2. **Drop old table and create new ones**:
   ```python
   from src import create_app
   from src.models import db
   
   app = create_app()
   with app.app_context():
       # Drop old table
       db.engine.execute("DROP TABLE IF EXISTS course_enrollments")
       
       # Create new tables
       db.create_all()
   ```

3. **Migrate data** to new structure:
   ```python
   from src import create_app
   from src.logic.student_logic import StudentLogic
   import json
   
   app = create_app()
   with app.app_context():
       # Load backup
       with open('enrollments_backup.json', 'r') as f:
           old_enrollments = json.load(f)
       
       # Create student profiles for all users who were enrolled
       user_ids = set(e['student_id'] for e in old_enrollments)
       for user_id in user_ids:
           try:
               StudentLogic.create_student_profile(user_id)
               print(f"Created profile for user {user_id}")
           except Exception as e:
               print(f"Error creating profile for user {user_id}: {e}")
       
       # Recreate enrollments
       for old_enrollment in old_enrollments:
           try:
               # Get student profile
               profile = StudentLogic.get_student_profile(old_enrollment['student_id'])
               if not profile:
                   continue
               
               # Create new enrollment
               StudentLogic.enroll_in_course(
                   student_id=profile.id,
                   course_id=old_enrollment['course_id'],
                   enrollment_data={'notes': 'Migrated from old system'}
               )
               print(f"Migrated enrollment for student {profile.id} in course {old_enrollment['course_id']}")
           except Exception as e:
               print(f"Error migrating enrollment: {e}")
   ```

### Option 3: Using Flask-Migrate (Recommended for Production)

If you're using Flask-Migrate (Alembic):

1. **Install Flask-Migrate** if not already:
   ```bash
   pip install Flask-Migrate
   ```

2. **Initialize migrations** (if not done):
   ```bash
   flask db init
   ```

3. **Create migration**:
   ```bash
   flask db migrate -m "Add StudentProfile and CourseEnrollment models"
   ```

4. **Review the migration file** in `migrations/versions/`

5. **Apply migration**:
   ```bash
   flask db upgrade
   ```

6. **Run data migration script** (create custom script):
   ```python
   # migrations/data_migration.py
   from alembic import op
   import sqlalchemy as sa
   from datetime import datetime
   
   def upgrade():
       # Create student profiles for existing users
       conn = op.get_bind()
       users = conn.execute("SELECT id FROM users WHERE is_admin = 0")
       
       for user in users:
           conn.execute(f"""
               INSERT INTO student_profiles (user_id, student_number, created_at, updated_at)
               VALUES ({user.id}, 'STU{user.id:05d}', '{datetime.utcnow()}', '{datetime.utcnow()}')
           """)
   ```

## Verification

After migration, verify the data:

```python
from src import create_app
from src.logic.student_logic import StudentLogic

app = create_app()
with app.app_context():
    # Check student profiles
    from src.models.student_profile import StudentProfile
    students = StudentProfile.query.all()
    print(f"Total students: {len(students)}")
    
    # Check enrollments
    from src.models.course_enrollment import CourseEnrollment
    enrollments = CourseEnrollment.query.all()
    print(f"Total enrollments: {len(enrollments)}")
    
    # Test a student's courses
    if students:
        student = students[0]
        courses = StudentLogic.get_student_courses(student.id)
        print(f"Student {student.student_number} has {len(courses)} enrollments")
```

## Rollback Plan

If you need to rollback:

### With Flask-Migrate:
```bash
flask db downgrade
```

### Manual Rollback:
1. Restore database backup:
   ```bash
   cp instance/app.db.backup instance/app.db
   ```

2. Or revert code changes and recreate database:
   ```bash
   git checkout HEAD~1  # or specific commit
   rm instance/app.db
   python run.py
   ```

## Testing the New System

After migration, test the new features:

```python
from src import create_app
from src.logic.student_logic import StudentLogic

app = create_app()
with app.app_context():
    # Get a student
    from src.models.student_profile import StudentProfile
    student = StudentProfile.query.first()
    
    # Enroll in course with vehicle info
    enrollment = StudentLogic.enroll_in_course(
        student_id=student.id,
        course_id=1,
        enrollment_data={
            'brings_motorcycle': True,
            'motorcycle_make': 'Honda',
            'motorcycle_model': 'CBR500R',
            'motorcycle_year': 2022,
            'notes': 'Testing new system'
        }
    )
    
    print(f"Enrollment created: {enrollment.id}")
    print(f"Vehicle: {enrollment.motorcycle_make} {enrollment.motorcycle_model}")
    
    # Complete the course
    StudentLogic.complete_course(enrollment.id, final_score=95.0)
    
    # Check student's overall score
    student = StudentLogic.get_student_profile_by_id(student.id)
    print(f"Overall score: {student.overall_score}")
```

## Common Issues and Solutions

### Issue: "Table already exists"
**Solution**: Drop the table first or use Flask-Migrate for proper versioning.

### Issue: "Foreign key constraint failed"
**Solution**: Ensure StudentProfile exists before creating CourseEnrollment.

### Issue: "Duplicate entry for student_id and course_id"
**Solution**: Check for existing enrollments before creating new ones.

### Issue: "User doesn't have student_profile"
**Solution**: Create student profile first using `StudentLogic.create_student_profile()`.

## Post-Migration Checklist

- [ ] All student profiles created
- [ ] All enrollments migrated
- [ ] Vehicle information preserved (if applicable)
- [ ] Scores and status preserved
- [ ] Relationships working (student.course_enrollments, course.enrollments)
- [ ] Business logic tested (enroll, complete, score updates)
- [ ] Seeds working correctly
- [ ] UI updated to use new models (if applicable)
- [ ] Tests updated (if applicable)

## Need Help?

If you encounter issues during migration:
1. Check the logs in `logs/` directory
2. Review the models in `src/models/`
3. Review the business logic in `src/logic/student_logic.py`
4. Check the documentation in `docs/student_profile_system.md`
