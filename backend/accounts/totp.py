"""
RFC 6238 Time-Based One-Time Password (TOTP) Algorithm.
Standard implementation compatible with Google Authenticator, Microsoft Authenticator, Authy, Apple Passwords.
Zero external dependencies (uses standard Python hmac, hashlib, struct, base64).
"""
import base64
import hashlib
import hmac
import secrets
import struct
import time
from typing import Optional


def generate_base32_secret(length: int = 32) -> str:
    """Generate a cryptographically secure 32-character Base32 secret key."""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
    return "".join(secrets.choice(chars) for _ in range(length))


def generate_totp(secret: str, interval: int = 30) -> str:
    """
    Generate the current 6-digit TOTP code for the given Base32 secret.
    Matches Google Authenticator at the current wall-clock second.
    """
    clean_secret = secret.strip().replace(" ", "").upper()
    # Add padding if needed
    missing_padding = len(clean_secret) % 8
    if missing_padding != 0:
        clean_secret += "=" * (8 - missing_padding)

    key = base64.b32decode(clean_secret, casefold=True)
    counter = int(time.time() // interval)
    msg = struct.pack(">Q", counter)

    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[19] & 0x0F
    binary = (struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF) % 1000000
    return f"{binary:06d}"


def verify_totp(secret: str, code: str, interval: int = 30, window: int = 1) -> bool:
    """
    Verify a 6-digit TOTP code against the secret key.
    Includes +/- 1 interval window (30-second clock skew tolerance).
    """
    clean_code = str(code).strip().replace(" ", "").replace("-", "")
    if len(clean_code) != 6 or not clean_code.isdigit():
        return False

    clean_secret = secret.strip().replace(" ", "").upper()
    missing_padding = len(clean_secret) % 8
    if missing_padding != 0:
        clean_secret += "=" * (8 - missing_padding)

    try:
        key = base64.b32decode(clean_secret, casefold=True)
    except Exception:
        return False

    counter = int(time.time() // interval)

    # Check previous interval, current interval, and next interval (clock drift resilience)
    for c in range(counter - window, counter + window + 1):
        msg = struct.pack(">Q", c)
        digest = hmac.new(key, msg, hashlib.sha1).digest()
        offset = digest[19] & 0x0F
        expected = (struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF) % 1000000
        if f"{expected:06d}" == clean_code:
            return True

    return False
