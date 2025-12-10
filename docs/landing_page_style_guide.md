# CWMT Landing Page Style Guide

> **Last Updated:** November 6, 2025  
> **Version:** 1.0  
> **Purpose:** Comprehensive style guide for maintaining consistency across the CWMT landing page and public-facing components

---

## Table of Contents

1. [Design Principles](#design-principles)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [Components](#components)
6. [CSS Architecture](#css-architecture)
7. [Accessibility](#accessibility)
8. [Code Standards](#code-standards)

---

## Design Principles

### Core Philosophy
- **Clean & Modern:** Minimalist design with purposeful use of whitespace
- **Professional:** Trust-building visual hierarchy for a training business
- **Dynamic:** Subtle animations that enhance without distracting
- **Accessible:** WCAG 2.1 AA compliant markup and interactions

### Visual Language
- **Bold Typography:** Large, weighted headlines for impact
- **Gradient Accents:** Primary/secondary color gradients for depth
- **Card-Based Layouts:** Elevated components with subtle shadows
- **Icon Support:** SVG icons with `currentColor` for theme flexibility

---

## Color System

### CSS Variables (defined in `main.css`)

#### Light Mode (Default)
```css
--bs-primary: #1f4168;        /* Deep navy blue */
--bs-secondary: #2b9c89;      /* Teal green */
--bs-success: #064e3b;        /* Dark green */
--bs-info: #0c4a6e;           /* Dark cyan */
--bs-warning: #78350f;        /* Brown */
--bs-danger: #7f1d1d;         /* Dark red */
--bs-light: #f9fafb;          /* Off-white */
--bs-dark: #111827;           /* Near black */

/* Semantic Colors */
--bg-primary: #ffffff;        /* Page background */
--bg-secondary: #f9fafb;      /* Card/section background */
--text-primary: #111827;      /* Body text */
--text-secondary: #333;       /* Muted text */
--border-color: #e5e7eb;      /* Border/divider */
--link-color: #4f46e5;        /* Hyperlinks */

/* Gradients */
--primary-gradient: linear-gradient(135deg, var(--bs-primary) 0%, var(--bs-secondary) 100%);
--secondary-gradient: linear-gradient(135deg, var(--bs-secondary) 0%, var(--bs-primary) 100%);
```

#### Dark Mode
```css
--bs-primary: #1e293b;
--bs-secondary: #374151;
--bg-primary: #0f172a;
--bg-secondary: #1e293b;
--text-primary: #dadada;
--text-secondary: #a8a8a8;
--border-color: #374151;
--link-color: #818cf8;
```

### Usage Guidelines

| Color Variable | Use Case | Examples |
|---------------|----------|----------|
| `--bs-primary` | Primary actions, brand elements | Main CTA buttons, active states |
| `--bs-secondary` | Secondary actions, accents | Icons, badges, secondary CTAs |
| `--text-primary` | Main content text | Headings, paragraphs, labels |
| `--text-secondary` | Supporting text | Descriptions, captions, eyebrows |
| `--bg-primary` | Page backgrounds | Body, main sections |
| `--bg-secondary` | Component backgrounds | Cards, panels, alternate sections |
| `--border-color` | Dividers and borders | Card borders, section dividers |

**✅ DO:**
- Use CSS variables for all colors
- Leverage gradients sparingly for hero sections and featured elements
- Maintain sufficient contrast ratios (4.5:1 for text, 3:1 for UI)

**❌ DON'T:**
- Use hex codes directly in component styles
- Override Bootstrap color utilities without using variables
- Mix light/dark mode values

---

## Typography

### Font Stack
```css
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", 
                 Roboto, "Helvetica Neue", Arial, sans-serif;
}
```

### Heading Scale

| Element | Size | Weight | Line Height | Use Case |
|---------|------|--------|-------------|----------|
| Hero Title | `3.5rem` (56px) | `900` | `1.1` | Landing hero headlines |
| `<h1>` | `2.5rem` (40px) | `800` | `1.2` | Section titles |
| `<h2>` | `2rem` (32px) | `700` | `1.3` | Subsection titles |
| `<h3>` | `1.5rem` (24px) | `600` | `1.4` | Card titles |
| `<h4>` | `1.25rem` (20px) | `600` | `1.4` | Component headers |
| Body | `1rem` (16px) | `400` | `1.6` | Paragraph text |
| Small | `0.875rem` (14px) | `400` | `1.5` | Captions, meta info |

### Typography Components

#### Eyebrow Text
Small label above headings for context
```css
.section__eyebrow {
    margin-bottom: 0.5rem;
    color: var(--text-secondary);
    font-size: 0.9rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
}
```

#### Section Title
```css
.section__title {
    margin-bottom: 1rem;
    color: var(--text-primary);
    font-size: 2.5rem;
    font-weight: 800;
}
```

#### Section Subtitle
```css
.section__subtitle {
    margin-bottom: 1.5rem;
    color: var(--text-secondary);
    font-size: 1.1rem;
    line-height: 1.6;
}
```

**✅ DO:**
- Use semantic HTML headings (`<h1>`, `<h2>`, etc.)
- Maintain heading hierarchy (don't skip levels)
- Use `rem` units for scalability
- Keep line-height comfortable (1.4-1.6 for body text)

**❌ DON'T:**
- Use pixel-based font sizes
- Style headings with classes alone (use semantic elements)
- Set line-height to `1` (causes readability issues)

---

## Spacing & Layout

### Spacing Scale
Based on `rem` units for consistency:

```css
/* Standard spacing tokens */
--space-xs: 0.5rem;    /* 8px */
--space-sm: 1rem;      /* 16px */
--space-md: 1.5rem;    /* 24px */
--space-lg: 2rem;      /* 32px */
--space-xl: 3rem;      /* 48px */
--space-2xl: 4rem;     /* 64px */
--space-3xl: 5rem;     /* 80px */
```

### Section Padding
```css
/* Standard section spacing */
section {
    padding: 80px 0;  /* Desktop */
}

@media (max-width: 768px) {
    section {
        padding: 48px 0;  /* Mobile */
    }
}
```

### Container Usage
Use Bootstrap container classes:
```html
<div class="container">      <!-- Max-width container with responsive breakpoints -->
<div class="container-fluid"> <!-- Full-width container -->
```

### Grid System
Leverage Bootstrap's 12-column grid:
```html
<div class="row g-4">  <!-- g-4 = 1.5rem gap between columns -->
    <div class="col-lg-4">...</div>
    <div class="col-lg-4">...</div>
    <div class="col-lg-4">...</div>
</div>
```

**Responsive Breakpoints:**
- `col-` — Extra small (<576px)
- `col-sm-` — Small (≥576px)
- `col-md-` — Medium (≥768px)
- `col-lg-` — Large (≥992px)
- `col-xl-` — Extra large (≥1200px)

**✅ DO:**
- Use consistent padding/margin values from the spacing scale
- Use Bootstrap grid for layout
- Apply responsive spacing with media queries
- Use gap utilities (`g-3`, `g-4`) for grid spacing

**❌ DON'T:**
- Use arbitrary spacing values
- Mix `px` and `rem` units inconsistently
- Create custom grid systems

---

## Components

### Button Patterns

#### Primary Button (CTA)
```html
<a href="/courses" class="btn btn-primary">
    View Courses
</a>
```

```css
.btn-primary {
    background-color: var(--bs-primary);
    border-color: var(--bs-primary);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-primary:hover {
    background-color: color-mix(in srgb, var(--bs-primary) 85%, black);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

#### Outline Button (Secondary Action)
```html
<a href="/contact" class="btn btn-outline-primary">
    Contact Us
</a>
```

#### Hero Custom Buttons (v2 Style)
```html
<a href="/courses" class="btn-v2 btn-v2-primary">
    <span class="btn-v2-text">View Courses</span>
    <span class="btn-v2-icon">
        <svg>...</svg>
    </span>
</a>
```

### Card Component

#### Standard Card
```html
<article class="card-component">
    <div class="card-component__header">
        <h3 class="card-component__title">Card Title</h3>
    </div>
    <div class="card-component__body">
        <p class="card-component__text">Card content...</p>
    </div>
</article>
```

```css
.card-component {
    display: flex;
    flex-direction: column;
    padding: 2rem;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    transition: all 0.3s ease;
}

.card-component:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    transform: translateY(-4px);
}
```

#### Testimonial Card
```html
<article class="testimonial-card">
    <div class="testimonial-card__rating" aria-label="5 out of 5 stars">
        ★★★★★
    </div>
    <blockquote class="testimonial-card__quote">
        Customer feedback...
    </blockquote>
    <div class="testimonial-card__author">
        <img src="..." alt="..." class="testimonial-card__avatar">
        <div class="testimonial-card__author-info">
            <p class="testimonial-card__name">Name</p>
            <p class="testimonial-card__role">Role</p>
        </div>
    </div>
</article>
```

#### Pricing Card
```html
<article class="pricing-card">
    <div class="pricing-card__header">
        <h3 class="pricing-card__name">Plan Name</h3>
        <div class="pricing-card__price">
            <span class="pricing-card__currency">$</span>
            <span class="pricing-card__amount">299</span>
        </div>
    </div>
    <ul class="pricing-card__features">
        <li class="pricing-card__feature">
            <span class="pricing-card__feature-icon">✓</span>
            <span class="pricing-card__feature-text">Feature</span>
        </li>
    </ul>
    <a href="#" class="pricing-card__cta">Get Started</a>
</article>
```

### Icon Usage

**SVG Icons with currentColor:**
```html
<div class="feature-icon feature-icon--primary">
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none">
        <path d="..." fill="currentColor"/>
    </svg>
</div>
```

```css
.feature-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    color: var(--bs-secondary);
}

.feature-icon--primary {
    color: var(--bs-primary);
}
```

### Badge Component
```html
<span class="badge badge-light">Trusted by 1,000+ students</span>
```

### FAQ Accordion
```html
<div class="faq__item">
    <button class="faq__question" 
            aria-expanded="false" 
            aria-controls="faq-answer-1"
            onclick="toggleFAQ(this)">
        <span class="faq__question-text">Question?</span>
        <span class="faq__icon">▼</span>
    </button>
    <div class="faq__answer" id="faq-answer-1">
        <div class="faq__answer-content">
            <p>Answer...</p>
        </div>
    </div>
</div>
```

---

## CSS Architecture

### File Structure
```
src/static/css/
├── main.css                    # Root variables, imports
├── bootstrap_addons/
│   ├── basic.css              # Display, sizing utilities
│   ├── buttons.css            # Button overrides
│   ├── colors.css             # Color utilities
│   ├── fonts.css              # Typography utilities
│   └── sizing.css             # Spacing utilities
├── components/
│   ├── cards.css              # Shared card styles
│   ├── tables.css             # Table styles
│   ├── utilities.css          # Component utilities
│   └── navbar.css             # Navigation
└── public/
    └── landing/
        ├── hero_v2.css        # Hero section
        ├── features_overview.css
        ├── testimonials.css
        ├── how_it_works.css
        ├── pricing.css
        └── faq.css
```

### BEM Naming Convention

**Block__Element--Modifier** pattern:

```css
/* Block */
.pricing-card { }

/* Element */
.pricing-card__header { }
.pricing-card__title { }

/* Modifier */
.pricing-card--featured { }
.pricing-card__cta--primary { }
```

**✅ DO:**
- Use double underscores for elements (`__`)
- Use double dashes for modifiers (`--`)
- Keep block names semantic and descriptive
- Group related elements under one block

**❌ DON'T:**
- Nest BEM selectors unnecessarily
- Mix BEM with non-BEM patterns in same component
- Use generic class names (`.card`, `.button`)

### CSS Property Order

Maintain consistent property ordering:

```css
.component {
    /* 1. Positioning */
    position: relative;
    top: 0;
    left: 0;
    z-index: 10;
    
    /* 2. Display & Box Model */
    display: flex;
    flex-direction: column;
    width: 100%;
    height: auto;
    margin: 1rem;
    padding: 1rem;
    
    /* 3. Typography */
    font-family: sans-serif;
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.5;
    color: var(--text-primary);
    
    /* 4. Visual */
    background-color: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    
    /* 5. Animation */
    transition: all 0.3s ease;
    transform: translateY(0);
}
```

### Component Template Structure

Every component CSS file should follow this pattern:

```css
/* ============================================
   Component Name
   Brief description
   ============================================ */

/* Section Comment */
.component {
    /* Properties */
}

.component__element {
    /* Properties */
}

.component--modifier {
    /* Properties */
}

/* Responsive */
@media (max-width: 768px) {
    .component {
        /* Mobile overrides */
    }
}
```

---

## Accessibility

### ARIA Landmarks
```html
<section class="features" aria-labelledby="features-heading">
    <h2 id="features-heading">Features</h2>
</section>
```

### Interactive Elements
```html
<!-- Buttons -->
<button aria-label="Close menu" aria-expanded="false">
    <span aria-hidden="true">×</span>
</button>

<!-- Links -->
<a href="/courses" aria-current="page">Courses</a>

<!-- Images -->
<img src="..." alt="Descriptive text" loading="lazy">
```

### Focus States
All interactive elements must have visible focus states:
```css
.btn:focus,
.btn:focus-visible {
    outline: 2px solid var(--bs-primary);
    outline-offset: 2px;
}
```

### Color Contrast
- **Text:** Minimum 4.5:1 contrast ratio
- **Large text (18pt+):** Minimum 3:1 contrast ratio
- **UI components:** Minimum 3:1 contrast ratio

### Keyboard Navigation
- All interactive elements accessible via Tab
- FAQ accordions support Arrow keys
- Modal dialogs trap focus
- Skip links for main content

**✅ DO:**
- Include `aria-label` for icon-only buttons
- Use semantic HTML elements
- Provide alt text for images
- Test with screen readers
- Support keyboard navigation

**❌ DON'T:**
- Use `div` or `span` for buttons
- Rely on color alone to convey information
- Hide focus indicators
- Use `tabindex` values > 0

---

## Code Standards

### HTML Guidelines

**✅ DO:**
- Use semantic HTML5 elements (`<section>`, `<article>`, `<nav>`)
- Include proper heading hierarchy
- Add ARIA attributes where needed
- Use `loading="lazy"` for images below the fold
- Validate markup with W3C validator

**❌ DON'T:**
- Use inline styles (`style=""`)
- Nest components more than 3 levels deep
- Use deprecated HTML attributes
- Mix inline JavaScript with HTML

### CSS Guidelines

**✅ DO:**
- Use CSS variables for colors and spacing
- Follow BEM naming convention
- Order properties consistently
- Comment complex selectors
- Use `rem` units for scalability
- Add vendor prefixes where needed
- Keep specificity low

**❌ DON'T:**
- Use `!important` (except for Bootstrap overrides)
- Use ID selectors for styling
- Hardcode color values
- Create overly specific selectors
- Use inline `<style>` tags in templates

### File Organization

**Per-Component CSS:**
Each landing page component has its own CSS file:
```html
<section class="testimonials">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/public/landing/testimonials.css') }}">
    <!-- Component content -->
</section>
```

**Global Styles:**
Import in `main.css`:
```css
@import url('components/cards.css');
@import url('bootstrap_addons/buttons.css');
```

---

## Section-Specific Patterns

### Hero Section

**Key Features:**
- Full viewport height (`min-height: 100vh`)
- Gradient background with animation
- Bold typography with staggered animation
- CTA buttons with icons
- Trust badges

**HTML Pattern:**
```html
<section class="hero hero-v2">
    <div class="hero-v2-background">
        <div class="bg-pattern"></div>
        <div class="bg-gradient"></div>
    </div>
    
    <div class="container hero-v2-content">
        <div class="row">
            <div class="col-lg-6">
                <div class="hero-v2-label">
                    <span class="label-text">Premium Motorcycle Training</span>
                </div>
                <h1 class="hero-v2-title">
                    <span class="title-line">Master the Road with</span>
                    <span class="hero-v2-brand">CWMT</span>
                </h1>
                <div class="hero-v2-actions">
                    <a href="#" class="btn-v2 btn-v2-primary">...</a>
                </div>
            </div>
        </div>
    </div>
</section>
```

### Features Section

**Key Features:**
- 3-4 column grid on desktop
- Icon + title + description pattern
- Hover effects with lift animation
- Centered header with eyebrow text

### Testimonials Section

**Key Features:**
- 3-column card grid
- Star ratings
- Avatar images
- Author info
- Trust statistics

### How It Works Section

**Key Features:**
- Numbered step progression
- Visual connector line (desktop only)
- Icon representation for each step
- Clear CTA at bottom

### Pricing Section

**Key Features:**
- 3-tier pricing cards
- Featured card styling (`--featured` modifier)
- Feature lists with checkmarks/crosses
- Distinctive CTA buttons per tier

### FAQ Section

**Key Features:**
- Accordion behavior
- ARIA-compliant interactions
- Keyboard navigation support
- JavaScript toggle functionality

---

## Animation Guidelines

### Transition Timing
```css
/* Standard transitions */
transition: all 0.3s ease;

/* Slower for complex animations */
transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
```

### Common Animations

**Hover Lift:**
```css
.card:hover {
    transform: translateY(-4px);
}
```

**Fade In:**
```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
```

**Slide In:**
```css
@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

**✅ DO:**
- Use `transform` and `opacity` for smooth animations
- Set reasonable animation durations (0.2s - 0.5s)
- Respect `prefers-reduced-motion` media query
- Use cubic-bezier for custom easing

**❌ DON'T:**
- Animate properties that trigger layout (width, height, top, left)
- Create animations longer than 1 second
- Use too many simultaneous animations
- Ignore accessibility preferences

---

## Responsive Design

### Breakpoint Strategy

**Mobile First Approach:**
```css
/* Base styles (mobile) */
.component {
    padding: 1rem;
}

/* Tablet */
@media (min-width: 768px) {
    .component {
        padding: 2rem;
    }
}

/* Desktop */
@media (min-width: 992px) {
    .component {
        padding: 3rem;
    }
}
```

### Typography Scaling
```css
/* Mobile */
.hero-title {
    font-size: 2rem;
}

/* Desktop */
@media (min-width: 992px) {
    .hero-title {
        font-size: 3.5rem;
    }
}
```

### Grid Adjustments
```html
<!-- Stack on mobile, 2 columns on tablet, 4 columns on desktop -->
<div class="col-12 col-md-6 col-lg-3">...</div>
```

---

## Testing Checklist

### Visual Testing
- [ ] Test in Chrome, Firefox, Safari, Edge
- [ ] Test on mobile devices (iOS, Android)
- [ ] Verify dark mode compatibility
- [ ] Check responsive breakpoints
- [ ] Validate hover states

### Accessibility Testing
- [ ] Run WAVE accessibility checker
- [ ] Test with keyboard only navigation
- [ ] Test with screen reader (NVDA/VoiceOver)
- [ ] Verify color contrast ratios
- [ ] Check ARIA labels and roles

### Performance Testing
- [ ] Optimize images (WebP, lazy loading)
- [ ] Minimize CSS (remove unused rules)
- [ ] Test page load speed (<3s)
- [ ] Check for layout shifts (CLS)

---

## Quick Reference

### Common Class Patterns

| Pattern | Usage |
|---------|-------|
| `.section__eyebrow` | Small label above headings |
| `.section__title` | Main section heading |
| `.section__subtitle` | Section description |
| `.[component]-card` | Card-style components |
| `.[component]-card__header` | Card header area |
| `.[component]-card--featured` | Highlighted card variant |
| `.btn-v2` | Hero-style custom button |
| `.feature-icon--primary` | Primary colored icon |

### Color Classes

| Class | Use |
|-------|-----|
| `.text-primary` | Primary text color |
| `.text-secondary` | Muted text |
| `.bg-primary` | Primary background |
| `.border-primary` | Primary border |

### Spacing Utilities

| Class | Size |
|-------|------|
| `.mb-0` | margin-bottom: 0 |
| `.mb-3` | margin-bottom: 1rem |
| `.mt-4` | margin-top: 1.5rem |
| `.p-3` | padding: 1rem |
| `.py-5` | padding-top/bottom: 3rem |

---

## Resources

### Internal Documentation
- [Theme System Implementation](../docs/theme_system_implementation.md)
- [Component Documentation](../docs/components/)
- [CSS Cleanup Instructions](../.github/instructions/css_cleanup.instructions.md)

### External Resources
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [BEM Methodology](http://getbem.com/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [CSS Guidelines](https://cssguidelin.es/)

---

## Changelog

### Version 1.0 (November 6, 2025)
- Initial style guide creation
- Documented all landing page components
- Established naming conventions
- Defined color system and typography scale
- Added accessibility guidelines

---

**Maintained by:** CWMT Development Team  
**Questions?** Refer to internal documentation or contact the team lead.
