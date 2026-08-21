"""Rotas da biblioteca de mídias (upload em lote, limpeza EXIF, rehash e vinculação por conta)."""
from __future__ import annotations

import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from .. import config, media, models
from ..deps import get_current_user, get_db
from ..schemas import MediaOut

router = APIRouter(prefix="/api/media", tags=["mídias"])


def _out(m: models.Media) -> MediaOut:
    return MediaOut(
        id=m.id, original_name=m.original_name, kind=m.kind, ext=m.ext,
        size_bytes=m.size_bytes, account_id=m.account_id, account_name=m.account_name,
        original_sha256=m.original_sha256, active_sha256=m.active_sha256,
        metadata_clean=m.metadata_clean, times_used=m.times_used, created_at=m.created_at,
    )


def _get_owned(db: Session, media_id: int, user_id: int) -> models.Media:
    m = db.get(models.Media, media_id)
    if not m or m.user_id != user_id:
        raise HTTPException(404, detail="Mídia não encontrada.")
    return m


@router.get("", response_model=list[MediaOut])
def list_media(account_id: Optional[int] = Query(None),
               user: models.User = Depends(get_current_user),
               db: Session = Depends(get_db)):
    q = db.query(models.Media).filter(models.Media.user_id == user.id)
    if account_id is not None:
        q = q.filter((models.Media.account_id == account_id) | (models.Media.account_id == None))
    items = q.order_by(models.Media.id.desc()).all()
    return [_out(m) for m in items]


