# Flash Messages Component - Integration Guide

## Overview
A centered flash message component with auto-dismissal, visual timeout indicator, and hover-to-pause functionality.

## Features
- **Centered Display**: Messages appear in the middle of the page
- **Auto-Dismiss**: 5-second timeout by default
- **Visual Progress**: Progress bar shows remaining time
- **Hover to Pause**: Timer pauses when cursor is over the message
- **Manual Close**: Users can click the X button to dismiss
- **Accessibility**: ARIA labels and keyboard support
- **Responsive**: Works on mobile, tablet, and desktop
- **Multiple Categories**: Success, error, warning, and info styles

## Integration Steps

### 1. Include CSS in Base Template

Add the flash messages CSS to your base template (`public.html` or `private.html`):

```html
<!-- In the <head> section, after other CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/components/flash_messages.css') }}">
```

### 2. Include JavaScript in Base Template

Add the flash messages JavaScript before the closing `</body>` tag:

```html
<!-- Before closing </body> tag, after Bootstrap JS -->
<script src="{{ url_for('static', filename='js/components/flash_messages.js') }}"></script>
```

### 3. Include Component in Your Templates

Add the flash messages component to your page templates where you want messages to appear:

```html
{% block content %}
    {# Flash Messages #}
    {% include 'components/flash_messages.html' %}
    
    {# Rest of your content #}
    <div class="container">
        <!-- Your page content -->
    </div>
{% endblock content %}
```

**Recommended**: Add it to the base template after the opening `<body>` tag or at the start of the `page_wrapper` block for site-wide coverage.

## Usage in Flask Routes

### Basic Flash Message
```python
from flask import flash, redirect, url_for

@app.route('/submit', methods=['POST'])
def submit_form():
    # Process form data
    flash('Form submitted successfully!', 'success')
    return redirect(url_for('dashboard'))
```

### Supported Categories
- `success` - Green checkmark icon
- `error` or `danger` - Red X icon
- `warning` - Yellow warning triangle
- `info` - Blue info icon

```python
# Success message
flash('User created successfully!', 'success')

# Error message
flash('Invalid credentials provided.', 'error')

# Warning message
flash('Your session will expire soon.', 'warning')

# Info message
flash('New features are available.', 'info')
```

## Customization

### Adjust Timeout Duration

Edit `flash_messages.js` and change the `defaultTimeout` value:

```javascript
const FLASH_CONFIG = {
    defaultTimeout: 7000, // Change to 7 seconds
    animationDuration: 300
};
```

### Change Colors

Edit `flash_messages.css` to customize category colors:

```css
.flash-message--success {
    border-left: 4px solid #10b981; /* Change border color */
    color: #10b981; /* Change icon color */
}
```

### Modify Position

To change from center to top-right, edit `.flash-messages-container` in `flash_messages.css`:

```css
.flash-messages-container {
    position: fixed;
    top: 1rem;      /* Changed from 50% */
    right: 1rem;    /* Changed from left/transform */
    z-index: 9999;
    transform: none; /* Remove centering transform */
}
```

## Complete Base Template Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/bootstrapcss/bootstrap.min.css') }}">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    
    <!-- Flash Messages CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/components/flash_messages.css') }}">
    
    {% block custom_css %}{% endblock custom_css %}
    
    <title>CWMT</title>
</head>
<body>
    {# Flash Messages - Global #}
    {% include 'components/flash_messages.html' %}
    
    {% block page_wrapper %}
    <div class="d-flex flex-column min-vh-100">
        <header>
            {% block header %}{% endblock header %}
        </header>
        
        <main class="flex-grow-1">
            {% block content %}{% endblock content %}
        </main>
        
        <footer class="mt-auto">
            {% block footer %}{% endblock footer %}
        </footer>
    </div>
    {% endblock page_wrapper %}
    
    <!-- Bootstrap JS -->
    <script src="{{ url_for('static', filename='js/bootstrapjs/bootstrap.bundle.min.js') }}"></script>
    
    <!-- Flash Messages JS -->
    <script src="{{ url_for('static', filename='js/components/flash_messages.js') }}"></script>
    
    {% block custom_js %}{% endblock custom_js %}
</body>
</html>
```

## Accessibility Features

- **ARIA Labels**: Close buttons have proper `aria-label` attributes
- **Live Regions**: Messages use `aria-live="polite"` for screen reader announcements
- **Keyboard Navigation**: Close buttons are keyboard accessible
- **Reduced Motion**: Respects `prefers-reduced-motion` system preference
- **Color Contrast**: Text and icons meet WCAG AA standards
- **Focus Indicators**: Visible focus outlines on interactive elements

## Browser Compatibility

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Full support

## Testing Checklist

- [ ] Messages appear centered on the page
- [ ] Progress bar animates smoothly
- [ ] Timer pauses when hovering over message
- [ ] Timer resumes when cursor leaves message
- [ ] Close button dismisses message immediately
- [ ] Multiple messages stack vertically
- [ ] Messages work on mobile devices
- [ ] Accessible via keyboard (Tab to close button, Enter/Space to close)
- [ ] Works with all message categories (success, error, warning, info)
