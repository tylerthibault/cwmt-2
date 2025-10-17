# Instructor Schedule Page Implementation

## Overview
This implementation provides instructors with a comprehensive interface to view upcoming courses and manage their teaching assignments. The page displays all scheduled courses and allows instructors to sign up for available positions or remove themselves from courses they're assigned to.

## Files Created/Modified

### 1. HTML Template
**File:** `src/templates/private/instructor/shedule/index.html`

**Features:**
- **Responsive Grid Layout**: Displays courses in a card-based grid (3 columns on desktop, 2 on tablet, 1 on mobile)
- **Advanced Filtering**:
  - Status filter: All, Available to Sign Up, My Assigned Courses, Fully Staffed
  - Date range filter: Next 7 Days (default), Next 30 Days, All Upcoming
- **Course Information Display**:
  - Course name and experience level
  - Date, time, and location
  - Duration and description
  - Student assignment status
  - Both instructor slots with current assignments
- **Interactive Actions**:
  - Sign up for courses (when slots available)
  - Remove yourself from assigned courses
  - Visual indicators for your assignments
- **Status Badges**:
  - "2 Spots Open" - Both instructor positions available
  - "1 Spot Open" - One instructor needed
  - "Fully Staffed" - Both instructors assigned
  - "You" - Indicates your assignments
- **Legend Section**: Explains all status badges for clarity

### 2. JavaScript Controller
**File:** `src/static/js/private/instructor_schedule.js`

**Functions:**
- `filterByStatus(status)` - Filters courses based on staffing status
- `filterByDate(range)` - Filters courses by date range
- `signUpForCourse(courseId)` - Handles instructor sign-up with confirmation
- `removeFromCourse(courseId)` - Handles instructor removal with confirmation
- `updateVisibleCount()` - Updates count of visible courses (for debugging)

**Features:**
- AJAX calls to backend for sign-up/removal actions
- Loading states on buttons during operations
- Error handling with user-friendly messages
- Automatic page reload after successful operations
- Confirmation dialogs before destructive actions

### 3. Backend Controller
**File:** `src/controllers/instructor_controller.py`

**Blueprint:** `instructor_bp` with prefix `/instructor`

**Routes:**
1. **GET /instructor/schedule** - Main schedule page
   - Displays all upcoming scheduled courses
   - Ordered by date and time
   - Includes course template, student, and instructor data

2. **POST /instructor/schedule/signup/<course_id>** - Sign up for a course
   - Validates course exists and is in the future
   - Checks user isn't already assigned
   - Assigns to first available instructor slot
   - Returns JSON response

3. **POST /instructor/schedule/remove/<course_id>** - Remove from course
   - Validates user is assigned to the course
   - Checks course is still in the future
   - Removes user from their assigned slot
   - Returns JSON response

4. **GET /instructor/my-courses** - View assigned courses (placeholder)
   - Future enhancement to show only courses where user is instructor

**Security:**
- `@login_required` decorator on all routes
- `@instructor_required` custom decorator ensures user has instructor role
- Role validation using the existing Role model

### 4. Application Registration
**File:** `src/__init__.py`

Added instructor blueprint registration in `init_blueprints()` function.

## Business Logic

### Course Assignment Rules
1. **Availability Check**: Only scheduled, future courses can be signed up for
2. **Slot Assignment**: 
   - First available slot gets filled (instructor1, then instructor2)
   - Prevents duplicate assignments (same person in both slots)
3. **Removal Restrictions**: Can only remove from future scheduled courses
4. **Role Validation**: Only users with 'instructor' role can access

### Data Flow
```
User Action → JavaScript (client-side validation) 
           → AJAX Request 
           → Flask Route (authentication & authorization) 
           → Database Update 
           → JSON Response 
           → Page Reload (to reflect changes)
```

## UI/UX Features

### Visual Design
- Follows existing Bootstrap 5 and custom component patterns
- Uses project's gradient card borders for visual consistency
- Color-coded badges for quick status recognition
- Font Awesome icons for visual clarity

### Responsive Design
- Mobile-first approach with Bootstrap grid
- Cards stack vertically on mobile
- Filters wrap gracefully on smaller screens
- Touch-friendly button sizes

### User Feedback
- Loading spinners during async operations
- Confirmation dialogs for important actions
- Success/error messages via flash messages
- Visual distinction for "My Courses" with bold text and badges

## Integration with Existing System

### Uses Existing Components:
- `bases/private.html` - Base template with navigation
- `src/models/courses_model.py` - Course and CourseTemplate models
- `src/logic/course_logic.py` - Course business logic methods
- `src/static/css/components/cards.css` - Card styling
- Flash message system for user notifications

### Follows Project Patterns:
- **Thin Controllers**: Routes only handle HTTP logic, delegate to logic layer
- **Role-Based Access Control**: Uses existing Role model and relationships
- **Blueprint Architecture**: Modular route organization
- **Template Inheritance**: Extends base templates
- **Asset Organization**: CSS/JS in proper directories

## Database Queries

### Main Schedule Query
```python
Course.query.filter(
    Course.course_date >= today,
    Course.status == 'scheduled'
).order_by(
    Course.course_date,
    Course.course_time
).all()
```

### Instructor's Courses Query
```python
CourseLogic.get_courses_for_instructor(instructor_id)
# Uses OR condition: instructor1_id OR instructor2_id
```

## Testing Checklist

- [ ] Page loads successfully with courses displayed
- [ ] Filters work correctly (status and date range)
- [ ] Sign-up button appears only when slots available
- [ ] Sign-up functionality works and assigns to correct slot
- [ ] Remove button appears only on assigned courses
- [ ] Remove functionality works correctly
- [ ] Proper authorization (only instructors can access)
- [ ] Visual indicators show correctly for user's assignments
- [ ] Error handling displays appropriate messages
- [ ] Responsive layout works on mobile, tablet, desktop
- [ ] Loading states display during operations

## Future Enhancements

1. **Calendar View**: Add calendar visualization option
2. **Email Notifications**: Notify instructors of new course opportunities
3. **Course History**: Show past courses taught
4. **Conflict Detection**: Warn about scheduling conflicts
5. **Bulk Actions**: Sign up for multiple courses at once
6. **Export**: Export schedule to calendar apps (iCal)
7. **Notes**: Allow instructors to add notes to their assigned courses
8. **Skill Matching**: Recommend courses based on instructor experience level

## Dependencies

All required dependencies are already in the project:
- Flask and Flask-Login (authentication)
- SQLAlchemy (database ORM)
- Bootstrap 5 (UI framework)
- Font Awesome (icons)

No additional packages need to be installed.

## Notes

- The folder name is "shedule" (typo in original structure) - maintained for consistency
- Current user context is available via `current_user` from Flask-Login
- All database operations use proper transaction handling with rollback on errors
- JSON API responses follow standard format with success/error indicators
