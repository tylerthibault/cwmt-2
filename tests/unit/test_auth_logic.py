"""
Unit tests for AuthLogic — login and registration with encrypted user fields.

All tests use the in-memory SQLite testing database seeded with default users
(superuser@cwmt.test, admin@cwmt.test, instructor@cwmt.test, student@cwmt.test).
"""
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def request_ctx(app):
    """
    Push a request context so Flask's `flash()` has an active session to write
    to, which is required by AuthLogic.validate_registration / validate_login.
    """
    with app.test_request_context():
        yield


# ---------------------------------------------------------------------------
# validate_login
# ---------------------------------------------------------------------------

class TestValidateLogin:

    def test_login_succeeds_with_correct_credentials(self, app_ctx):
        """validate_login returns the User when email+password are correct."""
        from src.logic.auth_logic import AuthLogic

        user = AuthLogic.validate_login({
            'email': 'student@cwmt.test',
            'password': 'Password123!',
        })
        assert user is not None
        assert user.email == 'student@cwmt.test'

    def test_login_returns_none_for_wrong_password(self, app_ctx):
        """validate_login returns None when the password is incorrect."""
        from src.logic.auth_logic import AuthLogic

        result = AuthLogic.validate_login({
            'email': 'student@cwmt.test',
            'password': 'WrongPassword!',
        })
        assert result is None

    def test_login_returns_none_for_unknown_email(self, app_ctx):
        """validate_login returns None when the email does not exist."""
        from src.logic.auth_logic import AuthLogic

        result = AuthLogic.validate_login({
            'email': 'nobody@nowhere.invalid',
            'password': 'Password123!',
        })
        assert result is None

    def test_login_returns_none_when_email_missing(self, app_ctx):
        """validate_login returns None when the email field is omitted."""
        from src.logic.auth_logic import AuthLogic

        result = AuthLogic.validate_login({'password': 'Password123!'})
        assert result is None

    def test_login_returns_none_when_password_missing(self, app_ctx):
        """validate_login returns None when the password field is omitted."""
        from src.logic.auth_logic import AuthLogic

        result = AuthLogic.validate_login({'email': 'student@cwmt.test'})
        assert result is None

    def test_login_works_for_all_seeded_roles(self, app_ctx):
        """Each default seeded user can log in successfully."""
        from src.logic.auth_logic import AuthLogic

        emails = [
            'superuser@cwmt.test',
            'admin@cwmt.test',
            'instructor@cwmt.test',
            'student@cwmt.test',
        ]
        for email in emails:
            user = AuthLogic.validate_login({'email': email, 'password': 'Password123!'})
            assert user is not None, f'Login should succeed for {email}'
            assert user.email == email


# ---------------------------------------------------------------------------
# validate_registration
# ---------------------------------------------------------------------------

class TestValidateRegistration:

    def test_registration_creates_new_user(self, app_ctx):
        """validate_registration returns a user_id on success."""
        from src.logic.auth_logic import AuthLogic
        from src.models.user import User

        result = AuthLogic.validate_registration({
            'username': 'smoke_new_user',
            'email': 'smoke_new@example.com',
            'password': 'ValidPass99!',
            'confirm_password': 'ValidPass99!',
            'first_name': 'Smoke',
            'last_name': 'Test',
        })
        assert result is not False and result is not None

        # Verify user is findable via encrypted lookup
        user = User.get_by_email('smoke_new@example.com')
        assert user is not None
        assert user.username == 'smoke_new_user'

    def test_registration_rejects_duplicate_email(self, app_ctx):
        """validate_registration returns False when email is already registered."""
        from src.logic.auth_logic import AuthLogic

        result = AuthLogic.validate_registration({
            'username': 'unique_username_dup_email',
            'email': 'student@cwmt.test',   # already seeded
            'password': 'ValidPass99!',
            'confirm_password': 'ValidPass99!',
        })
        assert result is False

    def test_registration_rejects_duplicate_username(self, app_ctx):
        """validate_registration returns False when username is already registered."""
        from src.logic.auth_logic import AuthLogic

        result = AuthLogic.validate_registration({
            'username': 'student',          # already seeded
            'email': 'unique_email_dup@example.com',
            'password': 'ValidPass99!',
            'confirm_password': 'ValidPass99!',
        })
        assert result is False

    def test_registration_rejects_short_password(self, app_ctx):
        """validate_registration returns False when password is shorter than 6 chars."""
        from src.logic.auth_logic import AuthLogic

        result = AuthLogic.validate_registration({
            'username': 'shortpass_user',
            'email': 'shortpass@example.com',
            'password': 'abc',
            'confirm_password': 'abc',
        })
        assert result is False

    def test_registration_rejects_mismatched_passwords(self, app_ctx):
        """validate_registration returns False when passwords do not match."""
        from src.logic.auth_logic import AuthLogic

        result = AuthLogic.validate_registration({
            'username': 'mismatch_user',
            'email': 'mismatch@example.com',
            'password': 'ValidPass99!',
            'confirm_password': 'DifferentPass99!',
        })
        assert result is False

    def test_registration_rejects_missing_username(self, app_ctx):
        """validate_registration returns False when username is omitted."""
        from src.logic.auth_logic import AuthLogic

        result = AuthLogic.validate_registration({
            'email': 'nouname@example.com',
            'password': 'ValidPass99!',
            'confirm_password': 'ValidPass99!',
        })
        assert result is False

    def test_registration_rejects_missing_email(self, app_ctx):
        """validate_registration returns False when email is omitted."""
        from src.logic.auth_logic import AuthLogic

        result = AuthLogic.validate_registration({
            'username': 'noemail_user',
            'password': 'ValidPass99!',
            'confirm_password': 'ValidPass99!',
        })
        assert result is False

    def test_registered_user_can_immediately_log_in(self, app_ctx):
        """A user registered via validate_registration can log in right away."""
        from src.logic.auth_logic import AuthLogic

        reg_result = AuthLogic.validate_registration({
            'username': 'login_after_register',
            'email': 'lar@example.com',
            'password': 'ValidPass99!',
            'confirm_password': 'ValidPass99!',
        })
        assert reg_result is not False

        user = AuthLogic.validate_login({
            'email': 'lar@example.com',
            'password': 'ValidPass99!',
        })
        assert user is not None
        assert user.email == 'lar@example.com'
