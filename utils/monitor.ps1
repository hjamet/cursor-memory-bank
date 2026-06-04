$ErrorActionPreference = "Stop"

# Fix character encoding issues in Windows Console
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
} catch {}
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=== Antigravity Cluster Monitor ===" -ForegroundColor Cyan

# 1. Models list
$models = @(
    "Gemini 3.5 Flash (Medium)",
    "Gemini 3.5 Flash (High)",
    "Gemini 3.5 Flash (Low)",
    "Gemini 3.1 Pro (Low)",
    "Gemini 3.1 Pro (High)",
    "Claude Sonnet 4.6 (Thinking)",
    "Claude Opus 4.6 (Thinking)",
    "GPT-OSS 120B (Medium)"
)

# 2. Let user select a model
Write-Host ""
function Show-Menu {
    param(
        [string]$Title,
        [string[]]$Options
    )
    $selectedIndex = 0
    $needsRedraw = $true
    
    $useClearHost = $false
    try {
        # Allocate lines to prevent scrolling during redraw
        $linesNeeded = $Options.Count + 1
        for ($i = 0; $i -lt $linesNeeded; $i++) { Write-Host "" }
        [Console]::SetCursorPosition(0, [Console]::CursorTop - $linesNeeded)
        $topPos = [Console]::CursorTop
    } catch {
        $useClearHost = $true
    }
    
    while ($true) {
        if ($needsRedraw) {
            if ($useClearHost) {
                Clear-Host
            } else {
                [Console]::SetCursorPosition(0, $topPos)
            }
            $padWidth = if ($Host.UI.RawUI.WindowSize.Width -gt 0) { $Host.UI.RawUI.WindowSize.Width - 1 } else { 80 }
            Write-Host $Title.PadRight($padWidth) -ForegroundColor Cyan
            for ($i = 0; $i -lt $Options.Count; $i++) {
                $line = if ($i -eq $selectedIndex) { " > $($Options[$i])" } else { "   $($Options[$i])" }
                $paddedLine = $line.PadRight($padWidth)
                
                if ($i -eq $selectedIndex) {
                    Write-Host $paddedLine -ForegroundColor Green -NoNewline
                } else {
                    Write-Host $paddedLine -ForegroundColor Gray -NoNewline
                }
                
                if ($i -lt $Options.Count - 1) {
                    Write-Host ""
                }
            }
            $needsRedraw = $false
        }
        
        $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        if ($key.VirtualKeyCode -eq 38) { # Up arrow
            $selectedIndex--
            if ($selectedIndex -lt 0) { $selectedIndex = $Options.Count - 1 }
            $needsRedraw = $true
        } elseif ($key.VirtualKeyCode -eq 40) { # Down arrow
            $selectedIndex++
            if ($selectedIndex -ge $Options.Count) { $selectedIndex = 0 }
            $needsRedraw = $true
        } elseif ($key.VirtualKeyCode -eq 13) { # Enter
            if (-not $useClearHost) {
                try {
                    [Console]::SetCursorPosition(0, $topPos + $Options.Count)
                    Write-Host ""
                    Write-Host ""
                } catch {}
            }
            return $selectedIndex
        }
    }
}

$choiceIndex = Show-Menu -Title "Selectionnez le modele a utiliser :" -Options $models
$selectedModel = $models[$choiceIndex]
Write-Host "Modele choisi : $selectedModel" -ForegroundColor Green
Write-Host ""

# 3. Ask user for custom prompt context (multiline support)
Write-Host "=== Contexte Initial (Prompt Optionnel) ===" -ForegroundColor Cyan
Write-Host "Saisissez des instructions ou du contexte a ajouter au debut de chaque appel de l'agent." -ForegroundColor Cyan
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
    Write-Host "Contexte utilisateur enregistre." -ForegroundColor Green
} else {
    Write-Host "Aucun contexte utilisateur saisi." -ForegroundColor Gray
}
Write-Host ""

# 4. Ask user for check interval
Write-Host "=== Frequence de verification ===" -ForegroundColor Cyan
Write-Host "A quelle frequence (en minutes) l'agent doit-il se reveiller pour analyser les logs de la commande en cours ?" -ForegroundColor Cyan

$intervalInput = Read-Host "Entrez le nombre de minutes (par defaut 60)"
if ([string]::IsNullOrWhiteSpace($intervalInput)) {
    $intervalInput = "60"
}
$intervalMin = 60
if ([int]::TryParse($intervalInput, [ref]$intervalMin)) {
    if ($intervalMin -le 0) { $intervalMin = 60 }
} else {
    $intervalMin = 60
}
$intervalSec = $intervalMin * 60
Write-Host "Verification toutes les $intervalMin minutes ($intervalSec secondes)." -ForegroundColor Green
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
        
        # Periodic check-in
        if ($timeSinceLastCheck -ge $intervalSec) {
            $timeSinceLastCheck = 0
            Write-Host "[Monitor] Periodic check timer ($intervalMin min) triggered. Waking up agent..." -ForegroundColor Cyan
            
            $promptParts = @()
            if (-not [string]::IsNullOrWhiteSpace($userPromptContext)) {
                $promptParts += "CONTEXTE UTILISATEUR :`n$userPromptContext"
            }
            $promptParts += "Voici le fichier de logs actuel pour la commande cluster run :`n$logFilePath"
            
            $promptParts += @"
INSTRUCTIONS IMPORTANTES DE DIAGNOSTIC :
Exécute une analyse critique approfondie et globale des logs de la commande :
1. Recherche des erreurs, avertissements ou comportements anormaux PARTOUT dans le log, et pas seulement à la fin.
2. Analyse les timings/horodatages des logs pour identifier des ralentissements suspects, des temps morts anormalement longs (freezes) ou des problèmes de vitesse d'exécution.
3. Rédige un diagnostic détaillé des performances et signale tout problème majeur.
4. Si tu détermines qu'il n'y a aucun problème et que tout se passe bien, tu n'as rien à faire : termine simplement ton intervention sans rien modifier. En revanche, si tu détectes des anomalies ou des résultats étranges, corrige tous les problèmes trouvés dans le code source.

CONSIGNES DE SÉCURITÉ :
- La commande suit actuellement son cours. Tes modifications éventuelles de code seront prises en compte automatiquement lors du prochain run de la commande par le script de monitoring.
- INTERDICTION ABSOLUE de lancer toi-même la commande 'cluster-run', de compiler, de tester ou d'exécuter des processus. Le script de monitoring / le cluster s'en charge automatiquement. Ton rôle est uniquement de diagnostiquer, de modifier le code source si nécessaire, et de t'arrêter proprement.
"@
            
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
        
        $promptParts += @"
INSTRUCTIONS IMPORTANTES DE CORRECTION :
Analyse ces logs et corrige l'erreur directement dans les fichiers de code source concernés :
1. Recherche l'origine de l'erreur dans l'ensemble des logs fournis, pas seulement sur la dernière ligne.
2. Analyse les timings/horodatages des logs pour identifier si l'erreur est liée à un freeze, un timeout ou un temps mort anormal.
3. Corrige le code source pour régler ce problème.

CONSIGNES DE SÉCURITÉ :
- Tes modifications de code seront prises en compte lors du prochain run.
- INTERDICTION ABSOLUE de lancer toi-même la commande 'cluster-run', de compiler, de tester ou d'exécuter des processus. Ton unique rôle est de modifier le code source pour corriger le problème et de t'arrêter proprement en expliquant ce que tu as fait. Le script de monitoring se charge de relancer la commande après ton arrêt.
"@
        
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
