"""
Middleware de proteção contra sobrecarga de servidor e rate limiting flexível,
incluindo bloqueio anti-força-bruta no login.
"""
from __future__ import annotations

import time
from collections import defaultdict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from . import config

# Armazenamento em memória leve
_ip_requests: dict[str, list[float]] = defaultdict(list)
_ip_blocks: dict[str, float] = {}

# Tentativas de login malsucedidas: chave -> lista de timestamps
_login_attempts: dict[str, list[float]] = defaultdict(list)

MAX_REQUESTS_PER_MINUTE = 1200  # Limite alto para permitir polling suave


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("CF-Connecting-IP") or request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


def _login_key(email: str, ip: str) -> str:
    return f"{(email or '').lower()}|{ip}"


def is_login_locked(email: str, ip: str) -> bool:
    """True se houve tentativas malsucedidas demais na janela de lockout."""
    window = config.LOGIN_LOCKOUT_MINUTES * 60
    if window <= 0 or config.LOGIN_MAX_ATTEMPTS <= 0:
        return False
    key = _login_key(email, ip)
    now = time.time()
    _login_attempts[key] = [t for t in _login_attempts[key] if now - t < window]
    return len(_login_attempts[key]) >= config.LOGIN_MAX_ATTEMPTS


def record_failed_login(email: str, ip: str = "") -> None:
    """Registra uma tentativa de login malsucedida para o par e-mail/IP."""
    window = config.LOGIN_LOCKOUT_MINUTES * 60
    key = _login_key(email, ip)
    now = time.time()
    _login_attempts[key] = [t for t in _login_attempts[key] if now - t < max(window, 1)]
    _login_attempts[key].append(now)


def clear_login_attempts(email: str, ip: str = "") -> None:
    """Zera as tentativas após um login bem-sucedido."""
    _login_attempts.pop(_login_key(email, ip), None)


def reset_all_blocks() -> None:
    _ip_blocks.clear()
    _ip_requests.clear()
    _login_attempts.clear()


class AntiAbuseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Whitelist de rotas críticas e estáticas (nunca bloqueia healthcheck, assets ou tela inicial)
        if (
            path in ("/", "/api/health", "/api/auth/login", "/api/auth/register", "/api/auth/me")
            or path.startswith("/static/")
            or path.endswith((".css", ".js", ".png", ".jpg", ".svg", ".ico", ".json"))
        ):
            return await call_next(request)

        ip = get_client_ip(request)
        now = time.time()

        # Verifica bloqueios ativos (se houver)
        if ip in _ip_blocks:
            if now < _ip_blocks[ip]:
                remaining = int(_ip_blocks[ip] - now)
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": f"Muitas requisições simultâneas. Aguarde {remaining}s."
                    },
                )
            else:
                del _ip_blocks[ip]

        # Janela de requisições por minuto
        _ip_requests[ip] = [t for t in _ip_requests[ip] if now - t < 60]
        _ip_requests[ip].append(now)

        if len(_ip_requests[ip]) > MAX_REQUESTS_PER_MINUTE:
            _ip_blocks[ip] = now + 15  # Pausa curta de 15 segundos apenas contra ataques DDoS massivos
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Limite de requisições excedido. Aguarde 15 segundos."
                },
            )

        response = await call_next(request)
        return response
