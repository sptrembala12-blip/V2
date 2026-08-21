"""
Serviço de E-mails Temporários compatíveis com Instagram e extração de códigos 2FA/Confirmação.
"""
from __future__ import annotations

import re
import secrets
import httpx
from typing import Optional, Dict, Any, List


def extract_instagram_code(text: str, subject: str = "") -> Optional[str]:
    """Extrai automaticamente códigos de 6 dígitos enviados pelo Instagram/Meta."""
    full_text = f"{subject}\n{text}"
    
    # 1. Padrão explícito do Instagram ("123456 é o seu código do Instagram" ou "123 456")
    m_ig = re.search(r"(\d{3}\s?\d{3})\s*(?:is your Instagram code|é o seu código|é seu código|is your code|código)", full_text, re.IGNORECASE)
    if m_ig:
        return m_ig.group(1).replace(" ", "")

    m_prefix = re.search(r"(?:code|código|código de confirmação|confirmation code|security code)[:\s]+(\d{6})", full_text, re.IGNORECASE)
    if m_prefix:
        return m_prefix.group(1)

    # 2. Procura sequências de 6 dígitos no texto
    matches = re.findall(r"\b(\d{6})\b", full_text)
    if matches:
        # Retorna o primeiro código válido encontrado
        return matches[0]

    # 3. Formato 3 dígitos + espaço + 3 dígitos (ex: 123 456)
    m_space = re.findall(r"\b(\d{3})\s(\d{3})\b", full_text)
    if m_space:
        return f"{m_space[0][0]}{m_space[0][1]}"

    return None


class TempEmailService:
    @staticmethod
    def generate_mailtm(prefix: Optional[str] = None) -> Dict[str, Any]:
        """Gera conta no Mail.tm (domínios limpos aceitos pelo Instagram)."""
        with httpx.Client(timeout=12) as client:
            r_dom = client.get("https://api.mail.tm/domains")
            if r_dom.status_code != 200:
                raise RuntimeError("Falha ao obter domínios do provedor primário.")
            domains = [d["domain"] for d in r_dom.json().get("hydra:member", []) if d.get("isActive")]
            if not domains:
                raise RuntimeError("Nenhum domínio ativo disponível no momento.")
            
            domain = domains[0]
            user_stem = prefix.strip().lower() if prefix else f"insta{secrets.token_hex(4)}"
            email = f"{user_stem}@{domain}"
            password = f"Pass_{secrets.token_hex(8)}!"

            r_acc = client.post("https://api.mail.tm/accounts", json={"address": email, "password": password})
            if r_acc.status_code not in (200, 201):
                # Se o nome já existe, tenta com sufixo aleatório
                email = f"{user_stem}{secrets.token_hex(2)}@{domain}"
                r_acc = client.post("https://api.mail.tm/accounts", json={"address": email, "password": password})
                if r_acc.status_code not in (200, 201):
                    raise RuntimeError(f"Erro ao criar conta: {r_acc.text}")

            r_tok = client.post("https://api.mail.tm/token", json={"address": email, "password": password})
            token = r_tok.json().get("token")

            return {
                "provider": "mailtm",
                "email": email,
                "token": token,
                "password": password,
                "domain": domain,
            }

    @staticmethod
    def get_inbox_mailtm(token: str) -> List[Dict[str, Any]]:
        """Busca mensagens recebidas no Mail.tm."""
        with httpx.Client(timeout=12) as client:
            headers = {"Authorization": f"Bearer {token}"}
            r = client.get("https://api.mail.tm/messages", headers=headers)
            if r.status_code != 200:
                return []
            
            items = r.json().get("hydra:member", [])
            messages = []
            for item in items:
                msg_id = item.get("id")
                subject = item.get("subject", "Sem assunto")
                from_addr = item.get("from", {}).get("address", "")
                intro = item.get("intro", "")
                created_at = item.get("createdAt", "")
                
                # Extração do código do Instagram
                code = extract_instagram_code(intro, subject)

                messages.append({
                    "id": msg_id,
                    "from": from_addr,
                    "subject": subject,
                    "intro": intro,
                    "created_at": created_at,
                    "code_extracted": code,
                    "is_instagram": ("instagram" in from_addr.lower() or "instagram" in subject.lower() or "meta" in from_addr.lower()),
                })
            return messages

    @staticmethod
    def get_message_mailtm(msg_id: str, token: str) -> Dict[str, Any]:
        """Obtém o conteúdo completo de um e-mail no Mail.tm."""
        with httpx.Client(timeout=12) as client:
            headers = {"Authorization": f"Bearer {token}"}
            r = client.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers)
            if r.status_code != 200:
                raise RuntimeError("Mensagem não encontrada.")
            
            data = r.json()
            body_text = data.get("text", "")
            body_html = data.get("html", "")
            subject = data.get("subject", "")
            code = extract_instagram_code(body_text or body_html, subject)

            return {
                "id": data.get("id"),
                "from": data.get("from", {}).get("address", ""),
                "subject": subject,
                "text": body_text,
                "html": body_html,
                "created_at": data.get("createdAt", ""),
                "code_extracted": code,
            }

    @staticmethod
    def generate_guerrilla() -> Dict[str, Any]:
        """Gera sessão temporária no GuerrillaMail."""
        with httpx.Client(timeout=12) as client:
            r = client.get("https://api.guerrillamail.com/ajax.php?f=get_email_address")
            if r.status_code != 200:
                raise RuntimeError("Falha ao conectar ao GuerrillaMail.")
            data = r.json()
            email = data.get("email_addr")
            sid_token = data.get("sid_token")
            return {
                "provider": "guerrilla",
                "email": email,
                "token": sid_token,
                "domain": email.split("@")[-1] if "@" in email else "",
            }

    @staticmethod
    def get_inbox_guerrilla(sid_token: str) -> List[Dict[str, Any]]:
        """Busca mensagens no GuerrillaMail."""
        with httpx.Client(timeout=12) as client:
            r = client.get(f"https://api.guerrillamail.com/ajax.php?f=check_email&seq=0&sid_token={sid_token}")
            if r.status_code != 200:
                return []
            data = r.json()
            messages = []
            for item in data.get("list", []):
                # Pula e-mail de boas-vindas do GuerrillaMail
                if "Welcome to Guerrilla" in item.get("mail_subject", ""):
                    continue
                subject = item.get("mail_subject", "")
                excerpt = item.get("mail_excerpt", "")
                from_addr = item.get("mail_from", "")
                code = extract_instagram_code(excerpt, subject)
                messages.append({
                    "id": str(item.get("mail_id")),
                    "from": from_addr,
                    "subject": subject,
                    "intro": excerpt,
                    "created_at": item.get("mail_date", ""),
                    "code_extracted": code,
                    "is_instagram": ("instagram" in from_addr.lower() or "instagram" in subject.lower()),
                })
            return messages

    @staticmethod
    def get_message_guerrilla(msg_id: str, sid_token: str) -> Dict[str, Any]:
        """Obtém mensagem completa do GuerrillaMail."""
        with httpx.Client(timeout=12) as client:
            r = client.get(f"https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={msg_id}&sid_token={sid_token}")
            if r.status_code != 200:
                raise RuntimeError("Mensagem não encontrada.")
            data = r.json()
            body = data.get("mail_body", "")
            subject = data.get("mail_subject", "")
            code = extract_instagram_code(body, subject)
            return {
                "id": str(data.get("mail_id")),
                "from": data.get("mail_from", ""),
                "subject": subject,
                "text": body,
                "html": body if "<" in body else "",
                "created_at": data.get("mail_date", ""),
                "code_extracted": code,
            }
