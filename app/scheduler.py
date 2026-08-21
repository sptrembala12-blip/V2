"""
Agendador de postagens (APScheduler) no Fuso Horário de Brasília.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from . import config, models


class SchedulerManager:
    def __init__(self, session_factory, posting) -> None:
        self.session_factory = session_factory
        self.posting = posting
        self.tz = ZoneInfo(config.APP_TZ)
        self.scheduler = BackgroundScheduler(
            timezone=self.tz,
            job_defaults={
                "coalesce": True,
                "max_instances": 1,
                "misfire_grace_time": 3600,
            },
        )

    def start(self) -> None:
        self.scheduler.start()
        self.rebuild()

    def shutdown(self) -> None:
        try:
            self.scheduler.shutdown(wait=False)
        except Exception:
            pass

    def _job_id(self, schedule_id: int, index: int = 0) -> str:
        return f"sch-{schedule_id}-{index}"

    def _triggers(self, schedule: models.Schedule) -> list[tuple[str, object]]:
        jitter_sec = max(0, schedule.jitter_min or 0) * 60
        if schedule.mode == "interval":
            hours = max(0.02, schedule.interval_hours or 24)
            return [(self._job_id(schedule.id), IntervalTrigger(hours=hours, jitter=jitter_sec, timezone=self.tz))]
        if schedule.mode == "once":
            try:
                raw_dt = schedule.times_json or ""
                dt = datetime.fromisoformat(raw_dt.replace("Z", ""))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=self.tz)
                return [(self._job_id(schedule.id), DateTrigger(run_date=dt, timezone=self.tz))]
            except Exception:
                return []

        times: list[str] = []
        try:
            times = json.loads(schedule.times_json or '["09:00"]')
        except json.JSONDecodeError:
            times = ["09:00"]
        triggers = []
        for i, t in enumerate(times):
            hh, mm = (t.strip().split(":") + ["0"])[:2]
            try:
                triggers.append((
                    self._job_id(schedule.id, i),
                    CronTrigger(hour=int(hh) % 24, minute=int(mm) % 60, jitter=jitter_sec, timezone=self.tz),
                ))
            except ValueError:
                continue
        return triggers

    def add_schedule(self, schedule: models.Schedule) -> None:
        self.remove_schedule(schedule.id)
        if not schedule.enabled:
            return
        for job_id, trigger in self._triggers(schedule):
            self.scheduler.add_job(
                self._fire, trigger=trigger, args=[schedule.id],
                id=job_id, replace_existing=True,
            )

    def remove_schedule(self, schedule_id: int) -> None:
        for job in self.scheduler.get_jobs():
            if job.id.startswith(f"sch-{schedule_id}-"):
                job.remove()

    def rebuild(self) -> None:
        for job in list(self.scheduler.get_jobs()):
            if job.id.startswith("sch-"):
                job.remove()
        with self.session_factory() as db:
            schedules = db.query(models.Schedule).filter(models.Schedule.enabled.is_(True)).all()
            for s in schedules:
                self.add_schedule(s)

    def _fire(self, schedule_id: int) -> None:
        with self.session_factory() as db:
            s = db.get(models.Schedule, schedule_id)
            if s and s.enabled:
                self.posting.queue(
                    schedule_id=schedule_id,
                    target_type=s.target_type or "reel",
                    run_by="schedule",
                )

    def run_now(self, schedule_id: int) -> dict:
        with self.session_factory() as db:
            s = db.get(models.Schedule, schedule_id)
            target_type = s.target_type if s else "reel"
        self.posting.queue(schedule_id=schedule_id, target_type=target_type, run_by="manual")
        return {"queued": True}

    def next_run(self, schedule_id: int) -> datetime | None:
        runs = [
            job.next_run_time
            for job in self.scheduler.get_jobs()
            if job.id.startswith(f"sch-{schedule_id}-") and job.next_run_time
        ]
        if not runs:
            return None
        return min(runs).astimezone(timezone.utc)
