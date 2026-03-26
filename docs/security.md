# Security Guide — PII Encryption & Transit Protection

This document describes how CWMT protects student PII (Personally Identifiable
Information) in compliance with data-privacy best practices.

---

## Data at Rest — Field-Level Encryption

Sensitive PII fields in the `users` table are encrypted using
**Fernet symmetric encryption** (AES-128-CBC + HMAC-SHA256) from the
[cryptography](https://cryptography.io) library.

### Encrypted Columns

| Table  | Column       | Notes                               |
|--------|--------------|-------------------------------------|
| users  | email        | Encrypted; searchable via hash      |
| users  | username     | Encrypted; searchable via hash      |
| users  | first_name   | Encrypted                           |
| users  | last_name    | Encrypted                           |

### Blind-Index Search Hashes

Because Fernet uses random IVs, the same plaintext encrypts to a different
ciphertext on every call, making direct SQL `WHERE email = ?` comparisons
impossible.  To preserve exact-match lookup capability without exposing
plaintext, an **HMAC-SHA256 blind index** is stored alongside each searchable
field:

| Table  | Hash Column           | Used For                      |
|--------|-----------------------|-------------------------------|
| users  | email_search_hash     | `WHERE email_search_hash = ?` |
| users  | username_search_hash  | `WHERE username = ?`          |

The hash columns are automatically populated by a SQLAlchemy `before_insert` /
`before_update` event listener — no application code change is required when
setting an email or username.

---

## Required Environment Variables

The application **will not start** unless both keys are present.

| Variable               | Purpose                                           |
|------------------------|---------------------------------------------------|
| `FIELD_ENCRYPTION_KEY` | Master secret for Fernet PII field encryption     |
| `SEARCH_HASH_KEY`      | HMAC secret for blind-index search hashes         |
| `SECRET_KEY`           | Flask session signing / CSRF protection           |

### Generating Keys

Use Python's `secrets` module to generate strong random keys:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Run this **three times** to get three independent secrets, one per variable.

> ⚠️ **Never commit secrets to source control.**  
> Store them in your container orchestration platform's secrets manager
> (CapRover app environment variables, Docker secrets, AWS Secrets Manager,
> etc.).

### Local Development

Create a `.env` file in the project root (already in `.gitignore`) and export
the variables:

```bash
export FIELD_ENCRYPTION_KEY=<your-local-dev-secret>
export SEARCH_HASH_KEY=<your-local-dev-hash-secret>
export SECRET_KEY=<your-local-dev-session-secret>
```

Or use `direnv`, `python-dotenv`, or your IDE's run configuration to inject
them automatically.

---

## Key Rotation

**If you rotate `FIELD_ENCRYPTION_KEY`:**

1. Stop the application.
2. Decrypt all encrypted columns using the OLD key.
3. Re-encrypt every column using the NEW key.
4. Update the environment variable.
5. Restart the application.

**If you rotate `SEARCH_HASH_KEY`:**

1. Stop the application.
2. Re-compute all `*_search_hash` columns using the NEW key
   (`UPDATE users SET email_search_hash = hmac(new_key, email)`).
3. Update the environment variable.
4. Restart the application.

> Automating this migration with Alembic or a one-off management script is
> strongly recommended.

---

## Data in Transit — HTTPS & Security Headers

### Flask-Talisman

[Flask-Talisman](https://github.com/GoogleCloudPlatform/flask-talisman) is
used to enforce HTTPS and set defensive HTTP headers on every response.

| Header                      | Value (production)                              |
|-----------------------------|-------------------------------------------------|
| Strict-Transport-Security   | `max-age=31536000` (1 year HSTS)                |
| Content-Security-Policy     | `default-src 'self'` (with Bootstrap allowances)|
| X-Frame-Options             | `DENY`                                          |
| X-Content-Type-Options      | `nosniff` (set by Talisman)                     |
| Referrer-Policy             | `strict-origin-when-cross-origin`               |

HTTPS enforcement and HSTS are **disabled in development** (controlled by
`TALISMAN_FORCE_HTTPS` in `config.py`) to allow plain-HTTP local development.

### Session Cookie Flags

| Flag           | Development | Production |
|----------------|-------------|------------|
| `HttpOnly`     | ✅ enabled  | ✅ enabled |
| `SameSite`     | `Lax`       | `Lax`      |
| `Secure`       | ❌ disabled | ✅ enabled |

---

## Rate Limiting — Flask-Limiter

[Flask-Limiter](https://flask-limiter.readthedocs.io) is applied globally and
with tighter limits on authentication endpoints to mitigate brute-force
attacks:

| Endpoint          | Limit         |
|-------------------|---------------|
| `POST /auth/login`    | 20 / hour per IP |
| `POST /auth/register` | 10 / hour per IP |
| All other routes  | 200 / day, 50 / hour per IP |

> For production deployments with multiple workers, configure a shared storage
> backend (Redis, Memcached) via the `RATELIMIT_STORAGE_URL` environment
> variable so limits are enforced across all workers.

---

## Password Storage

Passwords are **never stored in plaintext**.  They are hashed with
**bcrypt** (via Flask-Bcrypt) before storage, providing:

- Adaptive cost factor (resistant to GPU cracking)
- Built-in per-password salting
- One-way hash (no decryption possible)

---

## Running the Test Suite

The test suite validates all security properties described above.  Run it with:

```bash
export FIELD_ENCRYPTION_KEY=<your-dev-key>
export SEARCH_HASH_KEY=<your-dev-hash-key>
export SECRET_KEY=<your-dev-session-key>

pytest
```

Or inline:

```bash
FIELD_ENCRYPTION_KEY=dev-key SEARCH_HASH_KEY=dev-hash-key pytest
```

Tests are organised in:

```
tests/
├── conftest.py                    # shared fixtures and env-var bootstrap
├── unit/
│   ├── test_encryption.py         # Fernet encrypt/decrypt, blind-index hashing
│   ├── test_user_model.py         # PII stored encrypted, blind-index lookups
│   └── test_auth_logic.py         # login / register with encrypted fields
└── smoke/
    ├── test_security_headers.py   # HTTP response headers (CSP, HSTS, etc.)
    └── test_app_startup.py        # startup validation, rate-limiter init
```

If `FIELD_ENCRYPTION_KEY` or `SEARCH_HASH_KEY` is compromised:

1. Immediately rotate the affected key (see Key Rotation above).
2. Invalidate all active sessions (clear the `logbooks` table or set
   `has_logged_out = TRUE` for all rows).
3. Notify affected users per your organisation's data-breach policy.
4. Review access logs for unauthorised queries.
