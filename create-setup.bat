@echo off
echo [1/4] Limpando builds antigos...
if exist build rmdir /s /q build
if exist fleting.db rmdir /s /q fleting.db

echo [2/4] Força a instalação dentro da pasta 'pw-browsers' ou similar
set PLAYWRIGHT_BROWSERS_PATH=0  
playwright install firefox

echo [3/4] Gerando Build do Flet para Windows...
uv run fleting init
uv run fleting db migrate

uv run flet build windows

echo [4/4] Compilando Instalador com Inno Setup...
:: O caminho abaixo é o padrão do Inno Setup. Verifique se a sua versão é a 6.
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" InnoSetup\installer.iss

echo.
echo ======================================================
echo PROCESSO CONCLUIDO!
echo O instalador esta em: InnoSetup\Output\SAFTEC-Setup.exe
echo ======================================================
pause