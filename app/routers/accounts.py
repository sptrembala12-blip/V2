"""Rotas de gerenciamento de contas, perfis e proxies do Instagram."""
from __future__ import annotations

import threading
import time
import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from .. import config, fingerprint, instagram_service, media, models, security
from ..deps import get_current_user, get_db
from ..main_ctx import app_ctx
from ..schemas import (
    AccountCreate, AccountOut, AccountProfileOut, ProfileEditIn,
    UpdateCredentialsIn, VerifyCodeIn, normalize_proxy_url
)

router = APIRouter(prefix="/api/accounts", tags=["contas"])


class ProxyValidateIn(BaseModel):
    proxy_url: str = Field(min_length=1, max_length=500)


@router.post("/validate-proxy")
def validate_proxy(body: ProxyValidateIn,
                   user: models.User = Depends(get_current_user)):
    """Valida conexão direta através do proxy e mede latência."""
    raw_proxy = body.proxy_url.strip()
    proxy_url = normalize_proxy_url(raw_proxy)
    if not proxy_url:
        raise HTTPException(400, detail="Formato inválido. Use IP:PORTA:USUARIO:SENHA ou http://...")

    t0 = time.time()
    try:
        with httpx.Client(proxy=proxy_url, timeout=10) as client:
            r = client.get("https://api.ipify.org?format=json")
            latency_ms = int((time.time() - t0) * 1000)
            if r.status_code == 200:
                ip = r.json().get("ip", "OK")
                return {
                    "ok": True,
                    "ip": ip,
                    "latency_ms": latency_ms,
                    "message": f"Proxy 100% Funcional! IP de Saída: {ip} (Latência: {latency_ms}ms)",
                }
            raise RuntimeError(f"HTTP {r.status_code}")
    except Exception as e:
        err_msg = str(e)
        if "Connection refused" in err_msg or "Connection reset" in err_msg or "timed out" in err_msg.lower() or "ConnectTimeout" in err_msg:
            err_msg = "Tempo limite esgotado ou conexão recusada pelo servidor de Proxy."
        elif "ProxyError" in err_msg or "407" in err_msg:
            err_msg = "Falha de autenticação do Proxy. Verifique usuário e senha."
        return {
            "ok": False,
            "error": err_msg,
            "message": f"Falha na validação do Proxy: {err_msg}",
        }


def _out(acc: models.Account) -> AccountOut:
    fp = fingerprint.fingerprint_from_json(acc.fingerprint_json)
    return AccountOut(
        id=acc.id, name=acc.name, ig_username=acc.ig_username,
        proxy_url=acc.proxy_url, fingerprint=fp,
        fingerprint_summary=fingerprint.summary(fp),
        simulate=acc.simulate, humanize=acc.humanize,
        delay_min=acc.delay_min, delay_max=acc.delay_max, warmup=acc.warmup,
        status=acc.status, status_detail=acc.status_detail,
        created_at=acc.created_at,
    )


def _get_owned(db: Session, account_id: int, user_id: int) -> models.Account:
    acc = db.get(models.Account, account_id)
    if not acc or acc.user_id != user_id:
        raise HTTPException(404, detail="Conta não encontrada.")
    return acc


