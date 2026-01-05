# Flask-Mail Database Schema

## Tables Overview

1. **email_templates** - Stores admin-created email templates
2. **email_logs** - Records all emails sent by the system
3. **email_purposes** - (Optional) Reference table for valid purposes

---

## Table: `email_templates`

Stores customizable email templates created by admins.

### Schema

```sql
CREATE TABLE email_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Template Identification
    purpose VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    
    -- Template Content
    subject_template TEXT NOT NULL,
    body_html_template TEXT NOT NULL,
    body_text_template TEXT NOT NULL,
    
    -- Status & Metadata
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Audit Fields
    created_by INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (created_by) REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT unique_active_per_purpose UNIQUE (purpose, is_active) 
        WHERE is_active = TRUE
);
```

### Indexes

```sql
CREATE INDEX idx_email_templates_purpose ON email_templates(purpose);
CREATE INDEX idx_email_templates_active ON email_templates(is_active);
CREATE INDEX idx_email_templates_purpose_active ON email_templates(purpose, is_active);
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key |
| `purpose` | VARCHAR(50) | Purpose code (e.g., 'password_reset', 'new_user', 'course_signup') |
| `name` | VARCHAR(200) | Admin-friendly name (e.g., "Holiday Welcome Email") |
| `subject_template` | TEXT | Email subject with Jinja2 variables (e.g., "Welcome {{ user_name }}!") |
| `body_html_template` | TEXT | HTML email body with Jinja2 variables |
| `body_text_template` | TEXT | Plain text email body with Jinja2 variables (fallback) |
| `is_active` | BOOLEAN | Whether this template is currently active for its purpose |
| `is_default` | BOOLEAN | Whether this is a system default template (non-editable) |
| `created_by` | INTEGER | ID of admin who created the template |
| `created_at` | DATETIME | When template was created |
| `updated_at` | DATETIME | When template was last modified |

### Business Rules

1. **Only one active template per purpose**: Enforced by unique constraint
2. **Default templates cannot be deleted**: Enforced at application level
3. **Active templates cannot be deleted**: Must be deactivated first
4. **Templates must have valid Jinja2 syntax**: Validated before save

### Example Data

```sql
INSERT INTO email_templates (purpose, name, subject_template, body_html_template, body_text_template, is_active, created_by) 
VALUES (
    'new_user',
    'Welcome Email - Standard',
    'Welcome to CWMT, {{ user_name }}!',
    '<h1>Welcome!</h1><p>Hi {{ user_name }},</p><p>Your temporary password is: <strong>{{ temp_password }}</strong></p>',
    'Welcome!\n\nHi {{ user_name }},\n\nYour temporary password is: {{ temp_password }}',
    TRUE,
    1
);
```

---

## Table: `email_logs`

Records all emails sent by the system for auditing and troubleshooting.

### Schema

```sql
CREATE TABLE email_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Email Details
    purpose VARCHAR(50) NOT NULL,
    recipient_email VARCHAR(255) NOT NULL,
    recipient_user_id INTEGER,
    
    -- Content
    subject TEXT NOT NULL,
    body_html TEXT,
    body_text TEXT,
    
    -- Template Reference
    template_id INTEGER,
    template_name VARCHAR(200),
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    
    -- Metadata
    sent_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_by INTEGER,
    is_test BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Foreign Keys
    FOREIGN KEY (template_id) REFERENCES email_templates(id) ON DELETE SET NULL,
    FOREIGN KEY (recipient_user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (sent_by) REFERENCES users(id) ON DELETE SET NULL
);
```

### Indexes

```sql
CREATE INDEX idx_email_logs_recipient ON email_logs(recipient_email);
CREATE INDEX idx_email_logs_purpose ON email_logs(purpose);
CREATE INDEX idx_email_logs_sent_at ON email_logs(sent_at DESC);
CREATE INDEX idx_email_logs_status ON email_logs(status);
CREATE INDEX idx_email_logs_recipient_user ON email_logs(recipient_user_id);
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key |
| `purpose` | VARCHAR(50) | Purpose code of the email |
| `recipient_email` | VARCHAR(255) | Email address where sent |
| `recipient_user_id` | INTEGER | User ID if recipient is a system user (nullable) |
| `subject` | TEXT | Rendered subject line (as sent) |
| `body_html` | TEXT | Rendered HTML body (as sent) |
| `body_text` | TEXT | Rendered plain text body (as sent) |
| `template_id` | INTEGER | ID of template used (nullable if deleted) |
| `template_name` | VARCHAR(200) | Name of template at time of send |
| `status` | VARCHAR(20) | Email status: 'sent', 'failed', 'pending' |
| `error_message` | TEXT | Error details if status is 'failed' |
| `sent_at` | DATETIME | When email was sent/attempted |
| `sent_by` | INTEGER | Admin who triggered send (nullable for system sends) |
| `is_test` | BOOLEAN | Whether this was a test email |

