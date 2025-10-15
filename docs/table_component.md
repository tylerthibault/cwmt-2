# Table Component Documentation

## Overview
The table component provides a reusable, accessible, and responsive table styling system that can be used throughout the CWMT application.

## Basic Usage

### Simple Table
```html
<div class="table-container">
    <table class="table">
        <thead>
            <tr>
                <th>Column 1</th>
                <th>Column 2</th>
                <th>Column 3</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Data 1</td>
                <td>Data 2</td>
                <td>Data 3</td>
            </tr>
        </tbody>
    </table>
</div>
```

## Table Variants

### Striped Table
Alternating row colors for better readability:
```html
<table class="table table--striped">
    <!-- ... -->
</table>
```

### Bordered Table
Full borders around all cells:
```html
<table class="table table--bordered">
    <!-- ... -->
</table>
```

### Compact Table
Reduced padding for denser information display:
```html
<table class="table table--compact">
    <!-- ... -->
</table>
```

### Combined Variants
You can combine multiple variants:
```html
<table class="table table--striped table--bordered table--compact">
    <!-- ... -->
</table>
```

## Badge Component

Use badges to highlight status, roles, or categories:

```html
<span class="badge badge--primary">Primary</span>
<span class="badge badge--success">Success</span>
<span class="badge badge--warning">Warning</span>
<span class="badge badge--danger">Danger</span>
<span class="badge badge--secondary">Secondary</span>
```

## Table Action Buttons

Pre-styled buttons for common table actions:

```html
<a href="#" class="table-btn table-btn--edit">Edit</a>
<a href="#" class="table-btn table-btn--delete">Delete</a>
<a href="#" class="table-btn table-btn--view">View</a>
<a href="#" class="table-btn table-btn--primary">Action</a>
<a href="#" class="table-btn table-btn--secondary">Cancel</a>
```

## Filter Buttons

Use filter buttons to create interactive table filters:

```html
<div class="filter-container">
    <h3>Filter by Category:</h3>
    <div class="filter-buttons">
        <a href="?category=all" class="filter-btn filter-btn--active">All Items</a>
        <a href="?category=active" class="filter-btn">Active</a>
        <a href="?category=pending" class="filter-btn">Pending</a>
        <a href="?category=archived" class="filter-btn">Archived</a>
    </div>
</div>
```

**Filter Button States:**
- `.filter-btn` - Default state
- `.filter-btn--active` - Currently selected filter

**Best Practices:**
- Use query parameters to maintain filter state on page reload
- Add `filter-btn--active` class to the currently selected filter
- Place filter container above the table

## Add User to Role Feature

When filtering by a specific role, a menu icon appears in the upper right corner of the page header that allows adding users to that role:

**Page Header Structure:**
```html
<div class="page-header">
    <div>
        <h1>Page Title</h1>
        <p>Page description</p>
    </div>
    
    <div class="menu-icon-container">
        <button id="menuToggle" class="menu-icon-btn" aria-label="Add user menu">
            <i class="fas fa-user-plus"></i>
        </button>
        
        <div id="dropdownMenu" class="dropdown-menu" style="display: none;">
            <div class="dropdown-header">
                <h4>Add User to Role Name</h4>
                <button id="closeMenu" class="close-menu-btn" aria-label="Close menu">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="dropdown-content">
                <select id="userSelect" class="user-select">
                    <option value="">Select a user to add...</option>
                    <option value="1">username (email@example.com)</option>
                </select>
                <button id="addUserBtn" class="table-btn table-btn--primary">Add to Role</button>
                <div id="addUserMessage" class="add-user-message"></div>
            </div>
        </div>
    </div>
</div>
```

**Features:**
- Circular menu icon button in upper right corner
- Only shows users not already in the filtered role
- Dropdown menu appears when icon is clicked
- Close button (X) in dropdown header
- Closes when clicking outside the dropdown
- Success/error messages with appropriate styling
- Auto-refresh after successful addition
- AJAX-based, no full page reload during operation

**JavaScript Requirements:**
- Toggle dropdown on menu icon click
- Close on X button click
- Close on outside click
- Enable/disable "Add to Role" button based on selection
- Handle AJAX request and response

**CSS Classes:**
- `.page-header` - Flex container for header content
- `.menu-icon-container` - Container for menu icon and dropdown
- `.menu-icon-btn` - Circular icon button
- `.dropdown-menu` - Positioned dropdown container
- `.dropdown-header` - Dropdown header section
- `.dropdown-content` - Dropdown content section
- `.close-menu-btn` - Close button

**Message States:**
- `.add-user-message--success` - Green background for success
- `.add-user-message--error` - Red background for errors
## Complete Example

```html
<div class="table-container">
    <table class="table table--striped">
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <td>John Doe</td>
                <td><span class="badge badge--success">Active</span></td>
                <td>
                    <a href="#" class="table-btn table-btn--view">View</a>
                    <a href="#" class="table-btn table-btn--edit">Edit</a>
                    <a href="#" class="table-btn table-btn--delete">Delete</a>
                </td>
            </tr>
            <tr>
                <td>2</td>
                <td>Jane Smith</td>
                <td><span class="badge badge--warning">Pending</span></td>
                <td>
                    <a href="#" class="table-btn table-btn--view">View</a>
                    <a href="#" class="table-btn table-btn--edit">Edit</a>
                    <a href="#" class="table-btn table-btn--delete">Delete</a>
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

## Responsive Behavior

The table component is responsive by default:
- **Desktop**: Full padding and normal font sizes
- **Mobile (≤768px)**: Reduced padding and smaller font sizes
- The `table-container` provides horizontal scrolling on smaller screens

## Accessibility Features

- Proper semantic HTML structure with `<thead>`, `<tbody>`
- Clear visual hierarchy with hover states
- Color contrast meets WCAG AA standards
- Keyboard accessible buttons/links

## Customization

The table styles follow the project's CSS organization standards:
- Property order: Layout → Spacing → Visual → Animation
- BEM-like naming convention with modifiers
- Mobile-first responsive design
- No inline styles required

## File Location

**CSS**: `src/static/css/components/tables.css`  
**Imported in**: `src/static/css/main.css`

## Notes

- Always wrap tables in `table-container` for responsive behavior
- Use semantic class names (e.g., `table-btn--edit` not `table-btn--green`)
- Combine variants as needed for your specific use case
- The component automatically adapts to the application's theme
