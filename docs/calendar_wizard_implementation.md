# Schedule Management Calendar-First Wizard Flow

## Overview
Refactored the schedule management interface to use a calendar-first approach with a wizard modal for creating course instances.

## Changes Made

### 1. HTML Template (`src/templates/private/admin/schedule_management/index.html`)

#### Removed:
- Left sidebar with course templates list
- Old single-form modal for adding courses

#### Added:
- Full-width calendar layout (col-12 instead of col-9)
- New wizard modal with 3 steps:
  1. **Step 1: Choose Template** - Grid of course template cards to select from
  2. **Step 2: Course Details** - Time, location, and status configuration
  3. **Step 3: Assign Participants** - Student and instructor assignments

#### Wizard Modal Features:
- Step indicator showing progress (1/3, 2/3, 3/3)
- Visual step completion with checkmarks
- Template selection cards with hover effects
- Navigation: Previous/Next buttons and final Submit button
- Form data preserved across steps

### 2. JavaScript (`src/static/js/private/schedule_management.js`)

#### New Functionality:
- **`openWizardModal(dateStr)`** - Opens wizard when calendar date is clicked
- **`initializeWizard()`** - Sets up wizard interactions:
  - Template card selection handlers
  - Navigation button handlers (Next, Previous)
  - Modal reset on close
- **`validateCurrentStep()`** - Validates each step before proceeding:
  - Step 1: Ensures template is selected
  - Step 2: Validates time input
- **`updateWizardUI()`** - Updates wizard display:
  - Activates/completes step indicators
  - Shows/hides appropriate panels
  - Toggles navigation buttons based on current step
  - Updates template info display

#### Modified:
- **`handleDateClick(info)`** - Now directly opens wizard modal instead of checking for pre-selected template
- Removed old template sidebar selection logic
- Removed old modal opening logic

### 3. CSS (`src/static/css/private/schedule_management.css`)

#### Added Wizard Styles:

**Wizard Header & Steps:**
- Progress indicator with connecting line
- Circular step numbers with active/completed states
- Color transitions: gray → blue (active) → green (completed)
- Responsive step labels (hidden on mobile)

**Template Selection Grid:**
- Responsive grid layout (auto-fill minmax)
- Hover effects with shadow and transform
- Selected state with blue border and background tint
- Check icon indicator for selected card
- Scrollable container (max-height: 400px)

**Wizard Panels:**
- Fade-in animation on panel transition
- Display toggling based on active step

**Responsive Design:**
- Mobile-first grid adjustments
- Simplified step indicators on small screens
- Single column template grid on mobile

## User Flow

1. **User clicks on any calendar date**
   → Wizard modal opens with Step 1 visible

2. **Step 1: Choose Template**
   - User sees all active course templates in a grid
   - Click on a template card to select it
   - Visual feedback: border highlight, background tint, check icon
   - Click "Next" to proceed (validates selection)

3. **Step 2: Course Details**
   - Selected template info displayed at top
   - User sets:
     - Start time (default: 09:00)
     - Status (Scheduled, In Progress, Completed, Cancelled)
     - Location (optional)
   - Click "Next" or "Previous" to navigate

4. **Step 3: Assign Participants**
   - User optionally assigns:
     - Student (dropdown)
     - Instructor 1 (dropdown)
     - Instructor 2 (dropdown)
   - Click "Create Course" to submit form

5. **Form Submission**
   - Button shows loading spinner
   - Form POSTs to server
   - Server handles creation and redirect

## Benefits

1. **Simpler Interface**: No more sidebar, just the calendar
2. **Guided Process**: Wizard breaks down complex form into manageable steps
3. **Better UX**: Clear visual progress and validation at each step
4. **Mobile-Friendly**: Responsive design adapts to smaller screens
5. **Flexible**: Can still view/edit existing courses by clicking on calendar events

## Files Modified

- `src/templates/private/admin/schedule_management/index.html`
- `src/static/js/private/schedule_management.js`
- `src/static/css/private/schedule_management.css`

## Backend Compatibility

No backend changes required - the form still submits to the same endpoint with the same field names:
- `course_template_id`
- `course_date`
- `course_time`
- `location`
- `status`
- `student_id`
- `instructor1_id`
- `instructor2_id`

## Testing Checklist

- [ ] Calendar displays correctly in full width
- [ ] Clicking calendar date opens wizard modal
- [ ] Template selection in Step 1 works
- [ ] Validation prevents advancing without template selection
- [ ] Step 2 displays selected template info
- [ ] Step 3 shows participant dropdowns
- [ ] Navigation buttons work correctly
- [ ] Form submits successfully
- [ ] Existing courses still display on calendar
- [ ] Clicking existing course opens view modal
- [ ] Responsive design works on mobile
- [ ] Wizard resets when modal is closed
