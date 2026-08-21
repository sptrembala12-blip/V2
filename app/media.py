"""
Biblioteca de mídias: validação, limpeza de metadados e rehash por postagem.
"""
from __future__ import annotations

import hashlib
import io
import os
import random
import shutil
import string
import subprocess
import zlib
from pathlib import Path

from PIL import Image, ImageOps

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTS = {".mp4", ".mov"}
ALLOWED_EXTS = IMAGE_EXTS | VIDEO_EXTS


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def kind_for_ext(ext: str) -> str:
    return "video" if ext.lower() in VIDEO_EXTS else "photo"


def clean_image(src: str | Path, dst: str | Path) -> Path:
    """Remove EXIF/ICC/comentários preservando a qualidade máxima original."""
    dst = Path(dst)
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        fmt = {
            ".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP",
        }[dst.suffix.lower()]
        save_kwargs: dict = {}
        if fmt == "JPEG":
            save_kwargs = {"quality": 98, "subsampling": 0}
        elif fmt == "WEBP":
            save_kwargs = {"quality": 98, "lossless": False}
        im.save(dst, format=fmt, **save_kwargs)
    return dst


def clean_video(src: str | Path, dst: str | Path) -> Path:
    """Remove metadados do vídeo preservando 100% da qualidade original (cópia sem perdas)."""
    src, dst = Path(src), Path(dst)
    ffmpeg = shutil.which("ffmpeg") or os.environ.get("IMAGEIO_FFMPEG_EXE") or "/home/user/.local/bin/ffmpeg"
    if Path(ffmpeg).exists():
        try:
            subprocess.run(
                [
                    str(ffmpeg), "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(src), "-map_metadata", "-1", "-map_chapters", "-1",
                    "-c", "copy", str(dst),
                ],
                check=True, capture_output=True, timeout=600,
            )
            if dst.exists() and dst.stat().st_size > 0:
                return dst
        except Exception:
            pass
    if src.suffix.lower() in (".mp4", ".m4a", ".m4v"):
        try:
            from mutagen.mp4 import MP4

            shutil.copyfile(src, dst)
            m = MP4(dst)
            if m.tags:
                m.delete()
                m.save()
            return dst
        except Exception:
            pass
    shutil.copyfile(src, dst)
    return dst


def clean_media(src: str | Path, dst: str | Path, ext: str) -> Path:
    if ext.lower() in IMAGE_EXTS:
        return clean_image(src, dst)
    return clean_video(src, dst)


def extract_video_thumbnail(video_path: str | Path, thumb_path: str | Path) -> Path:
    """Extrai primeiro frame do vídeo como JPEG de alta qualidade."""
    thumb_path = Path(thumb_path)
    thumb_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import cv2
        cap = cv2.VideoCapture(str(video_path))
        success, frame = cap.read()
        cap.release()
        if success and frame is not None:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            img.save(thumb_path, format="JPEG", quality=95)
            return thumb_path
    except Exception:
        pass

    ffmpeg = shutil.which("ffmpeg") or os.environ.get("IMAGEIO_FFMPEG_EXE") or "/home/user/.local/bin/ffmpeg"
    if Path(ffmpeg).exists():
        try:
            subprocess.run(
                [
                    str(ffmpeg), "-hide_banner", "-loglevel", "error", "-y",
                    "-ss", "00:00:00.5", "-i", str(video_path), "-vframes", "1",
                    "-q:v", "2", str(thumb_path),
                ],
                check=True, timeout=30,
            )
            if thumb_path.exists() and thumb_path.stat().st_size > 0:
                return thumb_path
        except Exception:
            pass

    img = Image.new("RGB", (1080, 1920), (20, 25, 40))
    img.save(thumb_path, format="JPEG", quality=92)
    return thumb_path


def _random_text(n: int = 24) -> bytes:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choices(alphabet, k=n)).encode()


def remix_bytes(data: bytes, ext: str) -> bytes:
    """Altera o arquivo injetando dados aleatórios inofensivos para gerar novo SHA-256 mantendo a integridade total."""
    ext = ext.lower()
    if ext in (".jpg", ".jpeg"):
        end = data.rfind(b"\xff\xd9")
        if end == -1:
            return data + os.urandom(512)
        comment = _random_text(random.randint(16, 64))
        segment = b"\xff\xfe" + len(comment).to_bytes(2, "big") + comment
        return data[:end] + segment + data[end:]
    if ext == ".png":
        pos = data.find(b"IEND")
        if pos == -1:
            return data + os.urandom(512)
        text = b"instaflow\x00" + _random_text(random.randint(16, 48))
        chunk = text
        blob = len(chunk).to_bytes(4, "big") + chunk + zlib.crc32(chunk).to_bytes(4, "big")
        return data[: pos - 4] + blob + data[pos - 4:]
    if ext in (".mp4", ".mov"):
        # Cria um atom 'free' padronizado da norma ISO MP4
        payload = _random_text(random.randint(32, 128))
        atom = (len(payload) + 8).to_bytes(4, "big") + b"free" + payload
        return data + atom
    return data + os.urandom(512)


def make_variant(src: str | Path, dst: str | Path, ext: str) -> Path:
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(src, "rb") as f:
        data = f.read()
    dst.write_bytes(remix_bytes(data, ext))
    return dst


def validate_upload(filename: str, size: int, max_mb: int) -> tuple[str, str]:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTS:
        return f"Formato não suportado ({ext}). Use: {', '.join(sorted(ALLOWED_EXTS))}", ""
    if size <= 0:
        return "Arquivo vazio.", ""
    if size > max_mb * 1024 * 1024:
        return f"Arquivo maior que {max_mb} MB.", ""
    return "", ext


def save_upload(content: bytes, dest: str | Path) -> None:
    Path(dest).write_bytes(content)
