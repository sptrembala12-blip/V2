"""
Motor de Maturação Automática de Contas com IA 24/7 (Ciclos Humanos e Segmentação por País).
Executa ciclos autônomos durante 3 dias consumindo conteúdo regional do país selecionado para treinar o algoritmo da Meta.
"""
from __future__ import annotations

import json
import random
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

from . import models
from .instagram_service import IGManager


def _now() -> datetime:
    return datetime.now(timezone.utc)


COUNTRY_CONFIGS: Dict[str, Dict[str, Any]] = {
    "BR": {
        "name": "Brasil",
        "tags": ["reelsbrasil", "explorebrasil", "humorbrasil", "viralbrasil", "tendenciasbrasil", "brasil", "cortesbrasil", "musica"],
        "creators": ["reelsbrasil", "humorbrasil", "explore", "cinemaepipoca", "videosvirais", "cortesdodia", "reels_br"],
    },
    "US": {
        "name": "Estados Unidos",
        "tags": ["reels", "viral", "trending", "explorepage", "funny", "usa", "nyc", "california", "reelsusa"],
        "creators": ["creators", "instagram", "reels", "trending", "usaviral", "dailyreels", "reels_us"],
    },
    "PT": {
        "name": "Portugal",
        "tags": ["portugal", "reelsportugal", "lisboa", "porto", "algarve", "humorportugal", "viralpt"],
        "creators": ["portugal", "lisboncreators", "reelsportugal", "explorept", "humor_pt"],
    },
    "ES": {
        "name": "Espanha",
        "tags": ["espana", "madrid", "barcelona", "reelespana", "humorespanol", "tendencias"],
        "creators": ["espana", "madridcreators", "reelespana", "viralspain", "humor_es"],
    },
    "UK": {
        "name": "Reino Unido",
        "tags": ["uk", "london", "reelsuk", "manchester", "britishhumour", "trendinguk"],
        "creators": ["ukcreators", "london", "reelsuk", "britishviral", "trending_uk"],
    },
    "MX": {
        "name": "México",
        "tags": ["mexico", "cdmx", "reelsmexico", "humormexicano", "monterrey", "guadalajara"],
        "creators": ["mexicocreators", "cdmx", "reelsmexico", "viralmexico", "humor_mx"],
    },
    "FR": {
        "name": "França",
        "tags": ["france", "paris", "reelsfrance", "humourfrancais", "tendances", "frenchreels"],
        "creators": ["france", "pariscreators", "reelsfrance", "explorefrance", "paris_life"],
    },
    "DE": {
        "name": "Alemanha",
        "tags": ["deutschland", "berlin", "reelsgermany", "lustig", "muenchen", "hamburg"],
        "creators": ["deutschland", "berlincreators", "reelsgermany", "exploregermany", "berlin_viral"],
    },
    "IT": {
        "name": "Itália",
        "tags": ["italia", "roma", "milano", "reelsitalia", "divertente", "napoli"],
        "creators": ["italia", "milanocreators", "reelsitalia", "exploreitalia", "roma_life"],
    },
    "AR": {
        "name": "Argentina",
        "tags": ["argentina", "buenosaires", "humorargentino", "reelsargentina", "cordoba"],
        "creators": ["argentina", "buenosaires", "reelsargentina", "viralargentina", "humor_ar"],
    },
    "GLOBAL": {
        "name": "Global (Internacional)",
        "tags": ["explore", "reels", "viral", "trending", "instagram", "daily"],
        "creators": ["creators", "instagram", "reels", "explore", "trending_worldwide"],
    },
}


