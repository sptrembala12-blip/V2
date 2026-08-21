"""Modelos do banco de dados (SQLAlchemy 2.0)."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    """Usuário do SaaS."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    reset_password_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    theme_preference: Mapped[str] = mapped_column(String(20), default="auto")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class AuthToken(Base):
    """Sessão de login do usuário (Bearer token / Cookie persistente)."""

    __tablename__ = "auth_tokens"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Account(Base):
    """Conta do Instagram vinculada a um usuário do SaaS."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    ig_username: Mapped[str] = mapped_column(String(120))
    ig_password_enc: Mapped[str] = mapped_column(Text)          # criptografada (Fernet)
    proxy_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    fingerprint_json: Mapped[str] = mapped_column(Text)          # fingerprint anti-detecção
    simulate: Mapped[bool] = mapped_column(Boolean, default=False)  # False = conta real padrão
    humanize: Mapped[bool] = mapped_column(Boolean, default=True)   # pausas e variações
    delay_min: Mapped[int] = mapped_column(Integer, default=3)      # segundos
    delay_max: Mapped[int] = mapped_column(Integer, default=12)
    warmup: Mapped[bool] = mapped_column(Boolean, default=True)     # aquecimento pré-post
    status: Mapped[str] = mapped_column(String(30), default="pendente")
    status_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    follower_count: Mapped[int] = mapped_column(Integer, default=0)
    following_count: Mapped[int] = mapped_column(Integer, default=0)
    media_count: Mapped[int] = mapped_column(Integer, default=0)
    profile_pic_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    session_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)


class Media(Base):
    """Mídia da biblioteca (foto/vídeo) com metadados limpos e vinculação por conta."""

    __tablename__ = "medias"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True, index=True)
    account_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    original_name: Mapped[str] = mapped_column(String(255))
    kind: Mapped[str] = mapped_column(String(10))                # "photo" | "video"
    ext: Mapped[str] = mapped_column(String(10))
    size_bytes: Mapped[int] = mapped_column(Integer)
    original_path: Mapped[str] = mapped_column(Text)             # upload bruto
    active_path: Mapped[str] = mapped_column(Text)               # versão limpa
    original_sha256: Mapped[str] = mapped_column(String(64))
    active_sha256: Mapped[str] = mapped_column(String(64))
    metadata_clean: Mapped[bool] = mapped_column(Boolean, default=False)
    times_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class IpBlock(Base):
    """Rastreamento e bloqueio de abuso por IP."""

    __tablename__ = "ip_blocks"

    id: Mapped[int] = mapped_column(primary_key=True)
    ip_address: Mapped[str] = mapped_column(String(64), index=True)
    request_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0)
    blocked_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Schedule(Base):
    """Agendamento de postagens para uma conta."""

    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    mode: Mapped[str] = mapped_column(String(10))                # "interval" | "times" | "once"
    target_type: Mapped[str] = mapped_column(String(15), default="reel")  # "reel" | "feed" | "story"
    interval_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    times_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # ["09:00","18:30"] ou "2026-08-17T20:00"
    caption: Mapped[str] = mapped_column(Text, default="")
    usertags: Mapped[str | None] = mapped_column(Text, nullable=True)    # "@perfil1, @perfil2"
    jitter_min: Mapped[int] = mapped_column(Integer, default=0)   # variação de horário
    media_id: Mapped[int | None] = mapped_column(ForeignKey("medias.id"), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class WarmupSession(Base):
    """Sessão de maturação automática anti-queda com IA 24/7 e segmentação por país."""

    __tablename__ = "warmup_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    account_name: Mapped[str] = mapped_column(String(120), default="")
    account_age: Mapped[str] = mapped_column(String(30), default="hoje")  # "hoje" | "recente" | "madura"
    target_country: Mapped[str] = mapped_column(String(40), default="BR")  # BR, US, PT, ES, etc.
    current_day: Mapped[int] = mapped_column(Integer, default=1)
    total_days: Mapped[int] = mapped_column(Integer, default=3)
    cycles_completed: Mapped[int] = mapped_column(Integer, default=0)
    next_cycle_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    niche: Mapped[str] = mapped_column(String(255), default="Automático com IA")
    intensity: Mapped[str] = mapped_column(String(20), default="medio")
    watch_reels: Mapped[bool] = mapped_column(Boolean, default=True)
    like_posts: Mapped[bool] = mapped_column(Boolean, default=True)
    follow_profiles: Mapped[bool] = mapped_column(Boolean, default=False)
    explore_tab: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(20), default="em_andamento")
    status_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    views_done: Mapped[int] = mapped_column(Integer, default=0)
    likes_done: Mapped[int] = mapped_column(Integer, default=0)
    follows_done: Mapped[int] = mapped_column(Integer, default=0)
    logs_json: Mapped[str | None] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class PostLog(Base):
    """Histórico de cada execução de postagem."""

    __tablename__ = "post_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), nullable=True)
    account_name: Mapped[str] = mapped_column(String(120), default="")
    schedule_id: Mapped[int | None] = mapped_column(ForeignKey("schedules.id"), nullable=True)
    media_id: Mapped[int | None] = mapped_column(ForeignKey("medias.id"), nullable=True)
    media_name: Mapped[str] = mapped_column(String(255), default="")
    action: Mapped[str] = mapped_column(String(30))              # post_reel | post_photo | post_story
    status: Mapped[str] = mapped_column(String(15))              # success | error
    message: Mapped[str] = mapped_column(Text, default="")
    hash_before: Mapped[str | None] = mapped_column(String(64), nullable=True)
    hash_after: Mapped[str | None] = mapped_column(String(64), nullable=True)
    instagram_pk: Mapped[str | None] = mapped_column(String(64), nullable=True)
    duration_sec: Mapped[float] = mapped_column(Float, default=0.0)
    run_by: Mapped[str] = mapped_column(String(15), default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
