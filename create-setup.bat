@echo off
setlocal enabledelayedexpansion

:INICIO
cls
echo ======================================================
echo           SAFTEC - BUILD AUTOMATIZADO
echo ======================================================
echo.

REM ── Limpa a variável e pede a versão ───────────────────
set "VERSION="
set /p VERSION=">>> Digite a versao (ex: 1.2.0): "

if "%VERSION%"=="" (
    echo.
    echo [ERRO] Versao nao informada.
    timeout /t 2 >nul
    goto :INICIO
)

REM ── Valida formato x.y.z (COLADO NO PIPE) ──────────────
echo %VERSION%| findstr /R "^[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*$" >nul

if errorlevel 1 (
    echo.
    echo [ERRO] Formato "%VERSION%" invalido.
    timeout /t 3 >nul
    goto :INICIO
)

REM ── SE PASSOU NA VALIDAÇÃO, CONTINUA AQUI ──────────────
echo.
echo [OK] Versao %VERSION% validada!
echo.

REM ── Atualiza version.py automaticamente ────────────────
echo [1/7] Atualizando version.py...
echo APP_VERSION = "%VERSION%" > version.py
echo Arquivo version.py atualizado.

REM ... O resto do seu código de build vem aqui ...
REM Para testar se ele para, você pode colocar um 'pause' temporário aqui:
echo Teste: Validacao concluida. Iniciando processos...
pause

REM ── Atualiza installer.iss automaticamente ─────────────
echo [2/7] Atualizando installer.iss...
powershell -Command "(Get-Content 'InnoSetup\installer.iss') -replace 'AppVersion=.*', 'AppVersion=%VERSION%' -replace 'OutputBaseFilename=.*', 'OutputBaseFilename=SAFTEC_Setup_%VERSION%' | Set-Content 'InnoSetup\installer.iss'"
echo installer.iss atualizado.

REM ── Limpa builds antigos ───────────────────────────────
echo [3/7] Limpando builds antigos...
if exist data rmdir /s /q data
if exist build rmdir /s /q build
if exist InnoSetup\Output rmdir /s /q InnoSetup\Output

REM ── Instala Firefox do Playwright na pasta do projeto ──
echo [4/7] Instalando Firefox do Playwright no projeto...
set PLAYWRIGHT_BROWSERS_PATH=%CD%\ms-playwright
uv run playwright install firefox
if errorlevel 1 (
    echo ERRO: Falha ao instalar o Firefox do Playwright.
    pause & exit /b 1
)

REM ── Build Flet ─────────────────────────────────────────
echo [5/7] Gerando Build Flet para Windows...
uv run fleting db init
uv run fleting db migrate 
uv run flet build windows
if errorlevel 1 (
    echo ERRO: Falha no flet build.
    pause & exit /b 1
)

REM ── Gera version.json para auto-update ─────────────────
echo [6/7] Gerando version.json...
if not exist InnoSetup\Output mkdir InnoSetup\Output
echo {"version": "%VERSION%", "url": "https://github.com/bernardonogueira8/AppSAFTE/releases/download/v%VERSION%/SAFTEC_Setup_%VERSION%.exe"} > InnoSetup\Output\version.json
echo version.json gerado.

REM ── Compila instalador ─────────────────────────────────
echo [7/7] Compilando instalador com Inno Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" InnoSetup\installer.iss
if errorlevel 1 (
    echo ERRO: Falha no Inno Setup.
    pause & exit /b 1
)

REM ── Resumo final ───────────────────────────────────────
echo.
echo ======================================================
echo  BUILD CONCLUIDO COM SUCESSO!
echo  Versao   : %VERSION%
echo  Installer: InnoSetup\Output\SAFTEC_Setup_%VERSION%.exe
echo  JSON     : InnoSetup\Output\version.json
echo ======================================================
echo.

REM ── Pergunta se quer abrir a pasta de output ───────────
set /p OPEN="Abrir pasta de output? [s/n]: "
if /i "%OPEN%"=="s" explorer InnoSetup\Output

REM ── Pergunta se quer publicar no GitHub ────────────────
set /p PUBLISH="Publicar release no GitHub agora? [s/n]: "
if /i "%PUBLISH%"=="s" (
    where gh >nul 2>&1
    if errorlevel 1 (
        echo AVISO: GitHub CLI nao encontrado. Instale em https://cli.github.com
    ) else (
        git add version.py InnoSetup\installer.iss
        git commit -m "chore: bump version to %VERSION%"
        git tag v%VERSION%
        git push origin main --force
        git push origin v%VERSION%
        gh release create v%VERSION% ^
            "InnoSetup\Output\SAFTEC_Setup_%VERSION%.exe" ^
            "InnoSetup\Output\version.json" ^
            --title "v%VERSION%" ^
            --notes "Release %VERSION%"
        echo Release v%VERSION% publicada no GitHub!
    )
)

pause