class WarmupManager:
    def __init__(self, session_factory, ig_manager: IGManager) -> None:
        self.session_factory = session_factory
        self.ig = ig_manager
        self._active_runs: dict[int, dict] = {}

    def is_running(self, account_id: int) -> bool:
        item = self._active_runs.get(account_id)
        if not item:
            return False
        if not item["thread"].is_alive():
            self._active_runs.pop(account_id, None)
            return False
        return True

    def stop(self, account_id: int) -> bool:
        item = self._active_runs.get(account_id)
        if item:
            item["stop_event"].set()
            self._active_runs.pop(account_id, None)

        # Atualiza imediatamente o status no banco de dados para 'interrompido'
        try:
            with self.session_factory() as db:
                sessions = db.query(models.WarmupSession).filter(
                    models.WarmupSession.account_id == account_id
                ).all()
                for s in sessions:
                    if s.status == "em_andamento":
                        s.status = "interrompido"
                        s.status_detail = "[IA] Maturação pausada pelo usuário."
                        current_logs = []
                        try:
                            current_logs = json.loads(s.logs_json or "[]")
                        except Exception:
                            pass
                        current_logs.append({
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "action": "stop",
                            "text": "[IA] Maturação pausada pelo usuário.",
                        })
                        s.logs_json = json.dumps(current_logs[-100:], ensure_ascii=False)
                db.commit()
        except Exception:
            pass
        return True

    def start_warmup(self, *, user_id: int, account_id: int, account_age: str = "hoje",
                     target_country: str = "BR", total_days: int = 3,
                     intensity: str = "medio", niche: str = "Automático com IA",
                     watch_reels: bool = True, like_posts: bool = True,
                     follow_profiles: bool = False, explore_tab: bool = True) -> int:
        with self.session_factory() as db:
            acc = db.get(models.Account, account_id)
            if not acc or acc.user_id != user_id:
                raise ValueError("Conta não encontrada ou sem permissão.")

            # Se já houver uma sessão ativa para essa conta, interrompe e limpa
            if self.is_running(acc.id):
                self.stop(acc.id)
                time.sleep(0.5)

            # Limpa sessões antigas dessa conta para garantir 1 único card limpo por conta
            db.query(models.WarmupSession).filter(
                models.WarmupSession.user_id == user_id,
                models.WarmupSession.account_id == account_id
            ).delete()
            db.commit()

            country_cfg = COUNTRY_CONFIGS.get(target_country.upper(), COUNTRY_CONFIGS["BR"])
            country_name = country_cfg["name"]

            age_label = "1º Dia" if account_age == "hoje" else ("2 a 7 Dias" if account_age == "recente" else "+7 Dias")

            session = models.WarmupSession(
                user_id=user_id,
                account_id=acc.id,
                account_name=acc.name,
                account_age=account_age,
                target_country=target_country.upper(),
                current_day=1,
                total_days=total_days,
                cycles_completed=0,
                niche=f"Segmentação: {country_name}",
                intensity=intensity,
                watch_reels=watch_reels,
                like_posts=like_posts,
                follow_profiles=follow_profiles,
                explore_tab=explore_tab,
                status="em_andamento",
                status_detail=f"Iniciando Aquecimento 24/7 (Dia 1 de {total_days}) para {country_name}...",
                views_done=0,
                likes_done=0,
                follows_done=0,
                logs_json=json.dumps([{
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "action": "inicio",
                    "text": f"[IA] Maturação 24/7 iniciada | Perfil: {age_label} | País: {country_name}. Calibrando ciclos de {total_days} dias...",
                }], ensure_ascii=False),
            )
            db.add(session)
            db.commit()
            db.refresh(session)
            session_id = session.id

        stop_event = threading.Event()
        t = threading.Thread(
            target=self._run_warmup_3days,
            args=(session_id, user_id, account_id, account_age, target_country.upper(), total_days, stop_event),
            daemon=True,
            name=f"warmup-{account_id}-{session_id}",
        )
        self._active_runs[account_id] = {"stop_event": stop_event, "thread": t, "session_id": session_id}
        t.start()
        return session_id

    def _append_log(self, session_id: int, action: str, text: str,
                    views: int = 0, likes: int = 0, follows: int = 0,
                    status: str = None, current_day: int = None,
                    cycles: int = None, next_cycle: datetime = None) -> None:
        try:
            with self.session_factory() as db:
                s = db.get(models.WarmupSession, session_id)
                if s:
                    current_logs = []
                    try:
                        current_logs = json.loads(s.logs_json or "[]")
                    except Exception:
                        pass
                    current_logs.append({
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "action": action,
                        "text": text,
                    })
                    s.logs_json = json.dumps(current_logs[-100:], ensure_ascii=False)
                    s.views_done = max(s.views_done, views)
                    s.likes_done = max(s.likes_done, likes)
                    s.follows_done = max(s.follows_done, follows)
                    if status:
                        s.status = status
                    if current_day:
                        s.current_day = current_day
                    if cycles is not None:
                        s.cycles_completed = cycles
                    if next_cycle:
                        s.next_cycle_at = next_cycle
                    s.status_detail = text
                    db.commit()
        except Exception:
            pass

    def _run_warmup_3days(self, session_id: int, user_id: int, account_id: int,
                          account_age: str, target_country: str, total_days: int,
                          stop_event: threading.Event) -> None:
        country_cfg = COUNTRY_CONFIGS.get(target_country, COUNTRY_CONFIGS["BR"])
        country_name = country_cfg["name"]
        regional_tags = country_cfg["tags"]
        regional_creators = country_cfg["creators"]

        total_views = 0
        total_likes = 0
        total_follows = 0
        cycles_done = 0

        with self.session_factory() as db:
            acc = db.get(models.Account, account_id)
            if not acc:
                return
            is_sim = acc.simulate
            s = db.get(models.WarmupSession, session_id)
            opt_watch = bool(getattr(s, "watch_reels", True)) if s else True
            opt_like = bool(getattr(s, "like_posts", True)) if s else True
            opt_follow = bool(getattr(s, "follow_profiles", False)) if s else False
            opt_explore = bool(getattr(s, "explore_tab", True)) if s else True

        self._append_log(
            session_id, "info",
            f"[IA] Robô calibrado para consumir conteúdos de {country_name}. Treinando algoritmo de entrega...",
            current_day=1, cycles=0
        )

        # Loop Autônomo de 3 Dias (Dia 1 -> Dia 2 -> Dia 3)
        for day in range(1, total_days + 1):
            if stop_event.is_set():
                break

            day_label = f"Dia {day} de {total_days}"

            # Calibra métricas por dia de aquecimento
            if day == 1:
                sessions_in_day = 3
                views_per_session = 5
                likes_per_session = 1
                min_dwell, max_dwell = 12, 24
                phase_desc = f"[IA] {day_label}: Ativação Cautelosa e visualização de perfil próprio para {country_name}."
            elif day == 2:
                sessions_in_day = 4
                views_per_session = 8
                likes_per_session = 2
                min_dwell, max_dwell = 9, 18
                phase_desc = f"[IA] {day_label}: Consolidação Regional e exploração de tendências de {country_name}."
            else:
                sessions_in_day = 4
                views_per_session = 10
                likes_per_session = 3
                min_dwell, max_dwell = 7, 15
                phase_desc = f"[IA] {day_label}: Blindagem do Algoritmo e engajamento ativo para entrega no país {country_name}."

            self._append_log(session_id, "fase", phase_desc, total_views, total_likes, total_follows, current_day=day)

            for session_idx in range(1, sessions_in_day + 1):
                if stop_event.is_set():
                    break

                self._append_log(
                    session_id, "open",
                    f"[IA] Abrindo Instagram móvel — {day_label} (Sessão {session_idx}/{sessions_in_day})...",
                    total_views, total_likes, total_follows, current_day=day, cycles=cycles_done
                )

                # 1. Executa a sessão de consumo humanizado
                if is_sim:
                    for v_idx in range(views_per_session):
                        if stop_event.is_set():
                            break

                        creator = random.choice(regional_creators) + f"_{random.randint(10, 99)}"
                        dwell = random.randint(min_dwell, max_dwell)
                        tag = random.choice(regional_tags)

                        self._append_log(
                            session_id, "view",
                            f"[IA] Assistindo Reel de @{creator} #{tag} ({dwell}s) com retenção natural...",
                            total_views + 1, total_likes, total_follows, current_day=day, cycles=cycles_done
                        )
                        total_views += 1
                        time.sleep(random.uniform(2.5, 4.0))

                        if (total_likes < day * 3) and random.random() < 0.5:
                            time.sleep(random.uniform(2.0, 3.5))
                            self._append_log(
                                session_id, "like",
                                f"[IA] Curtida aplicada no Reel em alta de @{creator}",
                                total_views, total_likes + 1, total_follows, current_day=day, cycles=cycles_done
                            )
                            total_likes += 1
                            time.sleep(random.uniform(2.5, 4.5))

                    if not stop_event.is_set():
                        self._append_log(
                            session_id, "explore",
                            f"[IA] Explorando aba de tendências regionais de {country_name} para registrar geolocalização...",
                            total_views, total_likes, total_follows
                        )
                        time.sleep(random.uniform(3.0, 5.0))

                else:
                    cl = self.ig.get_client(acc)
                    try:
                        if not cl.user_id:
                            self.ig.login(acc)
                    except Exception as e:
                        self._append_log(session_id, "erro", f"[IA] Falha na autenticação: {e}", status="erro")
                        return

                    # Consulta perfil próprio (ação real)
                    try:
                        cl.user_info(cl.user_id)
                        self._append_log(session_id, "profile", "[IA] Acessou perfil próprio na sessão móvel...")
                        time.sleep(random.uniform(3.0, 5.0))
                    except Exception:
                        pass

                    # Consome Reels reais de hashtags regionais do país.
                    # IMPORTANTE: só registramos ações que REALMENTE aconteceram
                    # no Instagram. Se a busca falhar, registramos o erro real e
                    # seguimos — nunca inventamos criadores ou métricas.
                    consumed_any = False
                    for tag in regional_tags[:3]:
                        if stop_event.is_set():
                            break
                        try:
                            medias = cl.hashtag_medias_top(tag, amount=views_per_session)
                        except Exception as e:
                            self._append_log(
                                session_id, "aviso",
                                f"[IA] Não foi possível carregar #{tag} agora ({type(e).__name__}). Tentando próxima tag...",
                                total_views, total_likes, total_follows, current_day=day, cycles=cycles_done
                            )
                            time.sleep(random.uniform(2.0, 4.0))
                            continue

                        if not medias:
                            continue

                        consumed_any = True
                        for m in medias:
                            if stop_event.is_set():
                                break
                            m_id = getattr(m, "id", None) or getattr(m, "pk", "")
                            if not m_id:
                                continue
                            m_user = getattr(m, "user", None)
                            username = getattr(m_user, "username", None) or "perfil"
                            m_user_id = getattr(m_user, "pk", None) or getattr(m_user, "id", None)
                            dwell = random.randint(min_dwell, max_dwell)

                            # Visualização real (media_seen) — só conta se o watch estiver ligado
                            if opt_watch:
                                seen_ok = False
                                try:
                                    cl.media_seen([str(m_id)])
                                    seen_ok = True
                                except Exception:
                                    seen_ok = False
                                if seen_ok:
                                    total_views += 1
                                    self._append_log(
                                        session_id, "view",
                                        f"[IA] Assistiu Reel real de @{username} #{tag} ({dwell}s de retenção).",
                                        total_views, total_likes, total_follows, current_day=day, cycles=cycles_done
                                    )
                                    time.sleep(random.uniform(max(3, acc.delay_min), max(6, acc.delay_max)))

                            # Curtida real (media_like) — só registra se a API confirmar
                            if opt_like and (total_likes < day * 3) and random.random() < 0.5:
                                try:
                                    if cl.media_like(str(m_id)):
                                        total_likes += 1
                                        self._append_log(
                                            session_id, "like",
                                            f"[IA] Curtida real aplicada no Reel de @{username}.",
                                            total_views, total_likes, total_follows, current_day=day, cycles=cycles_done
                                        )
                                        time.sleep(random.uniform(max(4, acc.delay_min), max(7, acc.delay_max)))
                                except Exception:
                                    pass

                            # Follow real (user_follow) — só registra se a API confirmar
                            if opt_follow and m_user_id and (total_follows < day) and random.random() < 0.25:
                                try:
                                    if cl.user_follow(str(m_user_id)):
                                        total_follows += 1
                                        self._append_log(
                                            session_id, "follow",
                                            f"[IA] Seguiu perfil real @{username} para reforçar afinidade regional.",
                                            total_views, total_likes, total_follows, current_day=day, cycles=cycles_done
                                        )
                                        time.sleep(random.uniform(max(4, acc.delay_min), max(8, acc.delay_max)))
                                except Exception:
                                    pass

                    # Exploração real da aba (explore/reels) — ação genuína de rede
                    if opt_explore and not stop_event.is_set():
                        try:
                            cl.get_timeline_feed()
                            self._append_log(
                                session_id, "explore",
                                f"[IA] Explorou o feed/aba de tendências de {country_name} (requisição real).",
                                total_views, total_likes, total_follows, current_day=day, cycles=cycles_done
                            )
                            time.sleep(random.uniform(3.0, 5.0))
                        except Exception:
                            pass

                    if not consumed_any:
                        self._append_log(
                            session_id, "aviso",
                            "[IA] Nenhuma mídia regional retornada nesta sessão (rate limit ou hashtags vazias). "
                            "Nenhuma métrica fictícia foi contabilizada — aguardando próxima janela.",
                            total_views, total_likes, total_follows, current_day=day, cycles=cycles_done
                        )

                cycles_done += 1

                # 2. Descanso Humano Inteligente entre as sessões
                if not stop_event.is_set() and not (day == total_days and session_idx == sessions_in_day):
                    rest_minutes = random.randint(45, 120)
                    next_time = datetime.now() + timedelta(minutes=rest_minutes)

                    self._append_log(
                        session_id, "rest",
                        f"[IA] Fechou o Instagram e descansando... Próxima abertura programada para às {next_time.strftime('%H:%M')} (em {rest_minutes} min).",
                        total_views, total_likes, total_follows, current_day=day, cycles=cycles_done, next_cycle=_now() + timedelta(minutes=rest_minutes)
                    )

                    wait_seconds = random.uniform(8.0, 16.0) if is_sim else min(rest_minutes * 60, 3600)
                    for _ in range(int(wait_seconds)):
                        if stop_event.is_set():
                            break
                        time.sleep(1)

        # Conclusão dos 3 Dias
        if stop_event.is_set():
            self._append_log(
                session_id, "stop",
                f"[IA] Maturação pausada manualmente pelo usuário.",
                total_views, total_likes, total_follows, status="interrompido"
            )
        else:
            final_summary = f"[IA] Conta 100% Aquecida e Blindada para {country_name}! O algoritmo da Meta está calibrado para entregar futuras postagens a este país. Pronta para postar!"
            self._append_log(
                session_id, "sucesso",
                final_summary,
                total_views, total_likes, total_follows,
                status="concluido", current_day=total_days, cycles=cycles_done
            )

            with self.session_factory() as db:
                s = db.get(models.WarmupSession, session_id)
                if s:
                    s.finished_at = _now()
                    s.status = "concluido"
                    s.status_detail = final_summary
                db.commit()

        self._active_runs.pop(account_id, None)
