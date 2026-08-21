@echo off
title InstaFlow SaaS Launcher
color 0A

cd /d "%~dp0"
python iniciar.py
if errorlevel 1 (
    echo.
    echo Ocorreu um erro ao iniciar. Verifique se o Python esta instalado.
    pause
)
