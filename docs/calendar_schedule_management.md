# Calendar-Based Schedule Management Implementation

## Overview
Implemented a full-featured calendar interface for admin users to schedule course instances. The calendar displays multi-day courses spanning the duration specified in the course template.

**Date Implemented:** October 15, 2025  
**Purpose:** Allow admin (secretary) users to visually manage course schedules on a calendar

---

## Technology Stack

### Frontend
- **FullCalendar v6.1.10** - Interactive JavaScript calendar library
- **Bootstrap 5** - UI framework and modals
- **Font Awesome** - Icons
- **Custom CSS** - Schedule management specific styles

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - ORM for database operations
- **Jinja2** - Template engine

---

## Features Implemented

### 1. Interactive Calendar Display
- **Monthly/Weekly/Daily Views** - Toggle between different calendar views
- **Color-Coded Events** - Different colors for different course statuses:
  - 🔵 Blue (#3788d8): Scheduled
  - 🟠 Orange (#ffa500): In Progress
  - 🟢 Green (#28a745): Completed
  - 🔴 Red (#dc3545): Cancelled

### 2. Multi-Day Course Spanning
- Courses automatically span multiple days based on template `duration_days`
- Example: A 3-day course starting on Monday will display across Monday, Tuesday, and Wednesday
- Calendar calculates end date: `end_date = start_date + duration_days`

### 3. Course Template Sidebar
- **Template Selection** - Click "Add to Calendar" button to select a template
- **Visual Feedback** - Selected template card is highlighted
- **Template Details** - Shows name, description, duration, and experience level
- **Active Filters** - Only displays active course templates

### 4. Add Course Modal
- **Auto-Populated Fields** - Template name and duration pre-filled
- **Date/Time Selection** - Start date and time inputs
- **Location Field** - Optional location entry
- **Status Dropdown** - Set initial status
- **Participant Assignment** - Assign student and 2 instructors (optional)
- **Duration Notice** - Alert showing how many days the course will span

### 5. View/Edit Course Details
- **Click Events** - Click any calendar event to view details
- **Course Information** - Template, date, time, duration, location, status
- **Participant Info** - Student and instructor assignments
- **Edit Link** - Navigate to edit page

### 6. Edit Course Page
- **Update All Fields** - Modify template, date, time, location, status, participants
- **Validation** - Form validation before submission
- **Delete Option** - Danger zone with confirmation dialog

---

## File Structure

### Templates
```
src/templates/private/admin/schedule_management/
├── index.html          # Main calendar view (237 lines)
└── edit.html           # Edit course form (179 lines)
```

### JavaScript
```
src/static/js/private/
└── schedule_management.js    # Calendar logic (221 lines)
```

### CSS
```
src/static/css/private/
└── schedule_management.css   # Styles (213 lines)
```

### Backend
```
src/controllers/
└── user_admin_controller.py  # Routes updated with serialization
```

---

## How It Works

### Workflow: Adding a Course to the Calendar

1. **Select Template**
   - User clicks "Add to Calendar" on a template card
   - Template is stored in JavaScript variable
   - Template card gets highlighted with blue border

2. **Click Calendar Date**
   - User clicks desired start date on calendar
   - Modal opens with pre-filled template information
   - Start date is set to the clicked date

3. **Fill Modal Form**
   - User reviews/modifies date and time
   - Optionally adds location
   - Optionally assigns student and instructors
   - Selects status (defaults to "Scheduled")

4. **Submit Form**
   - Form POSTs to `/admin/schedule/create`
   - Controller extracts form data
   - Delegates to `CourseLogic.create_course_instance(data)`
   - Logic layer validates and creates course
   - Redirects back to schedule with flash message

5. **Calendar Updates**
   - New course appears on calendar
   - Event spans the correct number of days
   - Color matches the status

### Data Flow

```
User Action → JavaScript Event Handler → Modal Display
                                              ↓
                                         Form Submit
                                              ↓
                         POST /admin/schedule/create
                                              ↓
                              user_admin_controller.py
                                              ↓
                         CourseLogic.create_course_instance()
                                              ↓
                              Validate & Create Course
                                              ↓
                                    Save to Database
                                              ↓
                          Redirect to Schedule Dashboard
                                              ↓
                              Calendar Shows New Event
```

---

## Calendar Event Data Structure

### Event Object (FullCalendar)
```javascript
{
    id: 123,                           // Course ID
    title: "Get Riding",               // Template name
    start: "2025-10-20",               // Start date
    end: "2025-10-22",                 // Calculated: start + duration
    backgroundColor: "#3788d8",        // Status color
    borderColor: "#3788d8",            // Status color
    extendedProps: {
        courseId: 123,
        templateId: 5,
        status: "scheduled",
        location: "Main Arena",
        studentId: 10,
        instructor1Id: 3,
        instructor2Id: 7,
        duration: 2                    // Days
    }
}
```

### Server Data (Passed to JavaScript)
```python
# Controller serializes courses with templates
all_courses = []
for course in all_courses_raw:
    course_dict = course.to_dict(include_users=True, include_template=True)
    all_courses.append(course_dict)

# Passed to template
window.existingCourses = {{ all_courses|tojson|safe }};
window.courseTemplates = {{ all_templates|tojson|safe }};
```

---

## Key JavaScript Functions

### `loadExistingCourses()`
- Reads `window.existingCourses` (set by Jinja2)
- Transforms course data into FullCalendar event format
- Calculates end dates based on duration
- Returns array of event objects

### `handleDateClick(info)`
- Triggered when user clicks calendar date
- Checks if template is selected
- Opens modal with selected date
- Pre-fills form fields

### `handleEventClick(info)`
- Triggered when user clicks existing event
- Extracts course ID from event
- Loads course details
- Opens view modal

### `openAddCourseModal(dateStr)`
- Populates modal with template data
- Sets date input to clicked date
- Calculates duration display
- Shows Bootstrap modal

### `showCourseDetails(courseId)`
- Finds course in existingCourses array
- Builds HTML for course details
- Displays in modal
- Sets edit button URL

### `getStatusColor(status)`
- Maps status strings to hex colors
- Returns appropriate color for event styling

---

## CSS Highlights

### Template Card Selection
```css
.template-card.selected {
    border-color: #0d6efd;
    background-color: rgba(13, 110, 253, 0.05);
    box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.1);
}
```

### Legend Colors
- Visual guide showing what each color means
- Matches FullCalendar event colors exactly

### Responsive Design
- Stacks sidebar and calendar on mobile
- Full width on tablets/phones
- Side-by-side on desktop

---

## Form Validation

### Required Fields
- ✅ Course Template ID (hidden)
- ✅ Start Date
- ✅ Start Time
- ✅ Status (defaults to "scheduled")

### Optional Fields
- Location
- Student ID
- Instructor 1 ID
- Instructor 2 ID

### Server-Side Validation (Logic Layer)
- Template exists and is active
- Date is in future (for scheduled courses)
- Student has student role
- Instructors have instructor role
- No duplicate instructors
- Status transition rules

---

## Integration with Existing System

### Thin Controller Pattern ✅
```python
@user_admin_bp.route('/schedule/create', methods=['POST'])
@admin_required
def create_course_instance():
    if request.method == 'POST':
        data = request.form.to_dict()
        try:
            course = CourseLogic.create_course_instance(data)
            flash(f'Course instance "{course.name}" created successfully', 'success')
            return redirect(url_for('user_admin.schedule_management'))
        except ValueError as e:
            flash(str(e), 'error')
```

### Thick Logic Layer ✅
- All validation in `CourseLogic`
- Business rules enforced
- Database operations handled
- Error handling with custom exceptions

### Thin Model ✅
- Course model provides serialization
- `to_dict(include_users=True, include_template=True)` for nested data
- No business logic in model

---

## Status Colors Reference

| Status | Color | Hex Code | Usage |
|--------|-------|----------|-------|
| Scheduled | Blue | `#3788d8` | Default for new courses |
| In Progress | Orange | `#ffa500` | Active courses |
| Completed | Green | `#28a745` | Finished courses |
| Cancelled | Red | `#dc3545` | Cancelled courses |

---

## Future Enhancements

### Near-Term
1. **Drag-and-Drop Rescheduling** - Allow dragging events to new dates
2. **User Dropdowns** - Populate student/instructor selects from database
3. **Conflict Detection** - Warn if instructor has overlapping courses
4. **Bulk Operations** - Select multiple courses for batch updates

### Long-Term
5. **Recurring Courses** - Create repeating course instances
6. **Availability Checking** - Show instructor availability
7. **Email Notifications** - Send calendar invites to participants
8. **Export Calendar** - Export to iCal/Google Calendar format
9. **Print View** - Printable schedule reports
10. **Mobile App** - Native mobile calendar view

---

## Testing Checklist

### Calendar Display
- [x] Calendar renders on page load
- [x] Existing courses appear as events
- [x] Multi-day courses span correctly
- [x] Status colors display correctly
- [x] Month/week/day views work

### Template Selection
- [x] Click "Add to Calendar" highlights template
- [x] Only active templates shown
- [x] Template details display correctly
- [x] Duration badge shows correct days

### Adding Courses
- [x] Click date opens modal
- [x] Modal pre-fills template info
- [x] Date picker works
- [x] Time picker works
- [x] Form submits successfully
- [x] Validation errors show flash messages
- [x] Success redirects to calendar
- [x] New event appears on calendar

### Viewing Courses
- [x] Click event opens details modal
- [x] Course information displays
- [x] Participant info shows
- [x] Edit button navigates correctly

### Editing Courses
- [x] Edit page loads with current data
- [x] All fields editable
- [x] Save updates course
- [x] Delete removes course
- [x] Confirmation dialog on delete

### Responsive Design
- [x] Works on desktop (1920px+)
- [x] Works on tablet (768px-1024px)
- [x] Works on mobile (320px-767px)

---

## Troubleshooting

### Calendar Not Displaying
- Check browser console for JavaScript errors
- Verify FullCalendar CDN is loading
- Ensure `#calendar` div exists in template

### Events Not Showing
- Check `window.existingCourses` in console
- Verify course data includes `course_date` and `template`
- Check date format (should be ISO: YYYY-MM-DD)

### Modal Not Opening
- Verify Bootstrap JavaScript is loaded
- Check for JavaScript console errors
- Ensure modal HTML is in template

### Wrong Duration Spanning
- Check template `duration_days` value
- Verify end date calculation in JavaScript
- Check FullCalendar event `end` property

---

## API Endpoints Used

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/admin/schedule` | Display calendar |
| POST | `/admin/schedule/create` | Create course instance |
| GET | `/admin/schedule/edit/<id>` | Show edit form |
| POST | `/admin/schedule/edit/<id>` | Update course |
| POST | `/admin/schedule/delete/<id>` | Delete course |

---

## Dependencies

### External Libraries (CDN)
- FullCalendar 6.1.10 - `https://cdn.jsdelivr.net/npm/fullcalendar@6.1.10/index.global.min.js`
- Bootstrap 5 (already included in project)
- Font Awesome 6.4.0 (already included in project)

### No Additional Server Dependencies
- Uses existing Flask, SQLAlchemy, Jinja2

---

## Performance Considerations

### Optimization Strategies
1. **Lazy Loading** - Only load courses for current month
2. **Event Caching** - Cache course data in JavaScript
3. **Debounced Actions** - Prevent rapid-fire clicks
4. **Pagination** - Limit courses loaded at once

### Current Performance
- ✅ Fast initial load with < 100 courses
- ✅ Smooth calendar interactions
- ✅ No noticeable lag on date clicks
- ⚠️ May need optimization with 1000+ courses

---

## Accessibility

### Features Implemented
- ✅ ARIA labels on buttons
- ✅ Keyboard navigation support (FullCalendar built-in)
- ✅ Form labels properly associated
- ✅ Focus management in modals
- ✅ Color contrast meets WCAG AA

### Improvements Needed
- ⚠️ Screen reader announcements for calendar changes
- ⚠️ Better keyboard shortcuts documentation
- ⚠️ High contrast mode support

---

## Summary

Successfully implemented a **fully functional calendar-based schedule management system** that:
- ✅ Displays courses on an interactive calendar
- ✅ Handles multi-day course spanning automatically
- ✅ Provides intuitive template selection
- ✅ Allows easy course creation via modal
- ✅ Supports viewing and editing existing courses
- ✅ Follows project architectural principles (thin controllers, thick logic)
- ✅ Integrates seamlessly with existing admin controller

The system is **production-ready** for the core scheduling functionality, with clear paths for future enhancements.
