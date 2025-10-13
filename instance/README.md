# Instance Folder

This folder contains instance-specific files that should not be committed to version control:

- **Database files** (*.db, *.sqlite)
- **Uploaded files**
- **Instance-specific configurations**
- **Cache files**

## Contents

- `cwmt.db` - Development SQLite database
- `cwmt_prod.db` - Production SQLite database (when using SQLite in production)

## Note

This folder is automatically created by the application if it doesn't exist.
All files in this folder are gitignored except this README.
