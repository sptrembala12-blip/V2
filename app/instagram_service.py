"""
Gerenciador de clientes aiograpi por conta com suporte a proxy, 2FA legítimo,
validação de sessões prévias, checkpoint humanizado e dupla persistência (Disco + Banco).

Usa o aiograpi (fork assíncrono do instagrapi) através de uma ponte síncrona
(app.aiograpi_bridge.Client), mantendo o restante do aplicativo síncrono.
"""
from __future__ import annotations

import json
import threading
from typing import Optional

from aiograpi.exceptions import (
    BadCredentials,
    ChallengeRequired,
    ClientError,
    LoginRequired,
    TwoFactorRequired,
)

from . import config, fingerprint, security
from .aiograpi_bridge import Client, as_async_handler

ACCOUNT_STATUS_ACTIVE = "ativo"
ACCOUNT_STATUS_AWAITING_CODE = "aguardando_codigo"
ACCOUNT_STATUS_CHECKPOINT = "checkpoint"
ACCOUNT_STATUS_ERROR = "erro"
ACCOUNT_STATUS_CONNECTING = "conectando"


class IGManager:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory
        self._clients: dict[int, Client] = {}
        self._locks: dict[int, threading.Lock] = {}
        self._pending_codes: dict[int, dict] = {}

    def lock(self, account_id: int) -> threading.Lock:
        return self._locks.setdefault(account_id, threading.Lock())

    def _session_path(self, account_id: int):
        return config.SESSIONS_DIR / f"{account_id}.json"

    def get_client(self, account) -> Client:
        if account.id in self._clients:
            cl = self._clients[account.id]
            if account.proxy_url and cl.proxy != account.proxy_url:
                try:
                    cl.set_proxy(account.proxy_url)
                except Exception:
                    pass
            elif not account.proxy_url and cl.proxy:
                try:
                    cl.set_proxy(None)
                except Exception:
                    pass
            return cl

        cl = Client(
            proxy=account.proxy_url or None,
            delay_range=[max(1, account.delay_min), max(2, account.delay_max)],
        )

        fp = fingerprint.fingerprint_from_json(account.fingerprint_json)
        fingerprint.apply_to_client(cl, fp)

        cl.challenge_code_handler = as_async_handler(
            lambda username, choice=None: self._code_provider(account.id)
        )

        # Restauração resiliente de sessão (Disco ou Banco de Dados)
        session_path = self._session_path(account.id)
        loaded = False

        if session_path.exists():
            try:
                cl.load_settings(session_path)
                loaded = True
            except Exception:
                pass

        if not loaded and getattr(account, "session_data", None):
            try:
                settings_dict = json.loads(account.session_data)
                cl.set_settings(settings_dict)
                session_path.parent.mkdir(parents=True, exist_ok=True)
                session_path.write_text(json.dumps(settings_dict, indent=2), encoding="utf-8")
                loaded = True
            except Exception:
                pass

        self._clients[account.id] = cl
        return cl

    def save_session(self, account_id: int, cl: Client) -> None:
        """Salva a sessão em disco e persiste no banco de dados para suportar redeploys no Render."""
        try:
            settings = cl.get_settings()
            session_path = self._session_path(account_id)
            session_path.parent.mkdir(parents=True, exist_ok=True)
            session_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")

            from . import models
            with self.session_factory() as db:
                acc = db.get(models.Account, account_id)
                if acc:
                    acc.session_data = json.dumps(settings)
                    db.commit()
        except Exception as e:
            print(f"[Aviso] Falha ao persistir sessão da conta {account_id}: {e}")

    def drop_client(self, account_id: int) -> None:
        self._clients.pop(account_id, None)
        self._pending_codes.pop(account_id, None)

    def _code_provider(self, account_id: int) -> Optional[str]:
        event = threading.Event()
        self._pending_codes[account_id] = {"code": None, "event": event}
        self.update_status(
            account_id,
            ACCOUNT_STATUS_AWAITING_CODE,
            "Código 2FA solicitado pelo Instagram. Digite o código no campo de verificação.",
        )
        got = event.wait(timeout=config.CODE_TIMEOUT)
        state = self._pending_codes.pop(account_id, None)
        if got and state and state.get("code"):
            self.update_status(account_id, ACCOUNT_STATUS_CONNECTING, "Verificando código de segurança...")
            return state["code"]
        self.update_status(
            account_id,
            ACCOUNT_STATUS_AWAITING_CODE,
            "Tempo para digitação do código expirou. Clique em Reconectar.",
        )
        return None

    def submit_code(self, account_id: int, code: str) -> bool:
        state = self._pending_codes.get(account_id)
        if not state:
            return False
        state["code"] = code.strip()
        state["event"].set()
        return True

    def validate_existing_session(self, account, cl: Client) -> bool:
        """Valida se uma sessão já carregada ainda é aceita pelo Instagram sem forçar novo login."""
        if not cl.user_id:
            return False
        try:
            cl.get_timeline_feed()
            return True
        except (LoginRequired, BadCredentials):
            return False
        except Exception:
            # Erro temporário de rede ou rate limit leve — se o user_id existe, mantém
            return bool(cl.user_id)

    def login(self, account, force_reauth: bool = False, verification_code: str = "") -> dict:
        """
        Fluxo legítimo de autenticação:
        1. Se não for forçado e houver sessão válida salva, reutiliza imediatamente.
        2. Se não houver sessão ou estiver expirada, efetua login com credenciais.
        3. Se for fornecido verification_code (2FA), envia para autenticação em duas etapas.
        4. Suporta SessionID como método alternativo de importação com proteção contra loop de redirects.
        5. Trata 2FA e Checkpoints com instruções claras.
        """
        cl = self.get_client(account)

        # 1) Reutiliza sessão válida se disponível (apenas se não houver código 2FA sendo enviado)
        if not force_reauth and not verification_code and self.validate_existing_session(account, cl):
            self.save_session(account.id, cl)
            self.update_status(account.id, ACCOUNT_STATUS_ACTIVE, "Sessão válida restaurada com sucesso.")
            return {"logged_in": True, "user_id": str(cl.user_id), "restored": True}

        # 2) Login com credenciais
        password = security.decrypt_secret(account.ig_password_enc)

        # Opção de importação por SessionID / Cookie com proteção contra loop de redirects
        if password.startswith("sessionid:") or (len(password) > 30 and "%3A" in password):
            sessionid = password.removeprefix("sessionid:").strip()
            self._login_by_sessionid_resilient(cl, sessionid, account.ig_username)
        else:
            # Garante que proxy e parâmetros de localização móvel estão ativos
            if account.proxy_url:
                try:
                    cl.set_proxy(account.proxy_url)
                except Exception:
                    pass
            cl.set_country_code(55)
            cl.set_locale("pt_BR")
            cl.set_timezone_offset(-3 * 3600)

            # Login normal com Username e Password e suporte a verification_code (2FA)
            cl.login(
                account.ig_username,
                password,
                relogin=False,
                verification_code=verification_code.strip() if verification_code else "",
            )

        self.save_session(account.id, cl)
        self.update_status(account.id, ACCOUNT_STATUS_ACTIVE, "Conectado com sucesso ao Instagram.")
        return {"logged_in": True, "user_id": str(cl.user_id), "restored": False}

    def _login_by_sessionid_resilient(self, cl: Client, sessionid: str, username: str = "") -> None:
        """Configura login por SessionID com resiliência contra loops de redirect do GraphQL web."""
        import re

        sessionid = sessionid.strip().removeprefix("sessionid:")
        user_match = re.search(r"^\d+", sessionid)
        user_id = user_match.group() if user_match else None

        cl.settings["cookies"] = {"sessionid": sessionid}
        if user_id:
            cl.settings["cookies"]["ds_user_id"] = str(user_id)
        cl.init()

        if user_id:
            cl.authorization_data = {
                "ds_user_id": str(user_id),
                "sessionid": sessionid,
                "should_use_header_over_cookies": True,
            }
            if username:
                cl.username = username
            cl.private.cookies.set("sessionid", sessionid)
            cl.private.cookies.set("ds_user_id", str(user_id))
            cl.private.headers.update(cl.base_headers)
            try:
                if cl.authorization:
                    cl.private.headers.update({"Authorization": cl.authorization})
            except Exception:
                pass

        try:
            cl.login_by_sessionid(sessionid)
        except Exception as e:
            err_str = str(e).lower()
            if "redirect" in err_str or "toomanyredirects" in type(e).__name__.lower():
                # O endpoint web do Instagram entrou em loop. Testa se o endpoint privado funciona com esse cookie:
                try:
                    cl.get_timeline_feed()
                    return
                except Exception:
                    raise ValueError(
                        "O Cookie SessionID fornecido expirou no Instagram ou foi invalidado. "
                        "Gere um SessionID novo no navegador/app ou conecte informando Usuário + Senha."
                    )
            # Se já autenticou os cookies e o user_id é válido, aceita a sessão
            if cl.user_id:
                return
            raise

    def is_logged_in(self, account) -> bool:
        cl = self.get_client(account)
        return bool(cl.user_id)

    def ensure_logged_in(self, account) -> Client:
        cl = self.get_client(account)
        if not cl.user_id:
            self.login(account)
        return cl

    def warmup(self, account, cl: Client) -> list[str]:
        actions: list[str] = []
        try:
            cl.user_info(cl.user_id)
            actions.append("consultou o próprio perfil")
        except Exception:
            pass
        return actions

    def update_status(self, account_id: int, status: str, detail: str = "") -> None:
        try:
            from . import models

            with self.session_factory() as db:
                acc = db.get(models.Account, account_id)
                if acc:
                    acc.status = status
                    acc.status_detail = detail
                    db.commit()
        except Exception:
            pass


