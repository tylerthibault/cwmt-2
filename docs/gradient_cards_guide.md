# Gradient Cards Usage Guide

## Overview
Enhanced card components with gradient styling options using your CSS variable system.

## Gradient Card Variants

### 1. Full Gradient Cards
Cards with a complete gradient background.

**Primary Gradient:**
```html
<div class="card card-gradient-primary">
    <div class="card-header">
        <h5>Gradient Card</h5>
    </div>
    <div class="card-body">
        <p class="card-text">Content with primary gradient background</p>
    </div>
</div>
```

**Secondary Gradient:**
```html
<div class="card card-gradient-secondary">
    <div class="card-body">
        <h5 class="card-title">Secondary Gradient</h5>
        <p class="card-text">Content with secondary gradient background</p>
    </div>
</div>
```

### 2. Gradient Overlay Cards
Subtle gradient overlay that intensifies on hover.

```html
<div class="card card-gradient-overlay">
    <div class="card-body">
        <h5 class="card-title">Subtle Gradient</h5>
        <p class="card-text">Hover to see the gradient effect intensify</p>
    </div>
</div>
```

**Features:**
- 5% gradient opacity by default
- 10% gradient opacity on hover
- Smooth transition effect
- Works with all card content

### 3. Gradient Border Cards
Cards with animated gradient borders.

```html
<div class="card card-gradient-border">
    <div class="card-header">
        <h5>Gradient Border</h5>
    </div>
    <div class="card-body">
        <p class="card-text">Card with a gradient border effect</p>
    </div>
</div>
```

**Features:**
- 2px gradient border
- Clean background
- Professional look
- Compatible with headers and footers

### 4. Gradient Header Cards
Cards with gradient headers only.

**Primary Gradient Header:**
```html
<div class="card card-gradient-header">
    <div class="card-header">
        <h5>Gradient Header</h5>
    </div>
    <div class="card-body">
        <p class="card-text">Standard body with gradient header</p>
    </div>
</div>
```

**Secondary Gradient Header:**
```html
<div class="card card-gradient-header-secondary">
    <div class="card-header">
        <h5>Secondary Gradient Header</h5>
    </div>
    <div class="card-body">
        <p class="card-text">Standard body with secondary gradient header</p>
    </div>
</div>
```

## Combining with Existing Card Styles

### Gradient Card with Shadow
```html
<div class="card card-gradient-primary card-shadow">
    <div class="card-body">
        <h5 class="card-title">Enhanced Card</h5>
        <p class="card-text">Gradient with shadow effect</p>
    </div>
</div>
```

### Clickable Gradient Card
```html
<div class="card card-gradient-overlay card-clickable">
    <div class="card-body">
        <h5 class="card-title">Click Me</h5>
        <p class="card-text">Interactive gradient card</p>
    </div>
</div>
```

### Large Gradient Border Card
```html
<div class="card card-gradient-border card-lg">
    <div class="card-header">
        <h5>Large Gradient Card</h5>
    </div>
    <div class="card-body">
        <p class="card-text">More spacious card with gradient border</p>
    </div>
</div>
```

### Gradient Header with Top Border
```html
<div class="card card-gradient-header card-border-top">
    <div class="card-header">
        <h5>Combined Styles</h5>
    </div>
    <div class="card-body">
        <p class="card-text">Gradient header with accent border</p>
    </div>
</div>
```

## Card Grid with Gradients

```html
<div class="card-deck">
    <div class="card card-gradient-primary">
        <div class="card-body">
            <h5 class="card-title">Card 1</h5>
            <p class="card-text">Full primary gradient</p>
        </div>
    </div>
    
    <div class="card card-gradient-border">
        <div class="card-body">
            <h5 class="card-title">Card 2</h5>
            <p class="card-text">Gradient border</p>
        </div>
    </div>
    
    <div class="card card-gradient-header">
        <div class="card-header">
            <h5>Card 3</h5>
        </div>
        <div class="card-body">
            <p class="card-text">Gradient header</p>
        </div>
    </div>
</div>
```

## Complete Example: Dashboard Cards

```html
<div class="row">
    <div class="col-md-4">
        <div class="card card-gradient-primary card-shadow">
            <div class="card-body">
                <h5 class="card-title">Total Courses</h5>
                <h2>24</h2>
                <p class="card-text">Active courses this month</p>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card card-gradient-border card-clickable">
            <div class="card-body">
                <h5 class="card-title">Students Enrolled</h5>
                <h2>156</h2>
                <p class="card-text">New enrollments</p>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card card-gradient-header">
            <div class="card-header">
                <h5>Completion Rate</h5>
            </div>
            <div class="card-body">
                <h2>94%</h2>
                <p class="card-text">Above target</p>
            </div>
        </div>
    </div>
</div>
```

## CSS Variables Used

All gradient cards use the following CSS variables from `main.css`:

- `--primary-gradient` - Primary gradient (light mode: subtle blue, dark mode: deep slate)
- `--secondary-gradient` - Secondary gradient (reversed primary)
- `--bg-primary` - Primary background color
- `--text-primary` - Primary text color
- `--border-color` - Border color

## Theme Support

All gradient cards automatically support both light and dark themes:

**Light Mode:**
- Subtle, sophisticated gradients
- Clean backgrounds
- Professional appearance

**Dark Mode:**
- Rich, deep gradients
- Proper contrast
- Maintains readability

## Best Practices

### When to Use Each Style

**Full Gradient (`card-gradient-primary`):**
- Hero cards
- Call-to-action cards
- Featured content
- Dashboard summary cards

**Gradient Overlay (`card-gradient-overlay`):**
- Subtle enhancement
- Content cards
- Interactive elements
- List items

**Gradient Border (`card-gradient-border`):**
- Professional documents
- Form containers
- Important notices
- Highlighted sections

**Gradient Header (`card-gradient-header`):**
- Standard content cards
- Section headers
- Category cards
- Navigation cards

### Accessibility

- All gradient cards maintain proper text contrast
- Color is not the only indicator of importance
- Works with screen readers
- Keyboard navigation friendly

### Performance

- CSS-only gradients (no images)
- Hardware-accelerated transitions
- Minimal DOM manipulation
- Efficient pseudo-elements

## Customization

To create custom gradient cards, you can:

1. **Define new gradients in `main.css`:**
```css
:root {
    --custom-gradient: linear-gradient(135deg, #yourcolor1 0%, #yourcolor2 100%);
}
```

2. **Create new card variant:**
```css
.card-gradient-custom {
    background: var(--custom-gradient);
    border: none;
    color: var(--text-primary);
}
```

3. **Use in your HTML:**
```html
<div class="card card-gradient-custom">
    <!-- content -->
</div>
```

## Browser Support

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers
- ⚠️ IE11 (fallback to solid colors)

## Migration from Old Cards

**Before:**
```html
<div class="card card-primary">
    <div class="card-body">Content</div>
</div>
```

**After (with gradient):**
```html
<div class="card card-gradient-primary">
    <div class="card-body">Content</div>
</div>
```

Or keep the old style for solid colors - both are supported!
