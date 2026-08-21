"""Segurança: criptografia Fernet para credenciais, hashes fortes de senha e
validação de política de senha.

- Senhas de usuário: scrypt (forte, resistente a GPU) com verificação
  retrocompatível para hashes PBKDF2 antigos.
- Credenciais do Instagram: criptografia Fernet com chave derivada de SECRET_KEY.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets

from cryptography.fernet import Fernet, InvalidToken

from . import config

# PBKDF2 (legado — mantido só para verificar hashes antigos)
_PBKDF2_ITERATIONS = 260_000

# scrypt (padrão atual)
_SCRYPT_N = 2 ** 15   # fator de custo de CPU/memória
_SCRYPT_R = 8
_SCRYPT_P = 1
_SCRYPT_DKLEN = 32
# Memória máxima permitida ao scrypt (~128*N*r bytes + folga)
_SCRYPT_MAXMEM = 128 * _SCRYPT_N * _SCRYPT_R * 2 + 1024 * 1024


# --------------------------------------------------------------- senhas SaaS
def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_SCRYPT_DKLEN,
        maxmem=_SCRYPT_MAXMEM,
    )
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    if not stored:
        return False
    try:
        scheme = stored.split("$", 1)[0]
        if scheme == "scrypt":
            _, n, r, p, salt_hex, digest_hex = stored.split("$")
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
            actual = hashlib.scrypt(
                password.encode(), salt=salt,
                n=int(n), r=int(r), p=int(p), dklen=len(expected), maxmem=_SCRYPT_MAXMEM,
            )
            return hmac.compare_digest(actual, expected)
        if scheme == "pbkdf2":
            _, iters, salt_hex, digest_hex = stored.split("$")
            salt = bytes.fromhex(salt_hex)
            expected = bytes.fromhex(digest_hex)
            actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iters))
            return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False
    return False


def needs_rehash(stored: str) -> bool:
    """True se o hash usa esquema antigo (PBKDF2) e deve ser reescrito no login."""
    return bool(stored) and not stored.startswith("scrypt$")


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Valida a política mínima de senha. Retorna (ok, mensagem)."""
    if password is None:
        return False, "Informe uma senha."
    if len(password) < config.MIN_PASSWORD_LENGTH:
        return False, f"A senha deve ter no mínimo {config.MIN_PASSWORD_LENGTH} caracteres."
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    if not (has_letter and has_digit):
        return False, "A senha deve conter ao menos uma letra e um número."
    return True, "ok"


# --------------------------------------------------------------- tokens
def create_token() -> str:
    return secrets.token_urlsafe(32)


# --------------------------------------------------------------- Fernet
_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        key_file = config.DATA_DIR / "secret.key"
        # Prioridade 1 (retrocompatível): chave já existente em disco. Instalações
        # antigas criptografaram credenciais com esta chave — nunca a ignoramos.
        if key_file.exists() and key_file.stat().st_size >= 32:
            key = key_file.read_bytes().strip()
        # Prioridade 2: deriva de SECRET_KEY (permanente entre deploys) e persiste.
        else:
            derived = hashlib.sha256(config.SECRET_KEY.encode()).digest()
            key = base64.urlsafe_b64encode(derived)
            try:
                key_file.write_bytes(key)
            except Exception:
                pass
        _fernet = Fernet(key)
    return _fernet


def hash_recovery_code(code: str) -> str:
    """Hash simples e determinístico para códigos de recuperação 2FA."""
    return hashlib.sha256((code + config.SECRET_KEY).encode()).hexdigest()


def encrypt_secret(value: str) -> str:
    return _get_fernet().encrypt(value.encode()).decode()


def decrypt_secret(value: str) -> str:
    try:
        return _get_fernet().decrypt(value.encode()).decode()
    except (InvalidToken, AttributeError):
        return ""
