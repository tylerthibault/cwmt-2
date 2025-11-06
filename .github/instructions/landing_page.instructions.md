---
applyTo: 'src/templates/public/landing/**/*,src/static/css/public/landing/**/*,src/static/js/landing/**/*'
---

# Landing Page Development Instructions for CWMT

These instructions define standards for all landing page components to ensure visual consistency, accessibility, and maintainability. Follow these rules when creating or modifying landing page sections.

## Design Principles

### Visual Philosophy
- **Clean & Modern**: Use purposeful whitespace, avoid clutter
- **Professional**: Establish trust through clear hierarchy and polished design
- **Dynamic**: Add subtle animations that enhance without distracting
- **Accessible**: All components must meet WCAG 2.1 AA standards

### Brand Identity
- Primary color: `var(--bs-primary)` (#1f4168 - Navy blue)
- Secondary color: `var(--bs-secondary)` (#2b9c89 - Teal green)
- Use gradients sparingly for hero sections and featured elements
- Maintain professional tone in all copy and visual elements

---

## Color System (MANDATORY)

### CSS Variable Usage
**ALWAYS** use CSS variables from `main.css`. **NEVER** use hardcoded hex/rgb values.

```css
/* ✅ CORRECT */
.component {
    color: var(--text-primary);
    background-color: var(--bg-primary);
    border-color: var(--border-color);
}

/* ❌ WRONG */
.component {
    color: #111827;
    background-color: #ffffff;
    border-color: #e5e7eb;
}
```

### Available Color Variables

#### Semantic Colors
- `--bg-primary` - Main page/card backgrounds
- `--bg-secondary` - Alternate section backgrounds
- `--text-primary` - Primary text content
- `--text-secondary` - Muted/supporting text
- `--border-color` - Borders and dividers
- `--link-color` - Hyperlinks

#### Brand Colors
- `--bs-primary` - Primary actions, brand elements
- `--bs-secondary` - Secondary actions, accents
- `--bs-success`, `--bs-info`, `--bs-warning`, `--bs-danger` - Status colors

#### Gradients
- `--primary-gradient` - Primary to secondary gradient
- `--secondary-gradient` - Secondary to primary gradient

### Color Contrast Requirements
- **Body text**: Minimum 4.5:1 contrast ratio
- **Large text (18pt+)**: Minimum 3:1 contrast ratio
- **UI components**: Minimum 3:1 contrast ratio
- Test all color combinations with a contrast checker

---

## Typography Standards

### Font Sizing
**ALWAYS** use `rem` units for font sizes. **NEVER** use `px`.

```css
/* ✅ CORRECT */
.heading {
    font-size: 2.5rem;
}

/* ❌ WRONG */
.heading {
    font-size: 40px;
}
```

### Heading Scale (MANDATORY)
Follow this exact scale for consistent typography:

| Element | Size | Weight | Line Height | Use Case |
|---------|------|--------|-------------|----------|
| Hero Title | `3.5rem` | `900` | `1.1` | Landing hero headlines |
| `<h1>` | `2.5rem` | `800` | `1.2` | Section titles |
| `<h2>` | `2rem` | `700` | `1.3` | Subsection titles |
| `<h3>` | `1.5rem` | `600` | `1.4` | Card titles |
| `<h4>` | `1.25rem` | `600` | `1.4` | Component headers |
| Body | `1rem` | `400` | `1.6` | Paragraph text |
| Small | `0.875rem` | `400` | `1.5` | Captions, meta |

### Semantic HTML (MANDATORY)
**ALWAYS** use semantic heading elements. **NEVER** style divs/spans as headings.

```html
<!-- ✅ CORRECT -->
<h2 class="section__title">Features</h2>

<!-- ❌ WRONG -->
<div class="section__title">Features</div>
```

### Line Height Requirements
- Body text: `1.5` to `1.6`
- Headings: `1.1` to `1.4`
- **NEVER** set `line-height: 1` (causes readability issues)

---

## BEM Naming Convention (MANDATORY)

All CSS classes **MUST** follow Block__Element--Modifier pattern.

### Pattern Structure
```
.block                  /* Component root */
.block__element         /* Child element (double underscore) */
.block--modifier        /* Variant (double dash) */
.block__element--modifier
```

### Landing Page Examples

#### Testimonial Card
```css
/* Block */
.testimonial-card { }

/* Elements */
.testimonial-card__rating { }
.testimonial-card__quote { }
.testimonial-card__author { }
.testimonial-card__avatar { }
.testimonial-card__name { }

/* Modifiers */
.testimonial-card--featured { }
```

#### Pricing Card
```css
.pricing-card { }
.pricing-card__header { }
.pricing-card__name { }
.pricing-card__price { }
.pricing-card__currency { }
.pricing-card__amount { }
.pricing-card__features { }
.pricing-card__feature { }
.pricing-card__feature-icon { }
.pricing-card__cta { }
.pricing-card--featured { }
```

#### Feature Component
```css
.feature-icon { }
.feature-icon--primary { }
.feature-icon--secondary { }
```

### BEM Rules
- ✅ Use descriptive block names (`pricing-card`, not just `card`)
- ✅ Keep elements scoped to their block
- ✅ Use modifiers for variants, not separate classes
- ❌ Don't nest BEM selectors (`.block .block__element`)
- ❌ Don't mix BEM with generic Bootstrap classes for custom components

---

## Component Structure

### Section Pattern (MANDATORY)
Every landing page section must follow this structure:

```html
<section class="section-name" aria-labelledby="section-name-heading">
    <div class="container">
        <!-- Section Header (Optional) -->
        <div class="section-name__header">
            <p class="section-name__eyebrow">EYEBROW TEXT</p>
            <h2 id="section-name-heading" class="section-name__title">Section Title</h2>
            <p class="section-name__subtitle">Section description...</p>
        </div>
        
        <!-- Section Content -->
        <div class="section-name__content">
            <!-- Component-specific content -->
        </div>
    </div>
</section>
```

### Eyebrow Text Pattern
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

### Card Pattern
```html
<article class="card-component">
    <div class="card-component__header">
        <h3 class="card-component__title">Card Title</h3>
    </div>
    <div class="card-component__body">
        <p class="card-component__text">Card content...</p>
    </div>
    <div class="card-component__footer">
        <a href="#" class="card-component__cta">Learn More</a>
    </div>
</article>
```

---

## CSS Property Order (MANDATORY)

All CSS declarations **MUST** follow this exact order:

```css
.component {
    /* 1. POSITIONING */
    position: relative;
    top: 0;
    left: 0;
    z-index: 10;
    
    /* 2. DISPLAY & BOX MODEL */
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: auto;
    margin: 1rem;
    padding: 1rem;
    
    /* 3. TYPOGRAPHY */
    font-family: sans-serif;
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.5;
    color: var(--text-primary);
    text-align: center;
    
    /* 4. VISUAL */
    background-color: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    opacity: 1;
    
    /* 5. ANIMATION */
    transition: all 0.3s ease;
    transform: translateY(0);
}
```

**Add blank lines between property groups** for readability.

---

## Spacing System

### Spacing Scale (MANDATORY)
Use only these predefined spacing values:

```css
--space-xs: 0.5rem;    /* 8px */
--space-sm: 1rem;      /* 16px */
--space-md: 1.5rem;    /* 24px */
--space-lg: 2rem;      /* 32px */
--space-xl: 3rem;      /* 48px */
--space-2xl: 4rem;     /* 64px */
--space-3xl: 5rem;     /* 80px */
```

### Section Padding Standard
```css
section {
    padding: 80px 0;  /* Desktop */
}

@media (max-width: 768px) {
    section {
        padding: 48px 0;  /* Mobile */
    }
}
```

### Bootstrap Grid Usage
- **ALWAYS** use Bootstrap's container and grid system
- **NEVER** create custom grid layouts from scratch

```html
<!-- ✅ CORRECT -->
<div class="container">
    <div class="row g-4">
        <div class="col-lg-4 col-md-6">...</div>
        <div class="col-lg-4 col-md-6">...</div>
        <div class="col-lg-4 col-md-6">...</div>
    </div>
</div>

<!-- ❌ WRONG -->
<div class="custom-container">
    <div class="custom-grid">...</div>
</div>
```

### Gap Utilities
Use Bootstrap gap utilities for grid spacing:
- `g-3` - 1rem gap
- `g-4` - 1.5rem gap
- `g-5` - 3rem gap

---

## Button Components

### Primary Button (CTA)
```html
<a href="/courses" class="btn btn-primary">
    View Courses
</a>
```

### Outline Button (Secondary Action)
```html
<a href="/contact" class="btn btn-outline-primary">
    Contact Us
</a>
```

### Hero Custom Button (v2 Style)
```html
<a href="/courses" class="btn-v2 btn-v2-primary">
    <span class="btn-v2-text">View Courses</span>
    <span class="btn-v2-icon">
        <svg>...</svg>
    </span>
</a>
```

### Button Styling Rules
```css
.btn-custom {
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-custom:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

**DO NOT** use `<button>` elements for navigation links. Use `<a>` tags.

---

## Animation Standards

### Transition Timing (MANDATORY)
```css
/* Standard transitions */
transition: all 0.3s ease;

/* Complex animations */
transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
```

### Animation Rules
- ✅ Animate `transform` and `opacity` (GPU-accelerated)
- ✅ Keep durations between 0.2s - 0.5s
- ✅ Use `ease`, `ease-in-out`, or cubic-bezier timing functions
- ❌ Don't animate `width`, `height`, `top`, `left` (causes layout shifts)
- ❌ Don't create animations longer than 1 second
- ❌ Don't run multiple simultaneous animations on same element

### Hover Effects
```css
/* Card lift effect */
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

/* Button hover */
.btn:hover {
    transform: translateY(-2px);
}
```

### Accessibility
**MANDATORY**: Respect reduced motion preferences:

```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

---

## Accessibility Requirements (MANDATORY)

### ARIA Landmarks
All sections must include proper ARIA attributes:

```html
<section class="features" aria-labelledby="features-heading">
    <h2 id="features-heading">Our Features</h2>
    <!-- Content -->
</section>
```

### Interactive Elements
```html
<!-- Buttons with icons -->
<button aria-label="Close menu" aria-expanded="false">
    <span aria-hidden="true">×</span>
</button>

<!-- Current page indicator -->
<a href="/courses" aria-current="page">Courses</a>

<!-- Images -->
<img src="..." alt="Descriptive alternative text" loading="lazy">

<!-- Decorative images -->
<img src="..." alt="" aria-hidden="true">
```

### Focus States (MANDATORY)
All interactive elements **MUST** have visible focus states:

```css
.btn:focus,
.btn:focus-visible {
    outline: 2px solid var(--bs-primary);
    outline-offset: 2px;
}

/* Never remove focus outlines */
/* ❌ FORBIDDEN */
*:focus {
    outline: none;
}
```

### Keyboard Navigation
- All interactive elements must be accessible via Tab key
- Accordions/dropdowns support Arrow keys
- Modals trap focus within dialog
- Include skip links for main content

---

## Responsive Design

### Mobile-First Approach (MANDATORY)
**ALWAYS** write mobile styles first, then add desktop overrides:

```css
/* ✅ CORRECT: Mobile first */
.component {
    padding: 1rem;
    font-size: 1rem;
}

@media (min-width: 768px) {
    .component {
        padding: 2rem;
    }
}

@media (min-width: 992px) {
    .component {
        padding: 3rem;
        font-size: 1.25rem;
    }
}
```

```css
/* ❌ WRONG: Desktop first */
.component {
    padding: 3rem;
    font-size: 1.25rem;
}

@media (max-width: 992px) {
    .component {
        padding: 2rem;
    }
}
```

### Breakpoints
Use Bootstrap's standard breakpoints:

| Name | Min Width | Usage |
|------|-----------|-------|
| `xs` | <576px | Mobile phones |
| `sm` | ≥576px | Large phones |
| `md` | ≥768px | Tablets |
| `lg` | ≥992px | Desktops |
| `xl` | ≥1200px | Large desktops |

### Grid Responsiveness
```html
<!-- Stack on mobile, 2 cols on tablet, 3 cols on desktop -->
<div class="col-12 col-md-6 col-lg-4">...</div>
```

### Typography Scaling
```css
.hero-title {
    font-size: 2rem;      /* Mobile */
}

@media (min-width: 768px) {
    .hero-title {
        font-size: 2.75rem;  /* Tablet */
    }
}

@media (min-width: 992px) {
    .hero-title {
        font-size: 3.5rem;   /* Desktop */
    }
}
```

---

## File Organization

### CSS File Structure
```
src/static/css/
├── main.css                    # Root variables, imports
├── bootstrap_addons/
│   ├── buttons.css            # Button overrides
│   ├── colors.css             # Color utilities
│   └── fonts.css              # Typography utilities
├── components/
│   ├── cards.css              # Shared card styles
│   └── utilities.css          # Component utilities
└── public/
    └── landing/
        ├── hero_v2.css        # Hero section styles
        ├── features_overview.css
        ├── testimonials.css
        ├── how_it_works.css
        ├── pricing.css
        └── faq.css
```

### Component CSS Loading
Each component loads its own CSS file:

```html
<section class="testimonials">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/public/landing/testimonials.css') }}">
    <!-- Component content -->
</section>
```

### File Naming
- Use lowercase with hyphens: `features-overview.css`
- Match component name: `pricing-card` → `pricing.css`
- One component per file

---

## Icon Usage

### SVG with currentColor (MANDATORY)
**ALWAYS** use `currentColor` for fill/stroke to enable theming:

```html
<!-- ✅ CORRECT -->
<div class="feature-icon feature-icon--primary">
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none">
        <path d="..." fill="currentColor"/>
    </svg>
</div>

<!-- ❌ WRONG -->
<svg width="36" height="36">
    <path d="..." fill="#2b9c89"/>
</svg>
```

### Icon Styling
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

---

## Forbidden Practices

### ❌ NEVER Do These

#### Inline Styles
```html
<!-- ❌ FORBIDDEN -->
<div style="color: red; margin: 10px;">...</div>

<!-- ✅ CORRECT -->
<div class="component">...</div>
```

#### Hardcoded Colors
```css
/* ❌ FORBIDDEN */
.component {
    color: #111827;
    background: #ffffff;
}

/* ✅ CORRECT */
.component {
    color: var(--text-primary);
    background: var(--bg-primary);
}
```

#### Pixel Units for Typography
```css
/* ❌ FORBIDDEN */
.heading {
    font-size: 24px;
}

/* ✅ CORRECT */
.heading {
    font-size: 1.5rem;
}
```

#### !important (except Bootstrap overrides)
```css
/* ❌ FORBIDDEN */
.component {
    color: red !important;
}

/* ✅ CORRECT */
.component {
    color: var(--bs-danger);
}
```

#### ID Selectors for Styling
```css
/* ❌ FORBIDDEN */
#header {
    background: blue;
}

/* ✅ CORRECT */
.header {
    background: var(--bs-primary);
}
```

#### Non-Semantic HTML as Headings
```html
<!-- ❌ FORBIDDEN -->
<div class="heading">Title</div>
<span class="title">Subtitle</span>

<!-- ✅ CORRECT -->
<h2 class="heading">Title</h2>
<h3 class="title">Subtitle</h3>
```

---

## Component-Specific Patterns

### Hero Section
- Full viewport height: `min-height: 100vh`
- Gradient background with animation
- Bold typography with `font-weight: 900`
- Multiple CTA buttons (primary + secondary)
- Trust badges/social proof

### Features Section
- 3-4 column grid on desktop
- Icon + title + description pattern
- Hover effects with lift animation
- Centered section header with eyebrow

### Testimonials Section
- 3-column card grid
- Star ratings (5-star scale)
- Avatar images (circular, 64px)
- Author name + role
- Optional trust statistics

### How It Works Section
- Numbered step progression (1, 2, 3...)
- Visual connector line between steps (desktop only)
- Icon representation for each step
- Clear CTA at bottom

### Pricing Section
- 3-tier pricing cards
- Featured card highlighting (`--featured` modifier)
- Feature lists with checkmarks (✓) and crosses (✗)
- Distinctive CTA button per tier
- Annual/monthly toggle option

### FAQ Section
- Accordion behavior with expand/collapse
- ARIA-compliant interactions
- Keyboard navigation support (Arrow keys)
- JavaScript toggle functionality
- Answer content hidden by default

---

## Testing Checklist

Before committing landing page changes, verify:

### Visual Testing
- [ ] Tested in Chrome, Firefox, Safari, Edge
- [ ] Tested on mobile devices (iOS, Android)
- [ ] Verified dark mode compatibility
- [ ] Checked all responsive breakpoints (xs, sm, md, lg, xl)
- [ ] Validated hover states work on desktop
- [ ] Confirmed animations are smooth

### Accessibility Testing
- [ ] Ran WAVE accessibility checker (0 errors)
- [ ] Tested keyboard-only navigation
- [ ] Tested with screen reader (NVDA/VoiceOver)
- [ ] Verified color contrast ratios (≥4.5:1 for text)
- [ ] Checked all ARIA labels and roles
- [ ] Confirmed focus indicators visible

### Code Quality
- [ ] No inline styles in HTML
- [ ] All CSS follows BEM naming
- [ ] CSS variables used for all colors
- [ ] Properties ordered correctly
- [ ] No CSS validation errors
- [ ] No duplicate class definitions

### Performance
- [ ] Images optimized (WebP format preferred)
- [ ] Lazy loading enabled for below-fold images
- [ ] CSS file size reasonable (<50KB per component)
- [ ] Page load speed <3 seconds
- [ ] No Cumulative Layout Shift (CLS) issues

---

## Quick Reference

### Common BEM Patterns
```
.section__eyebrow
.section__title
.section__subtitle
.section__content

.[component]-card
.[component]-card__header
.[component]-card__body
.[component]-card__footer
.[component]-card--featured

.feature-icon
.feature-icon--primary
.feature-icon--secondary

.btn-v2
.btn-v2-primary
.btn-v2-text
.btn-v2-icon
```

### Bootstrap Grid Classes
```html
<div class="container">
<div class="container-fluid">
<div class="row g-4">
<div class="col-12 col-md-6 col-lg-4">
```

### Spacing Utilities
```
.mb-0, .mb-1, .mb-2, .mb-3, .mb-4, .mb-5
.mt-3, .mt-4, .mt-5
.p-3, .p-4, .p-5
.py-5 (padding top/bottom)
.px-3 (padding left/right)
```

---

## Resources

- [Full Style Guide](../../docs/landing_page_style_guide.md)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [BEM Methodology](http://getbem.com/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Last Updated:** November 6, 2025  
**Maintained by:** CWMT Development Team
