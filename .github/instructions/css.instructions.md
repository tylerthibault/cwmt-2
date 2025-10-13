---
applyTo: '**/*.css'
---

# CSS Development Instructions for CWMT Flask Application

These instructions enforce CSS best practices and organizational standards defined in the project constitution.

## Core CSS Structure

### Property Organization (MANDATORY)
CSS classes MUST follow this exact property order with blank lines between sections:

```css
.class_name {
    /* Layout Properties */
    display: flex;
    position: relative;
    flex-direction: column;

    /* Spacing Properties */
    padding: 1rem;
    margin: 0.5rem auto;
    border: 1px solid #ccc;

    /* Visual Properties */
    color: #333;
    background-color: #fff;
    font-size: 1rem;

    /* Animation Properties */
    transition: all 0.3s ease;
    transform: translateY(0);
}
```

### Property Groups Defined

1. **Layout**: `display`, `position`, `flex`, `grid`, `width`, `height`, `z-index`
2. **Spacing**: `padding`, `margin`, `border`, `border-radius`, `box-shadow`
3. **Visual**: `color`, `background`, `font-*`, `text-*`, `opacity`
4. **Animation**: `transition`, `transform`, `animation`

## File Organization

### Directory Structure
```
static/css/
├── main.css              # Global styles
├── components/           # Reusable components
└── pages/               # Page-specific styles
```

### No Inline CSS (Constitutional)
```html
<!-- ❌ NEVER -->
<div style="color: red;">Content</div>

<!-- ✅ ALWAYS -->
<div class="error-message">Content</div>
```

## Component-Based CSS

### BEM Methodology
```css
/* Block */
.button {
    display: inline-block;

    padding: 0.5rem 1rem;
    border: none;

    background-color: #007bff;
    color: white;

    transition: background-color 0.2s ease;
}

/* Element */
.button__icon {
    margin-right: 0.25rem;
}

/* Modifier */
.button--large {
    padding: 0.75rem 1.5rem;
}
```

### CSS Variables
```css
:root {
    --color-primary: #007bff;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
}

.primary-button {
    padding: var(--spacing-sm) var(--spacing-md);
    background-color: var(--color-primary);
}
```

## Responsive Design

### Mobile-First Approach
```css
.container {
    padding: 1rem;
    max-width: 100%;
}

@media (min-width: 768px) {
    .container {
        padding: 2rem;
        max-width: 750px;
    }
}
```

## Code Formatting Rules

- Use 2 spaces for indentation
- One blank line between property groups
- Space after colon in declarations
- Follow property order: Layout → Spacing → Visual → Animation

These instructions ensure all CSS follows constitutional principles and maintains organized, readable code structure.