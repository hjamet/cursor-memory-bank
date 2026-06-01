###############################################################################
# Antigravity Auto-Recovery Script
# Monitors the Language Server for crashes and automatically sends the
# /continue workflow instructions to all recently-active top-level
# conversations, so agents resume their work without manual intervention.
#
# Usage (run in a terminal EXTERNAL to the IDE):
#   powershell -NoExit -ExecutionPolicy Bypass -File utils\auto_recovery.ps1
#
# Parameters:
#   -PollIntervalSec     : How often to check for crashes (default: 5s)
#   -WaitAfterCrashSec   : Time to wait for LS restart before recovery (default: 20s)
#   -ActiveWindowMinutes : Only notify conversations active within this window (default: 30)
###############################################################################

param(
    [int]$PollIntervalSec     = 5,
    [int]$WaitAfterCrashSec   = 20,
    [int]$ActiveWindowMinutes = 30
)

$ErrorActionPreference = "Continue"

$mainLog     = "$env:APPDATA\Antigravity\logs\main.log"
$convosDir   = "$env:USERPROFILE\.gemini\antigravity\conversations"
$agentApi    = "$env:USERPROFILE\.gemini\antigravity\bin\agentapi.bat"
$crashMarker = "Language server crashed"

# ── Inline /continue workflow ────────────────────────────────────────────────
# Injected directly so agents get the full instructions without needing to
# read any file.

$continueMsg = @"
# Workflow de Reprise du Travail (Continue)

**Objectif** : Restaurer l'environnement et relancer toutes les taches, agents, superviseurs et programmations temporelles suite a une interruption inattendue (crash d'IDE, redemarrage du serveur, etc.).

> **EFFET DE L'INTERRUPTION :**
> 1. Les agents et sous-agents en cours d'execution ont pu etre annules.
> 2. Les taches d'arriere-plan, les timers et les taches planifiees (schedule / cron jobs) ont ete supprimes.
> 3. Ce workflow permet de tout retablir de maniere coherente pour reprendre le travail.

## 1. Diagnostic de l'Etat du Projet

1. **Recherche de l'etat** :
   Consulte le dossier .agents/ a la racine pour identifier le dossier de coordination ou de travail le plus recent.
2. **Identifier les taches interrompues** :
   Lis le dernier fichier de progression (progression_summary.md ou similaire) et inspecte les sous-dossiers actifs pour determiner exactement quel agent et quelle tache etaient en cours d'execution avant l'interruption.

## 2. Retablissement et Relance

Puisque toute l'infrastructure agentique et temporelle a ete arretee, retablis le flux de travail de maniere ordonnee :

1. **Relancer les agents superviseurs et coordinateurs** :
   Instancie a nouveau le ou les agents principaux annules (comme le Coordinator ou le Monitor) avec leur prompt initial et l'etat de reprise.
2. **Retablir les taches de supervision (Schedules)** :
   Demande a chaque niveau de supervision de reenregistrer ses taches planifiees (cron jobs de check, timers) qui ont ete effaces lors de l'arret.
3. **Restaurer les sous-agents et les commandes en cours** :
   Chaque superviseur doit a son tour relancer ses propres sous-agents et reactiver les taches ou commandes en cours qui ont ete annulees.

## 3. Arbitrage Intelligent de Reprise (Validation / Review)

Si le travail a ete interrompu en pleine phase de validation ou de review (Reviewer, Reviewer Final) :

- **Arbitrage** : S'il y a deja suffisamment d'anomalies averees et de bugs importants identifies a corriger, ne perds pas de temps a faire tourner a nouveau l'etape de validation. Enchaine immediatement sur l'Investigateur pour analyser et corriger directement les bugs et iterer plus rapidement.
- **Sinon** (ex: processus de validation live critique ou benchmark en cours avec logs interessants), relance l'etape de validation pour finaliser l'analyse.

