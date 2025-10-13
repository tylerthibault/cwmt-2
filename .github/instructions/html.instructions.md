# HTML Best Practices

## File Organization
- Place HTML templates in `src/templates/` following the existing structure:
  - `bases/` - Base templates (public.html, private.html)
  - `public/` - Public-facing pages
  - `private/` - Authenticated user pages
- Use descriptive folder names matching route structure
- Name files `index.html` for main page views

## Asset Organization
- **CSS Files**: `src/static/css/{page-name}/{component-name}.css`
- **JS Files**: `src/static/js/{page-name}/{component-name}.js`
- **Images**: `src/static/img/{page-name}/` or `src/static/img/` for shared assets
- Keep page-specific assets isolated for maintainability

## Template Structure
- Always extend base templates using Jinja2: `{% extends "bases/public.html" %}`
- Use semantic HTML5 elements (`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`)
- Maintain proper document outline with heading hierarchy (h1 → h6)

## Code Standards
- Use lowercase for all element names and attributes
- Quote all attribute values with double quotes
- Self-close void elements: `<img />`, `<input />`, `<br />`
- Indent with 2 or 4 spaces consistently (project uses 4 spaces)
- Keep line length reasonable (≤120 characters when possible)

## Accessibility
- Include `alt` attributes for all images (empty `alt=""` for decorative images)
- Use proper ARIA labels when needed: `aria-label`, `aria-describedby`
- Ensure form inputs have associated `<label>` elements
- Maintain logical tab order (avoid `tabindex` > 0)
- Use sufficient color contrast ratios (WCAG AA minimum)

## Performance
- Load critical CSS in `<head>`, defer non-critical styles
- Place `<script>` tags before closing `</body>` or use `defer`/`async`
- Optimize images before adding to project
- Use lazy loading for below-fold images: `loading="lazy"`
- Minimize inline styles and scripts

## Jinja2 Templates
- Use template inheritance to reduce duplication
- Define blocks for overridable sections: `{% block content %}{% endblock %}`
- Use `url_for()` for all internal links: `href="{{ url_for('route_name') }}"`
- Use `url_for('static', filename='...')` for static assets
- Escape user content automatically (Jinja2 default) or explicitly with `{{ var|e }}`

## Bootstrap Integration
- Use Bootstrap 5 classes from included bootstrap CSS
- Import custom Bootstrap addons: fonts.css, sizing.css
- Follow Bootstrap's grid system (container, row, col-*)
- Utilize Bootstrap components before creating custom elements
- Override Bootstrap variables via custom CSS files, not inline

## Forms
- Use proper input types: `email`, `tel`, `number`, `date`, etc.
- Add `required`, `minlength`, `maxlength`, `pattern` for validation
- Include CSRF tokens in all forms: `{{ csrf_token }}`
- Group related inputs in `<fieldset>` with `<legend>`
- Provide clear error messages near invalid fields

## Comments
- Comment complex layouts or conditional logic
- Use `{# Jinja2 comments #}` for template-only notes
- Use `<!-- HTML comments -->` for client-visible notes (sparingly)
- Document non-obvious Bootstrap customizations

## Security
- Never render raw user input without escaping
- Validate all form inputs server-side
- Use HTTPS for external resource links
- Include Content Security Policy meta tags when applicable
- Avoid inline event handlers (`onclick`, etc.) - use JS event listeners

## Testing Checklist
- [ ] Validates with W3C HTML validator
- [ ] Responsive across mobile, tablet, desktop viewports
- [ ] Accessible via keyboard navigation
- [ ] Works in major browsers (Chrome, Firefox, Safari, Edge)
- [ ] Images have appropriate alt text
- [ ] Forms submit correctly with CSRF protection
- [ ] No console errors or warnings
- [ ] Proper template inheritance and block usage
