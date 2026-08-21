@echo off
title InstaFlow — Gerador de Link Publico
color 0B

cd /d "%~dp0"
python gerar_link.py
if errorlevel 1 (
    echo.
    echo Ocorreu um erro ao gerar o link publico.
    pause
)
pause
