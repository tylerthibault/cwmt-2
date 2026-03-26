"""
Smoke tests for application startup security validation.

The application must refuse to start when mandatory encryption environment
variables are absent, and must start correctly when they are present.
"""
import os
import pytest


class TestStartupValidation:
    """create_app() must validate security env vars before any DB interaction."""

    def test_app_refuses_to_start_without_field_encryption_key(self):
        """RuntimeError is raised when FIELD_ENCRYPTION_KEY is missing."""
        original = os.environ.pop('FIELD_ENCRYPTION_KEY', None)
        try:
            from src import create_app
            with pytest.raises(RuntimeError, match='FIELD_ENCRYPTION_KEY'):
                create_app('testing')
        finally:
            if original:
                os.environ['FIELD_ENCRYPTION_KEY'] = original

    def test_app_refuses_to_start_without_search_hash_key(self):
        """RuntimeError is raised when SEARCH_HASH_KEY is missing."""
        original = os.environ.pop('SEARCH_HASH_KEY', None)
        try:
            from src import create_app
            with pytest.raises(RuntimeError, match='SEARCH_HASH_KEY'):
                create_app('testing')
        finally:
            if original:
                os.environ['SEARCH_HASH_KEY'] = original

    def test_app_refuses_to_start_when_both_keys_missing(self):
        """RuntimeError names both missing keys when neither is set."""
        orig_field = os.environ.pop('FIELD_ENCRYPTION_KEY', None)
        orig_hash = os.environ.pop('SEARCH_HASH_KEY', None)
        try:
            from src import create_app
            with pytest.raises(RuntimeError) as exc_info:
                create_app('testing')
            message = str(exc_info.value)
            assert 'FIELD_ENCRYPTION_KEY' in message
            assert 'SEARCH_HASH_KEY' in message
        finally:
            if orig_field:
                os.environ['FIELD_ENCRYPTION_KEY'] = orig_field
            if orig_hash:
                os.environ['SEARCH_HASH_KEY'] = orig_hash

    def test_app_starts_successfully_with_both_keys_present(self):
        """create_app() succeeds and returns a Flask application when both keys are set."""
        from flask import Flask
        from src import create_app
        application = create_app('testing')
        assert isinstance(application, Flask)


class TestRateLimiterConfiguration:
    """Rate-limiting must be initialised and attached to the Flask app."""

    def test_limiter_attached_to_app(self, app):
        """The Flask-Limiter extension must be registered on the app."""
        # Flask-Limiter registers itself in app.extensions
        assert any('limiter' in str(k).lower() for k in app.extensions), (
            'Flask-Limiter is not registered in app.extensions')

    def test_default_ratelimit_set_in_testing_config(self, app):
        """RATELIMIT_DEFAULT must be configured."""
        assert app.config.get('RATELIMIT_DEFAULT') is not None

    def test_login_endpoint_responds_to_get(self, client):
        """GET /auth/login must return a non-500 response (rate limiter not blocking)."""
        resp = client.get('/auth/login')
        assert resp.status_code < 500

    def test_register_endpoint_responds_to_get(self, client):
        """GET /auth/register must return a non-500 response."""
        resp = client.get('/auth/register')
        assert resp.status_code < 500
