"""
InstaFlow — SaaS de automação para Instagram.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import config, rate_limiter
from .database import SessionLocal, init_db
from .instagram_service import IGManager
from .main_ctx import init as init_ctx
from .posting import PostingService
from .routers import accounts, auth, media, schedules, stats, temp_email, warmup
from .scheduler import SchedulerManager
from .warmup import WarmupManager


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    yield
    sched.shutdown()
    posting.shutdown()


app = FastAPI(
    title="InstaFlow",
    description="SaaS de automação para Instagram com fingerprints de aparelhos reais, limpeza de metadados e agendador humanizado.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(media.router)
app.include_router(schedules.router)
app.include_router(stats.router)
app.include_router(warmup.router)
app.include_router(temp_email.router)


@app.api_route("/api/health", methods=["GET", "HEAD"], tags=["sistema"])
def health():
    return {"status": "ok", "service": "InstaFlow", "version": "1.0.0"}


app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(config.STATIC_DIR / "index.html")
