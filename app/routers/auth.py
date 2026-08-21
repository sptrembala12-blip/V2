"""Rotas de autenticação, verificação de e-mail real e configurações do usuário do SaaS."""
from __future__ import annotations

import random
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import config, email_service, models, rate_limiter, security
from ..deps import get_current_user, get_db
from ..schemas import (
    AuthIn, ChangeEmailIn, ChangePasswordIn, ChangePasswordWithCodeIn,
    ResendVerificationIn, ThemePreferenceIn, TokenOut, TwoFactorToggleIn,
    UserOut, UserSettingsOut, VerifyEmailIn
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str) -> None:
    """Define o cookie de sessão respeitando o TTL e as flags de segurança."""
    max_age = (config.SESSION_TTL_DAYS or 365) * 86400
    response.set_cookie(
        "token",
        token,
        max_age=max_age,
        httponly=False,  # o SPA lê o token para enviá-lo no header Authorization
        samesite="lax",
        secure=config.IS_PRODUCTION,
    )


@router.post("/register")
def register(body: AuthIn, response: Response, db: Session = Depends(get_db)):
    email = body.email.lower().strip()
    name = (body.name or "").strip() or None
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if user:
        if user.is_verified:
            # Se já é verificado e a senha confere, loga direto
            if security.verify_password(body.password, user.password_hash):
                if name and not user.name:
                    user.name = name
                if security.needs_rehash(user.password_hash):
                    user.password_hash = security.hash_password(body.password)
                db.commit()
                token = security.create_token()
                db.add(models.AuthToken(token=token, user_id=user.id))
                db.commit()
                _set_session_cookie(response, token)
                return {"verification_required": False, "token": token, "email": user.email, "name": user.name}
            raise HTTPException(409, detail="Este e-mail já existe. Faça login na aba Entrar.")
    else:
        ok, msg = security.validate_password_strength(body.password)
        if not ok:
            raise HTTPException(400, detail=msg)
        user = models.User(email=email, name=name, password_hash=security.hash_password(body.password), is_verified=False)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Gera código de verificação de 6 dígitos para o cadastro
    code = f"{random.randint(100000, 999999)}"
    user.verification_code = code
    db.commit()

    # Dispara e-mail real via SMTP
    mail_res = email_service.send_email_code(user.email, code, "verification")

    return {
        "verification_required": True,
        "email": user.email,
        "name": user.name,
        "code": code,
        "smtp_configured": email_service.is_smtp_configured(),
        "message": mail_res.get("message", f"Código de ativação: {code}"),
    }


@router.post("/verify-email", response_model=TokenOut)
def verify_email(body: VerifyEmailIn, response: Response, db: Session = Depends(get_db)):
    email = body.email.lower().strip()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(404, detail="Usuário não encontrado.")

    if not user.verification_code or body.code.strip() != user.verification_code.strip():
        raise HTTPException(400, detail="Código de verificação incorreto ou expirado.")

    user.is_verified = True
    user.verification_code = None
    db.commit()

    token = security.create_token()
    db.add(models.AuthToken(token=token, user_id=user.id))
    db.commit()

    _set_session_cookie(response, token)
    return TokenOut(token=token, email=user.email, name=user.name)


@router.post("/resend-verification")
def resend_verification(body: ResendVerificationIn, db: Session = Depends(get_db)):
    email = body.email.lower().strip()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(404, detail="Usuário não encontrado.")

    code = f"{random.randint(100000, 999999)}"
    user.verification_code = code
    db.commit()

    mail_res = email_service.send_email_code(user.email, code, "verification")

    return {
        "ok": True,
        "code": code,
        "smtp_configured": email_service.is_smtp_configured(),
        "message": mail_res.get("message", f"Código de ativação: {code}"),
    }


