"""Schemas Pydantic da API."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

# ---------------------------------------------------------------- autenticação

class AuthIn(BaseModel):
    name: Optional[str] = Field(None, max_length=120)
    email: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=128)


class TokenOut(BaseModel):
    token: str
    email: str
    name: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    two_factor_enabled: bool = False
    theme_preference: str = "auto"
    created_at: datetime


class VerifyEmailIn(BaseModel):
    email: str = Field(min_length=3, max_length=128)
    code: str = Field(min_length=4, max_length=10)


class ResendVerificationIn(BaseModel):
    email: str = Field(min_length=3, max_length=128)


class ChangePasswordWithCodeIn(BaseModel):
    code: str = Field(min_length=4, max_length=10)
    new_password: str = Field(min_length=4, max_length=128)


class ChangeEmailIn(BaseModel):
    new_email: str = Field(min_length=3, max_length=128)
    password: str = Field(min_length=4, max_length=128)


class ChangePasswordIn(BaseModel):
    current_password: str = Field(min_length=4, max_length=128)
    new_password: str = Field(min_length=4, max_length=128)


class TwoFactorToggleIn(BaseModel):
    enabled: bool
    code: Optional[str] = None


class ThemePreferenceIn(BaseModel):
    theme: str = Field("auto", pattern="^(claro|escuro|auto|light|dark)$")


class ProfileUpdateIn(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=40)
    company: Optional[str] = Field(None, max_length=120)
    locale_preference: Optional[str] = Field(None, max_length=10)


class TwoFactorEnableConfirmIn(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class TwoFactorDisableIn(BaseModel):
    password: str = Field(min_length=1, max_length=128)
    code: Optional[str] = Field(None, max_length=10)


class ProfileOut(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    locale_preference: str = "pt-BR"
    avatar_url: Optional[str] = None
    is_verified: bool = False
    two_factor_enabled: bool = False
    theme_preference: str = "auto"
    created_at: datetime
    password_changed_at: Optional[datetime] = None


class SessionOut(BaseModel):
    id: str          # token (mascarado no retorno)
    current: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    last_seen_at: Optional[datetime] = None


class LoginHistoryOut(BaseModel):
    id: int
    event: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    detail: Optional[str] = None
    created_at: datetime


class UserSettingsOut(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    is_verified: bool = True
    two_factor_enabled: bool
    theme_preference: str
    created_at: datetime
    accounts_count: int
    medias_count: int
    schedules_count: int
    storage_type: str = "SQLite + Disco Local"


def normalize_proxy_url(raw: str | None, default_protocol: str = "http") -> str | None:
    if not raw:
        return None
    raw = str(raw).strip()
    if not raw:
        return None
    if raw.startswith(("http://", "https://", "socks5://", "socks4://")):
        return raw

    # Formato IP:PORT:USER:PASS (ex: 92.112.200.18:6601:marketbetywuk:mbapydt8nkcz)
    parts = raw.split(":")
    if len(parts) == 4:
        ip, port, user, pwd = parts
        return f"{default_protocol}://{user}:{pwd}@{ip}:{port}"

    if "@" in raw:
        return f"{default_protocol}://{raw}"

    if len(parts) == 2:
        ip, port = parts
        return f"{default_protocol}://{ip}:{port}"

    return f"{default_protocol}://{raw}"


# ------------------------------------------------------------------- contas IG

class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    ig_username: str = Field(min_length=1, max_length=120)
    ig_password: str = Field(min_length=1, max_length=500)
    proxy_url: Optional[str] = Field(None, max_length=500)
    simulate: bool = False
    humanize: bool = True
    delay_min: int = Field(3, ge=1, le=120)
    delay_max: int = Field(12, ge=2, le=600)
    warmup: bool = True
    fingerprint_seed: Optional[str] = Field(None, max_length=200)

    @field_validator("proxy_url", mode="before")
    @classmethod
    def check_proxy(cls, v):
        return normalize_proxy_url(v)


class AccountOut(BaseModel):
    id: int
    name: str
    ig_username: str
    proxy_url: Optional[str]
    fingerprint: dict
    fingerprint_summary: dict
    simulate: bool
    humanize: bool
    delay_min: int
    delay_max: int
    warmup: bool
    status: str
    status_detail: Optional[str]
    created_at: datetime


class VerifyCodeIn(BaseModel):
    code: str = Field(min_length=4, max_length=12)


class UpdateCredentialsIn(BaseModel):
    ig_password: str = Field(min_length=1, max_length=500)
    proxy_url: Optional[str] = None

    @field_validator("proxy_url", mode="before")
    @classmethod
    def check_proxy(cls, v):
        return normalize_proxy_url(v)


class ProfileEditIn(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    biography: Optional[str] = Field(None, max_length=500)
    external_url: Optional[str] = Field(None, max_length=255)


class AccountProfileOut(BaseModel):
    account_id: int
    username: str
    full_name: str
    biography: str
    external_url: Optional[str]
    profile_pic_url: Optional[str]
    is_private: bool
    is_verified: bool
    follower_count: int
    following_count: int
    media_count: int
    recent_posts: list[dict] = []


# ---------------------------------------------------------------------- mídias

class MediaOut(BaseModel):
    id: int
    original_name: str
    kind: str
    ext: str
    size_bytes: int
    account_id: Optional[int] = None
    account_name: Optional[str] = None
    original_sha256: str
    active_sha256: str
    metadata_clean: bool
    times_used: int
    created_at: datetime


# -------------------------------------------------------------- agendamentos

class DirectPostIn(BaseModel):
    account_id: int
    media_id: Optional[int] = None
    target_type: str = Field("reel", pattern="^(reel|feed|story|trial_reel)$")
    caption: str = ""
    usertags: Optional[str] = None


class MultiPostIn(BaseModel):
    account_ids: list[int] = Field(min_length=1)
    media_id: Optional[int] = None
    target_type: str = Field("reel", pattern="^(reel|feed|story|trial_reel)$")
    caption: str = ""
    usertags: Optional[str] = None
    delay_sec: int = Field(15, ge=2, le=300)


class ScheduleCreate(BaseModel):
    account_id: int
    name: str = Field(min_length=1, max_length=120)
    mode: str = Field(pattern="^(interval|times|once)$")
    target_type: str = Field("reel", pattern="^(reel|feed|story|trial_reel)$")
    interval_hours: Optional[float] = Field(None, ge=0.02, le=8760)
    times: Optional[list[str]] = None
    scheduled_at: Optional[str] = None
    caption: str = ""
    usertags: Optional[str] = None
    jitter_min: int = Field(0, ge=0, le=240)
    media_id: Optional[int] = None
    enabled: bool = True

    @field_validator("times")
    @classmethod
    def check_times(cls, v):
        if v is None:
            return v
        out = []
        for t in v:
            t = t.strip().replace("h", ":").replace("H", ":")
            if ":" not in t:
                t = f"{t}:00"
            parts = t.split(":")
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                hh, mm = int(parts[0]), int(parts[1])
                if 0 <= hh <= 23 and 0 <= mm <= 59:
                    out.append(f"{hh:02d}:{mm:02d}")
                    continue
            raise ValueError(f"Horário inválido: {t!r} (use formato HH:MM, ex: 09:00)")
        return out or None


class ScheduleUpdate(BaseModel):
    enabled: Optional[bool] = None
    caption: Optional[str] = None
    usertags: Optional[str] = None
    interval_hours: Optional[float] = Field(None, ge=0.02, le=8760)
    times: Optional[list[str]] = None
    jitter_min: Optional[int] = Field(None, ge=0, le=240)
    media_id: Optional[int] = None


class ScheduleOut(BaseModel):
    id: int
    account_id: int
    account_name: str
    name: str
    mode: str
    target_type: str
    interval_hours: Optional[float]
    times: Optional[list[str]]
    caption: str
    usertags: Optional[str] = None
    jitter_min: int
    media_id: Optional[int]
    media_name: Optional[str]
    enabled: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    created_at: datetime


# -------------------------------------------------------------- aquecimento

class WarmupStartIn(BaseModel):
    account_id: int
    account_age: str = Field("hoje", pattern="^(hoje|recente|madura)$")
    target_country: str = Field("BR", max_length=40)
    total_days: int = Field(3, ge=1, le=7)
    niche: Optional[str] = Field("Automático com IA", max_length=255)
    intensity: str = Field("medio", pattern="^(leve|medio|intenso)$")
    watch_reels: bool = True
    like_posts: bool = True
    follow_profiles: bool = False
    explore_tab: bool = True


class WarmupSessionOut(BaseModel):
    id: int
    account_id: int
    account_name: str
    account_age: str = "hoje"
    target_country: str = "BR"
    current_day: int = 1
    total_days: int = 3
    cycles_completed: int = 0
    next_cycle_at: Optional[datetime] = None
    niche: str
    intensity: str
    watch_reels: bool
    like_posts: bool
    follow_profiles: bool
    explore_tab: bool
    status: str
    status_detail: Optional[str]
    views_done: int
    likes_done: int
    logs: list[dict]
    created_at: datetime
    finished_at: Optional[datetime]


# ---------------------------------------------------------------------- logs

class PostLogOut(BaseModel):
    id: int
    account_id: Optional[int]
    account_name: str
    schedule_id: Optional[int]
    media_id: Optional[int] = None
    media_name: str
    action: str
    status: str
    message: str
    hash_before: Optional[str]
    hash_after: Optional[str]
    instagram_pk: Optional[str]
    duration_sec: float
    run_by: str
    created_at: datetime


class StatsOut(BaseModel):
    total_accounts: int
    active_accounts: int
    total_medias: int
    posts_today: int
    total_posts: int
    schedules_enabled: int
    daily_activity: list[dict] = []
    upcoming: list[dict]
    recent_logs: list[PostLogOut]
