# Course Management UI Implementation

## Overview
Implemented a comprehensive course management interface for super-users to manage course templates in the CWMT application.

## Implementation Details

### Frontend Template
**File:** `src/templates/private/super_user/course_management/index.html`

#### Layout Structure
The page uses a two-column layout:
- **Left Sidebar (col-3)**: Lists all course templates with key information
- **Right Panel (col-9)**: Shows detailed information for the selected course template

#### Features Implemented

##### 1. Sidebar Course List
- Displays all course templates in a scrollable list
- Each course item shows:
  - Course name
  - Duration (in days)
  - Experience level badge
  - Active/Inactive status badge
- Click on any course to view its details
- Active selection is highlighted
- Sticky positioning keeps sidebar visible while scrolling

##### 2. Course Details Panel
Shows comprehensive information about the selected course template:

**Header Section:**
- Course name
- Badges: Duration, Experience level, Active/Inactive status
- Action buttons: Edit, Activate/Deactivate

**Description Section:**
- Full course description

**Course Information Section:**
- Duration
- Experience level
- Active status
- Number of scheduled courses created from this template

**Scheduled Courses Section:**
- Table showing all course instances created from this template
- Displays: Date, Time, Student, Instructors, Status
- Shows "Not assigned" for empty slots
- Color-coded status badges

##### 3. Add New Course Template
- Menu icon button in page header (+ icon)
- Dropdown form with fields:
  - Course Name (required)
  - Description (optional)
  - Duration in days (required, minimum 1)
  - Experience Level (required: Beginner/Intermediate/Advanced)
- Form validation
- Creates new course template on submission

##### 4. Edit Course Template
- Click "Edit" button to switch to edit mode
- Inline form with pre-filled values
- Update fields:
  - Course Name
  - Description
  - Duration
  - Experience Level
- Save or Cancel buttons
- Returns to detail view after save/cancel

##### 5. Activate/Deactivate Templates
- Deactivate button for active templates
- Activate button for inactive templates
- Uses POST forms for CSRF protection
- Flash messages for success/error feedback

#### Styling
Custom CSS included in template:
- Course sidebar styling
- Course item cards with hover effects
- Active state highlighting
- Details panel layout
- Info grid for course information
- Edit form styling
- Empty state design
- Responsive badges and buttons

#### JavaScript Functionality
- Toggle dropdown menu for adding templates
- Close menu on outside click
- Switch between course details views
- Toggle between detail and edit modes
- Active state management for sidebar items

### Backend Controller
**File:** `src/controllers/super_user_controller.py`

#### Routes Added

##### 1. `GET /super/course-management`
- Displays course management page
- Fetches all course templates from database
- Passes templates to template context

##### 2. `POST /super/course-management/create-template`
- Creates new course template
- Validates form data
- Uses `CourseTemplateLogic.create_template()`
- Returns with flash message
- Redirects to course management page

##### 3. `POST /super/course-management/update-template`
- Updates existing course template
- Validates template ID and form data
- Uses `CourseTemplateLogic.update_template()`
- Returns with flash message
- Redirects to course management page

##### 4. `POST /super/course-management/deactivate-template`
- Deactivates a course template (soft delete)
- Uses `CourseTemplateLogic.deactivate_template()`
- Returns with flash message
- Redirects to course management page

##### 5. `POST /super/course-management/activate-template`
- Reactivates a deactivated course template
- Updates `is_active` flag to True
- Returns with flash message
- Redirects to course management page

#### Error Handling
All routes include try-catch blocks:
- Catches `CourseValidationError` for validation issues
- Catches `CourseBusinessError` for business rule violations
- Catches generic exceptions for unexpected errors
- All errors display flash messages to user

### Integration with Logic Layer
All business logic delegated to `CourseTemplateLogic` class:
- `create_template(data)` - Validation and creation
- `update_template(template_id, data)` - Validation and updates
- `deactivate_template(template_id)` - Soft delete
- `get_template(template_id)` - Retrieve template

### User Experience Features

