@echo off
REM =====================================================================
REM Generatore Agenda Parrocchiale — Launcher Windows
REM =====================================================================
REM Uso:
REM   scripts\genera_agenda.bat [profilo] [anno]
REM
REM Esempi:
REM   scripts\genera_agenda.bat san_pietro_in_silki 2027
REM   scripts\genera_agenda.bat san_pietro_in_silki
REM =====================================================================

setlocal

REM Directory del progetto (parent di scripts\)
set "SCRIPT_DIR=%~dp0"
set "PROGETTO_DIR=%SCRIPT_DIR%.."

cd /d "%PROGETTO_DIR%"

REM Argomenti
set "PROFILO=%~1"
if "%PROFILO%"=="" set "PROFILO=san_pietro_in_silki"

set "ANNO=%~2"
if "%ANNO%"=="" (
    for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set "LD=%%i"
    set "ANNO=%LD:~0,4%"
)

echo ======================================================================
echo   GENERAZIONE AGENDA
echo   Profilo: %PROFILO%
echo   Anno:    %ANNO%
echo ======================================================================
echo.

REM Attiva venv se esiste
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo [ATTENZIONE] Nessun venv trovato in .venv\
    echo   Esegui prima: python -m venv .venv
    echo   e poi: pip install -r requirements.txt
    pause
    exit /b 1
)

REM STEP 1: Genera/aggiorna config.xlsx
echo ^>^>^> STEP 1/3: Generazione config.xlsx
python src\crea_config_template.py --profilo %PROFILO% --anno %ANNO% --force
if errorlevel 1 goto :errore
echo.

REM STEP 2: Genera PDF
echo ^>^>^> STEP 2/3: Generazione PDF
python -c "import sys; sys.path.insert(0, 'src'); from generatore_pdf import genera_pdf_da_profilo; percorso = genera_pdf_da_profilo('%PROFILO%'); print(f'PDF generato: {percorso}')"
if errorlevel 1 goto :errore
echo.

REM STEP 3: Riepilogo
echo ^>^>^> STEP 3/3: Riepilogo
set "PERCORSO_PDF=%PROGETTO_DIR%\output\Agenda_%ANNO%.pdf"
if exist "%PERCORSO_PDF%" (
    echo [OK] Fatto! PDF generato:
    echo      %PERCORSO_PDF%
    dir "%PERCORSO_PDF%"
) else (
    echo [ERRORE] PDF non trovato in %PERCORSO_PDF%
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo   COMPLETATO
echo ======================================================================
pause
exit /b 0

:errore
echo.
echo [ERRORE] Generazione fallita.
pause
exit /b 1