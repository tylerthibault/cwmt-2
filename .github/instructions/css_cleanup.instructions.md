# CSS Cleanup Instructions

## Overview
These instructions guide the systematic cleanup of CSS across the project by removing inline styles from HTML files and organizing CSS files for better maintainability.

## Core Principles

1. **No Inline Styles**: Remove ALL inline `style=""` attributes from HTML elements
2. **Class-Based Styling**: Use CSS classes for all styling needs
3. **In-File Style Tags**: Only use `<style>` tags within HTML files for truly ad-hoc, page-specific styles that won't be reused
4. **Organized CSS**: Maintain clean, well-organized CSS files with no duplicates

## HTML File Cleanup Process

### Step 1: Identify Inline Styles
- Scan all HTML files in `src/templates/` directory
- Look for any element with `style=""` attribute
- Document the styling being applied

### Step 2: Convert Inline Styles to Classes

#### For Common/Reusable Styles
1. Check if equivalent class exists in CSS files
2. If exists, replace inline style with existing class
3. If doesn't exist, create new semantic class in appropriate CSS file:
   - Component-specific styles → `src/static/css/components/`
   - Page-specific styles → `src/static/css/private/` or `src/static/css/public/`
   - Utility styles → `src/static/css/bootstrap_addons/`

#### For Ad-Hoc/One-Off Styles
1. If style is truly unique to single element on single page
2. Create `<style>` tag in the `<head>` section of that HTML file
3. Use descriptive, scoped class name (e.g., `.login-page-special-header`)
4. Apply class to element

### Step 3: Remove Inline Style Attributes
- After converting to classes, remove all `style=""` attributes
- Verify visual appearance remains unchanged

## CSS File Organization Process

### Step 1: Audit Current CSS Files
- Review all CSS files in `src/static/css/`
- Identify duplicate class definitions
- Note overlapping or redundant styles

### Step 2: Remove Duplicates
- Keep the most complete/correct version of duplicate classes
- Remove all other instances
- Consolidate variations into single, well-named class
- Add comments for clarity if needed

### Step 3: Organize Classes Logically

#### Main CSS File (`main.css`)
- Global imports
- Root variables
- Body/HTML base styles
- Global utility classes

#### Component Files (`components/`)
Each component file should contain:
```css
/* ============================================
   Component Name: [Component]
   Description: [Brief description]
   ============================================ */

/* Base Styles */
.component-base { }

/* Variants */
.component-variant { }

/* States */
.component-state { }

/* Modifiers */
.component-modifier { }
```

#### Bootstrap Addons (`bootstrap_addons/`)
- Organized by category (colors, fonts, sizing, etc.)
- One category per file
- Alphabetically sorted within category

#### Public/Private Styles
- Page-specific styles only
- Organized by page/feature
- Clear section comments

### Step 4: Naming Conventions

#### Class Names
- Use kebab-case: `.my-class-name`
- Be semantic and descriptive: `.submit-button` not `.btn-1`
- Use BEM methodology for complex components:
  - Block: `.card`
  - Element: `.card__header`
  - Modifier: `.card--featured`

#### File Organization
```css
/* ============================================
   Section Name
   ============================================ */

/* Subsection if needed */
.class-one {
    /* Properties in logical order:
       1. Positioning
       2. Display & Box Model
       3. Typography
       4. Visual
       5. Misc
    */
}
```

### Step 5: Property Order Within Classes
```css
.example-class {
    /* Positioning */
    position: relative;
    top: 0;
    left: 0;
    z-index: 10;
    
    /* Display & Box Model */
    display: flex;
    flex-direction: column;
    width: 100%;
    height: auto;
    margin: 1rem;
    padding: 1rem;
    
    /* Typography */
    font-family: Arial, sans-serif;
    font-size: 1rem;
    line-height: 1.5;
    color: #333;
    
    /* Visual */
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    
    /* Misc */
    cursor: pointer;
    transition: all 0.3s ease;
}
```

## Implementation Workflow

### Phase 1: HTML Cleanup
1. Start with public templates (auth, landing, etc.)
2. Move to private templates (dashboard, admin, etc.)
3. Finish with components and bases
4. Test each template after cleanup

### Phase 2: CSS Organization
1. Audit and document all existing classes
2. Identify and remove duplicates
3. Reorganize files by category/component
4. Consolidate similar styles
5. Add proper comments and sections

### Phase 3: Validation
1. Visual regression testing on all pages
2. Verify responsive behavior
3. Check browser compatibility
4. Validate CSS with linter

## Tools and Commands

### Search for Inline Styles
```bash
# Find all HTML files with inline styles
grep -r 'style="' src/templates/

# Count inline styles
grep -r 'style="' src/templates/ | wc -l
```

### Find Duplicate CSS Classes
```bash
# Look for duplicate class definitions (manual review needed)
grep -r '^\.[a-zA-Z]' src/static/css/ | sort
```

## Quality Checklist

Before considering cleanup complete:

- [ ] Zero inline `style=""` attributes in HTML files
- [ ] All `<style>` tags are documented as ad-hoc/necessary
- [ ] No duplicate class definitions across CSS files
- [ ] All CSS files have clear section comments
- [ ] Classes follow naming conventions
- [ ] Properties ordered consistently within classes
- [ ] All pages render correctly after changes
- [ ] Responsive layouts still work
- [ ] No console errors or warnings
- [ ] CSS files are minified for production (if applicable)

## Special Cases

### Bootstrap Overrides
- Keep in separate section or file
- Comment why override is necessary
- Use specific selectors to avoid unintended effects

### Third-Party Components
- Isolate third-party CSS
- Namespace if possible
- Document source and version

### Dynamic Styles
- If JavaScript applies styles, consider using class toggling instead
- Create state classes (`.is-active`, `.is-hidden`, etc.)
- Avoid mixing JS-applied inline styles with static styles

## Documentation

After cleanup, document:
1. New class naming patterns used
2. CSS file structure and organization
3. Any breaking changes or deprecated classes
4. Guidelines for future CSS additions

## Example Conversion

### Before
```html
<div style="display: flex; justify-content: space-between; padding: 20px; background-color: #f5f5f5;">
    <h2 style="color: #333; font-size: 24px;">Title</h2>
    <button style="background-color: #007bff; color: white; padding: 10px 20px; border-radius: 4px;">
        Click Me
    </button>
</div>
```

### After (HTML)
```html
<div class="content-header">
    <h2 class="content-header__title">Title</h2>
    <button class="btn btn-primary">Click Me</button>
</div>
```

### After (CSS)
```css
/* ============================================
   Content Header Component
   ============================================ */

.content-header {
    display: flex;
    justify-content: space-between;
    padding: 1.25rem;
    background-color: #f5f5f5;
}

.content-header__title {
    margin: 0;
    font-size: 1.5rem;
    color: #333;
}
```

## Maintenance

Going forward:
- Never add inline styles
- Create reusable classes first
- Only use `<style>` tags when absolutely necessary
- Regular audits for duplicate/unused CSS
- Keep CSS files organized and documented