@router.post("/upload", status_code=201)
async def upload_media(files: list[UploadFile] = File(...),
                       account_id: Optional[int] = Form(None),
                       user: models.User = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    created: list[models.Media] = []
    errors: list[str] = []

    account_name = None
    if account_id:
        acc = db.get(models.Account, account_id)
        if acc and acc.user_id == user.id:
            account_name = acc.name

    for f in files:
        content = await f.read()
        err, ext = media.validate_upload(f.filename or "", len(content), config.MAX_UPLOAD_MB)
        if err:
            errors.append(f"{f.filename}: {err}")
            continue

        base_dir = config.MEDIA_DIR / str(user.id)
        base_dir.mkdir(parents=True, exist_ok=True)
        stem = uuid.uuid4().hex
        original_path = base_dir / f"{stem}_orig{ext}"
        active_path = base_dir / f"{stem}_clean{ext}"

        media.save_upload(content, original_path)
        try:
            media.clean_media(original_path, active_path, ext)
        except Exception:
            errors.append(f"{f.filename}: falha ao processar.")
            original_path.unlink(missing_ok=True)
            active_path.unlink(missing_ok=True)
            continue

        m = models.Media(
            user_id=user.id,
            account_id=account_id,
            account_name=account_name,
            original_name=f.filename or original_path.name,
            kind=media.kind_for_ext(ext),
            ext=ext,
            size_bytes=len(content),
            original_path=str(original_path),
            active_path=str(active_path),
            original_sha256=media.sha256_file(original_path),
            active_sha256=media.sha256_file(active_path),
            metadata_clean=True,
        )
        db.add(m)
        created.append(m)

    db.commit()
    for m in created:
        db.refresh(m)

    if errors and not created:
        raise HTTPException(400, detail="; ".join(errors))
    return {"created": [_out(m) for m in created], "errors": errors}


@router.get("/{media_id}/file")
def get_media_file(media_id: int,
                   request: Request,
                   user: models.User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    m = _get_owned(db, media_id, user.id)
    path = Path(m.active_path)
    if not path.exists():
        path = Path(m.original_path)
    if not path.exists():
        raise HTTPException(404, detail="Arquivo não encontrado.")
    
    media_type = (
        "image/jpeg" if m.ext in (".jpg", ".jpeg")
        else "image/png" if m.ext == ".png"
        else "video/mp4" if m.ext == ".mp4"
        else "video/quicktime" if m.ext == ".mov"
        else "application/octet-stream"
    )

    file_size = path.stat().st_size
    range_header = request.headers.get("range")

    # Suporte a HTTP 206 Range Requests para reprodução instantânea e sem travamentos em iPhones/Android/PC
    if range_header and m.kind == "video":
        try:
            range_str = range_header.replace("bytes=", "").strip()
            parts = range_str.split("-")
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
            start = max(0, min(start, file_size - 1))
            end = max(start, min(end, file_size - 1))
            content_length = (end - start) + 1

            def iter_range():
                with open(path, "rb") as f:
                    f.seek(start)
                    bytes_left = content_length
                    while bytes_left > 0:
                        chunk_size = min(1 << 20, bytes_left)
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        bytes_left -= len(chunk)
                        yield chunk

            return StreamingResponse(
                iter_range(),
                status_code=206,
                headers={
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(content_length),
                    "Content-Type": media_type,
                }
            )
        except Exception:
            pass

    return FileResponse(path, media_type=media_type, headers={"Accept-Ranges": "bytes"})


@router.post("/{media_id}/clean", response_model=MediaOut)
def clean_again(media_id: int,
                user: models.User = Depends(get_current_user),
                db: Session = Depends(get_db)):
    m = _get_owned(db, media_id, user.id)
    try:
        media.clean_media(m.original_path, m.active_path, m.ext)
        m.active_sha256 = media.sha256_file(m.active_path)
        m.metadata_clean = True
        db.commit()
    except Exception as e:
        raise HTTPException(500, detail=f"Falha ao limpar metadados: {e}") from e
    return _out(m)


@router.post("/{media_id}/remix", response_model=MediaOut)
def remix_now(media_id: int,
              user: models.User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    m = _get_owned(db, media_id, user.id)
    tmp = Path(m.active_path).with_name(f"{uuid.uuid4().hex}_remix{m.ext}")
    try:
        media.make_variant(m.active_path, tmp, m.ext)
        Path(m.active_path).unlink(missing_ok=True)
        tmp.replace(m.active_path)
        m.active_sha256 = media.sha256_file(m.active_path)
        db.commit()
    except Exception as e:
        tmp.unlink(missing_ok=True)
        raise HTTPException(500, detail=f"Falha ao re-hashear: {e}") from e
    return _out(m)


@router.post("/reset-status")
def reset_all_media_status(account_id: Optional[int] = Query(None),
                           user: models.User = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    """Zera o status de envio (times_used = 0) para permitir iniciar uma nova rodada manualmente."""
    q = db.query(models.Media).filter(models.Media.user_id == user.id)
    if account_id is not None:
        q = q.filter((models.Media.account_id == account_id) | (models.Media.account_id.is_(None)))
    count = q.update({models.Media.times_used: 0})
    db.commit()
    return {"ok": True, "message": f"Status de envio resetado para {count} mídias.", "count": count}


@router.post("/{media_id}/reset-status", response_model=MediaOut)
def reset_single_media_status(media_id: int,
                              user: models.User = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    """Marca uma mídia individual como pendente (não enviada)."""
    m = _get_owned(db, media_id, user.id)
    m.times_used = 0
    db.commit()
    return _out(m)


@router.delete("/all/clear")
def delete_all_user_media(account_id: Optional[int] = Query(None),
                          user: models.User = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    """Exclui todas as mídias da biblioteca do usuário."""
    q = db.query(models.Media).filter(models.Media.user_id == user.id)
    if account_id is not None:
        q = q.filter((models.Media.account_id == account_id) | (models.Media.account_id.is_(None)))
    medias = q.all()
    count = 0
    for m in medias:
        db.query(models.Schedule).filter(models.Schedule.media_id == m.id).update({models.Schedule.media_id: None})
        for p in (m.original_path, m.active_path):
            Path(p).unlink(missing_ok=True)
        db.delete(m)
        count += 1
    db.commit()
    return {"ok": True, "deleted_count": count, "message": f"{count} mídias excluídas da biblioteca."}


@router.delete("/{media_id}")
def delete_media(media_id: int,
                 user: models.User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    m = _get_owned(db, media_id, user.id)
    db.query(models.Schedule).filter(models.Schedule.media_id == m.id).update({models.Schedule.media_id: None})
    for p in (m.original_path, m.active_path):
        Path(p).unlink(missing_ok=True)
    db.delete(m)
    db.commit()
    return {"ok": True}
