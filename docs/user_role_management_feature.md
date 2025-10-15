# User Role Management Feature

## Overview
This feature allows super-users to add users to specific roles through a dropdown interface in the User Management page.

## Implementation Details

### Backend (Controller)
**File**: `src/controllers/super_user_controller.py`

#### Updated Route: `/user-management`
- Calculates `users_not_in_role` when a role filter is active
- Passes this list to the template for the dropdown

#### New Route: `/user-management/add-to-role` (POST)
- **Purpose**: Add a user to a role via form submission
- **Method**: POST
- **Authentication**: Requires super-user access
- **Request Body** (Form Data):
  ```
  user_id: 123
  role_name: "student"
  ```
- **Response**: Redirect with flash message
  - Success: Flash success message, redirect back to filtered view
  - Error: Flash error message, redirect back to filtered view

#### Logic Flow:
1. Validates user_id and role_name are provided
2. Retrieves the role by name
3. Retrieves the user by ID
4. Checks if user already has the role
5. Uses `UserHasRoles.assign_role()` to assign the role
6. Flashes success or error message
7. Redirects back to user management page with role filter

### Frontend (HTML Template)
**File**: `src/templates/private/super_user/user_management/index.html`

#### Page Header with Menu Icon
- **Position**: Upper right corner of the page
- **Icon**: FontAwesome `fa-user-plus` icon in a circular button
- **Visibility**: Only shown when filtering by a specific role AND users exist to add

#### Dropdown Menu
- **Trigger**: Clicking the menu icon button
- **Position**: Absolutely positioned below the menu icon
- **Components**:
  - Header with role name and close button (X)
  - Dropdown select populated with users not in the current role
  - "Add to Role" button (disabled by default)
  - Message div for success/error feedback

#### JavaScript Functionality
- Toggles dropdown menu on icon click
- Closes menu when clicking the X button
- Closes menu when clicking outside the dropdown
- Enables button when user is selected from dropdown
- **Form submission** - Standard HTML form POST (no AJAX)
- Page refreshes automatically after submission
- Flash messages show success/error feedback

### Styling (CSS)
**File**: `src/static/css/components/tables.css`

#### New Classes:
- `.page-header` - Flex container for page title and menu icon
- `.menu-icon-container` - Container for the menu button and dropdown
- `.menu-icon-btn` - Circular button with user-plus icon
- `.dropdown-menu` - Absolutely positioned dropdown container
- `.dropdown-header` - Header section of dropdown with title and close button
- `.dropdown-content` - Content area of dropdown with form elements
- `.close-menu-btn` - X button to close the menu
- `.user-select` - Styled select dropdown
- `.add-user-message` - Message container
- `.add-user-message--success` - Success message styling (green)
- `.add-user-message--error` - Error message styling (red)

#### Visual Design:
- **Menu Button**: Circular, blue background, white icon, hover effects
- **Dropdown**: White card with shadow, rounded corners
- **Animations**: Scale on hover/active, smooth transitions
- **Z-index**: 1000 to appear above other content

#### Responsive Design:
- Desktop: Menu icon in upper right, dropdown aligned to right
- Mobile: Header stacks vertically, dropdown adjusts width
- Closes on outside click for better UX

## User Experience Flow

1. Super-user navigates to User Management
2. Clicks on a role filter button (e.g., "Student")
3. Page reloads showing only users with that role
4. **Menu icon (user-plus) appears in upper right corner**
5. User clicks the menu icon
6. Dropdown menu slides down with "Add User to Role" interface
7. Dropdown shows all users NOT in that role
8. User selects a user from dropdown → button becomes enabled
9. Clicks "Add to Role" button
10. **Form submits via POST request**
11. **Page refreshes with flash message showing result**
12. User appears in table if successfully added
13. User can click X or outside to close the menu

## Edge Cases Handled

1. **All users in role**: Shows info message instead of dropdown
2. **No role selected**: Add user section not shown
3. **User already has role**: Backend returns error
4. **Invalid user/role**: Backend returns 404 error
5. **Network error**: Shows error message to user
6. **Missing parameters**: Backend returns 400 error

## Architecture Compliance

✅ **Thin Controller**: Controller only extracts parameters and delegates to model
✅ **Thin Model**: Uses existing `UserHasRoles.assign_role()` method
✅ **No Inline Styles**: All styling in separate CSS file
✅ **Proper Separation**: Business logic in model, presentation in template, coordination in controller

## Database Operations

Uses the existing `UserHasRoles.assign_role(user_id, role_id)` method:
- Creates new UserHasRoles record
- Commits to database
- Handles exceptions
- Returns to user management page with flash message

## Testing Checklist

- [ ] Add user to role successfully
- [ ] Flash success message appears
- [ ] Try to add user already in role (should show warning)
- [ ] Try with invalid user ID (should error)
- [ ] Try with invalid role name (should error)
- [ ] All users already in role (menu icon should not appear)
- [ ] No role selected (menu icon should not appear)
- [ ] Mobile responsive layout
- [ ] Page refreshes after submission
- [ ] User appears in filtered table after adding