#### Visual Feedback
- Color-coded badges for status, level, duration
- Hover effects on sidebar items
- Active state highlighting
- Bootstrap-style flash messages
- Loading states (implicit through redirects)

#### Data Display
- Clean, organized information layout
- Responsive grid for course info
- Table for scheduled courses
- Empty states for no data
- "Not assigned" placeholders for null values

#### Form Validation
- Required field indicators
- Input type validation (number for duration)
- Dropdown constraints for experience level
- Server-side validation through logic layer

### Current Course Templates
Based on `seed_courses.py`, two default templates are created:

1. **Get Riding**
   - Duration: 2 days
   - Level: Beginner
   - Description: Essential motorcycle riding skills

2. **Street Smart**
   - Duration: 1 day
   - Level: Intermediate
   - Description: Street riding awareness and defensive riding

## Usage Flow

### Viewing Course Templates
1. Navigate to `/super/course-management`
2. See list of templates in sidebar
3. Click on any template to view details
4. View scheduled courses for that template

### Creating New Template
1. Click the + icon in page header
2. Fill in the form:
   - Course name
   - Description (optional)
   - Duration (days)
   - Experience level
3. Click "Create Template"
4. See success message
5. New template appears in sidebar

### Editing Template
1. Select a template from sidebar
2. Click "Edit" button
3. Modify fields as needed
4. Click "Save Changes" or "Cancel"
5. See success message
6. Changes reflected immediately

### Deactivating Template
1. Select an active template
2. Click "Deactivate" button
3. Confirm action (via form submission)
4. See success message
5. Template marked as inactive

### Activating Template
1. Select an inactive template
2. Click "Activate" button
3. See success message
4. Template marked as active

## Security Features
- `@super_user_required` decorator on all routes
- Session validation via logbook
- Role checking (super-user only)
- CSRF protection via POST forms
- No direct database manipulation in templates
- All operations through logic layer

## Architecture Compliance

✅ **Thin Controllers**
- Controllers only handle HTTP concerns
- Delegate to logic layer for business rules
- Simple request/response handling

✅ **Template Logic**
- Minimal logic in templates
- Display-only calculations
- No business rules

✅ **Separation of Concerns**
- UI layer (template)
- Controller layer (routes)
- Business logic layer (CourseTemplateLogic)
- Data layer (models)

## Future Enhancements

### Potential Improvements
1. **Course Instance Management**
   - Add/edit scheduled courses from this interface
   - Assign students and instructors
   - Manage course status

2. **Filtering & Searching**
   - Filter by experience level
   - Filter by active/inactive
   - Search by name

3. **Bulk Operations**
   - Select multiple templates
   - Bulk activate/deactivate
   - Bulk delete

4. **Analytics**
   - Most popular templates
   - Completion rates
   - Revenue per template

5. **Calendar Integration**
   - Visual calendar view
   - Drag-and-drop scheduling
   - Conflict detection

6. **Export/Import**
   - Export template configurations
   - Import from CSV/JSON
   - Clone templates

## Testing Recommendations

### Manual Testing Checklist
- [ ] Create new course template
- [ ] Edit existing template
- [ ] Deactivate template
- [ ] Reactivate template
- [ ] View template with no scheduled courses
- [ ] View template with scheduled courses
- [ ] Switch between different templates
- [ ] Test form validation (empty fields)
- [ ] Test duplicate template names
- [ ] Test with no templates (empty state)

### Automated Testing
Recommended test cases:
1. Test route access control (super-user only)
2. Test template creation validation
3. Test template update validation
4. Test activate/deactivate operations
5. Test error handling for missing IDs
6. Test error handling for invalid data

## Files Modified

### Created:
- `docs/course_management_ui_implementation.md` - This documentation

### Modified:
- `src/templates/private/super_user/course_management/index.html` - Full UI implementation
- `src/controllers/super_user_controller.py` - Added 5 new routes for course template management

### Dependencies:
- `src/logic/course_logic.py` - CourseTemplateLogic class
- `src/models/courses_model.py` - CourseTemplate and Course models
- Bootstrap CSS (via bases/private.html)
- Font Awesome icons (via bases/private.html)
