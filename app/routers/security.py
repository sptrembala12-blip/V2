"""
Rotas de Perfil & Segurança do usuário do SaaS:
- Perfil (nome, telefone, empresa, idioma, avatar)
- Troca de e-mail e senha
- 2FA real (TOTP + QR Code + códigos de recuperação)
- Sessões ativas (listar/revogar) e histórico de acessos
"""
from __future__ import annotations

import base64
import io
import json
import secrets
import uuid
from datetime import datetime, timezone

import pyotp
import qrcode
from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .. import config, media, models, security
from ..deps import get_current_user, get_db
from ..schemas import (
    ChangeEmailIn, ChangePasswordIn, LoginHistoryOut, ProfileOut,
    ProfileUpdateIn, SessionOut, TwoFactorDisableIn, TwoFactorEnableConfirmIn,
)

router = APIRouter(prefix="/api/security", tags=["segurança"])

TOTP_ISSUER = "InstaFlow"


# --------------------------------------------------------------- utilitários
def _client_ip(request: Request) -> str | None:
    fwd = request.headers.get("CF-Connecting-IP") or request.headers.get("X-Forwarded-For")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else None


def _log_event(db: Session, user_id: int, event: str, request: Request, detail: str = "") -> None:
    try:
        db.add(models.LoginHistory(
            user_id=user_id,
            event=event,
            ip_address=_client_ip(request),
            user_agent=(request.headers.get("User-Agent", "") or "")[:400],
            detail=detail or None,
        ))
        db.commit()
    except Exception:
        db.rollback()


def _current_token(request: Request) -> str:
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return request.headers.get("X-Auth-Token", "") or request.cookies.get("token", "")


def _avatar_url(user: models.User) -> str | None:
    if user.avatar_path:
        return f"/api/security/avatar/{user.id}"
    return None


def _profile_out(user: models.User) -> ProfileOut:
    return ProfileOut(
        id=user.id, email=user.email, name=user.name, phone=user.phone,
        company=user.company, locale_preference=user.locale_preference or "pt-BR",
        avatar_url=_avatar_url(user), is_verified=bool(user.is_verified),
        two_factor_enabled=bool(user.two_factor_enabled),
        theme_preference=user.theme_preference or "auto",
        created_at=user.created_at, password_changed_at=user.password_changed_at,
    )


# ------------------------------------------------------------------- perfil
@router.get("/profile", response_model=ProfileOut)
def get_profile(user: models.User = Depends(get_current_user)):
    return _profile_out(user)


