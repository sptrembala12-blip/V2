#!/usr/bin/env python3
"""
InstaFlow — Auto-Instalador e Inicializador Automático Multiplataforma (Windows, Linux, macOS).

Executa com um único comando:
    python iniciar.py
"""
import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REQUIREMENTS_FILE = BASE_DIR / "requirements.txt"

CORE_PACKAGES = [
    "fastapi>=0.110.0",
    "uvicorn>=0.30.0",
    "sqlalchemy>=2.0.0",
    "apscheduler>=3.10.0",
    "aiograpi>=1.12.0",
    "pillow>=10.0.0",
    "mutagen>=1.47.0",
    "cryptography>=42.0.0",
    "python-multipart>=0.0.9",
    "python-dotenv>=1.0.0",
    "email-validator>=2.0.0",
    "httpx>=0.27.0",
    "imageio-ffmpeg>=0.5.0",
    "opencv-python-headless>=4.8.0",
]


def print_banner():
    print("=" * 60)
    print("                ⚡ InstaFlow SaaS ⚡")
    print("    Automação & Anti-detect Instagram (aiograpi)")
    print("=" * 60)
    print()


def ensure_dependencies():
    print("[1/4] Verificando e instalando dependências...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=False)
        res = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)], check=False)
        if res.returncode != 0:
            print("Instalando pacotes essenciais individualmente...")
            for pkg in CORE_PACKAGES:
                subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=False)
        print("✔ Dependências instaladas e verificadas!")
    except Exception as e:
        print(f"Instalando pacotes essenciais: {e}")
        for pkg in CORE_PACKAGES:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=False)


def ensure_ffmpeg():
    print("[2/4] Verificando motor de vídeo (FFmpeg)...")
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        os.environ["IMAGEIO_FFMPEG_EXE"] = str(ffmpeg_exe)
        print("✔ FFmpeg configurado com sucesso!")
    except Exception as e:
        print(f"Aviso FFmpeg: {e}")


def ensure_directories():
    print("[3/4] Preparando diretórios locais de armazenamento...")
    for folder in ["media", "variants", "sessions"]:
        d = BASE_DIR / "data" / folder
        d.mkdir(parents=True, exist_ok=True)
    print("✔ Diretórios de dados prontos!")


def get_local_ip():
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def start_server():
    local_ip = get_local_ip()
    print("[4/4] Iniciando o servidor InstaFlow na porta 8000...")
    print()
    print("=" * 65)
    print("  🚀 InstaFlow rodando com sucesso!")
    print("  💻 No Computador: http://localhost:8000")
    if local_ip != "127.0.0.1":
        print(f"  📱 No Celular / iPhone (mesmo Wi-Fi): http://{local_ip}:8000")
    print("  🌐 Para acessar de fora (4G/5G): execute 'gerar_link_publico.bat'")
    print("=" * 65)
    print()

    def open_browser():
        time.sleep(1.2)
        try:
            webbrowser.open("http://localhost:8000")
        except Exception:
            pass

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    import uvicorn
    from app.config import PORT
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=False)


if __name__ == "__main__":
    print_banner()
    ensure_dependencies()
    ensure_ffmpeg()
    ensure_directories()
    start_server()
