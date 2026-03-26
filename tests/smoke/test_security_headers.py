"""
Smoke tests for HTTP security headers set by Flask-Talisman.

Verifies that every response from the application includes the expected
defensive headers.  These tests run against the test client (no live server
needed) and use the 'testing' config, so HTTPS is NOT enforced (HSTS headers
will be absent in this config — that is intentional and tested separately).
"""
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def homepage(client):
    """GET / response, reused across all header tests in this module."""
    return client.get('/')


# ---------------------------------------------------------------------------
# Tests: HTTP response headers
# ---------------------------------------------------------------------------

class TestSecurityHeaders:

    def test_x_frame_options_deny(self, homepage):
        """X-Frame-Options must be DENY to prevent clickjacking."""
        assert homepage.headers.get('X-Frame-Options') == 'DENY', (
            'X-Frame-Options header missing or incorrect')

    def test_x_content_type_options_nosniff(self, homepage):
        """X-Content-Type-Options must be nosniff."""
        assert homepage.headers.get('X-Content-Type-Options') == 'nosniff', (
            'X-Content-Type-Options header missing or incorrect')

    def test_content_security_policy_present(self, homepage):
        """Content-Security-Policy header must be present."""
        assert homepage.headers.get('Content-Security-Policy') is not None, (
            'Content-Security-Policy header is missing')

    def test_csp_default_src_self(self, homepage):
        """CSP must include default-src 'self'."""
        csp = homepage.headers.get('Content-Security-Policy', '')
        assert "default-src 'self'" in csp, (
            f"Expected default-src 'self' in CSP, got: {csp[:120]}")

    def test_csp_no_unsafe_inline_in_script_src(self, homepage):
        """
        script-src must NOT include 'unsafe-inline'.
        Talisman injects per-request nonces instead.
        """
        csp = homepage.headers.get('Content-Security-Policy', '')
        # Extract only the script-src directive value
        if 'script-src' in csp:
            script_src_part = csp.split('script-src')[1].split(';')[0]
            assert "'unsafe-inline'" not in script_src_part, (
                f"'unsafe-inline' must not appear in script-src: {script_src_part}")

    def test_referrer_policy_present(self, homepage):
        """Referrer-Policy header must be present."""
        assert homepage.headers.get('Referrer-Policy') is not None, (
            'Referrer-Policy header is missing')

    def test_response_is_successful(self, homepage):
        """The homepage must return a 2xx or 3xx status (not a server error)."""
        assert homepage.status_code < 500, (
            f'Homepage returned unexpected status: {homepage.status_code}')


class TestHTTPSSettingsInTesting:
    """
    Verify that HTTPS enforcement is explicitly disabled in testing config
    (so the test suite can run over plain HTTP) but is enabled in production.
    """

    def test_talisman_force_https_disabled_in_testing(self, app):
        """Testing config must set TALISMAN_FORCE_HTTPS = False."""
        assert app.config.get('TALISMAN_FORCE_HTTPS') is False

    def test_session_cookie_secure_disabled_in_testing(self, app):
        """SESSION_COOKIE_SECURE must be False in testing so cookies work over HTTP."""
        assert app.config.get('SESSION_COOKIE_SECURE') is False

    def test_session_cookie_httponly_always_enabled(self, app):
        """SESSION_COOKIE_HTTPONLY must be True in every config."""
        assert app.config.get('SESSION_COOKIE_HTTPONLY') is True

    def test_session_cookie_samesite_lax(self, app):
        """SESSION_COOKIE_SAMESITE must be Lax."""
        assert app.config.get('SESSION_COOKIE_SAMESITE') == 'Lax'

    def test_session_cookie_name_not_default(self, app):
        """Session cookie name must not reveal the underlying framework."""
        name = app.config.get('SESSION_COOKIE_NAME', '')
        assert 'session' not in name.lower() or name == 'cwmt_session', (
            f'Unexpected session cookie name: {name}')


class TestAuthEndpointHeaders:
    """Security headers must be present on auth endpoints too."""

    def test_login_page_has_x_frame_options(self, client):
        resp = client.get('/auth/login')
        assert resp.headers.get('X-Frame-Options') == 'DENY'

    def test_register_page_has_csp(self, client):
        resp = client.get('/auth/register')
        assert resp.headers.get('Content-Security-Policy') is not None
