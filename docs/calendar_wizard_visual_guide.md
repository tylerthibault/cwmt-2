# Schedule Management Wizard - Visual Guide

## Interface Layout

### Before (Old Design)
```
┌─────────────────────────────────────────────────────┐
│ Schedule Management                                  │
├───────────────┬─────────────────────────────────────┤
│ Templates     │          Calendar                   │
│ (Sidebar)     │                                     │
│               │                                     │
│ • Template 1  │   [Full Calendar View]             │
│   [Add]       │                                     │
│               │                                     │
│ • Template 2  │                                     │
│   [Add]       │                                     │
│               │                                     │
│ • Template 3  │                                     │
│   [Add]       │                                     │
└───────────────┴─────────────────────────────────────┘
```

**Old Flow:**
1. Click "Add to Calendar" on template in sidebar
2. Click date on calendar
3. Fill out single large form
4. Submit

### After (New Design)
```
┌─────────────────────────────────────────────────────┐
│ Schedule Management                                  │
│ Click on any date to add a new course               │
├─────────────────────────────────────────────────────┤
│                                                      │
│              [Full Width Calendar]                  │
│                                                      │
│                                                      │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**New Flow:**
1. Click any date on calendar
2. Wizard modal opens with 3 steps

## Wizard Modal Steps

### Step 1: Choose Template
```
┌──────────────────────────────────────────────────────┐
│ Add Course Instance                              [X] │
│                                                      │
│ ● ─────── ○ ─────── ○                              │
│ Choose      Course    Assign                         │
│ Template    Details   Participants                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Select a Course Template                            │
│ Choose the course for Wednesday, Oct 16, 2025       │
│                                                      │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ Template 1   │ │ Template 2   │ │ Template 3   │ │
│ │ 5 days       │ │ 3 days       │ │ 7 days       │ │
│ │ Beginner     │ │ Intermediate │ │ Advanced     │ │
│ │              │ │              │ │              │ │
│ │ Description  │ │ Description  │ │ Description  │ │
│ │    ...       │ │    ...       │ │    ...       │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
│                                                      │
├──────────────────────────────────────────────────────┤
│              [Cancel]         [Next →]              │
└──────────────────────────────────────────────────────┘
```

**Features:**
- Grid of template cards (auto-responsive)
- Click to select (visual highlight)
- Validation: Must select before proceeding
- Displays: name, duration, level, description

### Step 2: Course Details
```
┌──────────────────────────────────────────────────────┐
│ Add Course Instance                              [X] │
│                                                      │
│ ✓ ─────── ● ─────── ○                              │
│ Choose      Course    Assign                         │
│ Template    Details   Participants                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Course Details                                       │
│                                                      │
│ ┌────────────────────────────────────────────────┐  │
│ │ ℹ️ Template 1                                  │  │
│ │   5 days starting on Wednesday, Oct 16, 2025   │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
│ Start Time:      [09:00]                            │
│ Status:          [Scheduled ▼]                      │
│ Location:        [___________________]              │
│                                                      │
├──────────────────────────────────────────────────────┤
│         [← Previous]  [Cancel]  [Next →]           │
└──────────────────────────────────────────────────────┘
```

**Features:**
- Shows selected template info
- Time picker (default 09:00)
- Status dropdown (Scheduled, In Progress, Completed, Cancelled)
- Optional location field
- Navigation: Previous, Cancel, Next

### Step 3: Assign Participants
```
┌──────────────────────────────────────────────────────┐
│ Add Course Instance                              [X] │
│                                                      │
│ ✓ ─────── ✓ ─────── ●                              │
│ Choose      Course    Assign                         │
│ Template    Details   Participants                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Assign Participants (Optional)                       │
│ You can assign now or leave blank for later         │
│                                                      │
│ Student:         [Select student... ▼]              │
│                                                      │
│ Instructor 1:    [Select instructor... ▼]          │
│ Instructor 2:    [Select instructor... ▼]          │
│                                                      │
│ ┌────────────────────────────────────────────────┐  │
│ │ ✓ Ready to schedule!                           │  │
│ │   Click "Create Course" to add to calendar     │  │
│ └────────────────────────────────────────────────┘  │
│                                                      │
├──────────────────────────────────────────────────────┤
│    [← Previous]  [Cancel]  [✓ Create Course]       │
└──────────────────────────────────────────────────────┘
```

**Features:**
- Optional participant assignments
- Student dropdown
- Two instructor dropdowns
- Success message box
- Submit button (green)

## Step Indicator States

### Active Step
```
●        Step number in blue circle with white text
```

### Completed Step
```
✓        Checkmark in green circle with white background
```

### Upcoming Step
```
○        Empty circle with gray border
```

### Progress Line
```
─────── Gray line connecting circles (partially blue/green as steps complete)
```

## Template Card States

### Normal
```
┌──────────────┐
│ Template 1   │  Gray border
│ 5 days       │  White background
│ Beginner     │
│ Description  │
└──────────────┘
```

### Hover
```
┌──────────────┐
│ Template 1   │  Blue border
│ 5 days       │  Slight shadow
│ Beginner     │  Raised effect
│ Description  │
└──────────────┘
```

### Selected
```
┌──────────────┐
│ Template 1 ✓ │  Blue border
│ 5 days       │  Blue-tinted background
│ Beginner     │  Blue glow
│ Description  │
└──────────────┘
```

## Responsive Behavior

### Desktop (> 768px)
- Full wizard with step labels
- Template grid: 2-3 columns
- All form fields visible

### Tablet (768px)
- Step labels visible
- Template grid: 2 columns
- Compact layout

### Mobile (< 768px)
- Step numbers only (no labels)
- Template grid: 1 column
- Stacked form fields

## Color Scheme

- **Primary Blue**: #0d6efd (active states, borders)
- **Success Green**: #28a745 (completed steps, submit button)
- **Info Blue**: #0dcaf0 (badges)
- **Gray**: #dee2e6 (borders, inactive states)
- **Warning Orange**: #ffa500 (in progress courses)
- **Danger Red**: #dc3545 (cancelled courses)

## Keyboard Navigation

- **Tab**: Navigate through form fields
- **Enter**: Advance to next step (when valid)
- **Esc**: Close modal
- **Arrow Keys**: Navigate template cards (optional enhancement)

## Animations

1. **Modal Open**: Fade in with scale
2. **Step Transition**: Fade in from bottom
3. **Template Selection**: Border color transition
4. **Hover Effects**: Smooth shadow and transform
5. **Progress Line**: Animated color fill

## Accessibility

- ARIA labels on all interactive elements
- Screen reader announcements for step changes
- Keyboard navigable
- Focus indicators on all focusable elements
- Semantic HTML structure
- Proper heading hierarchy