## 4. Nettoyage Rapide
- Supprime les verrous orphelins (ex: .git/index.lock ou .dvc/tmp/lock) qui pourraient bloquer la reprise des commandes.
- Enregistre une note memoire AIVC (remember) pour marquer le point de relance et la reprise effective de l'activite.
"@

# ── Helpers ──────────────────────────────────────────────────────────────────

function Write-Log($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts] $msg"
}

function Get-ActiveTopLevelConversations {
    $cutoff = (Get-Date).AddMinutes(-$ActiveWindowMinutes)
    $dbs = Get-ChildItem -Path $convosDir -Filter "*.db" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.LastWriteTime -gt $cutoff -and
            $_.Length -gt 200KB -and
            $_.BaseName -match '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        } |
        Sort-Object LastWriteTime -Descending

    $topLevel = @()
    foreach ($db in $dbs) {
        $id = $db.BaseName
        try {
            $result = & $agentApi get-conversation-metadata $id 2>$null
            $json = $result | ConvertFrom-Json
            $depth = [int]$json.response.conversationMetadata.metadata.nestingDepth
            if ($depth -eq 0) {
                $topLevel += $id
            }
        } catch {
            # Skip conversations that can't be queried
        }
    }
    return $topLevel
}

function Get-LastCrashLineNumber {
    if (-not (Test-Path $mainLog)) { return -1 }
    $lines = Get-Content $mainLog -ErrorAction SilentlyContinue
    for ($i = $lines.Count - 1; $i -ge 0; $i--) {
        if ($lines[$i] -match [regex]::Escape($crashMarker)) {
            return $i
        }
    }
    return -1
}

function Wait-ForLanguageServer {
    for ($attempt = 1; $attempt -le 6; $attempt++) {
        try {
            & $agentApi get-conversation-metadata "00000000-0000-0000-0000-000000000000" 2>$null | Out-Null
            return $true
        } catch {}
        Write-Log "  LS not ready (attempt $attempt/6), waiting 5s..."
        Start-Sleep -Seconds 5
    }
    return $false
}

# ── Main Loop ────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "=========================================="
Write-Host "  Antigravity Auto-Recovery v1.1"
Write-Host "  Poll: ${PollIntervalSec}s | Wait: ${WaitAfterCrashSec}s"
Write-Host "  Active window: ${ActiveWindowMinutes}min"
Write-Host "=========================================="
Write-Host ""

$lastCrashLine = Get-LastCrashLineNumber
Write-Log "Monitoring $mainLog (last crash at line $lastCrashLine)"
Write-Log "Press Ctrl+C to stop."
Write-Host ""

while ($true) {
    Start-Sleep -Seconds $PollIntervalSec

    $currentCrashLine = Get-LastCrashLineNumber
    if ($currentCrashLine -le $lastCrashLine) { continue }

    # ── Crash detected! ──
    $lastCrashLine = $currentCrashLine
    Write-Host ""
    Write-Log "!!! CRASH DETECTED !!! (line $currentCrashLine)"
    Write-Log "Waiting ${WaitAfterCrashSec}s for LS restart..."
    Start-Sleep -Seconds $WaitAfterCrashSec

    if (-not (Wait-ForLanguageServer)) {
        Write-Log "WARNING: LS did not restart. Skipping recovery."
        continue
    }

    Write-Log "LS is back. Finding active top-level conversations..."
    $topLevel = Get-ActiveTopLevelConversations

    if ($topLevel.Count -eq 0) {
        Write-Log "No active top-level conversations found."
        continue
    }

    Write-Log "Sending /continue to $($topLevel.Count) conversation(s):"
    $sent = 0
    foreach ($id in $topLevel) {
        try {
            & $agentApi send-message $id $continueMsg 2>$null | Out-Null
            Write-Log "  OK  -> $id"
            $sent++
        } catch {
            Write-Log "  FAIL -> $id"
        }
    }

    Write-Log "Recovery complete: $sent/$($topLevel.Count) notified."
    Write-Host ""
    Write-Log "Resuming monitoring..."
}
