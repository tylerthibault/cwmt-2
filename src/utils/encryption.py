"""Encryption utilities for sensitive data like email passwords."""

import os
from cryptography.fernet import Fernet
from base64 import urlsafe_b64encode
import hashlib


def get_encryption_key():
    """Get or generate encryption key from environment.
    
    In production, this should come from a secure environment variable.
    For development, we generate a consistent key from the app secret.
    
    Returns:
        bytes: Fernet encryption key
    """
    # Try to get from environment first
    key = os.environ.get('ENCRYPTION_KEY')
    
    if not key:
        # Fallback: derive from app secret key (not ideal but works for development)
        secret = os.environ.get('SECRET_KEY', '5d67dfa6d956b2a6970680d9')
        # Use SHA256 to create a 32-byte key from the secret
        key_bytes = hashlib.sha256(secret.encode()).digest()
        key = urlsafe_b64encode(key_bytes).decode()
    
    return key.encode() if isinstance(key, str) else key


def encrypt_string(plaintext):
    """Encrypt a string value.
    
    Args:
        plaintext: String to encrypt
        
    Returns:
        str: Encrypted string (base64 encoded)
    """
    if not plaintext:
        return None
    
    key = get_encryption_key()
    f = Fernet(key)
    encrypted = f.encrypt(plaintext.encode())
    return encrypted.decode()


def decrypt_string(encrypted_text):
    """Decrypt an encrypted string.
    
    Args:
        encrypted_text: Encrypted string to decrypt
        
    Returns:
        str: Decrypted plaintext string
    """
    if not encrypted_text:
        return None
    
    try:
        key = get_encryption_key()
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_text.encode())
        return decrypted.decode()
    except Exception:
        # If decryption fails, return None
        return None
