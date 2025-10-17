# Instructor Schedule Page - Quick Reference

## Page URL
```
/instructor/schedule
```

## Access Requirements
- User must be logged in
- User must have 'instructor' role

## Page Sections

### 1. Header
```
┌─────────────────────────────────────────┐
│ Course Schedule                          │
│ View and sign up for upcoming courses   │
└─────────────────────────────────────────┘
```

### 2. Filter Bar
```
┌───────────────────────────────────────────────────────────┐
│ Filter by Status: [Available ▼]  Date Range: [Next 7 Days ▼] │
└───────────────────────────────────────────────────────────┘
```

**Status Filter Options:**
- All Courses
- Available to Sign Up (default)
- My Assigned Courses
- Fully Staffed

**Date Range Options:**
- Next 7 Days (default)
- Next 30 Days
- All Upcoming

### 3. Course Cards Grid

Each card displays:

```
┌─────────────────────────────────────┐
│ Course Name              [Badge]    │
│ Experience Level                    │
├─────────────────────────────────────┤
│ 📅 Monday, October 21, 2025        │
│ 🕐 09:00 AM                        │
│ 📍 Training Center (if set)        │
│                                     │
│ Duration: 2 days                    │
│ Description...                      │
│                                     │
│ Student: John Doe                   │
│                                     │
│ Instructors:                        │
│ 👔 Jane Smith [You]                │
│ 👔 Slot 2: Open                    │
├─────────────────────────────────────┤
│ [Sign Up] or [Remove Me]           │
└─────────────────────────────────────┘
```

### 4. Status Badges

| Badge | Meaning |
|-------|---------|
| 🔵 2 Spots Open | Both instructor positions available |
| 🟡 1 Spot Open | One instructor needed |
| 🟢 Fully Staffed | Both instructors assigned |
| 🔵 You | You are assigned to this course |

### 5. Legend Section
Visual guide explaining all badges and statuses

## User Actions

### Sign Up for Course
1. Click "Sign Up as Instructor" button
2. Confirm in dialog
3. System assigns you to first available slot
4. Page reloads showing updated assignment

### Remove from Course
1. Click "Remove Me from Course" button
2. Confirm in dialog
3. System removes your assignment
4. Page reloads showing updated availability

## Card States

### Available Course (Not Assigned)
- Blue/Yellow badge (spots available)
- "Sign Up as Instructor" button enabled
- Neutral card styling

### Your Assigned Course
- Your name shown in bold with "You" badge
- "Remove Me from Course" button visible
- Primary highlight on your instructor slot

### Fully Staffed Course (Not You)
- Green "Fully Staffed" badge
- "Fully Staffed" button disabled
- Both instructor names shown

## API Endpoints

### Sign Up
```
POST /instructor/schedule/signup/<course_id>
Response: { success: true, message: "...", course_id: 123 }
```

### Remove
```
POST /instructor/schedule/remove/<course_id>
Response: { success: true, message: "...", course_id: 123 }
```

## Error Handling

### Client-Side
- Confirmation dialogs prevent accidental actions
- Loading states during async operations
- Error alerts for failed operations
- Button state restoration on error

### Server-Side
- Course existence validation
- Date validation (no past courses)
- Status validation (only scheduled courses)
- Duplicate assignment prevention
- Role authorization

## Responsive Breakpoints

| Screen Size | Columns | Layout |
|-------------|---------|--------|
| < 768px (Mobile) | 1 | Stack vertically |
| 768-992px (Tablet) | 2 | Side by side |
| > 992px (Desktop) | 3 | Grid layout |

## Color Scheme

Follows project's design system:
- Primary: Blue gradient (#5587c0)
- Secondary: Green (#478169)
- Success: Light green (#d1fae5)
- Warning: Light yellow (#fef3c7)
- Info: Light blue (#dbeafe)
- Danger: Light red (#fee2e2)

## Icons Used (Font Awesome)

- 📅 `fa-calendar-day` - Course date
- 🕐 `fa-clock` - Course time
- 📍 `fa-map-marker-alt` - Location
- 👔 `fa-user-tie` - Instructor
- ➕ `fa-plus-circle` - Sign up action
- 🚪 `fa-sign-out-alt` - Remove action
- ✅ `fa-check-circle` - Fully staffed
- 📅❌ `fa-calendar-times` - No courses
- 🔄 `fa-spinner fa-spin` - Loading

## Data Requirements

The template expects a `courses` list where each course has:
- `id` - Course ID
- `template` - CourseTemplate object with:
  - `name` - Course name
  - `description` - Course description
  - `duration_days` - Duration in days
  - `experience_level` - Skill level
- `course_date` - Date object
- `course_time` - Time object
- `location` - Location string (optional)
- `student` - User object (optional)
- `instructor1` - User object (optional)
- `instructor2` - User object (optional)
- `instructor1_id` - User ID (optional)
- `instructor2_id` - User ID (optional)
- `status` - Course status string

## Empty State

When no courses are available:
```
┌─────────────────────────────┐
│    📅❌                     │
│  No Upcoming Courses        │
│  There are no courses       │
│  scheduled at this time.    │
└─────────────────────────────┘
```

## Best Practices for Instructors

1. **Check Regularly**: New courses may be added to the schedule
2. **Plan Ahead**: Use date filters to see upcoming commitments
3. **Communicate**: Contact other instructors if you need to swap
4. **Review Details**: Check student info and course requirements before signing up
5. **Be Reliable**: Only remove yourself if absolutely necessary

## Integration Points

### Navigation
- Access via sidebar: "Instructor" → "Schedule" (or similar)
- Breadcrumbs: Home → Instructor → Schedule

### Related Pages
- My Courses (`/instructor/my-courses`) - View only your assignments
- Dashboard - Overview of upcoming commitments

### Notifications (Future)
- Email alerts for new course opportunities
- Reminders for upcoming assigned courses
- Notifications when removed or when course is cancelled
