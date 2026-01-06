# Database Migration Guide for CapRover Deployment

## Overview
This guide explains how to apply database migrations to your production MySQL database on CapRover.

## Setup Requirements
1. Flask-Migrate is installed (already added to requirements.txt)
2. Migration files are committed to your repository
3. MySQL database is running in CapRover

## Migration Files Location
```
migrations/
├── alembic.ini
├── env.py
├── README
├── script.py.mako
└── versions/
    └── bdb5548afc4c_initial_migration_with_all_tables.py
```

## Steps to Apply Migration on CapRover

### Option 1: Via CapRover One-Click App (Recommended)

1. **SSH into your CapRover server:**
   ```bash
   ssh root@your-server-ip
   ```

2. **Enter your app container:**
   ```bash
   docker exec -it $(docker ps | grep cwmt | awk '{print $1}') /bin/sh
   ```

3. **Run the migration:**
   ```bash
   flask --app run.py db upgrade
   ```

### Option 2: Add Migration Command to Dockerfile

Add this line to your Dockerfile AFTER the requirements are installed but BEFORE the app starts:

```dockerfile
# In your Dockerfile, add:
RUN flask --app run.py db upgrade
```

Then rebuild and redeploy.

### Option 3: Via captain-definition Script

Create a migration script that runs on deployment. Add to your `captain-definition`:

```json
{
  "schemaVersion": 2,
  "dockerfilePath": "./Dockerfile",
  "hooks": {
    "postDeploy": [
      {
        "command": "flask --app run.py db upgrade",
        "workingDirectory": "/app"
      }
    ]
  }
}
```

## Manual Migration Commands

### Check current migration status:
```bash
flask --app run.py db current
```

### View migration history:
```bash
flask --app run.py db history
```

### Apply all pending migrations:
```bash
flask --app run.py db upgrade
```

### Rollback last migration:
```bash
flask --app run.py db downgrade
```

### Create new migration after model changes:
```bash
flask --app run.py db migrate -m "Description of changes"
```

## Important Notes

1. **Environment Variables**: Make sure your production MySQL connection string is set in CapRover:
   - Set `SQLALCHEMY_DATABASE_URI` environment variable in CapRover app settings
   - Format: `mysql+pymysql://username:password@host:3306/database_name`

2. **Backup First**: Always backup your production database before running migrations:
   ```bash
   # From CapRover server
   docker exec mysql-container mysqldump -u root -p database_name > backup.sql
   ```

3. **Test Migrations**: Test migrations in a staging environment first

4. **Migration Safety**:
   - Migrations are transactional for most operations
   - Some operations (like ALTER TABLE in MySQL) cannot be rolled back
   - Always review the generated migration file before applying

## Troubleshooting

### "No such command 'db'"
- Ensure Flask-Migrate is installed: `pip install Flask-Migrate==4.0.5`
- Check that `migrate.init_app(app, db)` is called in your `__init__.py`

### "Could not locate a Flask application"
- Use the `--app` flag: `flask --app run.py db upgrade`
- Or set `FLASK_APP=run.py` environment variable

### Migration fails with MySQL error
- Check MySQL connection string
- Verify database user has necessary permissions
- Check MySQL logs for specific errors

### "Target database is not up to date"
- Run `flask --app run.py db upgrade` to apply pending migrations
- Check `flask --app run.py db current` to see current version

## Current Migration
The initial migration (`bdb5548afc4c`) includes all tables:
- Users (users, students, instructors, admins, superusers)
- Courses (course_templates, course_instances, enrollments, payable_templates)
- Payments (payments, payment_line_items, stripe_webhook_events)
- Email (email_templates, email_logs, logs)
- Announcements
- App Settings

This migration removes old deprecated tables and creates the new schema.