@router.get("", response_model=list[AccountOut])
def list_accounts(user: models.User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    accounts = (
        db.query(models.Account)
        .filter(models.Account.user_id == user.id)
        .order_by(models.Account.id.desc())
        .all()
    )
    return [_out(a) for a in accounts]


@router.post("", response_model=AccountOut, status_code=201)
def create_account(body: AccountCreate,
                   user: models.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    fp = fingerprint.generate_fingerprint(body.fingerprint_seed)
    acc = models.Account(
        user_id=user.id,
        name=body.name,
        ig_username=body.ig_username.strip().lstrip("@"),
        ig_password_enc=security.encrypt_secret(body.ig_password),
        proxy_url=body.proxy_url,
        fingerprint_json=fingerprint.fingerprint_to_json(fp),
        simulate=body.simulate,
        humanize=body.humanize,
        delay_min=body.delay_min,
        delay_max=body.delay_max,
        warmup=body.warmup,
        status="ativo" if body.simulate else "conectando",
        status_detail=("Modo simulação — pipeline completo sem contato com o Instagram."
                       if body.simulate else "Autenticando sessão no Instagram..."),
    )
    db.add(acc)
    db.commit()
    db.refresh(acc)

    if not acc.simulate:
        _login_in_background(acc.id)

    return _out(acc)


def _login_in_background(account_id: int) -> None:
    def job():
        from ..database import SessionLocal
        db = SessionLocal()
        try:
            acc = db.get(models.Account, account_id)
            if not acc or acc.simulate:
                return
            app_ctx.ig.update_status(acc.id, "conectando", "Autenticando sessão no Instagram...")
            try:
                app_ctx.ig.login(acc)
            except Exception as e:
                status, detail = instagram_service.map_login_error(e)
                app_ctx.ig.update_status(acc.id, status, detail)
        finally:
            db.close()

    threading.Thread(target=job, daemon=True, name=f"login-acc-{account_id}").start()


@router.post("/{account_id}/update-credentials", response_model=AccountOut)
def update_credentials(account_id: int,
                       body: UpdateCredentialsIn,
                       user: models.User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    acc = _get_owned(db, account_id, user.id)
    acc.ig_password_enc = security.encrypt_secret(body.ig_password)
    if body.proxy_url is not None:
        acc.proxy_url = body.proxy_url.strip() or None
    acc.status = "conectando"
    acc.status_detail = "Autenticando nova sessão..."
    db.commit()

    app_ctx.ig.drop_client(acc.id)
    (config.SESSIONS_DIR / f"{acc.id}.json").unlink(missing_ok=True)

    if not acc.simulate:
        _login_in_background(acc.id)
    else:
        acc.status = "ativo"
        acc.status_detail = "Sessão de simulação atualizada."
        db.commit()

    return _out(acc)


@router.post("/{account_id}/retry-login", response_model=AccountOut)
def retry_login(account_id: int,
                user: models.User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    acc = _get_owned(db, account_id, user.id)
    if acc.simulate:
        raise HTTPException(400, detail="Conta em modo simulação.")
    app_ctx.ig.update_status(acc.id, "conectando", "Tentando login novamente...")
    _login_in_background(acc.id)
    return _out(acc)


@router.post("/{account_id}/verify", response_model=AccountOut)
def verify_code(account_id: int, body: VerifyCodeIn,
                user: models.User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    acc = _get_owned(db, account_id, user.id)
    code = body.code.strip()
    if not code:
        raise HTTPException(400, detail="Informe o código 2FA.")

    # Se houver um thread aguardando no handler de challenge, avisa
    app_ctx.ig.submit_code(acc.id, code)

    # Executa a validação do 2FA diretamente no cliente
    try:
        app_ctx.ig.update_status(acc.id, "conectando", "Validando código 2FA com o Instagram...")
        app_ctx.ig.login(acc, verification_code=code)
        app_ctx.ig.update_status(acc.id, "ativo", "Conectado com sucesso via autenticação 2FA.")
    except Exception as e:
        status, detail = instagram_service.map_login_error(e)
        app_ctx.ig.update_status(acc.id, status, detail)
        raise HTTPException(400, detail=f"Falha na validação 2FA: {detail}")

    db.refresh(acc)
    return _out(acc)


@router.post("/{account_id}/regenerate-fingerprint", response_model=AccountOut)
def regenerate_fingerprint(account_id: int,
                           user: models.User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    acc = _get_owned(db, account_id, user.id)
    fp = fingerprint.generate_fingerprint()
    acc.fingerprint_json = fingerprint.fingerprint_to_json(fp)
    db.commit()
    cl = app_ctx.ig._clients.get(acc.id)
    if cl is not None:
        try:
            fingerprint.apply_to_client(cl, fp)
        except Exception:
            pass
    return _out(acc)


@router.post("/{account_id}/check-connection")
def check_connection(account_id: int,
                     user: models.User = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    acc = _get_owned(db, account_id, user.id)
    fp_summary = fingerprint.summary(fingerprint.fingerprint_from_json(acc.fingerprint_json))
    if acc.simulate:
        return {
            "status": "connected_simulated",
            "message": "Conta em modo simulação (pipeline 100% ativo).",
            "username": acc.ig_username,
            "full_name": acc.name,
            "pk": "sim_987654321",
            "followers": 1420,
            "following": 380,
            "posts_count": 42,
            "is_verified": False,
            "device": fp_summary,
            "session_active": True,
        }

    cl = app_ctx.ig.get_client(acc)
    try:
        if not cl.user_id:
            app_ctx.ig.login(acc)
        info = cl.user_info(cl.user_id)
        return {
            "status": "connected_real",
            "message": "Conectado com sucesso ao Instagram!",
            "username": info.username,
            "full_name": info.full_name,
            "pk": str(info.pk),
            "followers": info.follower_count,
            "following": info.following_count,
            "posts_count": info.media_count,
            "is_verified": info.is_verified,
            "device": fp_summary,
            "session_active": True,
        }
    except Exception as e:
        status, detail = instagram_service.map_login_error(e)
        app_ctx.ig.update_status(acc.id, status, detail)
        return {
            "status": "error",
            "message": detail,
            "error_type": type(e).__name__,
            "device": fp_summary,
            "session_active": False,
        }


@router.get("/{account_id}/profile", response_model=AccountProfileOut)
def get_account_profile(account_id: int,
                        user: models.User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    acc = _get_owned(db, account_id, user.id)
    recent_logs = (
        db.query(models.PostLog)
        .filter(models.PostLog.account_id == acc.id)
        .order_by(models.PostLog.id.desc())
        .limit(8)
        .all()
    )
    posts_list = [
        {
            "id": l.id,
            "action": l.action,
            "media_name": l.media_name,
            "status": l.status,
            "created_at": l.created_at.isoformat(),
            "instagram_pk": l.instagram_pk,
        }
        for l in recent_logs
    ]

    full_name = acc.full_name or acc.name
    biography = acc.biography or ""
    external_url = acc.external_url
    profile_pic = f"/api/accounts/{acc.id}/profile-picture"
    followers = acc.follower_count or 0
    following = acc.following_count or 0
    media_count = acc.media_count or len(posts_list)

    return AccountProfileOut(
        account_id=acc.id,
        username=acc.ig_username,
        full_name=full_name,
        biography=biography,
        external_url=external_url,
        profile_pic_url=profile_pic,
        is_private=False,
        is_verified=False,
        follower_count=followers,
        following_count=following,
        media_count=media_count,
        recent_posts=posts_list,
    )


@router.get("/{account_id}/profile-picture")
def get_profile_picture(account_id: int,
                        user: models.User = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    acc = _get_owned(db, account_id, user.id)
    avatar_file = config.DATA_DIR / f"avatar_{acc.id}.jpg"
    if avatar_file.exists() and avatar_file.stat().st_size > 0:
        return FileResponse(avatar_file, media_type="image/jpeg")

    from PIL import Image, ImageDraw
    img = Image.new("RGB", (200, 200), (99, 102, 241))
    draw = ImageDraw.Draw(img)
    letter = (acc.ig_username or "U")[0].upper()
    draw.text((100, 100), letter, fill=(255, 255, 255), anchor="mm")
    img.save(avatar_file, format="JPEG", quality=90)
    return FileResponse(avatar_file, media_type="image/jpeg")


@router.post("/{account_id}/profile/edit", response_model=dict)
def edit_account_profile(account_id: int,
                         body: ProfileEditIn,
                         user: models.User = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    acc = _get_owned(db, account_id, user.id)
    if body.full_name is not None:
        acc.full_name = body.full_name.strip()
        acc.name = body.full_name.strip()
    if body.biography is not None:
        acc.biography = body.biography
    if body.external_url is not None:
        acc.external_url = body.external_url.strip() or None

    db.commit()

    if not acc.simulate:
        cl = app_ctx.ig.get_client(acc)
        try:
            if body.biography is not None:
                cl.account_set_biography(body.biography)
        except Exception:
            pass

    return {"ok": True, "message": "Perfil e Biografia atualizados com sucesso!"}


@router.post("/{account_id}/profile/picture", response_model=dict)
async def update_profile_picture(account_id: int,
                                 file: UploadFile = File(...),
                                 user: models.User = Depends(get_current_user),
                                 db: Session = Depends(get_db)):
    acc = _get_owned(db, account_id, user.id)
    content = await file.read()
    if not content:
        raise HTTPException(400, detail="Arquivo vazio.")

    import uuid
    temp_dir = config.VARIANTS_DIR
    temp_orig = temp_dir / f"pfp_{acc.id}_{uuid.uuid4().hex[:6]}_orig.jpg"
    temp_clean = temp_dir / f"pfp_{acc.id}_{uuid.uuid4().hex[:6]}_clean.jpg"

    temp_orig.write_bytes(content)
    try:
        media.clean_image(temp_orig, temp_clean)
    except Exception:
        temp_clean = temp_orig

    avatar_file = config.DATA_DIR / f"avatar_{acc.id}.jpg"
    avatar_file.write_bytes(temp_clean.read_bytes())
    acc.profile_pic_url = f"/api/accounts/{acc.id}/profile-picture"
    db.commit()

    if not acc.simulate:
        cl = app_ctx.ig.get_client(acc)
        try:
            if not cl.user_id:
                app_ctx.ig.login(acc)
            cl.account_change_picture(avatar_file)
        except Exception:
            pass

    temp_orig.unlink(missing_ok=True)
    temp_clean.unlink(missing_ok=True)
    return {"ok": True, "message": "Foto de perfil atualizada com sucesso!"}


@router.delete("/{account_id}")
def delete_account(account_id: int,
                   user: models.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    acc = _get_owned(db, account_id, user.id)
    for s in db.query(models.Schedule).filter(models.Schedule.account_id == acc.id).all():
        app_ctx.sched.remove_schedule(s.id)
        db.delete(s)
    db.query(models.PostLog).filter(models.PostLog.account_id == acc.id).delete()
    db.query(models.WarmupSession).filter(models.WarmupSession.account_id == acc.id).delete()
    db.delete(acc)
    db.commit()
    app_ctx.ig.drop_client(acc.id)
    (config.SESSIONS_DIR / f"{acc.id}.json").unlink(missing_ok=True)
    (config.DATA_DIR / f"avatar_{acc.id}.jpg").unlink(missing_ok=True)
    return {"ok": True}
