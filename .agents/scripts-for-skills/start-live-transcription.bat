chcp 65001 > nul
@echo off
title Transcripteur Live GPU Whisper - Antigravity
color 0A

echo =======================================================================
echo   DEMARRAGE DU TRANSCRIPTEUR LIVE GPU WHISPER (Faster-Whisper)
echo =======================================================================
echo.
echo Capture audio : Micro par defaut (16 kHz Mono float32)
echo Infeence      : GPU CUDA FP16 (RTX 3060)
echo Sortie MD     : VoiceNotes\voicenotes\Live Session [YYYY-MM-DD].md
echo Serveur API   : http://localhost:3055/recent?minutes=10
echo.
echo Pressez Ctrl+C pour arreter la transcription a tout moment.
echo =======================================================================
echo.

cd /d "C:\Users\hjamet\Documents\VoiceNotes"
python "_agents\scripts-for-skills\live_transcriber.py" %*

if errorlevel 1 (
    echo.
    echo [ERREUR] Le transcripteur s'est arrete avec un code d'erreur.
    pause
)

