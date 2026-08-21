"""
Utilitários de resiliência: retry com backoff exponencial para falhas
transitórias de rede ao falar com o Instagram.

Só reexecuta em erros claramente transitórios (rede/TLS/timeout/proxy). Erros
de credencial, 2FA, checkpoint ou "user not found" NÃO são reexecutados —
retentar não ajudaria e só desperdiçaria tentativas.
"""
from __future__ import annotations

import time
from typing import Callable, TypeVar

from . import config

T = TypeVar("T")

# Assinaturas de erro consideradas transitórias (vale a pena reexecutar).
_TRANSIENT_SIGNS = (
    "tls/ssl connection has been closed", "_ssl.c", "eof occurred",
    "connection refused", "connection reset", "connection aborted",
    "network is unreachable", "temporary failure in name resolution",
    "name or service not known", "getaddrinfo failed", "max retries exceeded",
    "read timed out", "timed out", "connecterror", "connecttimeout",
    "readtimeout", "connectionerror", "ssleoferror", "remotedisconnected",
    "connection broken", "server disconnected",
)

_TRANSIENT_TYPES = (
    "ConnectError", "ConnectTimeout", "ReadTimeout", "ConnectionError",
    "SSLError", "SSLEOFError", "RemoteProtocolError", "PoolTimeout",
    "ReadError", "WriteError", "NetworkError",
)


def is_transient_error(exc: Exception) -> bool:
    low = str(exc).lower()
    etype = type(exc).__name__
    if etype in _TRANSIENT_TYPES:
        return True
    return any(sign in low for sign in _TRANSIENT_SIGNS)


def with_retry(
    fn: Callable[[], T],
    *,
    attempts: int | None = None,
    backoff: int | None = None,
    on_retry: Callable[[int, Exception], None] | None = None,
) -> T:
    """Executa ``fn`` reexecutando em erros transitórios com backoff exponencial.

    - attempts: número total de tentativas (default: config.NETWORK_RETRY_ATTEMPTS)
    - backoff: base em segundos (default: config.NETWORK_RETRY_BACKOFF); o atraso
      cresce como backoff * 2**(tentativa-1).
    - on_retry: callback opcional (tentativa, exceção) para logar/atualizar status.
    """
    total = attempts if attempts is not None else config.NETWORK_RETRY_ATTEMPTS
    base = backoff if backoff is not None else config.NETWORK_RETRY_BACKOFF
    total = max(1, total)

    last_exc: Exception | None = None
    for attempt in range(1, total + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 - decidimos reexecutar ou propagar
            last_exc = exc
            if attempt >= total or not is_transient_error(exc):
                raise
            if on_retry:
                try:
                    on_retry(attempt, exc)
                except Exception:
                    pass
            time.sleep(base * (2 ** (attempt - 1)))
    # Inalcançável, mas mantém o tipo
    assert last_exc is not None
    raise last_exc
