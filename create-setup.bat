@echo off
echo [1/3] Limpando builds antigos...
if exist build rmdir /s /q build

echo [2/3] Gerando Build do Flet para Windows...
flet build windows

echo [3/3] Compilando Instalador com Inno Setup...
:: O caminho abaixo é o padrão do Inno Setup. Verifique se a sua versão é a 6.
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" InnoSetup\installer.iss

echo.
echo ======================================================
echo PROCESSO CONCLUIDO!
echo O instalador esta em: InnoSetup\Output\SAFTEC-Setup.exe
echo ======================================================
pause