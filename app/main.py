"""
InstaFlow — SaaS de automação para Instagram.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import config, rate_limiter
from .database import SessionLocal, init_db
from .instagram_service import IGManager
from .main_ctx import init as init_ctx
from .posting import PostingService
from .routers import accounts, auth, media, schedules, security, stats, temp_email, warmup
from .scheduler import SchedulerManager
from .warmup import WarmupManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
# Silencia loggers de terceiros muito verbosos (APScheduler emite por job/tick).
for _noisy in ("apscheduler", "httpx", "httpcore", "aiograpi"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)
logger = logging.getLogger("instaflow")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando InstaFlow v%s (ambiente=%s)", config.APP_VERSION, config.ENVIRONMENT)
    for warn in config.startup_warnings():
        logger.warning("[CONFIG] %s", warn)

    init_db()
    ig = IGManager(SessionLocal)
    posting = PostingService(SessionLocal, ig)
    sched = SchedulerManager(SessionLocal, posting)
    posting.scheduler = sched
    warmup_mgr = WarmupManager(SessionLocal, ig)
    init_ctx(ig, sched, posting, warmup_mgr)
    sched.start()
    app.state.ig = ig
    app.state.posting = posting
    app.state.sched = sched
    app.state.warmup = warmup_mgr
    logger.info("InstaFlow pronto na porta %s", config.PORT)
    yield
    logger.info("Encerrando InstaFlow...")
    sched.shutdown()
    posting.shutdown()


app = FastAPI(
    title="InstaFlow",
    description="SaaS de automação para Instagram com fingerprints de aparelhos reais, limpeza de metadados e agendador humanizado.",
    version=config.APP_VERSION,
    lifespan=lifespan,
    docs_url=None if config.IS_PRODUCTION else "/docs",
    redoc_url=None if config.IS_PRODUCTION else "/redoc",
)

# CORS configurável: em produção use CORS_ORIGINS; fora dela libera tudo.
_cors_origins = config.CORS_ORIGINS or ["*"]
_allow_credentials = _cors_origins != ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Proteção anti-abuso / rate limiting (estava importado mas não era aplicado).
app.add_middleware(rate_limiter.AntiAbuseMiddleware)


@app.exception_handler(Exception)
async def _unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Erro não tratado em %s %s", request.method, request.url.path)
    detail = "Erro interno do servidor." if config.IS_PRODUCTION else f"{type(exc).__name__}: {exc}"
    return JSONResponse(status_code=500, content={"detail": detail})


@app.exception_handler(RequestValidationError)
async def _validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": "Dados inválidos.", "errors": exc.errors()})


app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(media.router)
app.include_router(schedules.router)
app.include_router(stats.router)
app.include_router(warmup.router)
app.include_router(temp_email.router)
app.include_router(security.router)


@app.api_route("/api/health", methods=["GET", "HEAD"], tags=["sistema"])
def health():
    """Health-check detalhado para monitoramento/uptime e balanceadores."""
    db_ok = True
    try:
        from sqlalchemy import text
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    is_postgres = "postgres" in config.DATABASE_URL.lower()
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "InstaFlow",
        "version": config.APP_VERSION,
        "environment": config.ENVIRONMENT,
        "database": "postgresql" if is_postgres else "sqlite",
        "database_ok": db_ok,
    }


app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(config.STATIC_DIR / "index.html")
