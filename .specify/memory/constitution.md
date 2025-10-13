<!--
Sync Impact Report:
Version change: 1.0.0 → 1.1.0
Updated MVC Architecture principle with thin controllers/models, thick logic pattern
Added Technology Stack Standards section with SQLite and SQLAlchemy requirements
Templates requiring updates:
- plan-template.md ⚠ pending (Constitution Check needs technology stack compliance)
- spec-template.md ✅ compatible (no changes needed)
- tasks-template.md ✅ compatible (no changes needed)
-->

# CWMT Flask Web Application Constitution

## Core Principles

### I. MVC Architecture with Thin Layers (NON-NEGOTIABLE)
Flask application MUST follow Model-View-Controller pattern with strict layer responsibilities:
- **Models (THIN)**: Database interactions ONLY via SQLAlchemy ORM - no business logic, only data persistence and basic validation
- **Views**: Template rendering in `src/templates/` - Jinja2 templates with proper inheritance, no logic beyond presentation
- **Controllers (THIN)**: Route handling ONLY in `src/controllers/routes.py` - request/response mapping, parameter extraction, calling logic layer
- **Logic (THICK)**: All business logic in `src/logic/` - core application functionality, complex validations, business rules, data transformations

The bulk of application work MUST happen in the logic layer. Controllers and Models serve only as thin interfaces.

**Rationale**: Ensures maximum testability, maintainability, and separation of concerns. Business logic centralized in logic layer enables easier testing and modification without affecting data or presentation layers.

### II. Template Organization
Template structure MUST follow hierarchical organization:
- Public pages: `templates/public/<page-name>/index.html`
- Private pages: `templates/private/<page-name>/index.html`
- Page-specific components: stored within respective page directory
- Multi-page components: `templates/public/components/` or `templates/private/components/`
- Base templates: `templates/bases/public.html` and `templates/bases/private.html`
Jinja2 template inheritance and includes MUST be used for code reuse.

**Rationale**: Promotes component reusability, maintains clear page-to-template mapping, and supports scalable template architecture.

### III. Separation of Concerns (NON-NEGOTIABLE)
External resources MUST be separated from markup:
- **CSS**: All styles in external files under `static/css/` - NEVER inline CSS
- **JavaScript**: All scripts in external files under `static/js/` - minimal inline allowed only for configuration
- **Images/Assets**: Organized in `static/img/` with logical subdirectories
- **HTML**: Clean semantic markup only, no presentation or behavior
Each file MUST have single, clear responsibility.

**Rationale**: Enables better caching, maintainability, debugging, and follows web development best practices.

### IV. Testing Strategy
Testing approach MUST be lean but comprehensive:
- **Unit tests**: Critical business logic and utilities
- **Integration tests**: Route responses, template rendering, database operations
- **Simple smoke tests**: Ensure core functionality works after changes
- **No over-testing**: Focus on preventing regressions, not 100% coverage
Tests MUST be fast and maintainable. Complex testing infrastructure is explicitly discouraged.

**Rationale**: Balances quality assurance with development speed, focusing on practical testing that catches real issues.

### V. Performance & Lean Development
Development MUST prioritize speed and simplicity:
- **Lean code**: Prefer simple, readable solutions over complex abstractions
- **Fast development**: Optimize for developer velocity, not premature optimization
- **Minimal dependencies**: Add libraries only when essential benefit is clear
- **File-based organization**: Use filesystem structure for organization, not complex frameworks
Performance optimization only when bottlenecks are identified and measured.

**Rationale**: Supports rapid development cycles while maintaining code quality and avoiding over-engineering.

## File Structure Standards

All file organization MUST follow these patterns:
```
src/
├── models/          # Thin data models (SQLAlchemy ORM only)
├── controllers/     # Thin route handlers (request/response only)  
├── templates/       # Jinja2 templates (organized by access level)
├── static/          # CSS, JS, images (never inline)
├── logic/           # Thick business logic (core application work)
└── utils/           # General utilities
```

Template directories MUST use:
- `public/` for unauthenticated content
- `private/` for authenticated content  
- `components/` for reusable elements
- `bases/` for layout templates

Static asset organization is mandatory:
- CSS files in `static/css/`
- JavaScript files in `static/js/`
- Images in `static/img/`

## Technology Stack Standards

Core technology choices are standardized for consistency and development efficiency:

**Database & ORM**:
- **Development Database**: SQLite MUST be used for local development
- **ORM**: SQLAlchemy MUST be used for all database interactions
- **Database Location**: Development SQLite file in project root or `data/` directory
- **Migrations**: Use SQLAlchemy migrations for schema changes

**Flask Framework**:
- **Template Engine**: Jinja2 (Flask default) for all HTML rendering
- **Configuration**: Environment-based configuration (development/production)
- **Static Files**: Flask's built-in static file serving for development

**Development Standards**:
- Models MUST use SQLAlchemy declarative base and relationships
- Database queries MUST go through SQLAlchemy ORM, no raw SQL in models
- Logic layer MUST handle all business operations using model instances
- Controllers MUST only call logic layer functions, never direct model/database access

**Rationale**: Standardizes development environment, ensures consistent data access patterns, and supports rapid prototyping with production-ready ORM foundations.

## Development Workflow

Code changes MUST follow this workflow:
1. **Feature planning**: Clear understanding of requirements before coding
2. **Structure first**: Plan file organization and component breakdown
3. **Test-driven approach**: Write basic tests for critical paths
4. **Incremental development**: Small, focused commits with clear purposes
5. **Template validation**: Ensure template inheritance works correctly
6. **Asset validation**: Verify CSS/JS loads properly, no inline styles
7. **Integration testing**: Test complete user flows work end-to-end

All features MUST demonstrate adherence to MVC principles and file organization standards before being considered complete.

## Governance

This constitution supersedes all other development practices and guidelines.

**Amendment Process**: Changes require documentation of impact on existing code, approval of rationale, and migration plan for existing violations.

**Compliance Verification**: All code reviews MUST verify adherence to MVC principles, template organization, and separation of concerns. Violations MUST be documented and justified.

**Complexity Justification**: Any deviation from lean principles MUST include written justification of necessity and alternative approaches considered.

**Runtime Guidance**: Developers should reference this constitution for all architectural and organizational decisions during development.

**Version**: 1.1.0 | **Ratified**: 2025-10-12 | **Last Amended**: 2025-10-12