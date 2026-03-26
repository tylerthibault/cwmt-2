"""
Encryption utilities for PII data protection.

Provides:
- Fernet-based EncryptedType for SQLAlchemy columns (data at rest)
- HMAC-SHA256 blind-index helper for encrypted-but-searchable fields
"""
import os
import hmac
import hashlib
import base64

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import types


def _derive_fernet_key(raw_key: str) -> bytes:
    """Derive a valid 32-byte Fernet key from an arbitrary string via SHA-256."""
    digest = hashlib.sha256(raw_key.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def get_fernet() -> Fernet:
    """
    Return a Fernet instance using the FIELD_ENCRYPTION_KEY env variable.
    Raises RuntimeError if the key is not configured.
    """
    raw_key = os.environ.get('FIELD_ENCRYPTION_KEY')
    if not raw_key:
        raise RuntimeError(
            "FIELD_ENCRYPTION_KEY environment variable is not set. "
            "Set it to a strong random secret before starting the application."
        )
    return Fernet(_derive_fernet_key(raw_key))


def encrypt_value(value: str) -> str:
    """Encrypt a plaintext string value using Fernet symmetric encryption."""
    if value is None:
        return None
    return get_fernet().encrypt(str(value).encode()).decode()


def decrypt_value(value: str) -> str:
    """
    Decrypt a Fernet-encrypted string value.
    Returns the raw value unchanged if it is not a valid Fernet token so that
    legacy unencrypted rows (present before encryption was added) can still be
    read without crashing.  All other errors are raised normally.
    """
    if value is None:
        return None
    try:
        return get_fernet().decrypt(value.encode()).decode()
    except InvalidToken:
        # Legacy unencrypted value — return as-is
        return value


def compute_search_hash(value: str) -> str:
    """
    Compute an HMAC-SHA256 blind index for a plaintext value.

    This enables exact-match queries on encrypted columns without exposing the
    plaintext value in the database.  The SEARCH_HASH_KEY must remain stable —
    changing it invalidates all stored hashes.

    A dedicated SEARCH_HASH_KEY (separate from FIELD_ENCRYPTION_KEY) is
    required so that the two keys remain cryptographically independent.
    """
    if value is None:
        return None
    secret = os.environ.get('SEARCH_HASH_KEY')
    if not secret:
        raise RuntimeError(
            "SEARCH_HASH_KEY environment variable is not set. "
            "It must be independent of FIELD_ENCRYPTION_KEY."
        )
    return hmac.new(
        secret.encode(),
        str(value).lower().strip().encode(),
        hashlib.sha256
    ).hexdigest()


class EncryptedType(types.TypeDecorator):
    """
    SQLAlchemy TypeDecorator that transparently encrypts/decrypts string values
    using Fernet symmetric encryption.

    Usage::

        class User(db.Model):
            email = db.Column(EncryptedType(), nullable=False)
    """

    impl = types.Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Encrypt before storing to database."""
        if value is None:
            return None
        return encrypt_value(str(value))

    def process_result_value(self, value, dialect):
        """Decrypt after loading from database."""
        if value is None:
            return None
        return decrypt_value(value)
