# Quick Reference: Menu Icon Component

## HTML Structure

```html
<!-- Page Header with Menu Icon -->
<div class="page-header">
    <div>
        <h1>Page Title</h1>
        <p>Description</p>
    </div>
    
    <div class="menu-icon-container">
        <button id="menuToggle" class="menu-icon-btn" aria-label="Menu">
            <i class="fas fa-icon-name"></i>
        </button>
        
        <div id="dropdownMenu" class="dropdown-menu" style="display: none;">
            <div class="dropdown-header">
                <h4>Menu Title</h4>
                <button id="closeMenu" class="close-menu-btn" aria-label="Close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="dropdown-content">
                <!-- Your content here -->
            </div>
        </div>
    </div>
</div>
```

## JavaScript Template

```javascript
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menuToggle');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const closeMenu = document.getElementById('closeMenu');
    
    if (menuToggle && dropdownMenu) {
        // Toggle on icon click
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            const isVisible = dropdownMenu.style.display === 'block';
            dropdownMenu.style.display = isVisible ? 'none' : 'block';
        });
        
        // Close button
        if (closeMenu) {
            closeMenu.addEventListener('click', function() {
                dropdownMenu.style.display = 'none';
            });
        }
        
        // Close on outside click
        document.addEventListener('click', function(e) {
            if (!dropdownMenu.contains(e.target) && e.target !== menuToggle) {
                dropdownMenu.style.display = 'none';
            }
        });
        
        // Close on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && dropdownMenu.style.display === 'block') {
                dropdownMenu.style.display = 'none';
            }
        });
    }
});
```

## CSS Classes

### Layout
- `.page-header` - Flex container for header content
- `.menu-icon-container` - Relative positioning container

### Menu Button
- `.menu-icon-btn` - Circular icon button
  - 48px diameter
  - Blue background (#1976d2)
  - White icon
  - Hover: scale + shadow

### Dropdown
- `.dropdown-menu` - Positioned dropdown container
  - Min-width: 350px
  - White background
  - Shadow and border
  - Z-index: 1000

### Dropdown Sections
- `.dropdown-header` - Header section
  - Light gray background
  - Flex layout
  - Contains title and close button
  
- `.dropdown-content` - Content section
  - Padding: 1.25rem
  - Flex column layout

### Close Button
- `.close-menu-btn` - X close button
  - 32px circle
  - Transparent background
  - Hover: light gray background

## Common Icons

```html
<!-- Add User -->
<i class="fas fa-user-plus"></i>

<!-- Settings -->
<i class="fas fa-cog"></i>

<!-- More Options -->
<i class="fas fa-ellipsis-v"></i>

<!-- Filter -->
<i class="fas fa-filter"></i>

<!-- Download -->
<i class="fas fa-download"></i>
```

## Responsive Behavior

```css
/* Desktop: >768px */
.page-header { flex-direction: row; }
.dropdown-menu { min-width: 350px; }

/* Tablet: ≤768px */
.page-header { flex-direction: column; }
.dropdown-menu { min-width: 300px; }

/* Mobile: ≤480px */
.dropdown-menu { min-width: 280px; }
```

## Event Handlers

| Event | Action |
|-------|--------|
| Click menu icon | Toggle dropdown |
| Click X button | Close dropdown |
| Click outside | Close dropdown |
| Press Escape | Close dropdown |
| Click inside dropdown | Stay open |

## Accessibility

```html
<!-- Required ARIA attributes -->
<button id="menuToggle" 
        class="menu-icon-btn" 
        aria-label="Open menu"
        aria-expanded="false">
    <i class="fas fa-icon"></i>
</button>

<!-- Update aria-expanded with JS -->
menuToggle.setAttribute('aria-expanded', 'true'); // when open
menuToggle.setAttribute('aria-expanded', 'false'); // when closed
```

## Color Palette

```css
/* Primary Blue */
--menu-icon-bg: #1976d2;
--menu-icon-hover: #1565c0;

/* Grays */
--dropdown-bg: #ffffff;
--dropdown-header-bg: #f8f9fa;
--border-color: #dee2e6;
--text-gray: #6c757d;

/* Shadows */
--menu-shadow: 0 4px 8px rgba(25, 118, 210, 0.3);
--dropdown-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
```

## Common Use Cases

### 1. Actions Menu
```html
<i class="fas fa-ellipsis-v"></i>
<!-- Dropdown with: Edit, Delete, Archive -->
```

### 2. Add/Create Menu
```html
<i class="fas fa-plus"></i>
<!-- Dropdown with: Add User, Add Course, etc. -->
```

### 3. Filter Menu
```html
<i class="fas fa-filter"></i>
<!-- Dropdown with filter options -->
```

### 4. Settings Menu
```html
<i class="fas fa-cog"></i>
<!-- Dropdown with settings options -->
```

## Z-Index Hierarchy

```css
.dropdown-menu { z-index: 1000; }  /* Dropdown menus */
.modal { z-index: 1050; }           /* Modals above dropdowns */
.tooltip { z-index: 1100; }         /* Tooltips above modals */
```

## Best Practices

✅ **DO:**
- Use semantic HTML
- Include ARIA labels
- Close on Escape key
- Close on outside click
- Provide clear close button
- Use appropriate icons
- Test keyboard navigation

❌ **DON'T:**
- Nest dropdowns inside dropdowns
- Use for primary actions
- Make dropdown too wide
- Forget mobile responsiveness
- Omit accessibility features
- Use without close mechanism

## File Locations

- **CSS**: `src/static/css/components/tables.css`
- **Icons**: FontAwesome (already loaded in base template)
- **Template**: Any page that extends `bases/private.html` or `bases/public.html`

## Browser Support

✅ Chrome 90+
✅ Firefox 88+
✅ Safari 14+
✅ Edge 90+

## Dependencies

- FontAwesome icons
- Modern browser with ES6 support
- CSS Flexbox support
- No external JavaScript libraries required
