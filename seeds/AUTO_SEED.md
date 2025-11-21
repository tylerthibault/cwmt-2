# Auto-Seeding Database

The application now supports automatic database seeding on startup in development mode.

## How It Works

1. **Configuration**: The `AUTO_SEED` flag in `config.py` controls whether seeding runs automatically
   - **Development**: `AUTO_SEED = True` (enabled by default)
   - **Production**: `AUTO_SEED = False` (disabled for safety)

2. **Flag File**: The system uses a `.seeded` flag file in the `instance/` folder to track if the database has been seeded
   - On first run: Seeds are executed and the flag file is created
   - On subsequent runs: Flag file is detected, seeding is skipped

3. **Seed Order**: Seeds run in the correct dependency order:
   1. Roles (required first)
   2. Users (depends on roles)
   3. Courses
   4. Students (depends on users and courses)
   5. Email Settings
   6. Email Actions
   7. Email Templates

## Usage

### Automatic Seeding (Development)
Simply start the app in development mode:
```bash
python run.py
```

The database will be automatically seeded on the first run.

### Manual Seeding
You can still run seeds manually:
```bash
python seeds/run_seeds.py --all
```

### Reset Database and Re-seed
To force re-seeding, delete both the database and the flag file:
```bash
# Windows
del instance\cwmt.db instance\.seeded

# Linux/Mac
rm instance/cwmt.db instance/.seeded
```

Then restart the app.

### Disable Auto-Seeding
To disable auto-seeding in development, either:

1. Set environment variable:
   ```bash
   export FLASK_CONFIG=production
   ```

2. Or temporarily modify `config.py`:
   ```python
   class DevelopmentConfig(Config):
       AUTO_SEED = False  # Disable auto-seeding
   ```

## Benefits

- ✅ **No Manual Steps**: Database is ready with test data immediately
- ✅ **Idempotent**: Won't re-seed on every restart
- ✅ **Safe**: Only enabled in development by default
- ✅ **Fast**: Seeding happens once during app initialization
- ✅ **Clean**: Easy to reset by deleting flag file

## Files Modified

- `config.py` - Added `AUTO_SEED` configuration
- `src/__init__.py` - Added `run_auto_seed()` function and integration
- `instance/.seeded` - Flag file (auto-created)
