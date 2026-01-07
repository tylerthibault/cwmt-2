# Email Configuration Fix - Encryption Implementation

## Problem
Gmail was rejecting emails with "Authentication Required" error because:
1. The mail password was being stored as a bcrypt hash (one-way)
2. Flask-Mail needs the actual plaintext password to authenticate with Gmail
3. Bcrypt hashes cannot be decrypted back to the original password

## Solution
Changed from bcrypt hashing to Fernet encryption (two-way):
- **Bcrypt (old)**: One-way hash - cannot retrieve original password
- **Fernet (new)**: Symmetric encryption - can decrypt to get original password

## Changes Made

### 1. Created Encryption Utility
**File**: `src/utils/encryption.py`
- Uses `cryptography.fernet` for secure encryption/decryption
- Derives encryption key from environment or app secret
- Functions: `encrypt_string()`, `decrypt_string()`

### 2. Updated AppSettings Model
**File**: `src/models/app_settings.py`
- Renamed: `mail_password_hash` → `mail_password_encrypted`
- Changed: `set_mail_password()` now encrypts instead of hashes
- Added: `get_mail_password()` to decrypt password
- Removed: `verify_mail_password()` (no longer needed)
- Updated: `get_mail_config()` returns decrypted password

### 3. Updated App Initialization
**File**: `src/__init__.py`
- Added: `init_mail()` function to load email config from database
- Now loads settings from database instead of only environment variables
- Falls back to environment variables if database not configured

### 4. Created Database Migration
**File**: `migrations/versions/a1b2c3d4e5f6_rename_mail_password_hash_to_encrypted.py`
- Renames column from `mail_password_hash` to `mail_password_encrypted`
- Changes column type from `String(255)` to `Text` for encrypted data

## Deployment Steps

### 1. Run Database Migration
```bash
flask db upgrade
```
Or on production:
```bash
python -m flask --app run.py db upgrade
```

### 2. Re-enter Email Password
After deployment, go to **Settings → Email Configuration** and re-enter the email password. The old bcrypt hash cannot be converted to an encrypted password, so it must be re-entered.

### 3. Verify Email Sending
Test email sending by:
- Creating a new user account
- Triggering password reset
- Checking application logs for any email errors

## Security Notes

### Encryption Key
The encryption key is derived from:
1. `ENCRYPTION_KEY` environment variable (preferred)
2. `SECRET_KEY` environment variable (fallback)
3. Hardcoded secret in `__init__.py` (development only)

**For Production**: Set a secure `ENCRYPTION_KEY` environment variable:
```bash
export ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

### Why This is Secure
1. **Database**: Passwords are encrypted, not plaintext
2. **Fernet**: Uses AES-128 encryption with HMAC authentication
3. **Key Management**: Encryption key stored in environment, not in code
4. **One Active Setting**: Only one non-deleted settings row exists at a time

## Files Modified
1. ✅ `src/utils/encryption.py` (NEW)
2. ✅ `src/models/app_settings.py`
3. ✅ `src/__init__.py`
4. ✅ `migrations/versions/a1b2c3d4e5f6_rename_mail_password_hash_to_encrypted.py` (NEW)

## Testing
After deployment:
1. Go to `/superuser/settings`
2. Enter email configuration:
   - SMTP Server: smtp.gmail.com
   - Port: 587
   - Username: your-email@gmail.com
   - Password: your-app-password
   - Use TLS: ✓
3. Save settings
4. Test by registering a new user
5. Check if welcome email is sent successfully