@router.post("/login", response_model=TokenOut)
def login(body: AuthIn, request: Request, response: Response, db: Session = Depends(get_db)):
    email = body.email.lower().strip()
    ip = rate_limiter.get_client_ip(request)

    # Proteção contra força bruta: bloqueia após muitas tentativas malsucedidas.
    if rate_limiter.is_login_locked(email, ip):
        raise HTTPException(
            429,
            detail=f"Muitas tentativas de login. Aguarde {config.LOGIN_LOCKOUT_MINUTES} minutos e tente novamente.",
        )

    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        if config.ALLOW_LOGIN_AUTOCREATE:
            # Cadastro implícito no primeiro login (só quando explicitamente habilitado)
            ok, msg = security.validate_password_strength(body.password)
            if not ok:
                raise HTTPException(400, detail=msg)
            user = models.User(
                email=email,
                password_hash=security.hash_password(body.password),
                is_verified=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            rate_limiter.record_failed_login(email, ip)
            raise HTTPException(401, detail="E-mail ou senha incorretos.")
    else:
        if not security.verify_password(body.password, user.password_hash):
            rate_limiter.record_failed_login(email, ip)
            raise HTTPException(401, detail="E-mail ou senha incorretos.")

        # Reforço de segurança: reescreve hashes antigos (PBKDF2 -> scrypt).
        if security.needs_rehash(user.password_hash):
            user.password_hash = security.hash_password(body.password)
            db.commit()

    # Exigir verificação de e-mail, se configurado
    if config.REQUIRE_EMAIL_VERIFICATION and not user.is_verified:
        raise HTTPException(403, detail="Confirme seu e-mail antes de entrar. Verifique sua caixa de entrada.")

    rate_limiter.clear_login_attempts(email, ip)

    token = security.create_token()
    db.add(models.AuthToken(token=token, user_id=user.id))
    db.commit()

    _set_session_cookie(response, token)
    return TokenOut(token=token, email=user.email, name=user.name)


@router.get("/me", response_model=UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user


@router.get("/settings", response_model=UserSettingsOut)
def get_settings(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    acc_count = db.query(models.Account).filter(models.Account.user_id == user.id).count()
    med_count = db.query(models.Media).filter(models.Media.user_id == user.id).count()
    sched_count = db.query(models.Schedule).filter(models.Schedule.user_id == user.id).count()

    is_postgres = "postgres" in config.DATABASE_URL.lower()
    storage_label = "PostgreSQL Nuvem Permanente" if is_postgres else "SQLite Local"

    return UserSettingsOut(
        id=user.id,
        email=user.email,
        name=user.name,
        is_verified=bool(user.is_verified),
        two_factor_enabled=bool(user.two_factor_enabled),
        theme_preference=user.theme_preference or "auto",
        created_at=user.created_at,
        accounts_count=acc_count,
        medias_count=med_count,
        schedules_count=sched_count,
        storage_type=f"{storage_label} (Sessões Duplamente Persistidas)",
    )


@router.post("/request-password-code")
def request_password_code(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Gera e envia código de 6 dígitos para o e-mail cadastrado para redefinir senha."""
    code = f"{random.randint(100000, 999999)}"
    user.reset_password_code = code
    db.commit()

    mail_res = email_service.send_email_code(user.email, code, "reset_password")

    return {
        "ok": True,
        "code": code,
        "smtp_configured": email_service.is_smtp_configured(),
        "message": mail_res.get("message", f"Código de redefinição de senha: {code}"),
    }


@router.post("/change-password-with-code")
def change_password_with_code(body: ChangePasswordWithCodeIn,
                              user: models.User = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    """Altera a senha após conferência do código recebido no e-mail."""
    if not user.reset_password_code or body.code.strip() != user.reset_password_code.strip():
        raise HTTPException(400, detail="Código de redefinição incorreto ou expirado. Clique em Enviar Código.")

    ok, msg = security.validate_password_strength(body.new_password)
    if not ok:
        raise HTTPException(400, detail=msg)

    user.password_hash = security.hash_password(body.new_password)
    user.reset_password_code = None
    db.commit()
    return {"ok": True, "message": "Senha atualizada com sucesso!"}


@router.post("/theme")
def update_theme(body: ThemePreferenceIn, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.theme_preference = body.theme.lower()
    db.commit()
    return {"ok": True, "theme": user.theme_preference}


@router.post("/two-factor")
def toggle_two_factor(body: TwoFactorToggleIn, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.two_factor_enabled = body.enabled
    db.commit()
    status_str = "ativada" if body.enabled else "desativada"
    return {"ok": True, "two_factor_enabled": user.two_factor_enabled, "message": f"Autenticação em dois fatores {status_str} com sucesso!"}


@router.post("/logout")
def logout(request: Request, response: Response,
           user: models.User = Depends(get_current_user),
           db: Session = Depends(get_db)):
    # Revoga o token atual (não só apaga o cookie), encerrando a sessão de fato.
    token = ""
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
    token = token or request.cookies.get("token", "")
    if token:
        db.query(models.AuthToken).filter(models.AuthToken.token == token).delete()
        db.commit()
    response.delete_cookie("token")
    return {"ok": True}


@router.post("/logout-all")
def logout_all(response: Response,
               user: models.User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    """Encerra a sessão em todos os dispositivos (revoga todos os tokens)."""
    count = db.query(models.AuthToken).filter(models.AuthToken.user_id == user.id).delete()
    db.commit()
    response.delete_cookie("token")
    return {"ok": True, "sessions_revoked": count, "message": f"{count} sessão(ões) encerradas em todos os dispositivos."}


@router.post("/change-password")
def change_password(body: ChangePasswordIn,
                    user: models.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """Altera a senha diretamente (conhecendo a senha atual), sem código de e-mail."""
    if not security.verify_password(body.current_password, user.password_hash):
        raise HTTPException(400, detail="Senha atual incorreta.")
    ok, msg = security.validate_password_strength(body.new_password)
    if not ok:
        raise HTTPException(400, detail=msg)
    user.password_hash = security.hash_password(body.new_password)
    db.commit()
    return {"ok": True, "message": "Senha alterada com sucesso!"}


@router.get("/export-data")
def export_data(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Exporta todos os dados do usuário (LGPD/portabilidade), sem segredos."""
    accounts = db.query(models.Account).filter(models.Account.user_id == user.id).all()
    medias = db.query(models.Media).filter(models.Media.user_id == user.id).all()
    schedules = db.query(models.Schedule).filter(models.Schedule.user_id == user.id).all()
    logs = db.query(models.PostLog).filter(models.PostLog.user_id == user.id).all()

    def _dt(v):
        return v.isoformat() if v else None

    return {
        "exported_at": models.utcnow().isoformat(),
        "user": {"id": user.id, "email": user.email, "name": user.name, "created_at": _dt(user.created_at)},
        "accounts": [
            {
                "id": a.id, "name": a.name, "ig_username": a.ig_username,
                "status": a.status, "simulate": a.simulate,
                "followers": a.follower_count, "following": a.following_count,
                "posts": a.media_count, "created_at": _dt(a.created_at),
            }
            for a in accounts
        ],
        "medias": [
            {"id": m.id, "name": m.original_name, "kind": m.kind, "times_used": m.times_used}
            for m in medias
        ],
        "schedules": [
            {"id": s.id, "name": s.name, "mode": s.mode, "target_type": s.target_type, "enabled": s.enabled}
            for s in schedules
        ],
        "post_logs": [
            {
                "id": l.id, "account": l.account_name, "action": l.action,
                "status": l.status, "message": l.message, "created_at": _dt(l.created_at),
            }
            for l in logs
        ],
        "totals": {
            "accounts": len(accounts), "medias": len(medias),
            "schedules": len(schedules), "post_logs": len(logs),
        },
    }


@router.get("/system-info")
def system_info(user: models.User = Depends(get_current_user)):
    """Informações do sistema e limites de automação (para o painel de Configurações)."""
    is_postgres = "postgres" in config.DATABASE_URL.lower()
    return {
        "version": config.APP_VERSION,
        "environment": config.ENVIRONMENT,
        "database": "PostgreSQL" if is_postgres else "SQLite",
        "timezone": config.APP_TZ,
        "email_configured": email_service.is_smtp_configured(),
        "limits": {
            "max_posts_per_day": config.MAX_POSTS_PER_DAY,
            "max_upload_mb": config.MAX_UPLOAD_MB,
            "posting_workers": config.POSTING_WORKERS,
            "network_retry_attempts": config.NETWORK_RETRY_ATTEMPTS,
            "log_retention_days": config.LOG_RETENTION_DAYS,
            "session_ttl_days": config.SESSION_TTL_DAYS,
            "account_healthcheck_minutes": config.ACCOUNT_HEALTHCHECK_MINUTES,
        },
        "security": {
            "min_password_length": config.MIN_PASSWORD_LENGTH,
            "login_max_attempts": config.LOGIN_MAX_ATTEMPTS,
            "require_email_verification": config.REQUIRE_EMAIL_VERIFICATION,
            "cors_restricted": bool(config.CORS_ORIGINS),
            "secret_key_configured": not config.secret_is_ephemeral(),
        },
    }
