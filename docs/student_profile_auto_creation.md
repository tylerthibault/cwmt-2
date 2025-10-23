# Student Profile Auto-Creation

## Overview
This document describes the automatic StudentProfile creation when a user is assigned the "student" role.

## Implementation

### When StudentProfile is Created
StudentProfile is automatically created in the following scenarios:

#### 1. User Registration (auth_logic.py)
When a new user registers through the public registration form:
- User is created
- "student" role is assigned
- **StudentProfile is automatically created**

```python
# In AuthLogic.validate_registration()
user = User.create(...)
role = Role.query.filter_by(name='student').first()
UserHasRoles.assign_role(user.id, role.id)

# Auto-create student profile
StudentLogic.create_student_profile(user.id)
```

#### 2. Admin/Super-User Creates User (user_logic.py)
When an admin or super-user creates a new user with the "student" role:
- User is created
- Role is assigned based on form data
- **If role is "student", StudentProfile is automatically created**

```python
# In UserLogic.create_user()
user = User.create(...)
if data.get('role_name'):
    role = Role.get_by_name(data.get('role_name'))
    if role:
        UserHasRoles.assign_role(user.id, role.id)
        
        # If role is student, create student profile
        if role.name == 'student':
            StudentLogic.create_student_profile(user.id)
```

#### 3. Adding Student Role to Existing User (super_user_controller.py)
When a super-user adds the "student" role to an existing user:
- Role is assigned
- **StudentProfile is created if it doesn't already exist**

```python
# In add_user_to_role()
UserHasRoles.assign_role(int(user_id), role.id)

# If role is student, create student profile if it doesn't exist
if role_name == 'student':
    if not StudentLogic.get_student_profile(int(user_id)):
        StudentLogic.create_student_profile(int(user_id))
```

## Error Handling

All auto-creation attempts include proper error handling:

### Non-Critical Failures
StudentProfile creation failures are treated as warnings rather than fatal errors:
- User creation/role assignment still succeeds
- Warning message is flashed to the user
- Error is logged for debugging

This ensures that:
- User accounts are not left in an inconsistent state
- Admins can manually create the profile later if needed
- The system remains functional even if profile creation fails

### Example Error Handling
```python
try:
    StudentLogic.create_student_profile(user.id)
except Exception as e:
    flash(f'Warning: Student profile creation failed: {str(e)}', 'warning')
    # User creation/role assignment continues
```

## Database Relationships

When a StudentProfile is created:
1. **StudentProfile** record created with:
   - `user_id` (foreign key to User)
   - Default values for optional fields (student_number, grade_level, etc.)
   
2. **User** can access profile via:
   - `user.student_profile` (one-to-one relationship)
   
3. **No CourseEnrollments** created yet:
   - Enrollments are created separately when student is enrolled in courses
   - Use `StudentLogic.enroll_in_course()` to create enrollments

## Manual Profile Creation

If auto-creation fails or a profile needs to be created manually:

```python
from src.logic.student_logic import StudentLogic

# Basic profile
StudentLogic.create_student_profile(user_id)

# Profile with initial data
student_data = {
    'student_number': 'S001',
    'grade_level': '10',
    'emergency_contact_name': 'John Doe',
    'emergency_contact_phone': '555-1234'
}
StudentLogic.create_student_profile(user_id, student_data)
```

## Validation

StudentLogic.create_student_profile() includes validation:
- User must exist
- StudentProfile must not already exist for that user
- Any provided student_data is validated

## Modified Files

1. **src/logic/auth_logic.py**
   - Added auto-creation in `validate_registration()`
   
2. **src/logic/user_logic.py**
   - Added auto-creation in `create_user()`
   
3. **src/controllers/super_user_controller.py**
   - Added auto-creation in `add_user_to_role()`

## Testing Checklist

- [ ] Register new user → StudentProfile created
- [ ] Admin creates user with student role → StudentProfile created
- [ ] Super-user creates user with student role → StudentProfile created
- [ ] Super-user adds student role to existing user → StudentProfile created
- [ ] Verify profile not duplicated if already exists
- [ ] Verify error handling doesn't break user creation
- [ ] Verify student can be enrolled in courses after profile creation

## Related Documentation

- [Student Profile System](student_profile_system.md) - Complete system overview
- [Student Migration Guide](student_migration_guide.md) - Database migration
- [Student Quick Reference](student_quick_reference.md) - API reference
