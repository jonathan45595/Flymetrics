@echo off
title Flymetrics - Tunel Cloudflare Seguro
cls
echo ================================================================
echo      FLYMETRICS - TUNEL CLOUDFLARE PUBLICO (100%% GRATUITO)
echo ================================================================
echo.
echo  Iniciando conexion directa HTTP/2 hacia http://127.0.0.1:3000...
echo.

"%~dp0cloudflared.exe" tunnel --protocol http2 --url http://127.0.0.1:3000

pause