def map_login_error(e: Exception) -> tuple[str, str]:
    err_str = str(e).strip()
    err_type = type(e).__name__

    if "429" in err_str or "too many 429" in err_str.lower() or "too many requests" in err_str.lower() or "max retries exceeded" in err_str.lower() and "429" in err_str:
        return (
            ACCOUNT_STATUS_ERROR,
            "IP em repouso temporário no Instagram (Erro 429 - Muitas tentativas no IP). "
            "O Instagram colocou este IP em repouso por 15 a 30 minutos. "
            "Soluções: 1) Troque a porta do seu proxy para renovar o IP na operadora, ou "
            "2) Conecte via Cookie SessionID (clique em 'Opção de Recuperação / Importar via Cookie SessionID') para entrar imediatamente sem passar pela tela de login.",
        )

    if isinstance(e, TwoFactorRequired) or "two_factor" in err_str.lower() or "two-factor" in err_str.lower():
        return (
            ACCOUNT_STATUS_AWAITING_CODE,
            "Autenticação em dois fatores (2FA) solicitada. Digite o código de 6 dígitos recebido por SMS ou App Autenticador.",
        )

    if isinstance(e, ChallengeRequired) or "challenge_required" in err_str.lower() or "checkpoint" in err_str.lower():
        return (
            ACCOUNT_STATUS_CHECKPOINT,
            "O Instagram solicitou uma verificação de segurança (Checkpoint). "
            "Abra o aplicativo do Instagram no seu celular para aprovar o acesso ("
            "Fui Eu"
            ") ou confirme o código por SMS/e-mail. Em seguida, clique no botão 'Testar' para validar.",
        )

    if isinstance(e, (BadCredentials,)) or "bad_password" in err_str.lower() or "invalid credentials" in err_str.lower():
        return ACCOUNT_STATUS_ERROR, "Nome de usuário ou senha do Instagram incorretos. Verifique suas credenciais."

    if "ProxyAddressIsBlocked" in err_type or "blocked your ip" in err_str.lower():
        return ACCOUNT_STATUS_ERROR, "O endereço IP da conexão foi bloqueado temporariamente pelo Instagram. Recomenda-se o uso de um proxy residencial."

    if "PleaseWaitFewMinutes" in err_type or "throttled" in err_str.lower() or "too many requests" in err_str.lower():
        return ACCOUNT_STATUS_ERROR, "Muitas tentativas em pouco tempo. Aguarde alguns minutos antes de tentar novamente."

    if "UserNotFound" in err_type or "user not found" in err_str.lower():
        return ACCOUNT_STATUS_ERROR, "Perfil do Instagram não encontrado. Verifique o @ digitado."

    if "toomanyredirects" in err_type.lower() or "exceeded 30 redirects" in err_str.lower() or "redirect" in err_str.lower():
        return (
            ACCOUNT_STATUS_ERROR,
            "O Cookie SessionID expirou ou o Instagram redirecionou para o login web. Obtenha um novo SessionID no navegador ou conecte com Usuário + Senha.",
        )

    if isinstance(e, LoginRequired):
        return ACCOUNT_STATUS_ERROR, "Sessão expirada. Clique em 'Reconectar' para atualizar o acesso."

    # Erros de rede / TLS: sem rota até o Instagram (ambiente sem internet de
    # saída, proxy fora do ar/errado, DNS bloqueado ou firewall).
    _low = err_str.lower()
    _net_signs = (
        "tls/ssl connection has been closed", "_ssl.c", "eof occurred",
        "connecterror", "connecttimeout", "connectionerror", "connection refused",
        "connection reset", "connection aborted", "network is unreachable",
        "temporary failure in name resolution", "name or service not known",
        "getaddrinfo failed", "max retries exceeded", "ssleoferror",
        "connectproxyerror", "proxyerror", "read timed out", "timed out",
    )
    if any(s in _low for s in _net_signs) or err_type in (
        "ConnectError", "ConnectTimeout", "ConnectionError", "ReadTimeout",
        "ConnectProxyError", "ProxyError", "SSLError", "SSLEOFError",
    ):
        # Só atribui ao proxy quando o erro indica autenticação/407 de proxy.
        # (O aiograpi usa o nome ConnectProxyError mesmo em conexões diretas.)
        if "407" in _low or "proxy authentication" in _low or "proxyerror" == err_type.lower():
            return (
                ACCOUNT_STATUS_ERROR,
                "Não foi possível conectar ao Instagram através do proxy configurado. "
                "Verifique se o proxy está ativo e correto (use o botão 'Testar Proxy'), "
                "ou remova o proxy para usar a conexão direta do servidor.",
            )
        return (
            ACCOUNT_STATUS_ERROR,
            "Não foi possível alcançar o Instagram (falha de rede/TLS). "
            "Isso acontece quando o servidor não tem acesso à internet de saída — "
            "comum no ambiente de teste/preview. Rode o app em um servidor com internet "
            "(Render, Fly.io, VPS ou seu computador) e, se necessário, configure um proxy "
            "residencial/móvel. Detalhe técnico: " + err_str,
        )

    if isinstance(e, ClientError):
        return ACCOUNT_STATUS_ERROR, f"Mensagem do Instagram: {err_str}"

    return ACCOUNT_STATUS_ERROR, f"Falha na conexão com o Instagram: {err_str}"

