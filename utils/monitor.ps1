$ErrorActionPreference = "Stop"

# Fix character encoding issues in Windows Console
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
} catch {}
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=== Antigravity Cluster Monitor ===" -ForegroundColor Cyan

# 1. Retrieve supported models from agy
Write-Host "[Monitor] Detecting supported models..." -ForegroundColor Gray
$models = @()
try {
    $modelsOutput = & agy models 2>$null
    if ($modelsOutput) {
        foreach ($line in $modelsOutput) {
            $trimmed = $line.Trim()
            # Ignore headers if any, keep non-empty lines
            if (-not [string]::IsNullOrWhiteSpace($trimmed) -and $trimmed -notmatch "Available models" -and $trimmed -notmatch "^-") {
                $models += $trimmed
            }
        }
    }
} catch {}

# Fallback models if agy models detection failed or returned empty
if ($models.Count -eq 0) {
    $models = @("gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash", "gemini-1.5-pro")
}

# 2. Let user select a model
Write-Host ""
Write-Host "Sélectionnez le modèle à utiliser :" -ForegroundColor Cyan
for ($i = 0; $i -lt $models.Count; $i++) {
    Write-Host " [$($i + 1)] $($models[$i])" -ForegroundColor Gray
}

$choiceIndex = -1
while ($choiceIndex -lt 0 -or $choiceIndex -ge $models.Count) {
    $input = Read-Host "Entrez le numéro du modèle (par défaut 1)"
    if ([string]::IsNullOrWhiteSpace($input)) {
        $choiceIndex = 0
        break
    }
    if ([int]::TryParse($input, [ref]$val)) {
        $choiceIndex = $val - 1
    }
}
$selectedModel = $models[$choiceIndex]
Write-Host "Modèle choisi : $selectedModel" -ForegroundColor Green
Write-Host ""

# 3. Ask user for custom prompt context (multiline support)
Write-Host "=== Contexte Initial (Prompt Optionnel) ===" -ForegroundColor Cyan
Write-Host "Saisissez des instructions ou du contexte à ajouter au début de chaque appel de l'agent." -ForegroundColor Cyan
Write-Host "Collez votre texte et entrez 'EOF' sur une ligne vide pour valider :" -ForegroundColor Gray

$PromptLines = @()
while ($true) {
    $line = Read-Host
    if ($line.Trim() -eq 'EOF') {
        break
    }
    if ([string]::IsNullOrEmpty($line) -and $PromptLines.Count -gt 0 -and $PromptLines[-1] -eq "") {
        # Double entry on empty line terminates
        $PromptLines = $PromptLines[0..($PromptLines.Count-2)]
        break
    }
    if ([string]::IsNullOrEmpty($line) -and $PromptLines.Count -eq 0) {
        break
    }
    $PromptLines += $line
}
$userPromptContext = $PromptLines -join "`n"

if (-not [string]::IsNullOrWhiteSpace($userPromptContext)) {
    Write-Host "Contexte utilisateur enregistré." -ForegroundColor Green
} else {
    Write-Host "Aucun contexte utilisateur saisi." -ForegroundColor Gray
}
Write-Host ""

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

$HourlyIntervalSec = 3600

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
            
            $promptParts = @()
            if (-not [string]::IsNullOrWhiteSpace($userPromptContext)) {
                $promptParts += "CONTEXTE UTILISATEUR :`n$userPromptContext"
            }
            $promptParts += "Voici le fichier de logs actuel pour la commande cluster run :`n$logFilePath"
            $promptParts += "Vérifie que tout se passe bien et qu'il n'y a pas de problème. Réponds simplement par un court résumé ou diagnostic. Ne modifie aucun fichier."
            
            $prompt = $promptParts -join "`n`n---`n`n"
            $safePrompt = $prompt -replace '"', '\"'
            try {
                & agy --dangerously-skip-permissions --model "$selectedModel" --print "$safePrompt"
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
        
        $promptParts = @()
        if (-not [string]::IsNullOrWhiteSpace($userPromptContext)) {
            $promptParts += "CONTEXTE UTILISATEUR :`n$userPromptContext"
        }
        $promptParts += "La commande cluster run s'est arrêtée avec une erreur (code de sortie $exitCode).`nVoici les 100 dernières lignes de logs de la commande :`n$lastLogs"
        $promptParts += "Analyse ces logs et corrige l'erreur directement dans les fichiers de code source concernés.`nATTENTION : Modifie uniquement le code source pour corriger le problème. Ne lance aucune commande de build, de test ou d'exécution de processus. Ton unique rôle est de corriger le code et de t'arrêter proprement en expliquant ce que tu as fait."
        
        $prompt = $promptParts -join "`n`n---`n`n"
        $safePrompt = $prompt -replace '"', '\"'
        
        try {
            & agy --dangerously-skip-permissions --model "$selectedModel" --print "$safePrompt"
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
