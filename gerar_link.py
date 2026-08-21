#!/usr/bin/env python3
"""
Gerador de Link Público Seguro para o InstaFlow (via Cloudflare Tunnel).
Funciona automaticamente no Windows, Linux e macOS sem necessidade de cadastro.
"""
import os
import re
import sys
import time
import urllib.request
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def print_banner():
    print("=" * 65)
    print("        ⚡ InstaFlow — Gerador de Link Público Gratuito ⚡")
    print("                (Acesse de qualquer celular ou PC)")
    print("=" * 65)
    print()


def check_local_server():
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/api/health")
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.status == 200:
                return True
    except Exception:
        pass
    return False


def get_cloudflared_binary():
    import platform
    system = platform.system().lower()

    if system == "windows":
        bin_name = "cloudflared.exe"
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    elif system == "darwin":
        bin_name = "cloudflared"
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64"
    else:
        bin_name = "cloudflared"
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"

    bin_path = BASE_DIR / bin_name
    if not bin_path.exists():
        print(f"Baixando utilitário oficial seguro do Cloudflare ({bin_name})...")
        try:
            urllib.request.urlretrieve(url, str(bin_path))
            if system != "windows":
                bin_path.chmod(0o755)
            print("✔ Utilitário pronto!")
        except Exception as e:
            print(f"Erro ao baixar: {e}")
            return None
    return str(bin_path)


def start_tunnel():
    print("[1/2] Verificando se o InstaFlow está aberto...")
    if not check_local_server():
        print("⚠️ O InstaFlow ainda não foi iniciado na porta 8000!")
        print("👉 Inicie o 'iniciar.bat' primeiro em outra janela.")
        print("Aguardando o servidor iniciar...")
        for _ in range(15):
            time.sleep(2)
            if check_local_server():
                print("✔ Servidor local detectado!")
                break
        else:
            print("❌ Servidor local não respondeu. Certifique-se de que o 'iniciar.bat' está rodando.")
            input("\nPressione Enter para sair...")
            return

    binary = get_cloudflared_binary()
    if not binary:
        print("Não foi possível inicializar o Cloudflare Tunnel.")
        input("\nPressione Enter para sair...")
        return

    print()
    print("[2/2] Conectando aos servidores globais com criptografia HTTPS...")
    print("Aguarde alguns segundos para gerar seu link seguro...")
    print()

    cmd = [
        binary, "tunnel",
        "--url", "http://127.0.0.1:8000",
        "--protocol", "http2",
        "--no-autoupdate",
        "--heartbeat-interval", "5s",
    ]
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        found_url = None
        for line in iter(proc.stdout.readline, ""):
            match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if match:
                found_url = match.group(0)
                print("=" * 65)
                print("  🎉 SEU LINK PÚBLICO COM HTTPS ESTÁ ATIVO:")
                print(f"  👉 {found_url}")
                print("=" * 65)
                print()
                print("  📱 Abra este link no seu celular ou em outro computador.")
                print("  ⚡ O InstaFlow abrirá com login sincronizado e PWA!")
                print("=" * 65)
                print("\n(Mantenha esta janela aberta enquanto quiser acessar externamente)")
                break

        proc.wait()
    except KeyboardInterrupt:
        print("\nLink público encerrado.")
    except Exception as e:
        print(f"\nErro ao iniciar tunnel: {e}")
        input("\nPressione Enter para sair...")


if __name__ == "__main__":
    print_banner()
    start_tunnel()
