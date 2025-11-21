# Seed Files

This directory contains seed files for populating the database with default data for development and testing purposes.

## ⚡ Auto-Seeding (Recommended)

**The database now seeds automatically in development mode!**

Just run:
```bash
python run.py
```

On first startup, the app will automatically seed all data. See [AUTO_SEED.md](./AUTO_SEED.md) for details.

### Reset & Re-seed
```bash
# Windows
reset_db.bat

# Linux/Mac
./reset_db.sh
```

## Manual Seeding

You can still run seeds manually:

```bash
# Run all seeds (easiest method)
python seeds/run_seeds.py --all

# Or use convenience scripts
./seeds/seed.sh --all        # Unix/Linux/Mac
seeds\seed.bat --all         # Windows
```

## Available Seed Files

### 1. `seed_roles.py`
Seeds default user roles into the database:
- **super-user**: Full system access and administrative privileges
- **admin**: Administrative access for managing users and content
- **instructor**: Teaching and content creation privileges
- **student**: Basic access for learning and participation

### 2. `seed_users.py`
Seeds default test users into the database, one for each role:
- **superuser** (superuser@cwmt.test) - Super User role
- **admin** (admin@cwmt.test) - Admin role
- **instructor** (instructor@cwmt.test) - Instructor role
- **student** (student@cwmt.test) - Student role

**Default Password**: `Password123!` (for all test users)

⚠️ **Security Note**: These test users should only be used in development environments. Change or remove them in production.

### 3. `seed_courses.py`
Seeds default course templates:
- **Get Riding**: 2-day beginner course
- **Street Smart**: 1-day intermediate course

## Automatic Seeding

All seed files are automatically run when the database is initialized via `init_db()` in `src/models/__init__.py`. The seeding functions are idempotent - they check if data already exists before creating new records.

## Manual Seeding

### Using the Seed Runner Script (Recommended)

The easiest way to run seeds is using the `run_seeds.py` script:

```bash
# Run all seeds (recommended - ensures correct order)
python seeds/run_seeds.py --all

# Run individual seed files
python seeds/run_seeds.py --roles
python seeds/run_seeds.py --users
python seeds/run_seeds.py --courses

# Get help
python seeds/run_seeds.py --help
```

**Convenience Scripts**: For even easier usage, you can use the wrapper scripts:

```bash
# Unix/Linux/Mac
./seeds/seed.sh --all

# Windows
seeds\seed.bat --all
```

These scripts automatically activate the virtual environment if it exists.

**Note**: If using a virtual environment, activate it first or use the full path to your Python executable.

### Using Python One-Liners

You can also run seed files manually using the Flask shell:

```bash
# Run all seeds
python -c "from src import create_app; from seeds.seed_roles import seed_default_roles; from seeds.seed_users import seed_default_users; from seeds.seed_courses import seed_default_course_templates; app = create_app(); app.app_context().push(); seed_default_roles(app); seed_default_users(app); seed_default_course_templates(app)"
```

Or individually:

```bash
# Seed roles only
python -c "from src import create_app; from seeds.seed_roles import seed_default_roles; app = create_app(); app.app_context().push(); seed_default_roles(app)"

# Seed users only
python -c "from src import create_app; from seeds.seed_users import seed_default_users; app = create_app(); app.app_context().push(); seed_default_users(app)"

# Seed courses only
python -c "from src import create_app; from seeds.seed_courses import seed_default_course_templates; app = create_app(); app.app_context().push(); seed_default_course_templates(app)"
```

## Test User Login Credentials

All test users share the same default password for easy testing:

| Username   | Email                   | Role        | Password      |
|------------|-------------------------|-------------|---------------|
| superuser  | superuser@cwmt.test     | super-user  | Password123!  |
| admin      | admin@cwmt.test         | admin       | Password123!  |
| instructor | instructor@cwmt.test    | instructor  | Password123!  |
| student    | student@cwmt.test       | student     | Password123!  |

## Development Workflow

1. **Initial Setup**: Seeds run automatically on first `db.create_all()`
2. **Reset Database**: Drop all tables and recreate to re-run seeds
3. **Add More Seed Data**: Create new seed files following the existing patterns

## Creating New Seed Files

Follow this pattern when creating new seed files:

```python
"""
Module docstring explaining what gets seeded
"""
from src.models import db
from src.models.your_model import YourModel


def seed_default_items(app):
    """
    Docstring explaining the seeding function
    
    Args:
        app: Flask application instance
    """
    default_items = [
        # Your default data here
    ]
    
    items_created = 0
    
    for item_data in default_items:
        # Check if exists
        existing = YourModel.query.filter_by(name=item_data['name']).first()
        
        if not existing:
            item = YourModel(**item_data)
            db.session.add(item)
            items_created += 1
            app.looger.info(f"Created item: {item_data['name']}")
    
    if items_created > 0:
        try:
            db.session.commit()
            app.looger.info(f"Successfully seeded {items_created} item(s)")
        except Exception as e:
            db.session.rollback()
            app.looger.error(f"Error seeding items: {str(e)}")
            raise


__all__ = ['seed_default_items']
```

Then add the import to `src/models/__init__.py` in the `init_db()` function.

## Seed Runner Script

The `run_seeds.py` script provides a convenient command-line interface for running seed files:

### Features:
- ✅ Run all seeds or individual seed files
- ✅ Proper error handling and reporting
- ✅ Clear progress output
- ✅ Ensures correct seeding order (roles → users → courses)

### Arguments:
- `--all` - Run all seed files in correct order (recommended)
- `--roles` - Run only roles seed
- `--users` - Run only users seed (requires roles to exist first)
- `--courses` - Run only courses seed

### Examples:
```bash
# First time setup - run all seeds
python seeds/run_seeds.py --all

# Add new users after roles already exist
python seeds/run_seeds.py --users

# Get help
python seeds/run_seeds.py --help
```

### Important Notes:
- The `--users` option requires roles to exist first
- Use `--all` to ensure dependencies are met
- Seeds are idempotent - safe to run multiple times
