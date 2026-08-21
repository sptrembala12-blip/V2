"""Dependências do FastAPI: sessão de banco e autenticação multi-dispositivo."""
from __future__ import annotations

from fastapi import Cookie, Depends, Header, HTTPException, Query, Request
from sqlalchemy.orm import Session

from . import models
from .database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    authorization: str = Header(default=""),
    x_auth_token: str = Header(default="", alias="X-Auth-Token"),
    token_cookie: str = Cookie(default="", alias="token"),
    token_query: str = Query(default="", alias="token"),
    db: Session = Depends(get_db),
) -> models.User:
    token = ""
    if authorization:
        if authorization.lower().startswith("bearer "):
            token = authorization[7:].strip()
        else:
            token = authorization.strip()
    elif x_auth_token:
        token = x_auth_token.strip()
    elif token_cookie:
        token = token_cookie.strip()
    elif token_query:
        token = token_query.strip()

    if not token:
        raise HTTPException(401, detail="Não autenticado. Faça login.")

    row = db.query(models.AuthToken).filter(models.AuthToken.token == token).first()
    if row is None:
        raise HTTPException(401, detail="Sessão inválida ou expirada. Faça login.")
    user = db.get(models.User, row.user_id)
    if user is None:
        raise HTTPException(401, detail="Usuário não encontrado.")
    return user
