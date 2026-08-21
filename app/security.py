"""Segurança: criptografia Fernet para credenciais e hashes PBKDF2."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from cryptography.fernet import Fernet, InvalidToken

from . import config

_ITERATIONS = 260_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return f"pbkdf2${_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iters, salt_hex, digest_hex = stored.split("$")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iters))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_token() -> str:
    return secrets.token_urlsafe(32)


_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key_file = config.DATA_DIR / "secret.key"
        if key_file.exists() and key_file.stat().st_size >= 32:
            key = key_file.read_bytes().strip()
        else:
            # Deriva chave permanente a partir de SECRET_KEY para nunca perder acesso em restarts do Render
            master_secret = os.getenv("SECRET_KEY", "instaflow-master-permanent-encryption-secret-key-2026-v3")
            derived = hashlib.sha256(master_secret.encode()).digest()
            key = base64.urlsafe_b64encode(derived)
            try:
                key_file.write_bytes(key)
            except Exception:
                pass
        _fernet = Fernet(key)
    return _fernet


def encrypt_secret(value: str) -> str:
    return _get_fernet().encrypt(value.encode()).decode()


def decrypt_secret(value: str) -> str:
    try:
        return _get_fernet().decrypt(value.encode()).decode()
    except (InvalidToken, AttributeError):
        return ""
