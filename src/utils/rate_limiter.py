"""
Shared Flask-Limiter instance.

Import this module wherever rate limiting decorators are needed.
The limiter is initialised against the Flask app in src/__init__.py.
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(get_remote_address)
