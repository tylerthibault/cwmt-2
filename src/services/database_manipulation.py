"""Database manipulation service for administrative operations."""
import os
from pathlib import Path
from flask import flash
from src.models.main import db


def reset_database():
    """
    Reset the database by dropping and recreating all tables.
    
    Returns:
        bool: True if successful, False otherwise
    """
    is_mysql = 'mysql' in db.engine.url.drivername
    
    try:
        if is_mysql:
            _reset_mysql_database()
        else:
            _reset_sqlite_database()
        
        db.create_all()
        flash('Database tables recreated.', 'success')
        
        _remove_seed_flag()
        flash('✅ Database reset complete! Refresh the page to see the empty database.', 'success')
        return True
        
    except Exception as e:
        flash(f'Error resetting database: {str(e)}', 'danger')
        if is_mysql:
            _ensure_mysql_foreign_keys_enabled()
        return False


def _reset_mysql_database():
    """Drop all tables in MySQL database."""
    db.session.execute(db.text('SET FOREIGN_KEY_CHECKS=0;'))
    db.session.commit()
    
    result = db.session.execute(db.text("SHOW TABLES"))
    tables = [row[0] for row in result]
    
    for table in tables:
        db.session.execute(db.text(f"DROP TABLE IF EXISTS `{table}`"))
    db.session.commit()
    
    db.session.execute(db.text('SET FOREIGN_KEY_CHECKS=1;'))
    db.session.commit()
    
    flash(f'Dropped {len(tables)} tables from database.', 'success')


def _reset_sqlite_database():
    """Drop all tables in SQLite database."""
    db.drop_all()
    flash('All database tables dropped.', 'success')


def _remove_seed_flag():
    """Remove seed flag file to trigger reseeding."""
    seed_flag_path = Path('instance') / '.seeded'
    if seed_flag_path.exists():
        os.remove(seed_flag_path)
        flash('Seed flag deleted - data will be reseeded on next page load.', 'success')


def _ensure_mysql_foreign_keys_enabled():
    """Ensure MySQL foreign key checks are re-enabled after error."""
    try:
        db.session.execute(db.text('SET FOREIGN_KEY_CHECKS=1;'))
        db.session.commit()
    except:
        pass
