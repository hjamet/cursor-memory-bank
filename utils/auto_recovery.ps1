###############################################################################
# Antigravity Auto-Recovery Script v2.1
# Monitors the Language Server for crashes and automatically sends the
# /continue workflow to conversations that were active during monitoring.
#
# Uses `agy --conversation <ID> -p <msg>` to wake up agents (not just
# deposit a message like agentapi send-message).
#
# Usage (run in a terminal EXTERNAL to the IDE):
#   powershell -NoExit -ExecutionPolicy Bypass -File utils\auto_recovery.ps1
#
# Parameters:
#   -PollIntervalSec   : How often to check for crashes (default: 5s)
#   -WaitAfterCrashSec : Time to wait for LS restart (default: 20s)
###############################################################################

param(
    [int]$PollIntervalSec   = 5,
    [int]$WaitAfterCrashSec = 20
)

$ErrorActionPreference = "Continue"

$mainLog     = "$env:APPDATA\Antigravity\logs\main.log"
$convosDir   = "$env:USERPROFILE\.gemini\antigravity\conversations"
$agentApi    = "$env:USERPROFILE\.gemini\antigravity\bin\agentapi.bat"
$agyCli      = "agy"
$crashMarker = "Language server crashed"

# ── Inline /continue workflow ────────────────────────────────────────────────

$continueMsg = @"
# Workflow de Reprise du Travail (Continue)

L'IDE a crashe (Language Server). Tous tes sous-agents, timers et cron jobs ont ete annules.

## 1. Diagnostic
- Consulte .agents/ pour identifier le dossier de coordination le plus recent.
- Lis le dernier fichier de progression pour determiner les taches interrompues.

## 2. Retablissement
- Relance les agents superviseurs et coordinateurs annules.
- Retablis les taches planifiees (cron jobs, timers) effaces lors de l'arret.
- Chaque superviseur relance ses sous-agents et commandes en cours.

## 3. Arbitrage de Reprise
- Si deja suffisamment de bugs identifies : enchaine sur l'Investigateur.
- Sinon : relance l'etape de validation.

## 4. Nettoyage
- Supprime les verrous orphelins (.git/index.lock, .dvc/tmp/lock).
- Enregistre une note AIVC (remember) pour marquer la reprise.
"@

# ── Helpers ──────────────────────────────────────────────────────────────────

function Write-Log($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    Write-Host "[$ts] $msg"
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

function Is-TopLevelConversation($convId) {
    try {
        $result = & $agentApi get-conversation-metadata $convId 2>$null
        $json = $result | ConvertFrom-Json
        $depth = [int]$json.response.conversationMetadata.metadata.nestingDepth
        return ($depth -eq 0)
    } catch {
        return $false
    }
}

function Take-DbSnapshot {
    $snapshot = @{}
    Get-ChildItem -Path $convosDir -Filter "*.db" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.BaseName -match '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        } |
        ForEach-Object {
            $snapshot[$_.BaseName] = $_.Length
        }
    return $snapshot
}

function Get-ChangedConversations($oldSnapshot, $newSnapshot) {
    $changed = @()
    foreach ($id in $newSnapshot.Keys) {
        if (-not $oldSnapshot.ContainsKey($id)) {
            $changed += $id
        } elseif (($newSnapshot[$id] - $oldSnapshot[$id]) -ge 10KB) {
            $changed += $id
        }
    }
    return $changed
}

function Send-Recovery($convId) {
    <#
      Tries agy first (true wake-up), falls back to agentapi (message deposit).
    #>
    # Try agy -p (forces agent execution)
    try {
        $process = Start-Process -FilePath $agyCli `
            -ArgumentList "--conversation", $convId, "-p", $continueMsg, "--print-timeout", "30s" `
            -NoNewWindow -PassThru -RedirectStandardOutput "NUL" -RedirectStandardError "NUL"

        # Don't wait for completion — fire and forget
        # agy will run in background and handle the conversation
        return "agy"
    } catch {
        # agy not available or failed, fall back to agentapi
        try {
            & $agentApi send-message $convId $continueMsg 2>$null | Out-Null
            return "agentapi"
        } catch {
            return $null
        }
    }
}

# ── Main Loop ────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "=========================================="
Write-Host "  Antigravity Auto-Recovery v2.1"
Write-Host "  Poll: ${PollIntervalSec}s | Wait: ${WaitAfterCrashSec}s"
Write-Host "  Mode: Track conversations during runtime"
Write-Host "  Wake: agy -p (fallback: agentapi)"
Write-Host "=========================================="
Write-Host ""

$lastCrashLine = Get-LastCrashLineNumber
$baselineSnapshot = Take-DbSnapshot
$trackedConversations = @{}

Write-Log "Baseline: $($baselineSnapshot.Count) conversations snapshotted"
Write-Log "Monitoring $mainLog (last crash at line $lastCrashLine)"
Write-Log "Press Ctrl+C to stop."
Write-Host ""

while ($true) {
    Start-Sleep -Seconds $PollIntervalSec

    # ── Track new/growing conversations ──
    $currentSnapshot = Take-DbSnapshot
    $changed = Get-ChangedConversations $baselineSnapshot $currentSnapshot
    foreach ($id in $changed) {
        if (-not $trackedConversations.ContainsKey($id)) {
            $trackedConversations[$id] = $true
            Write-Log "Tracking: $id"
        }
    }
    $baselineSnapshot = $currentSnapshot

    # ── Check for crash ──
    $currentCrashLine = Get-LastCrashLineNumber
    if ($currentCrashLine -le $lastCrashLine) { continue }

    # ── Crash detected! ──
    $lastCrashLine = $currentCrashLine
    Write-Host ""
    Write-Log "!!! CRASH DETECTED !!! (line $currentCrashLine)"
    Write-Log "Tracked conversations: $($trackedConversations.Count)"
    Write-Log "Waiting ${WaitAfterCrashSec}s for LS restart..."
    Start-Sleep -Seconds $WaitAfterCrashSec

    if (-not (Wait-ForLanguageServer)) {
        Write-Log "WARNING: LS did not restart. Skipping recovery."
        continue
    }

    Write-Log "LS is back. Filtering top-level conversations..."

    $topLevel = @()
    foreach ($id in $trackedConversations.Keys) {
        if (Is-TopLevelConversation $id) {
            $topLevel += $id
        }
    }

    Write-Log "Sending /continue to $($topLevel.Count) top-level conversation(s):"

    if ($topLevel.Count -eq 0) {
        Write-Log "  (none to notify)"
    } else {
        $sent = 0
        foreach ($id in $topLevel) {
            $method = Send-Recovery $id
            if ($method) {
                Write-Log "  OK  ($method) -> $id"
                $sent++
            } else {
                Write-Log "  FAIL -> $id"
            }
        }
        Write-Log "Recovery complete: $sent/$($topLevel.Count) notified."
    }

    # Reset tracking for next cycle
    $trackedConversations = @{}
    $baselineSnapshot = Take-DbSnapshot
    Write-Host ""
    Write-Log "Tracking reset. Resuming monitoring..."
}
