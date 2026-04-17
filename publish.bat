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