"""Configuração central do InstaFlow SaaS."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Configura ffmpeg se disponível via imageio_ffmpeg
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    os.environ["IMAGEIO_FFMPEG_EXE"] = str(ffmpeg_exe)
    local_bin = "/home/user/.local/bin"
    if local_bin not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{local_bin}:{os.environ.get('PATH', '')}"
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MEDIA_DIR = DATA_DIR / "media"          # mídias originais + limpas (por usuário)
VARIANTS_DIR = DATA_DIR / "variants"    # variantes re-hasheadas usadas por post
SESSIONS_DIR = DATA_DIR / "sessions"    # sessões do aiograpi por conta
STATIC_DIR = BASE_DIR / "static"

for d in (DATA_DIR, MEDIA_DIR, VARIANTS_DIR, SESSIONS_DIR):
    d.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'app.db'}")
APP_TZ = os.getenv("APP_TZ", "America/Sao_Paulo")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "500"))
POSTING_WORKERS = int(os.getenv("POSTING_WORKERS", "8"))
CODE_TIMEOUT = int(os.getenv("CODE_TIMEOUT", "180"))
PORT = int(os.getenv("PORT", "8000"))
