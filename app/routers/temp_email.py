"""
Rotas para o Gerador de E-mails Temporários Compatíveis com Instagram.
"""
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ..deps import get_current_user
from ..models import User
from ..temp_email import TempEmailService

router = APIRouter(prefix="/api/temp-email", tags=["temp-email"])


class GenerateEmailIn(BaseModel):
    provider: str = Field("mailtm", pattern="^(mailtm|guerrilla)$")
    prefix: Optional[str] = Field(None, max_length=30)


@router.post("/generate")
def generate_email(body: GenerateEmailIn = GenerateEmailIn(),
                   user: User = Depends(get_current_user)):
    """Gera um e-mail temporário compatível com Instagram para receber códigos de confirmação."""
    try:
        if body.provider == "guerrilla":
            data = TempEmailService.generate_guerrilla()
        else:
            try:
                data = TempEmailService.generate_mailtm(prefix=body.prefix)
            except Exception:
                # Fallback para GuerrillaMail se Mail.tm estiver temporariamente fora
                data = TempEmailService.generate_guerrilla()
        return data
    except Exception as e:
        raise HTTPException(500, detail=f"Erro ao gerar e-mail temporário: {e}") from e


@router.get("/inbox")
def get_inbox(provider: str = Query("mailtm"),
              token: str = Query(...),
              user: User = Depends(get_current_user)):
    """Consulta mensagens recebidas na caixa de entrada e extrai códigos do Instagram."""
    try:
        if provider == "guerrilla":
            messages = TempEmailService.get_inbox_guerrilla(token)
        else:
            messages = TempEmailService.get_inbox_mailtm(token)
        
        # Encontra se há algum código recente detectado
        latest_code = None
        for m in messages:
            if m.get("code_extracted"):
                latest_code = m.get("code_extracted")
                break

        return {
            "messages": messages,
            "latest_code": latest_code,
            "total": len(messages),
        }
    except Exception as e:
        return {"messages": [], "latest_code": None, "error": str(e)}


@router.get("/message/{msg_id}")
def get_message(msg_id: str,
                provider: str = Query("mailtm"),
                token: str = Query(...),
                user: User = Depends(get_current_user)):
    """Busca o conteúdo completo (texto e HTML) de um e-mail recebido."""
    try:
        if provider == "guerrilla":
            data = TempEmailService.get_message_guerrilla(msg_id, token)
        else:
            data = TempEmailService.get_message_mailtm(msg_id, token)
        return data
    except Exception as e:
        raise HTTPException(404, detail=f"Mensagem não encontrada: {e}") from e
