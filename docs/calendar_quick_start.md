# Calendar Schedule Management - Quick Start Guide

## 🎯 What You Got

A **calendar-based course scheduling system** where admins can:
- View all courses on an interactive calendar
- Add courses by clicking dates
- Courses automatically span multiple days based on template duration
- Edit and delete courses
- Color-coded by status

---

## 🚀 How to Use

### Step 1: Access the Schedule
Navigate to: `/admin/schedule`

### Step 2: Add a Course to Calendar
1. Click "Add to Calendar" on any course template (left sidebar)
2. Template card will highlight in blue
3. Click any date on the calendar
4. Modal opens with form
5. Review/modify date, time, location
6. Optionally assign student and instructors
7. Click "Add to Schedule"

### Step 3: View Course Details
- Click any event on the calendar
- Details modal shows all information
- Click "Edit Course" to modify

### Step 4: Edit a Course
- From details modal, click "Edit Course" OR
- Navigate to `/admin/schedule/edit/<course_id>`
- Update any fields
- Click "Save Changes"

### Step 5: Delete a Course
- On edit page, scroll to "Danger Zone"
- Click "Delete Course"
- Confirm deletion

---

## 📊 Calendar Features

### Views
- **Month View** - See whole month at a glance (default)
- **Week View** - Detailed week schedule
- **Day View** - Single day timeline

### Navigation
- **Previous/Next** - Arrow buttons
- **Today** - Jump to current date
- **View Buttons** - Top right corner

### Event Colors
- 🔵 **Blue** = Scheduled
- 🟠 **Orange** = In Progress
- 🟢 **Green** = Completed
- 🔴 **Red** = Cancelled

---

## ⚙️ Multi-Day Course Spanning

**Automatic Duration Calculation:**

| Template Duration | Start Date | End Date (Auto) | Calendar Display |
|-------------------|------------|-----------------|------------------|
| 1 day | Oct 20 | Oct 20 | Single day block |
| 2 days | Oct 20 | Oct 21 | Spans 2 days |
| 3 days | Oct 20 | Oct 22 | Spans 3 days |
| 5 days | Oct 20 | Oct 24 | Spans full week |

The system reads `duration_days` from the course template and automatically creates a multi-day event on the calendar.

---

## 📁 Files Created

```
Templates:
  src/templates/private/admin/schedule_management/
    ├── index.html          # Calendar page
    └── edit.html           # Edit form

JavaScript:
  src/static/js/private/
    └── schedule_management.js    # Calendar logic

CSS:
  src/static/css/private/
    └── schedule_management.css   # Styles

Documentation:
  docs/
    ├── calendar_schedule_management.md    # Full docs
    └── calendar_quick_start.md            # This file
```

---

## 🔧 Technical Details

### Form Fields (Create/Edit)
**Required:**
- Course Template
- Start Date
- Start Time

**Optional:**
- Location
- Status (default: Scheduled)
- Student
- Instructor 1
- Instructor 2

### Validation (Server-Side)
- Template must exist and be active
- Date must be in future (for scheduled courses)
- Student must have student role
- Instructors must have instructor role
- Cannot assign same instructor twice

---

## 🐛 Troubleshooting

### Calendar is blank
- Check if any courses exist in database
- Verify course has `course_date` and template
- Check browser console for errors

### Can't add course
- Make sure you clicked "Add to Calendar" on a template first
- Template card should be highlighted blue
- Check if you have admin permissions

### Modal won't open
- Check if Bootstrap JS is loaded
- Look for JavaScript errors in console
- Try refreshing the page

### Event shows wrong duration
- Check template `duration_days` value
- Verify in database: `SELECT * FROM course_templates;`
- Event should span `start_date` to `start_date + duration_days`

---

## 💡 Tips & Tricks

1. **Keep Template Selected**: After adding a course, the template stays selected so you can quickly add multiple instances
2. **Use Keyboard**: Arrow keys navigate calendar, Enter opens modal
3. **Filter by Status**: Edit CSS to hide certain statuses if needed
4. **Bulk Scheduling**: Select template once, click multiple dates quickly
5. **Color Reference**: Use the Legend card in sidebar to remember colors

---

## 🔗 Related Routes

| URL | Purpose |
|-----|---------|
| `/admin/schedule` | Calendar view |
| `/admin/schedule/create` | Create (POST only) |
| `/admin/schedule/edit/<id>` | Edit form |
| `/admin/schedule/delete/<id>` | Delete (POST only) |
| `/admin/reports` | Reports dashboard |
| `/admin/announcements` | Announcements |

---

## 📞 Support

For questions:
1. Check `docs/calendar_schedule_management.md` for full documentation
2. Review `docs/user_admin_controller_implementation.md` for admin controller details
3. Check Python instructions: `.github/instructions/python.instructions.md`

---

## ✅ Quick Test

1. Navigate to `/admin/schedule`
2. Click "Add to Calendar" on "Get Riding" template
3. Click tomorrow's date on calendar
4. Set time to 10:00 AM
5. Click "Add to Schedule"
6. Verify event appears on calendar
7. Click event to view details
8. Click "Edit Course"
9. Change time to 2:00 PM
10. Click "Save Changes"
11. Verify time updated on calendar

If all steps work: **✅ System is working correctly!**

---

**Last Updated:** October 15, 2025  
**Version:** 1.0  
**Compatibility:** Flask 2.x, Bootstrap 5, FullCalendar 6
