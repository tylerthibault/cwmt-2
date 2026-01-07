-- Fix for renaming mail_password_hash to mail_password_encrypted
-- Run this SQL directly on your production database

-- Rename the column
ALTER TABLE app_settings 
CHANGE COLUMN mail_password_hash mail_password_encrypted TEXT;

-- Verify the change
DESCRIBE app_settings;
