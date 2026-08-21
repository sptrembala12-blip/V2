"""Rotas para aquecimento e maturação de contas por nicho."""
from __future__ import annotations

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..deps import get_current_user, get_db
from ..main_ctx import app_ctx
from ..schemas import WarmupSessionOut, WarmupStartIn

router = APIRouter(prefix="/api/warmup", tags=["aquecimento"])


def _out(s: models.WarmupSession) -> WarmupSessionOut:
    logs = []
    if s.logs_json:
        try:
            logs = json.loads(s.logs_json)
        except Exception:
            logs = []
    return WarmupSessionOut(
        id=s.id,
        account_id=s.account_id,
        account_name=s.account_name,
        account_age=getattr(s, "account_age", "hoje") or "hoje",
        target_country=getattr(s, "target_country", "BR") or "BR",
        current_day=getattr(s, "current_day", 1) or 1,
        total_days=getattr(s, "total_days", 3) or 3,
        cycles_completed=getattr(s, "cycles_completed", 0) or 0,
        next_cycle_at=getattr(s, "next_cycle_at", None),
        niche=s.niche,
        intensity=s.intensity,
        watch_reels=s.watch_reels,
        like_posts=s.like_posts,
        follow_profiles=s.follow_profiles,
        explore_tab=s.explore_tab,
        status=s.status,
        status_detail=s.status_detail,
        views_done=s.views_done,
        likes_done=s.likes_done,
        logs=logs,
        created_at=s.created_at,
        finished_at=s.finished_at,
    )


@router.get("/sessions", response_model=list[WarmupSessionOut])
def list_sessions(user: models.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    items = (
        db.query(models.WarmupSession)
        .filter(models.WarmupSession.user_id == user.id)
        .order_by(models.WarmupSession.id.desc())
        .all()
    )
    # Garante estritamente 1 único card por conta (sem duplicatas)
    seen_accounts = set()
    unique_items = []
    has_changes = False
    for s in items:
        if s.account_id not in seen_accounts:
            # Se no banco está 'em_andamento', mas o thread não está ativo na memória
            if s.status == "em_andamento" and not app_ctx.warmup.is_running(s.account_id):
                s.status = "interrompido"
                s.status_detail = "[IA] Maturação pausada."
                has_changes = True
            seen_accounts.add(s.account_id)
            unique_items.append(s)

    if has_changes:
        try:
            db.commit()
        except Exception:
            pass

    return [_out(s) for s in unique_items]


@router.get("/sessions/{session_id}", response_model=WarmupSessionOut)
def get_session(session_id: int,
                user: models.User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    s = db.get(models.WarmupSession, session_id)
    if not s or s.user_id != user.id:
        raise HTTPException(404, detail="Sessão não encontrada.")
    return _out(s)


@router.post("/start", response_model=dict)
def start_warmup(body: WarmupStartIn,
                 user: models.User = Depends(get_current_user)):
    try:
        session_id = app_ctx.warmup.start_warmup(
            user_id=user.id,
            account_id=body.account_id,
            account_age=body.account_age,
            target_country=body.target_country or "BR",
            total_days=body.total_days or 3,
            intensity=body.intensity,
            niche=body.niche or "Automático com IA",
            watch_reels=body.watch_reels,
            like_posts=body.like_posts,
            follow_profiles=body.follow_profiles,
            explore_tab=body.explore_tab,
        )
        return {"session_id": session_id, "message": "Maturação iniciada com sucesso!"}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))


@router.post("/stop/{account_id}", response_model=dict)
def stop_warmup(account_id: int,
                user: models.User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    acc = db.get(models.Account, account_id)
    if not acc or acc.user_id != user.id:
        raise HTTPException(404, detail="Conta não encontrada.")
    stopped = app_ctx.warmup.stop(account_id)
    return {"stopped": stopped, "message": "Sinal de parada enviado." if stopped else "Nenhum aquecimento ativo para esta conta."}