@router.post("/profile", response_model=ProfileOut)
def update_profile(body: ProfileUpdateIn,
                   user: models.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    if body.name is not None:
        user.name = body.name.strip() or None
    if body.phone is not None:
        user.phone = body.phone.strip() or None
    if body.company is not None:
        user.company = body.company.strip() or None
    if body.locale_preference is not None:
        user.locale_preference = body.locale_preference.strip() or "pt-BR"
    db.commit()
    db.refresh(user)
    return _profile_out(user)


@router.post("/avatar", response_model=ProfileOut)
async def upload_avatar(file: UploadFile = File(...),
                        user: models.User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    content = await file.read()
    if not content:
        raise HTTPException(400, detail="Arquivo vazio.")
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(400, detail="Imagem muito grande (máx. 8 MB).")

    base_dir = config.DATA_DIR / "avatars"
    base_dir.mkdir(parents=True, exist_ok=True)
    tmp = base_dir / f"tmp_{uuid.uuid4().hex}.img"
    dst = base_dir / f"user_{user.id}.jpg"
    tmp.write_bytes(content)
    try:
        media.clean_image(tmp, dst)
    except Exception:
        dst.write_bytes(content)
    finally:
        tmp.unlink(missing_ok=True)

    user.avatar_path = str(dst)
    db.commit()
    db.refresh(user)
    return _profile_out(user)


@router.get("/avatar/{user_id}")
def get_avatar(user_id: int, db: Session = Depends(get_db)):
    u = db.get(models.User, user_id)
    if not u or not u.avatar_path:
        raise HTTPException(404, detail="Sem avatar.")
    from pathlib import Path
    p = Path(u.avatar_path)
    if not p.exists():
        raise HTTPException(404, detail="Arquivo não encontrado.")
    return FileResponse(p, media_type="image/jpeg")


@router.delete("/avatar", response_model=ProfileOut)
def delete_avatar(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.avatar_path:
        from pathlib import Path
        Path(user.avatar_path).unlink(missing_ok=True)
        user.avatar_path = None
        db.commit()
        db.refresh(user)
    return _profile_out(user)


# -------------------------------------------------------------- credenciais
@router.post("/change-email", response_model=ProfileOut)
def change_email(body: ChangeEmailIn, request: Request,
                 user: models.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    if not security.verify_password(body.password, user.password_hash):
        raise HTTPException(400, detail="Senha incorreta.")
    new_email = body.new_email.lower().strip()
    if "@" not in new_email or "." not in new_email:
        raise HTTPException(400, detail="E-mail inválido.")
    exists = db.query(models.User).filter(models.User.email == new_email, models.User.id != user.id).first()
    if exists:
        raise HTTPException(409, detail="Este e-mail já está em uso.")
    old = user.email
    user.email = new_email
    db.commit()
    db.refresh(user)
    _log_event(db, user.id, "email_changed", request, detail=f"{old} → {new_email}")
    return _profile_out(user)


@router.post("/change-password")
def change_password(body: ChangePasswordIn, request: Request,
                    user: models.User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if not security.verify_password(body.current_password, user.password_hash):
        raise HTTPException(400, detail="Senha atual incorreta.")
    ok, msg = security.validate_password_strength(body.new_password)
    if not ok:
        raise HTTPException(400, detail=msg)
    user.password_hash = security.hash_password(body.new_password)
    user.password_changed_at = datetime.now(timezone.utc)
    db.commit()
    _log_event(db, user.id, "password_changed", request)
    return {"ok": True, "message": "Senha alterada com sucesso!"}


# --------------------------------------------------------------------- 2FA
@router.post("/2fa/setup")
def setup_2fa(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Gera um segredo TOTP pendente e o QR Code para o app autenticador."""
    if user.two_factor_enabled:
        raise HTTPException(400, detail="A verificação em duas etapas já está ativa.")
    secret = pyotp.random_base32()
    user.two_factor_pending_secret = secret
    db.commit()

    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=user.email, issuer_name=TOTP_ISSUER)
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return {
        "secret": secret,
        "otpauth_uri": uri,
        "qr_code": f"data:image/png;base64,{qr_b64}",
        "message": "Escaneie o QR Code no Google Authenticator, Authy ou similar e informe o código de 6 dígitos para confirmar.",
    }


@router.post("/2fa/enable")
def enable_2fa(body: TwoFactorEnableConfirmIn, request: Request,
               user: models.User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    """Confirma o código do app autenticador e ativa o 2FA, gerando recovery codes."""
    if not user.two_factor_pending_secret:
        raise HTTPException(400, detail="Inicie a configuração do 2FA primeiro.")
    totp = pyotp.TOTP(user.two_factor_pending_secret)
    if not totp.verify(body.code.strip(), valid_window=1):
        raise HTTPException(400, detail="Código inválido. Verifique o app autenticador e tente novamente.")

    user.two_factor_secret = user.two_factor_pending_secret
    user.two_factor_pending_secret = None
    user.two_factor_enabled = True

    # Gera 10 códigos de recuperação de uso único (mostrados só uma vez).
    recovery_codes = [f"{secrets.token_hex(2)}-{secrets.token_hex(2)}" for _ in range(10)]
    user.two_factor_recovery = json.dumps([security.hash_recovery_code(c) for c in recovery_codes])
    db.commit()
    _log_event(db, user.id, "2fa_enabled", request)

    return {
        "ok": True,
        "recovery_codes": recovery_codes,
        "message": "Verificação em duas etapas ativada! Guarde os códigos de recuperação em local seguro.",
    }


@router.post("/2fa/disable")
def disable_2fa(body: TwoFactorDisableIn, request: Request,
                user: models.User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    if not user.two_factor_enabled:
        raise HTTPException(400, detail="A verificação em duas etapas não está ativa.")
    if not security.verify_password(body.password, user.password_hash):
        raise HTTPException(400, detail="Senha incorreta.")
    user.two_factor_enabled = False
    user.two_factor_secret = None
    user.two_factor_pending_secret = None
    user.two_factor_recovery = None
    db.commit()
    _log_event(db, user.id, "2fa_disabled", request)
    return {"ok": True, "message": "Verificação em duas etapas desativada."}


@router.post("/2fa/recovery-codes")
def regenerate_recovery_codes(body: TwoFactorDisableIn,
                              user: models.User = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    if not user.two_factor_enabled:
        raise HTTPException(400, detail="Ative o 2FA primeiro.")
    if not security.verify_password(body.password, user.password_hash):
        raise HTTPException(400, detail="Senha incorreta.")
    recovery_codes = [f"{secrets.token_hex(2)}-{secrets.token_hex(2)}" for _ in range(10)]
    user.two_factor_recovery = json.dumps([security.hash_recovery_code(c) for c in recovery_codes])
    db.commit()
    return {"ok": True, "recovery_codes": recovery_codes}


# ------------------------------------------------------------- sessões/auditoria
@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(request: Request,
                  user: models.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    current = _current_token(request)
    rows = (
        db.query(models.AuthToken)
        .filter(models.AuthToken.user_id == user.id)
        .order_by(models.AuthToken.created_at.desc())
        .all()
    )
    out = []
    for r in rows:
        out.append(SessionOut(
            id=r.token[:8] + "…" + r.token[-4:],
            current=(r.token == current),
            ip_address=r.ip_address,
            user_agent=r.user_agent,
            created_at=r.created_at,
            last_seen_at=r.last_seen_at,
        ))
    return out


@router.delete("/sessions/{session_prefix}")
def revoke_session(session_prefix: str, request: Request,
                   user: models.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    """Revoga uma sessão específica pelo prefixo mostrado na lista."""
    prefix = session_prefix.split("…")[0]
    current = _current_token(request)
    rows = db.query(models.AuthToken).filter(models.AuthToken.user_id == user.id).all()
    target = next((r for r in rows if r.token.startswith(prefix)), None)
    if not target:
        raise HTTPException(404, detail="Sessão não encontrada.")
    if target.token == current:
        raise HTTPException(400, detail="Não é possível revogar a sessão atual aqui. Use 'Sair'.")
    db.delete(target)
    db.commit()
    return {"ok": True, "message": "Sessão revogada."}


@router.post("/sessions/revoke-others")
def revoke_other_sessions(request: Request,
                          user: models.User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    """Encerra todas as outras sessões, mantendo apenas a atual."""
    current = _current_token(request)
    count = (
        db.query(models.AuthToken)
        .filter(models.AuthToken.user_id == user.id, models.AuthToken.token != current)
        .delete(synchronize_session=False)
    )
    db.commit()
    return {"ok": True, "revoked": count, "message": f"{count} outra(s) sessão(ões) encerradas."}


@router.get("/login-history", response_model=list[LoginHistoryOut])
def login_history(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(models.LoginHistory)
        .filter(models.LoginHistory.user_id == user.id)
        .order_by(models.LoginHistory.id.desc())
        .limit(30)
        .all()
    )
    return [
        LoginHistoryOut(
            id=r.id, event=r.event, ip_address=r.ip_address,
            user_agent=r.user_agent, detail=r.detail, created_at=r.created_at,
        )
        for r in rows
    ]
