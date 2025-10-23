# Student Detail View System - Implementation Guide

## Overview

A comprehensive student detail viewing system allowing **instructors**, **admins**, and **super-users** to view and manage student profiles, enrollments, and academic performance.

## Features

### Role-Based Access

| Feature | Instructor | Admin | Super User |
|---------|------------|-------|------------|
| View Student List | ❌ | ✅ | ✅ |
| View Student Details | ✅ (their courses) | ✅ (all) | ✅ (all) |
| Edit Student Profile | ❌ | ✅ | ✅ |
| Update Scores | ❌ | ✅ | ✅ |
| Manage Enrollments | ❌ | ✅ | ✅ |
| View Course Roster | ✅ | ✅ | ✅ |

### Student Information Displayed

**Profile Section:**
- Student number
- Name and contact info
- Grade level
- Emergency contact details
- Account status

**Academic Performance:**
- Overall score (average of completed courses)
- GPA (0-4.0 scale)
- Course completion count
- Active enrollment count
- Progress visualization

**Course Enrollments:**
- Course name and schedule
- Enrollment status (active, completed, withdrawn, failed)
- Course score and attendance percentage
- Vehicle information (motorcycle/car details per course)
- Enrollment and completion dates
- Course-specific notes

## Routes

### Admin Routes (`/admin`)

```python
GET  /admin/students                              # List all students
GET  /admin/students/<student_id>                 # View student details
GET  /admin/students/<student_id>/edit            # Edit student profile (form)
POST /admin/students/<student_id>/edit            # Update student profile

# AJAX API Endpoints
PUT  /admin/api/students/<student_id>/enrollment/<enrollment_id>
     # Update enrollment details (attendance, notes, vehicle info)

PUT  /admin/api/students/<student_id>/enrollment/<enrollment_id>/score
     # Update course score (auto-updates overall score)

POST /admin/api/students/<student_id>/enrollment/<enrollment_id>/complete
     # Mark course as completed with optional final score
```

### Instructor Routes (`/instructor`)

```python
GET  /instructor/students/<student_id>            # View student details (read-only)
GET  /instructor/course/<course_id>/students      # View course roster
```

### Super User Routes (`/super`)

```python
GET  /super/students                              # List all students
GET  /super/students/<student_id>                 # View student details
GET  /super/students/<student_id>/edit            # Edit student profile (form)
POST /super/students/<student_id>/edit            # Update student profile

# Super users use same AJAX endpoints as admin (with /super prefix if needed)
```

## Templates

### Admin Templates
- `private/admin/students/list.html` - Student list with search
- `private/admin/students/detail.html` - Full student details with editing
- `private/admin/students/edit.html` - Profile edit form

### Instructor Templates
- `private/instructor/students/detail.html` - Read-only student view
- `private/instructor/students/course_roster.html` - Course student list

### Super User Templates
- `private/super_user/students/list.html` - Student list (same as admin)
- `private/super_user/students/detail.html` - Full student details (same as admin)
- `private/super_user/students/edit.html` - Profile edit form (same as admin)

## UI Components

### Student List Page

**Features:**
- Search functionality (name, email, student number)
- Filter by grade level
- Stats cards (total students, active students)
- Quick actions (View, Edit)
- Sortable columns

**Student Cards Display:**
- Avatar with initials
- Student number
- Name and username
- Email address
- Grade level badge
- Overall score (color-coded)
- Enrollment count
- Action buttons

### Student Detail Page

**Left Column:**
- Profile card (student info)
- Emergency contact card
- Academic performance card with:
  - Large overall score display
  - Progress bar (color-coded)
  - GPA calculation
  - Course statistics

**Right Column:**
- Enrollment cards for each course:
  - Course name and schedule
  - Status badge
  - Score input (editable for admin)
  - Attendance input (editable for admin)
  - Vehicle information display
  - Notes section
  - Enrollment dates
  - Action buttons (Complete, Withdraw)

### Edit Profile Form

**Editable Fields:**
- Student number (required)
- Grade level (dropdown)
- Emergency contact name
- Emergency contact phone

**Read-only Display:**
- User account information (name, email, username)
- Academic performance statistics
- Note about score management

## JavaScript Features

### AJAX Operations

```javascript
// Update course score
PUT /admin/api/students/{student_id}/enrollment/{enrollment_id}/score
Body: { score: 95.5 }

// Update attendance
PUT /admin/api/students/{student_id}/enrollment/{enrollment_id}
Body: { attendance_percentage: 90.0 }

// Complete course
POST /admin/api/students/{student_id}/enrollment/{enrollment_id}/complete
Body: { final_score: 92.5 }

// Withdraw from course
PUT /admin/api/students/{student_id}/enrollment/{enrollment_id}
Body: { status: 'withdrawn' }
```

