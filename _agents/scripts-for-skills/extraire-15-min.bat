@echo off
title Extraction Live 15 Dernieres Minutes - Antigravity
color 0B

echo =======================================================================
echo   EXTRACTION DES 15 DERNIERES MINUTES DE DISCUSSION (1 CLIC)
echo =======================================================================
echo.

cd /d "C:\Users\hjamet\Documents\VoiceNotes"
python "_agents\scripts-for-skills\get_recent_transcript.py" --minutes 15 %*

if errorlevel 1 (
    echo.
    echo [ERREUR] L'extraction a rencontre une erreur.
    pause
    exit /b 1
)

echo.
echo =======================================================================
echo   Vous pouvez directement faire Ctrl+V dans le chat Antigravity !
echo =======================================================================
echo.
timeout /t 4 >nul 2>&1
