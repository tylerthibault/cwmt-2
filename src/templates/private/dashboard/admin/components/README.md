# Admin Dashboard Components

This folder contains reusable components for the admin/secretary dashboard.

## Components Overview

### 1. **stats_cards.html**
**Purpose:** Display key metrics at a glance  
**Data Required:**
- `total_students` (int) - Total number of students
- `new_students_this_month` (int) - New registrations this month
- `active_courses` (int) - Number of active courses
- `courses_this_week` (int) - Classes scheduled this week
- `todays_classes` (int) - Classes scheduled today
- `classes_in_progress` (int) - Currently running classes
- `pending_items` (int) - Total pending items
- `urgent_items` (int) - High priority pending items

**Features:**
- Color-coded stat cards with gradient icons
- Positive/negative change indicators
- Hover animations
- Responsive grid layout

---

### 2. **quick_actions.html**
**Purpose:** Fast access to common admin tasks  
**Data Required:** None (uses route URLs)

**Features:**
- Grid of action buttons with icons
- Color-coded by category (primary, success, info, etc.)
- Links to:
  - Add Student
  - Schedule Class
  - Find Student
  - Send Email
  - View Courses
  - Reports

**Customization:** Update `data-action` attributes for custom modal triggers

---

### 3. **todays_schedule.html**
**Purpose:** Display today's class schedule with status  
**Data Required:**
- `current_date` (string) - Display date (e.g., "November 7, 2025")
- `todays_schedule` (list) - List of class objects with:
  - `start_time` (string) - e.g., "9:00 AM"
  - `end_time` (string) - e.g., "11:00 AM"
  - `course_name` (string) - Course title
  - `instructor_name` (string) - Instructor's name
  - `enrolled_count` (int) - Number of enrolled students
  - `max_students` (int) - Maximum capacity
  - `status` (string) - "in_progress", "upcoming", or "completed"

**Features:**
- Timeline-style layout with dots and lines
- Active class highlighting with pulse animation
- Status badges
- Empty state with "Schedule a Class" CTA

---

### 4. **pending_items.html**
**Purpose:** Show items requiring admin attention  
**Data Required:**
- `pending_items` (list) - List of pending item objects with:
  - `type` (string) - "registration", "payment", "document", "approval", or "default"
  - `title` (string) - Item title
  - `description` (string) - Brief description
  - `student_name` (string, optional) - Related student
  - `time_ago` (string) - e.g., "2 hours ago"
  - `action_url` (string, optional) - Link to review item
  - `priority` (string, optional) - "high" for urgent items

**Features:**
- Type-specific icons and colors
- Priority badges for urgent items
- Review buttons
- "View all" link in footer

---

### 5. **recent_activity.html**
**Purpose:** Activity feed of recent system changes  
**Data Required:**
- `recent_activities` (list) - List of activity objects with:
  - `user_name` (string) - Person who performed action
  - `user_avatar` (string, optional) - Avatar URL
  - `action` (string) - Action description (e.g., "created a new student")
  - `target` (string, optional) - Target of action
  - `type` (string) - "create", "update", "delete", "complete", or "default"
  - `time_ago` (string) - e.g., "5 minutes ago"

**Features:**
- User avatars with fallback initials
- Type-specific icons
- Color-coded action types
- Hover effects

---

### 6. **upcoming_deadlines.html**
**Purpose:** Display important dates and reminders  
**Data Required:**
- `upcoming_deadlines` (list) - List of deadline objects with:
  - `day` (string) - Day number (e.g., "15")
  - `month` (string) - Month abbreviation (e.g., "NOV")
  - `title` (string) - Deadline title
  - `description` (string) - Details
  - `is_overdue` (bool) - Overdue flag
  - `is_today` (bool) - Due today flag
  - `days_until` (int) - Days until due
  - `action_url` (string, optional) - Link to related page

**Features:**
- Calendar-style date display
- Color-coded urgency (overdue, today, upcoming)
- Status badges
- Action buttons

---

### 7. **student_search.html**
**Purpose:** Quick student lookup and access  
**Data Required:** None (uses AJAX)

**API Endpoint Required:**
```python
@app.route('/api/students/search')
def search_students():
    query = request.args.get('q', '')
    # Return JSON: {"students": [{"id": 1, "name": "...", "email": "...", "phone": "...", "status": "active", "avatar": "..."}]}
```

**Features:**
- Real-time search with debouncing (300ms)
- Dropdown results with avatars
- Shortcuts to "All Students" and "Add New Student"
- Click-outside to close
- Empty state handling

---

## Layout Structure

The main dashboard uses a two-column grid:

```
┌─────────────────────────────────────────┬──────────────────┐
│ Stats Cards (4 columns)                 │                  │
├─────────────────────────────────────────┴──────────────────┤
│ Left Column (Main)          │ Right Column (Sidebar)       │
│ - Quick Actions             │ - Student Search             │
│ - Today's Schedule          │ - Pending Items              │
│ - Recent Activity           │ - Upcoming Deadlines         │
└─────────────────────────────┴──────────────────────────────┘
```

## Design System

All components follow the Apple-inspired design system:

- **Prefix:** `ad-` (admin dashboard)
- **Colors:**
  - Primary: `#007AFF`
  - Success: `#34C759`
  - Warning: `#FF9500`
  - Danger: `#FF3B30`
  - Muted: `#86868B`
- **Border Radius:** 8px-16px
- **Shadows:** Subtle, layered
- **Transitions:** 0.2s ease
- **Typography:** System fonts, -apple-system

## Responsive Breakpoints

- Desktop: `> 1200px` - Two-column layout
- Tablet: `768px - 1200px` - Single column
- Mobile: `< 768px` - Stacked, full-width

## Usage Example

```python
@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('private/dashboard/admin/index.html',
        # Stats
        total_students=150,
        new_students_this_month=12,
        active_courses=8,
        # ... etc
        
        # Schedule
        todays_schedule=[
            {
                'start_time': '9:00 AM',
                'end_time': '11:00 AM',
                'course_name': 'CWMT Basic Course',
                'instructor_name': 'John Doe',
                'enrolled_count': 15,
                'max_students': 20,
                'status': 'in_progress'
            }
        ],
        
        # Pending Items
        pending_items=[
            {
                'type': 'registration',
                'title': 'New Student Registration',
                'description': 'Jane Smith completed registration form',
                'student_name': 'Jane Smith',
                'time_ago': '2 hours ago',
                'action_url': '/admin/students/123',
                'priority': 'high'
            }
        ]
        # ... etc
    )
```

## Customization

Each component can be customized by:
1. Modifying the CSS variables in the `<style>` section
2. Adding custom data attributes for JavaScript interactions
3. Extending the template with additional blocks
4. Override styles in `main.css` with higher specificity

## Future Enhancements

- [ ] Add filtering to recent activity
- [ ] Make deadline actions interactive
- [ ] Add quick email compose modal
- [ ] Implement notifications center
- [ ] Add data export functionality
- [ ] Create mobile app shortcuts
