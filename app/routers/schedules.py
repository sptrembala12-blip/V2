"""Rotas de agendamentos e postagens imediatas."""
from __future__ import annotations

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..deps import get_current_user, get_db
from ..main_ctx import app_ctx
from ..schemas import DirectPostIn, MultiPostIn, ScheduleCreate, ScheduleOut, ScheduleUpdate

router = APIRouter(tags=["agendamentos"])


@router.post("/api/posting/now", response_model=dict, tags=["postagem"])
def post_now_direct(body: DirectPostIn,
                    user: models.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    acc = db.get(models.Account, body.account_id)
    if not acc or acc.user_id != user.id:
        raise HTTPException(404, detail="Conta não encontrada.")
    if body.media_id:
        m = db.get(models.Media, body.media_id)
        if not m or m.user_id != user.id:
            raise HTTPException(404, detail="Mídia não encontrada.")
    app_ctx.posting.queue(
        account_id=body.account_id,
        media_id=body.media_id,
        target_type=body.target_type,
        caption=body.caption,
        usertags=body.usertags,
        run_by="direto",
        user_id=user.id,
    )
    return {"queued": True, "message": "Publicação enfileirada com sucesso!"}


@router.post("/api/posting/multi", response_model=dict, tags=["postagem"])
def post_multi_accounts(body: MultiPostIn,
                        user: models.User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    # Valida contas pertencentes ao usuário
    valid_acc_ids = []
    for acc_id in body.account_ids:
        acc = db.get(models.Account, acc_id)
        if acc and acc.user_id == user.id:
            valid_acc_ids.append(acc.id)

    if not valid_acc_ids:
        raise HTTPException(400, detail="Nenhuma conta válida selecionada.")

    if body.media_id:
        m = db.get(models.Media, body.media_id)
        if not m or m.user_id != user.id:
            raise HTTPException(404, detail="Mídia não encontrada.")

    app_ctx.posting.queue_multi(
        account_ids=valid_acc_ids,
        media_id=body.media_id,
        target_type=body.target_type,
        caption=body.caption,
        usertags=body.usertags,
        run_by="multi_conta",
        user_id=user.id,
        delay_sec=body.delay_sec,
    )
    return {
        "queued": True,
        "accounts_count": len(valid_acc_ids),
        "message": f"Distribuição iniciada para {len(valid_acc_ids)} conta(s) com variantes e hashes únicos!",
    }


def _out(db: Session, s: models.Schedule) -> ScheduleOut:
    acc = db.get(models.Account, s.account_id)
    media_name = None
    if s.media_id:
        m = db.get(models.Media, s.media_id)
        media_name = m.original_name if m else None
    times = None
    if s.mode == "times" and s.times_json:
        try:
            times = json.loads(s.times_json)
        except json.JSONDecodeError:
            times = []
    elif s.mode == "once" and s.times_json:
        times = [s.times_json]
    next_run = app_ctx.sched.next_run(s.id) if s.enabled else None
    return ScheduleOut(
        id=s.id, account_id=s.account_id,
        account_name=acc.name if acc else "(excluída)",
        name=s.name, mode=s.mode, target_type=s.target_type or "reel",
        interval_hours=s.interval_hours, times=times,
        caption=s.caption, usertags=s.usertags, jitter_min=s.jitter_min,
        media_id=s.media_id, media_name=media_name,
        enabled=s.enabled, last_run_at=s.last_run_at, next_run_at=next_run,
        created_at=s.created_at,
    )


def _get_owned(db: Session, schedule_id: int, user_id: int) -> models.Schedule:
    s = db.get(models.Schedule, schedule_id)
    if not s or s.user_id != user_id:
        raise HTTPException(404, detail="Agendamento não encontrado.")
    return s


@router.get("/api/schedules", response_model=list[ScheduleOut])
def list_schedules(user: models.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    items = (
        db.query(models.Schedule)
        .filter(models.Schedule.user_id == user.id)
        .order_by(models.Schedule.id.desc())
        .all()
    )
    return [_out(db, s) for s in items]


@router.post("/api/schedules", response_model=ScheduleOut, status_code=201)
def create_schedule(body: ScheduleCreate,
                    user: models.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    acc = db.get(models.Account, body.account_id)
    if not acc or acc.user_id != user.id:
        raise HTTPException(404, detail="Conta não encontrada.")
    if body.mode == "interval" and not body.interval_hours:
        raise HTTPException(400, detail="Informe o intervalo em horas.")
    if body.mode == "times" and not body.times:
        raise HTTPException(400, detail="Informe ao menos um horário fixo (HH:MM).")
    if body.mode == "once" and not body.scheduled_at:
        raise HTTPException(400, detail="Informe a data e hora do agendamento.")
    if body.media_id:
        m = db.get(models.Media, body.media_id)
        if not m or m.user_id != user.id:
            raise HTTPException(404, detail="Mídia não encontrada.")

    times_json = None
    if body.mode == "times":
        times_json = json.dumps(body.times)
    elif body.mode == "once":
        times_json = body.scheduled_at

    s = models.Schedule(
        user_id=user.id,
        account_id=body.account_id,
        name=body.name,
        mode=body.mode,
        target_type=body.target_type or "reel",
        interval_hours=body.interval_hours if body.mode == "interval" else None,
        times_json=times_json,
        caption=body.caption,
        usertags=body.usertags,
        jitter_min=body.jitter_min,
        media_id=body.media_id,
        enabled=body.enabled,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    app_ctx.sched.add_schedule(s)
    return _out(db, s)


@router.patch("/api/schedules/{schedule_id}", response_model=ScheduleOut)
def update_schedule(schedule_id: int, body: ScheduleUpdate,
                    user: models.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    s = _get_owned(db, schedule_id, user.id)
    if body.enabled is not None:
        s.enabled = body.enabled
    if body.caption is not None:
        s.caption = body.caption
    if body.usertags is not None:
        s.usertags = body.usertags
    if body.interval_hours is not None:
        if s.mode != "interval":
            raise HTTPException(400, detail="Este agendamento não usa intervalo em horas.")
        s.interval_hours = body.interval_hours
    if body.times is not None:
        if s.mode != "times":
            raise HTTPException(400, detail="Este agendamento não usa horários fixos.")
        s.times_json = json.dumps(body.times)
    if body.jitter_min is not None:
        s.jitter_min = body.jitter_min
    if body.media_id is not None:
        if body.media_id != 0:
            m = db.get(models.Media, body.media_id)
            if not m or m.user_id != user.id:
                raise HTTPException(404, detail="Mídia não encontrada.")
        s.media_id = body.media_id if body.media_id else None
    db.commit()
    app_ctx.sched.add_schedule(s)
    return _out(db, s)


@router.post("/api/schedules/{schedule_id}/run-now", response_model=dict)
def run_now(schedule_id: int,
            user: models.User = Depends(get_current_user),
            db: Session = Depends(get_db)):
    _get_owned(db, schedule_id, user.id)
    return app_ctx.sched.run_now(schedule_id)


@router.delete("/api/schedules/{schedule_id}")
def delete_schedule(schedule_id: int,
                    user: models.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    s = _get_owned(db, schedule_id, user.id)
    app_ctx.sched.remove_schedule(s.id)
    db.delete(s)
    db.commit()
    return {"ok": True}
