"""Rotas de logs, histórico e estatísticas."""
from __future__ import annotations

from datetime import datetime, time, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from ..deps import get_current_user, get_db
from ..schemas import PostLogOut, StatsOut

router = APIRouter(tags=["monitoramento"])


def _log_out(l: models.PostLog) -> PostLogOut:
    return PostLogOut(
        id=l.id, account_id=l.account_id, account_name=l.account_name,
        schedule_id=l.schedule_id, media_id=l.media_id, media_name=l.media_name,
        action=l.action, status=l.status, message=l.message,
        hash_before=l.hash_before, hash_after=l.hash_after,
        instagram_pk=l.instagram_pk, duration_sec=l.duration_sec,
        run_by=l.run_by, created_at=l.created_at,
    )


@router.get("/api/logs", response_model=list[PostLogOut])
def list_logs(limit: int = Query(50, ge=1, le=500),
              account_id: int | None = None,
              user: models.User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    q = db.query(models.PostLog).filter(
        models.PostLog.user_id == user.id,
        models.PostLog.action.not_in(["maturacao_ia", "aquecimento_ia"])
    )
    if account_id:
        q = q.filter(models.PostLog.account_id == account_id)
    return [_log_out(l) for l in q.order_by(models.PostLog.id.desc()).limit(limit).all()]


@router.delete("/api/logs")
def clear_logs(user: models.User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    db.query(models.PostLog).filter(models.PostLog.user_id == user.id).delete()
    db.commit()
    return {"ok": True}


@router.get("/api/stats", response_model=StatsOut)
def stats(user: models.User = Depends(get_current_user),
          db: Session = Depends(get_db)):
    from datetime import timedelta

    accounts = db.query(models.Account).filter(models.Account.user_id == user.id).all()
    total_medias = (
        db.query(func.count(models.Media.id))
        .filter(models.Media.user_id == user.id).scalar() or 0
    )
    today_start = datetime.combine(datetime.now(timezone.utc).date(), time.min, tzinfo=timezone.utc)
    posts_today = (
        db.query(func.count(models.PostLog.id))
        .filter(models.PostLog.user_id == user.id,
                models.PostLog.action.not_in(["maturacao_ia", "aquecimento_ia"]),
                models.PostLog.created_at >= today_start,
                models.PostLog.status == "success")
        .scalar() or 0
    )
    total_posts = (
        db.query(func.count(models.PostLog.id))
        .filter(models.PostLog.user_id == user.id,
                models.PostLog.action.not_in(["maturacao_ia", "aquecimento_ia"]),
                models.PostLog.status == "success")
        .scalar() or 0
    )
    schedules_enabled = (
        db.query(func.count(models.Schedule.id))
        .filter(models.Schedule.user_id == user.id,
                models.Schedule.enabled.is_(True))
        .scalar() or 0
    )

    # Atividade real dos últimos 7 dias (0 se não houver postagens)
    daily_activity = []
    day_names = {0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"}
    today_date = datetime.now(timezone.utc).date()

    for i in range(6, -1, -1):
        day_date = today_date - timedelta(days=i)
        d_start = datetime.combine(day_date, time.min, tzinfo=timezone.utc)
        d_end = datetime.combine(day_date, time.max, tzinfo=timezone.utc)
        
        cnt = (
            db.query(func.count(models.PostLog.id))
            .filter(
                models.PostLog.user_id == user.id,
                models.PostLog.action.not_in(["maturacao_ia", "aquecimento_ia"]),
                models.PostLog.created_at >= d_start,
                models.PostLog.created_at <= d_end,
                models.PostLog.status == "success",
            )
            .scalar() or 0
        )
        label = "Hoje" if i == 0 else day_names.get(day_date.weekday(), "Dia")
        daily_activity.append({"day": label, "count": cnt, "date": day_date.isoformat()})

    upcoming = []
    for s in (db.query(models.Schedule)
              .filter(models.Schedule.user_id == user.id,
                      models.Schedule.enabled.is_(True)).all()):
        acc = db.get(models.Account, s.account_id)
        nr = app_next_run(s.id)
        if nr:
            upcoming.append({
                "schedule_id": s.id, "name": s.name,
                "account": acc.name if acc else "?",
                "next_run": nr.isoformat(),
            })
    upcoming.sort(key=lambda x: x["next_run"])
    upcoming = upcoming[:8]

    recent = (
        db.query(models.PostLog)
        .filter(models.PostLog.user_id == user.id,
                models.PostLog.action.not_in(["maturacao_ia", "aquecimento_ia"]))
        .order_by(models.PostLog.id.desc()).limit(8).all()
    )
    return StatsOut(
        total_accounts=len(accounts),
        active_accounts=sum(1 for a in accounts if a.status == "ativo"),
        total_medias=total_medias,
        posts_today=posts_today,
        total_posts=total_posts,
        schedules_enabled=schedules_enabled,
        daily_activity=daily_activity,
        upcoming=upcoming,
        recent_logs=[_log_out(l) for l in recent],
    )


def app_next_run(schedule_id: int):
    from ..main_ctx import app_ctx
    return app_ctx.sched.next_run(schedule_id)
