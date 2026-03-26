"""
Unit tests for src/utils/encryption.py

Covers:
- Fernet encrypt/decrypt round-trip
- Null handling
- Legacy unencrypted value passthrough
- HMAC blind-index hashing (deterministic, normalised, key-isolated)
- Missing-key error conditions
- EncryptedType SQLAlchemy TypeDecorator
"""
import os
import pytest


# ---------------------------------------------------------------------------
# Helpers — ensure env vars are present before importing the module under test
# ---------------------------------------------------------------------------

FIELD_KEY = os.environ['FIELD_ENCRYPTION_KEY']
HASH_KEY = os.environ['SEARCH_HASH_KEY']


# ---------------------------------------------------------------------------
# encrypt_value / decrypt_value
# ---------------------------------------------------------------------------

class TestEncryptDecrypt:

    def test_round_trip(self):
        """Encrypting then decrypting returns the original plaintext."""
        from src.utils.encryption import encrypt_value, decrypt_value
        plaintext = 'student@example.com'
        assert decrypt_value(encrypt_value(plaintext)) == plaintext

    def test_ciphertext_differs_from_plaintext(self):
        """Stored value must not equal the plaintext (Fernet token prefix check)."""
        from src.utils.encryption import encrypt_value
        plaintext = 'hello@example.com'
        ciphertext = encrypt_value(plaintext)
        assert ciphertext != plaintext
        assert ciphertext.startswith('gAAAAA'), (
            f"Expected Fernet token, got: {ciphertext[:30]}")

    def test_same_input_produces_different_ciphertext(self):
        """Fernet uses a random IV so the same plaintext encrypts differently each time."""
        from src.utils.encryption import encrypt_value
        v1 = encrypt_value('same-value')
        v2 = encrypt_value('same-value')
        assert v1 != v2

    def test_null_encrypt_returns_none(self):
        from src.utils.encryption import encrypt_value
        assert encrypt_value(None) is None

    def test_null_decrypt_returns_none(self):
        from src.utils.encryption import decrypt_value
        assert decrypt_value(None) is None

    def test_legacy_plaintext_passthrough(self):
        """decrypt_value returns the raw value unchanged for non-Fernet strings."""
        from src.utils.encryption import decrypt_value
        raw = 'plaintext-legacy-value'
        assert decrypt_value(raw) == raw

    def test_missing_field_key_raises(self):
        """get_fernet() raises RuntimeError when FIELD_ENCRYPTION_KEY is absent."""
        from src.utils.encryption import get_fernet
        original = os.environ.pop('FIELD_ENCRYPTION_KEY', None)
        try:
            with pytest.raises(RuntimeError, match='FIELD_ENCRYPTION_KEY'):
                get_fernet()
        finally:
            if original:
                os.environ['FIELD_ENCRYPTION_KEY'] = original


# ---------------------------------------------------------------------------
# compute_search_hash
# ---------------------------------------------------------------------------

class TestComputeSearchHash:

    def test_deterministic(self):
        """Same input always produces the same hash."""
        from src.utils.encryption import compute_search_hash
        h1 = compute_search_hash('user@example.com')
        h2 = compute_search_hash('user@example.com')
        assert h1 == h2

    def test_normalised_case_insensitive(self):
        """Hash is normalised: upper and lower case produce identical digests."""
        from src.utils.encryption import compute_search_hash
        assert (compute_search_hash('User@Example.COM')
                == compute_search_hash('user@example.com'))

    def test_normalised_strips_whitespace(self):
        """Leading/trailing whitespace is stripped before hashing."""
        from src.utils.encryption import compute_search_hash
        assert (compute_search_hash('  user@example.com  ')
                == compute_search_hash('user@example.com'))

    def test_different_inputs_produce_different_hashes(self):
        """Distinct inputs must not collide."""
        from src.utils.encryption import compute_search_hash
        assert (compute_search_hash('alice@example.com')
                != compute_search_hash('bob@example.com'))

    def test_null_returns_none(self):
        from src.utils.encryption import compute_search_hash
        assert compute_search_hash(None) is None

    def test_missing_hash_key_raises(self):
        """compute_search_hash raises RuntimeError when SEARCH_HASH_KEY is absent."""
        from src.utils.encryption import compute_search_hash
        original = os.environ.pop('SEARCH_HASH_KEY', None)
        try:
            with pytest.raises(RuntimeError, match='SEARCH_HASH_KEY'):
                compute_search_hash('anything')
        finally:
            if original:
                os.environ['SEARCH_HASH_KEY'] = original

    def test_hash_key_is_independent_of_field_key(self):
        """The hash must NOT change when only FIELD_ENCRYPTION_KEY changes."""
        from src.utils.encryption import compute_search_hash
        h_before = compute_search_hash('test@example.com')
        original = os.environ['FIELD_ENCRYPTION_KEY']
        os.environ['FIELD_ENCRYPTION_KEY'] = 'a-totally-different-field-key'
        try:
            h_after = compute_search_hash('test@example.com')
        finally:
            os.environ['FIELD_ENCRYPTION_KEY'] = original
        assert h_before == h_after, (
            'Search hash should not depend on FIELD_ENCRYPTION_KEY')


# ---------------------------------------------------------------------------
# EncryptedType SQLAlchemy TypeDecorator
# ---------------------------------------------------------------------------

class TestEncryptedType:

    def test_process_bind_param_encrypts(self):
        from src.utils.encryption import EncryptedType
        et = EncryptedType()
        result = et.process_bind_param('hello', None)
        assert result is not None
        assert result != 'hello'
        assert result.startswith('gAAAAA')

    def test_process_result_value_decrypts(self):
        from src.utils.encryption import EncryptedType, encrypt_value
        et = EncryptedType()
        encrypted = encrypt_value('hello')
        assert et.process_result_value(encrypted, None) == 'hello'

    def test_process_bind_param_null(self):
        from src.utils.encryption import EncryptedType
        et = EncryptedType()
        assert et.process_bind_param(None, None) is None

    def test_process_result_value_null(self):
        from src.utils.encryption import EncryptedType
        et = EncryptedType()
        assert et.process_result_value(None, None) is None

    def test_round_trip_via_type_decorator(self):
        from src.utils.encryption import EncryptedType
        et = EncryptedType()
        original = 'john.doe@example.com'
        stored = et.process_bind_param(original, None)
        recovered = et.process_result_value(stored, None)
        assert recovered == original
