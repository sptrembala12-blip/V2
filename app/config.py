"""Configuração central do InstaFlow SaaS.

Todas as opções são configuráveis por variáveis de ambiente (.env), com
defaults seguros. Nada de valores fixos escondidos no código.
"""
from __future__ import annotations

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on", "sim")


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _env_list(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


# --------------------------------------------------------------------- ffmpeg
# Configura ffmpeg se disponível via imageio_ffmpeg
try:
    import imageio_ffmpeg

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    os.environ["IMAGEIO_FFMPEG_EXE"] = str(ffmpeg_exe)
    local_bin = os.path.expanduser("~/.local/bin")
    if local_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{local_bin}:{os.environ.get('PATH', '')}"
except Exception:
    pass

# ---------------------------------------------------------------- diretórios
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
MEDIA_DIR = DATA_DIR / "media"          # mídias originais + limpas (por usuário)
VARIANTS_DIR = DATA_DIR / "variants"    # variantes re-hasheadas usadas por post
SESSIONS_DIR = DATA_DIR / "sessions"    # sessões do aiograpi por conta
STATIC_DIR = BASE_DIR / "static"

for d in (DATA_DIR, MEDIA_DIR, VARIANTS_DIR, SESSIONS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- ambiente
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()
IS_PRODUCTION = ENVIRONMENT in ("production", "prod")
DEBUG = _env_bool("DEBUG", not IS_PRODUCTION)

# ---------------------------------------------------------------- banco
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'app.db'}")

# ---------------------------------------------------------------- segurança
# SECRET_KEY é a base da criptografia de credenciais e assinatura de sessão.
# Em produção DEVE ser definida; se ausente, geramos uma efêmera (com aviso).
SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
_SECRET_IS_EPHEMERAL = False
if not SECRET_KEY:
    SECRET_KEY = secrets.token_urlsafe(48)
    _SECRET_IS_EPHEMERAL = True

# Expiração de sessão (dias). 0 = nunca expira.
SESSION_TTL_DAYS = _env_int("SESSION_TTL_DAYS", 30)

# Política de senha do usuário do SaaS
MIN_PASSWORD_LENGTH = _env_int("MIN_PASSWORD_LENGTH", 8)

# Bloqueio por tentativas de login malsucedidas
LOGIN_MAX_ATTEMPTS = _env_int("LOGIN_MAX_ATTEMPTS", 8)
LOGIN_LOCKOUT_MINUTES = _env_int("LOGIN_LOCKOUT_MINUTES", 15)

# Se o login deve criar a conta automaticamente quando o e-mail não existe.
# Padrão: desligado (comportamento seguro). Ligue só se quiser cadastro implícito.
ALLOW_LOGIN_AUTOCREATE = _env_bool("ALLOW_LOGIN_AUTOCREATE", False)

# Exigir verificação de e-mail antes de permitir login
REQUIRE_EMAIL_VERIFICATION = _env_bool("REQUIRE_EMAIL_VERIFICATION", False)

# CORS: lista de origens permitidas. Vazio = "*" (apenas fora de produção).
CORS_ORIGINS = _env_list("CORS_ORIGINS", "")

# ---------------------------------------------------------------- app / tz
APP_TZ = os.getenv("APP_TZ", "America/Sao_Paulo")
PORT = _env_int("PORT", 8000)
APP_VERSION = "2.0.0"

# ---------------------------------------------------------------- uploads
MAX_UPLOAD_MB = _env_int("MAX_UPLOAD_MB", 500)

# ---------------------------------------------------------------- automação
POSTING_WORKERS = _env_int("POSTING_WORKERS", 8)
CODE_TIMEOUT = _env_int("CODE_TIMEOUT", 180)

# Tentativas automáticas em falhas transitórias de rede ao postar/logar
NETWORK_RETRY_ATTEMPTS = _env_int("NETWORK_RETRY_ATTEMPTS", 3)
NETWORK_RETRY_BACKOFF = _env_int("NETWORK_RETRY_BACKOFF", 5)  # segundos (base)

# Limites anti-ban por conta (janela de 24h)
MAX_POSTS_PER_DAY = _env_int("MAX_POSTS_PER_DAY", 25)

# Retenção de logs de postagem (dias). 0 = manter para sempre.
LOG_RETENTION_DAYS = _env_int("LOG_RETENTION_DAYS", 90)

# Intervalo do health-check automático de contas (minutos). 0 = desligado.
ACCOUNT_HEALTHCHECK_MINUTES = _env_int("ACCOUNT_HEALTHCHECK_MINUTES", 0)


def secret_is_ephemeral() -> bool:
    """True quando SECRET_KEY não foi definida e usamos uma efêmera (inseguro)."""
    return _SECRET_IS_EPHEMERAL


def startup_warnings() -> list[str]:
    """Lista de avisos de configuração exibidos no boot."""
    warns: list[str] = []
    if IS_PRODUCTION and _SECRET_IS_EPHEMERAL:
        warns.append(
            "SECRET_KEY não definida em produção! As credenciais criptografadas e "
            "as sessões serão perdidas a cada reinício. Defina SECRET_KEY no ambiente."
        )
    if IS_PRODUCTION and not CORS_ORIGINS:
        warns.append(
            "CORS_ORIGINS não definido em produção — a API aceita qualquer origem (*). "
            "Defina CORS_ORIGINS com o domínio do seu app para maior segurança."
        )
    if IS_PRODUCTION and DATABASE_URL.startswith("sqlite"):
        warns.append(
            "Usando SQLite em produção. Para múltiplas instâncias/escala use PostgreSQL "
            "(defina DATABASE_URL)."
        )
    return warns
