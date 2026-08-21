#!/usr/bin/env python3
"""
InstaFlow SaaS — Full Stack Launcher com Servidor Web + Túneis Públicos Automáticos.
"""
import os
import re
import sys
import time
import json
import threading
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
URL_FILE = DATA_DIR / "public_urls.json"

# Garante permissão executável no cloudflared
cloudflared_bin = BASE_DIR / "cloudflared"
if cloudflared_bin.exists():
    try:
        cloudflared_bin.chmod(0o755)
    except Exception:
        pass


def monitor_cloudflared(urls_dict):
    while True:
        try:
            cmd = [
                str(cloudflared_bin), "tunnel",
                "--url", "http://127.0.0.1:8000",
                "--protocol", "http2",
                "--no-autoupdate",
                "--heartbeat-interval", "5s",
            ]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            for line in iter(proc.stdout.readline, ""):
                m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                if m:
                    cf_url = m.group(0)
                    urls_dict["cloudflare"] = cf_url
                    print(f"\n⚡ [LINK_CLOUDFLARE_ATIVO]: {cf_url}\n", flush=True)
                    try:
                        with open(URL_FILE, "w") as f:
                            json.dump(urls_dict, f, indent=2)
                    except Exception:
                        pass
            proc.wait()
        except Exception as e:
            print(f"[Cloudflare Tunnel] Erro: {e}", flush=True)
        time.sleep(3)


def monitor_pinggy(urls_dict):
    while True:
        try:
            cmd = [
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-o", "ServerAliveInterval=10",
                "-o", "ServerAliveCountMax=3",
                "-p", "443",
                "-R0:localhost:8000",
                "a.pinggy.io",
            ]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            for line in iter(proc.stdout.readline, ""):
                m = re.search(r"https://[a-zA-Z0-9-]+\.run\.pinggy-free\.link", line) or re.search(r"https://[a-zA-Z0-9-]+\.free\.pinggy\.net", line)
                if m:
                    p_url = m.group(0)
                    urls_dict["pinggy"] = p_url
                    print(f"\n⚡ [LINK_PINGGY_ATIVO]: {p_url}\n", flush=True)
                    try:
                        with open(URL_FILE, "w") as f:
                            json.dump(urls_dict, f, indent=2)
                    except Exception:
                        pass
            proc.wait()
        except Exception as e:
            print(f"[Pinggy Tunnel] Erro: {e}", flush=True)
        time.sleep(3)


def main():
    import uvicorn
    from app.config import PORT

    urls = {"cloudflare": None, "pinggy": None, "local": f"http://0.0.0.0:{PORT}"}

    # Inicia threads dos túneis após 1 segundo (tempo de uvicorn subir)
    def start_tunnels():
        time.sleep(1.5)
        t_cf = threading.Thread(target=monitor_cloudflared, args=(urls,), daemon=True)
        t_pinggy = threading.Thread(target=monitor_pinggy, args=(urls,), daemon=True)
        t_cf.start()
        t_pinggy.start()

    threading.Thread(target=start_tunnels, daemon=True).start()

    # Inicia Uvicorn no thread principal
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=False)


if __name__ == "__main__":
    main()
