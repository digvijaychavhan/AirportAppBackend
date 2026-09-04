"""
Security & Cryptography Utilities
Provides secure password hashing (PBKDF2-HMAC-SHA256 with salt), constant-time verification,
cryptographically secure token generation, and OTP generation.
"""

import os
import hmac
import hashlib
import secrets
import string
from typing import Optional

# OWASP Recommended Iteration Count for PBKDF2-HMAC-SHA256
PBKDF2_ITERATIONS = 600_000
SALT_SIZE = 16


def hash_password(password: str) -> str:
    """
    Hashes a plaintext password using PBKDF2-HMAC-SHA256 with a unique 16-byte salt.
    Format: pbkdf2_sha256$<iterations>$<hex_salt>$<hex_hash>
    """
    if not password:
        raise ValueError("Password cannot be empty")
    salt = secrets.token_bytes(SALT_SIZE)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        PBKDF2_ITERATIONS
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a stored hashed password in constant time.
    Also handles legacy plaintext comparison during migration.
    """
    if not plain_password or not hashed_password:
        return False

    # Check for PBKDF2-SHA256 format
    if hashed_password.startswith("pbkdf2_sha256$"):
        try:
            parts = hashed_password.split("$")
            if len(parts) != 4:
                return False
            _, iterations_str, salt_hex, expected_hash_hex = parts
            iterations = int(iterations_str)
            salt = bytes.fromhex(salt_hex)
            computed_key = hashlib.pbkdf2_hmac(
                'sha256',
                plain_password.encode('utf-8'),
                salt,
                iterations
            )
            return hmac.compare_digest(computed_key.hex(), expected_hash_hex)
        except Exception:
            return False

    # Fallback to constant-time comparison for legacy plaintext passwords
    return hmac.compare_digest(plain_password, hashed_password)


def generate_secure_token(nbytes: int = 32) -> str:
    """
    Generates a URL-safe random string for sessions, invitations, or API tokens.
    """
    return secrets.token_urlsafe(nbytes)


def generate_numeric_otp(length: int = 6) -> str:
    """
    Generates a cryptographically secure numeric OTP of given length.
    """
    return "".join(secrets.choice(string.digits) for _ in range(length))