### Interactive Features

- **Search:** Real-time filtering of student list
- **Score Update:** Inline editing with validation (0-100)
- **Attendance Update:** Inline editing with validation (0-100)
- **Course Completion:** One-click completion with confirmation
- **Withdrawal:** One-click withdrawal with confirmation
- **Auto-reload:** Page refreshes after updates to show new overall score

### Validation

- Score must be 0-100
- Attendance must be 0-100
- Student number required
- Phone number formatting (optional)
- Confirmation dialogs for destructive actions

## Styling

### Color Coding

**Score Ranges:**
- 90-100%: Green (success)
- 80-89%: Blue (primary)
- 70-79%: Yellow (warning)
- Below 70%: Red (danger)

**Status Badges:**
- Active: Blue (primary)
- Completed: Green (success)
- Withdrawn: Gray (secondary)
- Failed: Red (danger)

### Responsive Design

- Mobile-friendly cards
- Collapsible sections on small screens
- Touch-friendly buttons
- Responsive tables

## Usage Examples

### Admin Workflow

1. **View All Students:**
   - Navigate to `/admin/students`
   - Use search to find specific student
   - Click "View" to see details

2. **Update Student Score:**
   - Go to student detail page
   - Find enrollment in list
   - Enter new score in input field
   - Click "Update" button
   - Page reloads with updated overall score

3. **Complete a Course:**
   - On student detail page
   - Click "Mark as Completed" button
   - Confirm action
   - Course status changes to "completed"
   - Overall score recalculates automatically

4. **Edit Profile:**
   - Click "Edit Profile" button
   - Update fields as needed
   - Click "Save Changes"
   - Returns to detail view

### Instructor Workflow

1. **View Course Roster:**
   - Navigate to `/instructor/course/{course_id}/students`
   - See all enrolled students
   - Click student name to view details

2. **Check Student Info:**
   - View student's overall performance
   - See their grade level and contact info
   - Review vehicle they're bringing to course
   - Check their academic history

## Security

- **Authentication Required:** All routes require active session
- **Role-Based Access:** Decorators enforce role requirements
- **Session Validation:** Checks for token expiration
- **Authorization:** Instructors can only view students in their assigned courses
- **CSRF Protection:** Forms use Flask's CSRF token system (if enabled)

## Error Handling

```python
try:
    StudentLogic.update_course_score(enrollment_id, score)
    return jsonify({'success': True, 'message': 'Score updated'})
except ValueError as e:
    return jsonify({'success': False, 'message': str(e)}), 400
except Exception as e:
    return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
```

## Future Enhancements

Possible additions:
- Bulk score updates
- Export student data to CSV/PDF
- Email notifications to students
- Progress charts and graphs
- Student messaging system
- File upload for documents
- Photo upload for student profiles
- Certification tracking
- Payment/invoice tracking
- Attendance calendar view

## Dependencies

- Flask (web framework)
- SQLAlchemy (database ORM)
- Bootstrap 5 (UI framework)
- Bootstrap Icons (icons)
- Vanilla JavaScript (no additional JS libraries)

## Files Modified/Created

**Controllers:**
- `src/controllers/user_admin_controller.py` - Added student routes and API endpoints
- `src/controllers/instructor_controller.py` - Added read-only student viewing
- `src/controllers/super_user_controller.py` - Added full student management

**Templates:**
- `src/templates/private/admin/students/list.html`
- `src/templates/private/admin/students/detail.html`
- `src/templates/private/admin/students/edit.html`
- `src/templates/private/instructor/students/detail.html`
- `src/templates/private/instructor/students/course_roster.html`
- `src/templates/private/super_user/students/*.html` (copied from admin)

**Documentation:**
- This file

## Testing Checklist

- [ ] Admin can view student list
- [ ] Admin can view student details
- [ ] Admin can edit student profile
- [ ] Admin can update course scores
- [ ] Admin can update attendance
- [ ] Admin can complete courses
- [ ] Admin can withdraw students
- [ ] Instructor can view students in their courses
- [ ] Instructor cannot view students in other courses
- [ ] Super user has full access
- [ ] Search functionality works
- [ ] AJAX updates work without page refresh
- [ ] Overall score recalculates correctly
- [ ] Form validation works
- [ ] Mobile responsive
- [ ] Error messages display correctly

## Support

For issues or questions, refer to:
- `docs/student_profile_system.md` - System architecture
- `docs/student_quick_reference.md` - API quick reference
- `src/logic/student_logic.py` - Business logic implementation
