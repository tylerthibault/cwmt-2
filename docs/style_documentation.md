## Short Style Guide

Purpose: keep components consistent and themeable across the site. The hero implementation lives at `src/templates/public/landing/components/hero_v2_dynamic.html` and the styles at `src/static/css/landing/hero_v2.css`.

Key rules (most important things)
1. **NEVER use inline styles** — always use CSS classes instead. Inline styles break theming, are harder to maintain, and violate separation of concerns.
2. **Always use color variables** defined in `src/static/css/main.css` so changing the theme is a single-source update.

Color tokens to use (examples)
- --bs-primary — primary brand color (dark text/brand)
- --bs-secondary — accent color
- --bs-light — light text/background for high-contrast over dark gradients
- --bg-primary / --bg-secondary — page surface backgrounds
- --text-primary / --text-secondary — typographic colors
- --border-color — borders and subtle separators
- --primary-gradient / --secondary-gradient — gradients used in hero backgrounds

Example usage: prefer variable usage rather than hard-coded colors, e.g.:

	background: var(--primary-gradient);
	color: var(--bs-light);

Structure & class conventions
- **No inline styles** — create CSS classes instead. If you need a one-off style, create a utility class or component-specific class.
- Follow BEM-like class naming already used (example: `.hero-v2`, `.hero-v2-title`, `.btn-v2`). Keep modifiers and element names readable and consistent.
- Keep markup structure similar to `hero_v2_dynamic.html` so the CSS selectors remain predictable.
- Check existing CSS files before adding new styles — reuse `.btn-primary`, `.badge`, `.card`, and other existing classes from `bootstrap_addons/` and `components/`.

CSS ordering & formatting
- Follow the project's CSS property groups and order: Layout → Spacing → Visual → Animation. Keep one blank line between groups.
- Use 2-space indentation and CSS variables for values that represent theme tokens.

Accessibility & responsiveness
- Respect `prefers-reduced-motion` and keep animations non-essential (informational only).
- Ensure text over gradients meets contrast requirements; if a background is complex, prefer `var(--bs-light)` or a semi-opaque overlay to preserve legibility.
- The hero already contains responsive breakpoints (1400, 1200, 991, 576px). When making changes, test at those widths.

Contract (quick)
- Inputs: hero HTML structure (BEM classes) and theme tokens in `src/static/css/main.css`.
- Output: a visually consistent hero across pages and themes when variables in `main.css` change.
- Error modes: avoid hard-coded colors; if a variable is missing fallback to a safe value (e.g., `color: var(--text-primary, #111827)`).

Edge cases to watch
- Dark theme: verify `[data-bs-theme="dark"]` variable set in `main.css` produces readable text.
- Reduced motion: animations should either not run or be simplified.
- Long or internationalized headings: ensure the title wraps and maintains spacing without overlapping visual elements.
- Image load failure: provide a sensible background color (use `--bg-primary`) and keep CTAs visible.

Small checklist for contributors
- **NEVER use inline styles** (style="...") — always create CSS classes.
- Use variables from `src/static/css/main.css` for colors and gradients.
- Follow BEM naming and existing markup structure.
- Keep property ordering Layout → Spacing → Visual → Animation.
- Test changes at defined breakpoints and in dark mode.
- Check for existing styles in `bootstrap_addons/` and `components/` before creating new ones.

Next steps (optional)
- Consider adding a small color token reference file (`docs/color-tokens.md`) mapping tokens to their role (brand, accent, surface, text). This makes on-boarding designers/devs faster.

That's it — short, actionable, and focused on making theme changes safe by relying on `main.css` variables.
