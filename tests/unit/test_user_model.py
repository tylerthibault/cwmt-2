"""
Unit tests for the User model — verifying PII encryption and blind-index lookups.

These tests exercise the database layer directly using an in-memory SQLite DB
(provided by the 'testing' Flask config) so no external services are required.
"""
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def db_session(app_ctx):
    """
    Each test runs inside a DB transaction that is rolled back afterward,
    so tests remain isolated without recreating the schema.
    """
    from src.models import db
    db.session.begin_nested()
    yield db
    db.session.rollback()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_user(suffix='test', email=None, username=None):
    """Create and persist a minimal User for testing."""
    from src.models.user import User
    from src.logic.auth_logic import AuthLogic

    user = User(
        email=email or f'{suffix}@example.com',
        username=username or f'testuser_{suffix}',
        password_hash=AuthLogic.generate_password_hash('Password99!'),
        first_name='Test',
        last_name='User',
        is_active=True,
    )
    from src.models import db
    db.session.add(user)
    db.session.flush()
    return user


# ---------------------------------------------------------------------------
# Tests: PII stored encrypted in the database
# ---------------------------------------------------------------------------

class TestPIIStoredEncrypted:

    def test_email_is_encrypted_in_db(self, app_ctx):
        """The raw value stored in the DB for 'email' must be a Fernet token."""
        import sqlite3
        from src.models import db

        user = _make_user('enc_email')
        db.session.flush()

        # Query raw bytes directly so SQLAlchemy TypeDecorators are bypassed
        result = db.session.execute(
            db.text('SELECT email FROM users WHERE id = :uid'),
            {'uid': user.id}
        ).fetchone()

        raw_email = result[0]
        assert raw_email.startswith('gAAAAA'), (
            f'Email should be Fernet-encrypted in the DB, got: {raw_email[:40]}')

    def test_username_is_encrypted_in_db(self, app_ctx):
        """The raw value stored in the DB for 'username' must be a Fernet token."""
        from src.models import db

        user = _make_user('enc_uname')
        db.session.flush()

        result = db.session.execute(
            db.text('SELECT username FROM users WHERE id = :uid'),
            {'uid': user.id}
        ).fetchone()

        raw_username = result[0]
        assert raw_username.startswith('gAAAAA'), (
            f'Username should be Fernet-encrypted in the DB, got: {raw_username[:40]}')

    def test_first_name_is_encrypted_in_db(self, app_ctx):
        """first_name PII column must be stored encrypted."""
        from src.models import db

        user = _make_user('enc_fname')
        db.session.flush()

        result = db.session.execute(
            db.text('SELECT first_name FROM users WHERE id = :uid'),
            {'uid': user.id}
        ).fetchone()

        raw = result[0]
        assert raw.startswith('gAAAAA'), (
            f'first_name should be encrypted, got: {raw[:40]}')

    def test_last_name_is_encrypted_in_db(self, app_ctx):
        """last_name PII column must be stored encrypted."""
        from src.models import db

        user = _make_user('enc_lname')
        db.session.flush()

        result = db.session.execute(
            db.text('SELECT last_name FROM users WHERE id = :uid'),
            {'uid': user.id}
        ).fetchone()

        raw = result[0]
        assert raw.startswith('gAAAAA'), (
            f'last_name should be encrypted, got: {raw[:40]}')

    def test_decrypted_values_readable_via_orm(self, app_ctx):
        """SQLAlchemy ORM must transparently decrypt PII columns on read."""
        from src.models.user import User

        user = _make_user('decrypt_check')
        uid = user.id

        # Expire to force a reload from DB
        from src.models import db
        db.session.expire(user)
        reloaded = User.query.get(uid)

        assert reloaded.email == 'decrypt_check@example.com'
        assert reloaded.username == 'testuser_decrypt_check'
        assert reloaded.first_name == 'Test'
        assert reloaded.last_name == 'User'


# ---------------------------------------------------------------------------
# Tests: blind-index hashes populated automatically
# ---------------------------------------------------------------------------

class TestSearchHashesAutoPopulated:

    def test_email_search_hash_set_on_insert(self, app_ctx):
        """email_search_hash must be populated automatically on INSERT."""
        from src.utils.encryption import compute_search_hash

        user = _make_user('hash_insert')
        assert user.email_search_hash is not None
        assert user.email_search_hash == compute_search_hash('hash_insert@example.com')

    def test_username_search_hash_set_on_insert(self, app_ctx):
        """username_search_hash must be populated automatically on INSERT."""
        from src.utils.encryption import compute_search_hash

        user = _make_user('hash_uname')
        assert user.username_search_hash is not None
        assert user.username_search_hash == compute_search_hash('testuser_hash_uname')

    def test_email_search_hash_updated_on_email_change(self, app_ctx):
        """email_search_hash must be recalculated when the email changes."""
        from src.utils.encryption import compute_search_hash
        from src.models import db

        user = _make_user('hash_update')
        old_hash = user.email_search_hash

        user.email = 'updated@example.com'
        db.session.flush()

        assert user.email_search_hash != old_hash
        assert user.email_search_hash == compute_search_hash('updated@example.com')


# ---------------------------------------------------------------------------
# Tests: get_by_email / get_by_username lookups
# ---------------------------------------------------------------------------

class TestBlindIndexLookups:

    def test_get_by_email_returns_correct_user(self, app_ctx):
        """get_by_email must find the user via the blind-index hash."""
        from src.models.user import User

        user = _make_user('lookup_email')
        found = User.get_by_email('lookup_email@example.com')

        assert found is not None
        assert found.id == user.id
        assert found.email == 'lookup_email@example.com'

    def test_get_by_username_returns_correct_user(self, app_ctx):
        """get_by_username must find the user via the blind-index hash."""
        from src.models.user import User

        user = _make_user('lookup_uname')
        found = User.get_by_username('testuser_lookup_uname')

        assert found is not None
        assert found.id == user.id

    def test_get_by_email_case_insensitive(self, app_ctx):
        """Lookup must succeed regardless of email case (hash is normalised)."""
        from src.models.user import User

        _make_user('case_email', email='CaseTest@Example.COM')
        found = User.get_by_email('casetest@example.com')
        assert found is not None

    def test_get_by_email_returns_none_for_unknown_email(self, app_ctx):
        """get_by_email must return None for an email that doesn't exist."""
        from src.models.user import User
        assert User.get_by_email('nobody@nowhere.invalid') is None

    def test_get_by_username_returns_none_for_unknown_username(self, app_ctx):
        """get_by_username must return None for a username that doesn't exist."""
        from src.models.user import User
        assert User.get_by_username('ghostuser_xyz') is None
