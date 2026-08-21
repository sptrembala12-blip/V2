"""Contexto global da aplicação."""
from __future__ import annotations

from types import SimpleNamespace

app_ctx = SimpleNamespace(ig=None, sched=None, posting=None, warmup=None)


def init(ig_manager, scheduler, posting, warmup=None) -> None:
    app_ctx.ig = ig_manager
    app_ctx.sched = scheduler
    app_ctx.posting = posting
    app_ctx.warmup = warmup
