"""
Pipeline de postagem multi-formato (Reels, Feed e Stories) com rehash por postagem.
"""
from __future__ import annotations

import os
import random
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from . import config, media, models
from .instagram_service import IGManager, map_login_error


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PostingService:
    def __init__(self, session_factory, ig_manager: IGManager) -> None:
        self.session_factory = session_factory
        self.ig = ig_manager
        self.scheduler = None
        self.executor = ThreadPoolExecutor(max_workers=config.POSTING_WORKERS, thread_name_prefix="post")

    def queue(self, *, schedule_id: int | None = None, account_id: int | None = None,
              media_id: int | None = None, target_type: str = "reel",
              caption: str | None = None, usertags: str | None = None,
              run_by: str = "manual", user_id: int | None = None) -> dict:
        self.executor.submit(
            self._run, schedule_id=schedule_id, account_id=account_id,
            media_id=media_id, target_type=target_type, caption=caption,
            usertags=usertags, run_by=run_by, user_id=user_id,
        )
        return {"queued": True}

    def queue_multi(self, *, account_ids: list[int], media_id: int | None = None,
                    target_type: str = "reel", caption: str | None = None,
                    usertags: str | None = None, run_by: str = "multi_account",
                    user_id: int | None = None, delay_sec: int = 15) -> dict:
        """Dispara a mesma mídia para múltiplas contas aplicando variantes e hashes criptográficos exclusivos por conta."""
        def _multi_job():
            for idx, acc_id in enumerate(account_ids):
                self._run(
                    schedule_id=None,
                    account_id=acc_id,
                    media_id=media_id,
                    target_type=target_type,
                    caption=caption,
                    usertags=usertags,
                    run_by=run_by,
                    user_id=user_id,
                )
                if idx < len(account_ids) - 1:
                    time.sleep(random.uniform(max(3, delay_sec - 4), max(6, delay_sec + 4)))

        self.executor.submit(_multi_job)
        return {"queued": True, "accounts_count": len(account_ids)}

    def shutdown(self) -> None:
        self.executor.shutdown(wait=False, cancel_futures=False)

    def _run(self, *, schedule_id, account_id, media_id, target_type, caption, usertags, run_by, user_id) -> None:
        with self.session_factory() as db:
            try:
                account, schedule = self._resolve_targets(db, schedule_id, account_id, user_id)
                if account is None:
                    return
                with self.ig.lock(account.id):
                    self._execute(db, account, schedule, media_id, target_type, caption, usertags, run_by)
            except Exception as e:
                self._log(db, account_id=account_id, schedule_id=schedule_id,
                          media_id=media_id, account_name="?",
                          action="erro_interno", status="error",
                          message=f"Erro inesperado: {e}", run_by=run_by)

    def _resolve_targets(self, db, schedule_id, account_id, user_id):
        account = schedule = None
        if schedule_id:
            schedule = db.get(models.Schedule, schedule_id)
            if schedule and (user_id is None or schedule.user_id == user_id):
                account = db.get(models.Account, schedule.account_id)
        if account is None and account_id:
            account = db.get(models.Account, account_id)
            if account and user_id is not None and account.user_id != user_id:
                account = None
        if account is None:
            self._log(db, account_id=account_id, schedule_id=schedule_id,
                      account_name="?", action="erro_interno", status="error",
                      message="Conta não encontrada ou sem permissão.", run_by="manual")
        return account, schedule

    def _execute(self, db, account, schedule, media_id, target_type, caption, usertags, run_by) -> None:
        t0 = time.time()

        post_target = target_type or (schedule.target_type if schedule else "reel")

        # 1) Escolha da mídia com verificação em disco e rotação inteligente (menos usadas primeiro)
        m = None
        if media_id:
            cand = db.get(models.Media, media_id)
            if cand and (os.path.exists(cand.active_path) or os.path.exists(cand.original_path)):
                m = cand
        elif schedule and schedule.media_id:
            cand = db.get(models.Media, schedule.media_id)
            if cand and (os.path.exists(cand.active_path) or os.path.exists(cand.original_path)):
                m = cand

        if m is None:
            expected_kind = "video" if post_target == "reel" else ("photo" if post_target == "feed" else None)
            
            # 1. Busca mídias vinculadas à conta que AINDA NÃO FORAM ENVIADAS (times_used == 0)
            q_acc = db.query(models.Media).filter(
                models.Media.user_id == account.user_id,
                models.Media.account_id == account.id,
                (models.Media.times_used == 0) | (models.Media.times_used.is_(None))
            )
            if expected_kind:
                q_acc = q_acc.filter(models.Media.kind == expected_kind)
            pending_medias = q_acc.order_by(models.Media.id.asc()).all()

            # 2. Se não houver exclusivas pendentes, busca mídias gerais pendentes (times_used == 0)
            if not pending_medias:
                q_gen = db.query(models.Media).filter(
                    models.Media.user_id == account.user_id,
                    (models.Media.times_used == 0) | (models.Media.times_used.is_(None))
                )
                if expected_kind:
                    q_gen = q_gen.filter(models.Media.kind == expected_kind)
                pending_medias = q_gen.order_by(models.Media.id.asc()).all()

            # Procura a primeira mídia pendente existente no disco
            for cand in pending_medias:
                if os.path.exists(cand.active_path) or os.path.exists(cand.original_path):
                    m = cand
                    break

            # Se NÃO houver nenhuma mídia pendente (todas já foram enviadas):
            if m is None:
                # Verifica se existem mídias no total
                total_medias = db.query(models.Media).filter(models.Media.user_id == account.user_id).count()
                if total_medias == 0:
                    self._log(db, account, schedule, None, "erro_interno", "error",
                              "Nenhuma mídia encontrada na biblioteca. Envie fotos ou vídeos na aba Mídias.",
                              run_by=run_by)
                    return

                # TODAS as mídias já foram postadas! Finaliza a fila e conclui o agendamento
                if schedule:
                    schedule.enabled = False
                    schedule.last_run_at = _now()
                    db.commit()
                    if hasattr(self, "scheduler") and self.scheduler:
                        try:
                            self.scheduler.remove_schedule(schedule.id)
                        except Exception:
                            pass

                self._log(
                    db, account=account, schedule=schedule, media_item=None,
                    action=f"fila_{post_target}_concluida", status="success",
                    message="Todos os vídeos/fotos da lista já foram enviados. Fila finalizada com sucesso (sem repetição).",
                    run_by=run_by
                )
                return

        source_path = m.active_path if os.path.exists(m.active_path) else m.original_path

        # 2) Cria variante com hash único
        variant_path = config.VARIANTS_DIR / f"{account.id}_{int(t0)}_{uuid.uuid4().hex[:6]}{m.ext}"
        try:
            media.make_variant(source_path, variant_path, m.ext)
        except Exception as e:
            self._log(db, account, schedule, m, "erro_interno", "error",
                      f"Falha ao gerar variante re-hasheada: {e}", run_by=run_by)
            return
        hash_before = m.active_sha256 or media.sha256_file(source_path)
        hash_after = media.sha256_file(variant_path)

        caption = (caption if caption is not None else
                   (schedule.caption if schedule else "")) or ""
        tags_raw = (usertags if usertags is not None else
                    (schedule.usertags if schedule else None))

        # 3) Pausa humanizada
        if account.humanize:
            time.sleep(random.uniform(2.0, 5.0))
        warmup_actions: list[str] = []

        # 4) Publicação
        if account.simulate:
            time.sleep(random.uniform(1.0, 3.0))
            pk = f"SIM-{uuid.uuid4().hex[:10]}"
            action = f"post_{post_target}_simulado"
            message = f"[SIMULAÇÃO] Post de {m.kind} ({post_target}) publicado (modo teste)"
            status = "success"
        else:
            try:
                cl = self.ig.ensure_logged_in(account)
                if account.warmup and account.humanize:
                    warmup_actions = self.ig.warmup(account, cl)
                    time.sleep(random.uniform(max(1, account.delay_min), max(2, account.delay_max)))

                parsed_usertags = []
                if tags_raw:
                    from aiograpi.types import Usertag, UserShort
                    raw_names = [u.strip().lstrip("@") for u in tags_raw.split(",") if u.strip().lstrip("@")]
                    for i, uname in enumerate(raw_names[:8]):
                        try:
                            uid = cl.user_id_from_username(uname)
                            if uid:
                                parsed_usertags.append(Usertag(
                                    user=UserShort(pk=str(uid), username=uname),
                                    x=round(0.3 + (i * 0.15) % 0.5, 2),
                                    y=round(0.4 + (i * 0.1) % 0.4, 2),
                                ))
                        except Exception:
                            pass

                if post_target == "story":
                    if m.kind == "photo":
                        result = cl.photo_upload_to_story(variant_path)
                    else:
                        result = cl.video_upload_to_story(variant_path)
                    action = "post_story"
                elif post_target == "feed" and m.kind == "photo":
                    result = cl.photo_upload(variant_path, caption, usertags=parsed_usertags)
                    action = "post_feed_photo"
                elif post_target == "trial_reel":
                    thumb_path = config.VARIANTS_DIR / f"{account.id}_{int(t0)}_thumb.jpg"
                    media.extract_video_thumbnail(variant_path, thumb_path)
                    try:
                        result = cl.clip_upload(variant_path, caption or " ", thumbnail=thumb_path, usertags=parsed_usertags, extra_data={"is_trial_reel": True})
                    except Exception:
                        result = cl.clip_upload(variant_path, caption or " ", thumbnail=thumb_path, usertags=parsed_usertags)
                    finally:
                        thumb_path.unlink(missing_ok=True)
                    action = "post_trial_reel"
                else:
                    # Reel de vídeo em qualidade máxima
                    thumb_path = config.VARIANTS_DIR / f"{account.id}_{int(t0)}_thumb.jpg"
                    media.extract_video_thumbnail(variant_path, thumb_path)
                    try:
                        result = cl.clip_upload(variant_path, caption or " ", thumbnail=thumb_path, usertags=parsed_usertags)
                    finally:
                        thumb_path.unlink(missing_ok=True)
                    action = "post_reel"

                pk = str(getattr(result, "pk", "") or getattr(result, "id", "")) or "?"
                message = f"Publicado no Instagram com sucesso (pk={pk})"
                status = "success"
            except Exception as e:
                estatus, edetail = map_login_error(e)
                self.ig.update_status(account.id, estatus, edetail)
                self._log(db, account, schedule, m, f"post_{post_target}", "error",
                          f"Falha ao publicar: {edetail}", run_by=run_by,
                          hash_before=hash_before, hash_after=hash_after,
                          duration=time.time() - t0)
                return

        # 5) Registro e atualização
        m.times_used = (m.times_used or 0) + 1
        if schedule:
            schedule.last_run_at = _now()
        db.commit()

        human_note = f" | aquecimento: {', '.join(warmup_actions)}" if warmup_actions else ""
        self._log(db, account, schedule, m, action, status,
                  message + human_note, run_by=run_by,
                  hash_before=hash_before, hash_after=hash_after,
                  instagram_pk=pk, duration=time.time() - t0)

    def _log(self, db, account=None, schedule=None, media_item=None,
             action: str = "?", status: str = "success", message: str = "",
             run_by: str = "manual", hash_before: str | None = None,
             hash_after: str | None = None, instagram_pk: str | None = None,
             duration: float = 0.0) -> None:
        try:
            db.add(models.PostLog(
                user_id=(getattr(account, "user_id", None) or 0),
                account_id=getattr(account, "id", None),
                account_name=getattr(account, "name", "?") if account else "?",
                schedule_id=getattr(schedule, "id", None) if schedule else None,
                media_id=getattr(media_item, "id", None) if media_item else None,
                media_name=getattr(media_item, "original_name", "") if media_item else "",
                action=action, status=status, message=message,
                hash_before=hash_before, hash_after=hash_after,
                instagram_pk=instagram_pk, duration_sec=round(duration, 2),
                run_by=run_by,
            ))
            db.commit()
        except Exception:
            db.rollback()
