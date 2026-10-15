@echo off
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
 py -3 painel.py
) else (
 python painel.py
)
if errorlevel 1 (
 echo Nao foi possivel abrir. Instale Python 3 com Tkinter e tente novamente.
 pause
)
