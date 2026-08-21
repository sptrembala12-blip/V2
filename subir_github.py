#!/usr/bin/env python3
"""
InstaFlow — Assistente para Subir o Código no GitHub (Passo a Passo Automático).
"""
import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def print_banner():
    print("=" * 60)
    print("        🚀 InstaFlow — Publicar no GitHub 🚀")
    print("=" * 60)
    print()


def check_git():
    try:
        res = subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            return True
    except Exception:
        pass
    return False


def main():
    print_banner()

    if not check_git():
        print("⚠️ O utilitário 'git' não foi detectado no seu computador.")
        print()
        print("Como fazer o upload direto pelo navegador (sem Git):")
        print("1. Abra o site do seu repositório no GitHub (github.com).")
        print("2. Clique no botão 'Add file' -> 'Upload files'.")
        print("3. Arraste todos os arquivos e pastas de dentro da pasta 'instaflow'.")
        print("4. Clique no botão verde 'Commit changes'.")
        print()
        input("Pressione Enter para sair...")
        return

    print("Este assistente vai subir todos os arquivos descompactados no seu GitHub.")
    print()
    repo_url = input("👉 Cole a URL do seu repositório GitHub (ex: https://github.com/seu-usuario/instaflow.git): ").strip()

    if not repo_url:
        print("❌ Nenhuma URL informada. Cancelando.")
        input("\nPressione Enter para sair...")
        return

    print("\n[1/4] Inicializando repositório Git local...")
    subprocess.run(["git", "init"], cwd=str(BASE_DIR))

    print("[2/4] Adicionando arquivos do InstaFlow...")
    subprocess.run(["git", "add", "."], cwd=str(BASE_DIR))

    print("[3/4] Criando commit inicial...")
    subprocess.run(["git", "commit", "-m", "InstaFlow SaaS v1.0"], cwd=str(BASE_DIR))
    subprocess.run(["git", "branch", "-M", "main"], cwd=str(BASE_DIR))

    print("[4/4] Conectando ao repositório remoto e enviando...")
    subprocess.run(["git", "remote", "remove", "origin"], cwd=str(BASE_DIR), stderr=subprocess.DEVNULL)
    subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=str(BASE_DIR))

    res = subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=str(BASE_DIR))

    if res.returncode == 0:
        print()
        print("=" * 60)
        print("  🎉 CÓDIGO PUBLICADO COM SUCESSO NO GITHUB!")
        print("  Agora você pode conectar no Render.com ou Fly.io.")
        print("=" * 60)
    else:
        print()
        print("⚠️ Ocorreu um aviso no envio. Se o repositório exigir autenticação,")
        print("faça login no Git ou use o método de arrastar os arquivos pelo site.")

    input("\nPressione Enter para finalizar...")


if __name__ == "__main__":
    main()
