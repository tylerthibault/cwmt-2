"""
Shared pytest fixtures for the CWMT test suite.

Environment variables for encryption are set here once so every test module
can import the app without triggering the startup validation error.
"""
import os
import pytest

# Set test-only encryption keys BEFORE the app is imported so the startup
# validation passes.  These are fixed values — suitable for tests only.
os.environ.setdefault('FIELD_ENCRYPTION_KEY', 'test-field-encryption-key-for-tests')
os.environ.setdefault('SEARCH_HASH_KEY', 'test-search-hash-key-for-tests')
os.environ.setdefault('SECRET_KEY', 'test-session-secret-key-for-tests')


@pytest.fixture(scope='session')
def app():
    """
    Create a Flask application configured for testing.

    Uses an in-memory SQLite database and seeds it with the default roles and
    test users so individual tests can rely on known data without extra setup.
    """
    from src import create_app
    application = create_app('testing')
    application.config['WTF_CSRF_ENABLED'] = False
    return application


@pytest.fixture(scope='session')
def client(app):
    """Return a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope='session')
def app_ctx(app):
    """Push an application context for the duration of the session."""
    ctx = app.app_context()
    ctx.push()
    yield ctx
    ctx.pop()
