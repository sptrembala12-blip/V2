"""
Serviço de envio de e-mails reais (SMTP com suporte a Gmail, Resend, SendGrid, Mailgun)
com fallback inteligente para visualização direta de códigos.
"""
from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "InstaFlow <noreply@instaflow.app>")


def is_smtp_configured() -> bool:
    return bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def send_email_code(to_email: str, code: str, subject_type: str = "verification") -> dict:
    """Envia código de 6 dígitos por e-mail real via SMTP com fallback."""
    subject = (
        "Seu Código de Ativação — InstaFlow"
        if subject_type == "verification"
        else "Seu Código de Redefinição de Senha — InstaFlow"
    )

    action_text = (
        "para ativar sua conta e liberar o acesso ao painel de automação"
        if subject_type == "verification"
        else "para confirmar a redefinição da sua senha de acesso"
    )

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #07090e; color: #f1f5f9; padding: 30px; margin: 0; }}
        .card {{ max-width: 480px; margin: 0 auto; background: #111726; border: 1px solid #1e293b; border-radius: 16px; padding: 32px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        .logo {{ font-size: 22px; font-weight: 800; color: #6366f1; margin-bottom: 16px; text-align: center; }}
        .title {{ font-size: 18px; font-weight: 700; color: #ffffff; text-align: center; margin-bottom: 8px; }}
        .sub {{ font-size: 13.5px; color: #94a3b8; text-align: center; line-height: 1.5; margin-bottom: 24px; }}
        .code-box {{ background: #07090e; border: 2px dashed #6366f1; border-radius: 12px; padding: 18px; text-align: center; font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #6366f1; margin-bottom: 24px; font-family: monospace; }}
        .footer {{ font-size: 11.5px; color: #64748b; text-align: center; border-top: 1px solid #1e293b; padding-top: 16px; }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="logo">InstaFlow</div>
        <div class="title">Código de Segurança</div>
        <div class="sub">Utilize o código de 6 dígitos abaixo {action_text}:</div>
        <div class="code-box">{code}</div>
        <div class="footer">Se você não solicitou este código, por favor ignore este e-mail.<br>InstaFlow SaaS — Todos os direitos reservados.</div>
      </div>
    </body>
    </html>
    """

    if is_smtp_configured():
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = SMTP_FROM
            msg["To"] = to_email

            text_content = f"InstaFlow - Seu código de segurança: {code}\nUtilize este código {action_text}."
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            if SMTP_PORT == 465:
                server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=12)
            else:
                server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=12)
                server.starttls()

            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, [to_email], msg.as_string())
            server.quit()

            print(f"✔ [E-mail Enviado com Sucesso] Código {code} enviado via SMTP para {to_email}")
            return {"sent": True, "method": "smtp", "message": f"Código enviado para o e-mail {to_email}."}
        except Exception as e:
            print(f"⚠️ [Falha no envio SMTP para {to_email}]: {e}")
            return {
                "sent": False,
                "method": "fallback",
                "error": str(e),
                "message": f"Código de segurança gerado: {code}",
            }

    # Se SMTP não estiver configurado nas variáveis de ambiente, usa o fallback na tela
    print(f"ℹ [SMTP não configurado] Código {code} para {to_email} (Defina SMTP_HOST, SMTP_USER, SMTP_PASSWORD no Render para disparo real)")
    return {
        "sent": False,
        "method": "fallback",
        "message": f"Código de ativação: {code}",
    }