### Status Values

- `pending` - Email queued but not yet sent
- `sent` - Email successfully sent
- `failed` - Email send failed (see error_message)

### Example Data

```sql
INSERT INTO email_logs (purpose, recipient_email, recipient_user_id, subject, body_html, body_text, template_id, template_name, status, sent_at, is_test) 
VALUES (
    'course_signup',
    'student@example.com',
    42,
    'Welcome to Python 101!',
    '<h1>Welcome to Python 101!</h1>...',
    'Welcome to Python 101!...',
    3,
    'Course Enrollment - Spring 2026',
    'sent',
    '2026-01-02 14:30:00',
    FALSE
);
```

---

## Table: `email_purposes` (Optional Reference Table)

Optional reference table to store valid email purposes. This can be useful for validation and documentation, but could also be defined in Python code.

### Schema

```sql
CREATE TABLE email_purposes (
    code VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    available_variables JSON NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `code` | VARCHAR(50) | Purpose code (e.g., 'password_reset') |
| `name` | VARCHAR(100) | Display name (e.g., 'Password Reset') |
| `description` | TEXT | What this email purpose is for |
| `available_variables` | JSON | JSON object defining variables for this purpose |
| `is_active` | BOOLEAN | Whether this purpose is currently in use |
| `created_at` | DATETIME | When purpose was created |

### Example Data

```sql
INSERT INTO email_purposes (code, name, description, available_variables) 
VALUES (
    'password_reset',
    'Password Reset',
    'Email sent when user requests password reset',
    '{"user_name": "User full name", "reset_link": "Password reset URL", "expiry_hours": "Hours until link expires", "user_email": "User email address"}'
);
```

**Note**: This table is optional. The purposes and their variables can be defined in Python code as a constant dictionary instead, which may be simpler and more maintainable.

---

## Relationships

```
users (1) ---> (many) email_templates [created_by]
users (1) ---> (many) email_logs [recipient_user_id]
users (1) ---> (many) email_logs [sent_by]
email_templates (1) ---> (many) email_logs [template_id]
```

---

## Migration Notes

### Creation Order
1. Create `email_templates` table
2. Create `email_logs` table
3. Insert default templates for each purpose
4. Create indexes for performance

### Default Templates
The system should ship with basic default templates for:
- `password_reset`
- `new_user`
- `course_signup`
- `course_reminder`
- `course_cancellation`
- (add more as needed)

These should be marked with `is_default=TRUE` and `is_active=TRUE` initially.

---

## Query Examples

### Get active template for a purpose
```sql
SELECT * FROM email_templates 
WHERE purpose = 'password_reset' 
AND is_active = TRUE 
LIMIT 1;
```

### Get all templates for a purpose
```sql
SELECT * FROM email_templates 
WHERE purpose = 'course_signup' 
ORDER BY is_active DESC, created_at DESC;
```

### Get recent email logs
```sql
SELECT el.*, et.name as template_name, u.email as user_email
FROM email_logs el
LEFT JOIN email_templates et ON el.template_id = et.id
LEFT JOIN users u ON el.recipient_user_id = u.id
ORDER BY el.sent_at DESC
LIMIT 50;
```

### Count emails by purpose
```sql
SELECT purpose, status, COUNT(*) as count
FROM email_logs
WHERE sent_at >= date('now', '-30 days')
GROUP BY purpose, status
ORDER BY purpose, status;
```

### Failed emails in last 24 hours
```sql
SELECT * FROM email_logs
WHERE status = 'failed'
AND sent_at >= datetime('now', '-1 day')
ORDER BY sent_at DESC;
```
