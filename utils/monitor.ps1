param(
    [int]$HourlyIntervalSec = 3600
)

$ErrorActionPreference = "Stop"

# Fix character encoding issues in Windows Console
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
} catch {}
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=== Antigravity Cluster Monitor ===" -ForegroundColor Cyan
Write-Host "Monitoring the 'cluster-run' command..." -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop the monitoring script." -ForegroundColor Gray
Write-Host ""

$tempDir = [System.IO.Path]::GetTempPath()
$stdoutFile = Join-Path $tempDir "cluster_run_stdout.log"
$stderrFile = Join-Path $tempDir "cluster_run_stderr.log"

function Start-ClusterRun {
    if (Test-Path $stdoutFile) { Remove-Item $stdoutFile }
    if (Test-Path $stderrFile) { Remove-Item $stderrFile }
    
    Write-Host "[Monitor] Launching 'cluster-run' in background..." -ForegroundColor Green
    $proc = Start-Process -FilePath "powershell.exe" `
                          -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"cluster-run`"" `
                          -RedirectStandardOutput $stdoutFile `
                          -RedirectStandardError $stderrFile `
                          -NoNewWindow `
                          -PassThru
    return $proc
}

# Main process execution and monitoring loop
$running = $true
while ($running) {
    $process = Start-ClusterRun
    $logFilePath = $null
    
    # 1. Detect log file path from output stream
    Write-Host "[Monitor] Waiting to detect log file path..." -ForegroundColor Yellow
    $detected = $false
    for ($i = 0; $i -lt 30; $i++) {
        if ($process.HasExited) {
            Write-Host "[Monitor] Process exited prematurely." -ForegroundColor Red
            break
        }
        if (Test-Path $stdoutFile) {
            $content = Get-Content -Path $stdoutFile -ErrorAction SilentlyContinue
            foreach ($line in $content) {
                if ($line -match "Logs are duplicated to:\s*(.*)" -or $line -match "Logs written to:\s*(.*)" -or $line -match "Log file:\s*(.*)") {
                    $logFilePath = $Matches[1].Trim()
                    $detected = $true
                    break
                }
            }
        }
        if ($detected) { break }
        Start-Sleep -Seconds 1
    }
    
    if (-not $logFilePath) {
        Write-Warning "[Monitor] Log file path could not be detected from stdout. Using stdout redirection file as fallback."
        $logFilePath = $stdoutFile
    } else {
        Write-Host "[Monitor] Log file detected: $logFilePath" -ForegroundColor Green
    }
    
    # 2. Monitor process state
    $timeSinceLastCheck = 0
    $checkInterval = 10 # Check process status every 10 seconds
    
    while (-not $process.HasExited) {
        Start-Sleep -Seconds $checkInterval
        $timeSinceLastCheck += $checkInterval
        
        # Hourly check-in
        if ($timeSinceLastCheck -ge $HourlyIntervalSec) {
            $timeSinceLastCheck = 0
            Write-Host "[Monitor] Hourly check timer triggered. Waking up agent..." -ForegroundColor Cyan
            
            $prompt = @"
Voici le fichier de logs actuel pour la commande cluster run :
$logFilePath

Vérifie que tout se passe bien et qu'il n'y a pas de problème. Réponds simplement par un court résumé ou diagnostic. Ne modifie aucun fichier.
"@
            $safePrompt = $prompt -replace '"', '\"'
            try {
                & agy --dangerously-skip-permissions --print "$safePrompt"
            } catch {
                Write-Host "[Monitor] Failed to invoke agy check: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
    
    # 3. Process has exited. Handle exit codes
    $exitCode = $process.ExitCode
    Write-Host "[Monitor] Process exited with code: $exitCode" -ForegroundColor Yellow
    
    if ($exitCode -ne 0) {
        # Process crashed! Read last logs and request correction from agy
        Write-Host "[Monitor] ERROR/CRASH DETECTED. Reading last 100 log lines..." -ForegroundColor Red
        $lastLogs = ""
        if (Test-Path $logFilePath) {
            $lastLogs = Get-Content -Path $logFilePath -Tail 100 | Out-String
        }
        
        Write-Host "[Monitor] Waking up agent in non-interactive print mode for repair..." -ForegroundColor Cyan
        $prompt = @"
La commande cluster run s'est arrêtée avec une erreur (code de sortie $exitCode).
Voici les 100 dernières lignes de logs de la commande :
$lastLogs

Analyse ces logs et corrige l'erreur directement dans les fichiers de code source concernés.
ATTENTION : Modifie uniquement le code source pour corriger le problème. Ne lance aucune commande de build, de test ou d'exécution de processus. Ton unique rôle est de corriger le code et de t'arrêter proprement en expliquant ce que tu as fait.
"@
        $safePrompt = $prompt -replace '"', '\"'
        
        try {
            & agy --dangerously-skip-permissions --print "$safePrompt"
            Write-Host "[Monitor] Agent repair finished. Restarting cluster-run..." -ForegroundColor Green
        } catch {
            Write-Host "[Monitor] Failed to run agy repair agent: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "[Monitor] Waiting 10 seconds before restarting..." -ForegroundColor Yellow
            Start-Sleep -Seconds 10
        }
    } else {
        # Process completed successfully
        Write-Host ""
        $choice = Read-Host "La commande s'est terminee proprement. [R]elancer, ou [Q]uitter le script ? (R/Q)"
        if ($choice -match '^[qQ]') {
            Write-Host "Fin de la supervision." -ForegroundColor Green
            $running = $false
        } else {
            Write-Host "Relancement..." -ForegroundColor Cyan
        }
    }
}
