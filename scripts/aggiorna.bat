@echo off
REM =====================================================================
REM Aggiorna Agenda Parrocchiale da GitHub
REM =====================================================================
REM Uso:
REM   Doppio clic su questo file per aggiornare l'applicazione.
REM
REM Fa:
REM   1. git pull (scarica le novità)
REM   2. Aggiorna le dipendenze Python
REM   3. Mostra un riepilogo
REM
REM NON tocca i tuoi dati (config.xlsx, intenzioni, ecc.)
REM =====================================================================

setlocal

REM Directory del progetto (parent di scripts\)
set "SCRIPT_DIR=%~dp0"
set "PROGETTO_DIR=%SCRIPT_DIR%.."

cd /d "%PROGETTO_DIR%"

echo ======================================================================
echo   AGGIORNAMENTO AGENDA PARROCCHIALE
echo ======================================================================
echo.

REM Verifica che git sia disponibile
where git >nul 2>nul
if errorlevel 1 (
    echo [ERRORE] Git non trovato nel PATH.
    echo   Installa Git da https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Verifica che siamo in un repository git
if not exist ".git" (
    echo [ERRORE] Questa cartella non e' un repository Git.
    echo   Assicurati di aver scaricato il progetto con:
    echo     git clone https://github.com/hac114/agenda-parrocchiale.git
    pause
    exit /b 1
)

REM STEP 1: git pull
echo ^>^>^> STEP 1/3: Scarico le novita' da GitHub
git pull
if errorlevel 1 (
    echo.
    echo [ERRORE] git pull non riuscito.
    echo   Possibili cause:
    echo   - Connessione Internet assente
    echo   - Modifiche locali in conflitto
    echo   Contatta il supporto tecnico.
    pause
    exit /b 1
)
echo.

REM STEP 2: Aggiorna dipendenze (se il venv esiste)
echo ^>^>^> STEP 2/3: Aggiornamento dipendenze Python
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    pip install --upgrade -r requirements.txt --quiet
    if errorlevel 1 (
        echo [ATTENZIONE] Aggiornamento dipendenze non riuscito.
        echo   Il programma potrebbe funzionare comunque.
        echo   Se hai problemi, contatta il supporto.
    ) else (
        echo     [OK] Dipendenze aggiornate
    )
) else (
    echo [ATTENZIONE] Nessun venv trovato in .venv\
    echo   Esegui prima: python -m venv .venv
    echo   e poi: pip install -r requirements.txt
)
echo.

REM STEP 3: Riepilogo
echo ^>^>^> STEP 3/3: Riepilogo
echo.
echo ======================================================================
echo   AGGIORNAMENTO COMPLETATO
echo ======================================================================
echo.
echo   I tuoi dati (config.xlsx, intenzioni, ecc.) NON sono stati toccati.
echo.
echo   Per generare il PDF aggiornato:
echo     1. Doppio clic su scripts\genera_agenda.bat
echo.
pause
exit /b 0