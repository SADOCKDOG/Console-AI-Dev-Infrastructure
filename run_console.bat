@echo off
title Autonomous Dev Control Center - Sdog Farm Software Factory
cd /d "%~dp0"
echo Iniciando Consola de Gestion Integral de Escritorio para Windows...
echo Organizacion: Sdog Farm Software Factory (sadogfarm.onmicrosoft.com)
echo.
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocurrio un error al ejecutar la consola.
    pause
)
