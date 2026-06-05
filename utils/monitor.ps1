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
$monitorLogPath = Join-Path (Get-Location).Path ".monitor.log"
if (Test-Path $monitorLogPath) { Clear-Content -Path $monitorLogPath -ErrorAction SilentlyContinue }
$global:lastMonitorLogSize = 0

function Read-HostWithEscape {
    param([string]$Prompt)
    Write-Host $Prompt -NoNewline -ForegroundColor Yellow
    $inputStr = ""
    while ($true) {
        $k = [Console]::ReadKey($true)
        if ($k.Key -eq [System.ConsoleKey]::Enter) {
            Write-Host ""
            return $inputStr
        } elseif ($k.Key -eq [System.ConsoleKey]::Escape) {
            Write-Host " (Annule)" -ForegroundColor DarkGray
            return $null
        } elseif ($k.Key -eq [System.ConsoleKey]::Backspace) {
            if ($inputStr.Length -gt 0) {
                $inputStr = $inputStr.Substring(0, $inputStr.Length - 1)
                Write-Host "`b `b" -NoNewline
            }
        } else {
            $inputStr += $k.KeyChar
            Write-Host $k.KeyChar -NoNewline
        }
    }
}
function Start-ClusterRun {
    if (Test-Path $stdoutFile) { Remove-Item $stdoutFile -Force -ErrorAction SilentlyContinue }
    if (Test-Path $stderrFile) { Remove-Item $stderrFile -Force -ErrorAction SilentlyContinue }
    
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
try {
    while ($running) {
    $process = Start-ClusterRun
    $logFilePath = $null
    $isAgentRestart = $false
    
    # 1. Detect log file path from output stream
    Write-Host "[Monitor] Waiting to detect log file path..." -ForegroundColor Yellow
    $detected = $false
    for ($i = 0; -not $detected; $i++) {
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
    
    if (-not $detected) {
        Write-Warning "[Monitor] Process exited without providing a log file path. Using stdout for crash analysis."
        $logFilePath = $stdoutFile
    } else {
        Write-Host "[Monitor] Log file detected: $logFilePath" -ForegroundColor Green
    }
    
    # 2. Monitor process state
    $timeSinceLastCheck = 0
    $checkInterval = 10 # Check process status every 10 seconds
    
    while (-not $process.HasExited) {
        $manualWakeup = $false
        $manualMessage = $null
        
        # Check for user input or sleep in small increments
        $sleptFor = 0
        while ($sleptFor -lt $checkInterval -and -not $process.HasExited) {
            if ([Console]::KeyAvailable) {
                $key = [Console]::ReadKey($true)
                if ($key.Key -eq [System.ConsoleKey]::Enter) {
                    Write-Host "`n[Monitor] Touche Entree detectee." -ForegroundColor Yellow
                    Write-Host "Voulez-vous reveiller l'agent ? (Entree = Oui, Echap/Autre = Annuler)" -ForegroundColor Yellow
                    $confirmKey = [Console]::ReadKey($true)
                    if ($confirmKey.Key -eq [System.ConsoleKey]::Enter) {
                        $manualMessage = Read-HostWithEscape -Prompt "Message (laisser vide pour aucun, Echap pour annuler) : "
                        if ($null -ne $manualMessage) {
                            $manualWakeup = $true
                            break
                        }
                    } else {
                        Write-Host "Annule." -ForegroundColor DarkGray
                    }
                }
            }
            Start-Sleep -Milliseconds 100
            $sleptFor += 0.1
        }
        
        if ($manualWakeup) {
            $timeSinceLastCheck = 0
            Write-Host "`n[Monitor] Reveil manuel declenche." -ForegroundColor Cyan
        } else {
            $timeSinceLastCheck += $checkInterval
        }
        
        # Periodic check-in or manual check
        if ($timeSinceLastCheck -ge $intervalSec -or $manualWakeup) {
            if (-not $manualWakeup) {
                $timeSinceLastCheck = 0
                Write-Host "[Monitor] Periodic check timer ($intervalMin min) triggered. Waking up agent..." -ForegroundColor Cyan
            }
            
            $promptParts = @()
            if (-not [string]::IsNullOrWhiteSpace($userPromptContext)) {
                $promptParts += "CONTEXTE UTILISATEUR :`n$userPromptContext"
            }
            if ($manualWakeup -and -not [string]::IsNullOrWhiteSpace($manualMessage)) {
                $promptParts += "MESSAGE MANUEL DE L'UTILISATEUR POUR CE REVEIL :`n$manualMessage"
            }
            
            $diff = ""
            if (Test-Path $monitorLogPath) {
                $currentSize = (Get-Item $monitorLogPath).Length
                if ($currentSize -gt $global:lastMonitorLogSize) {
                    $fs = [System.IO.File]::Open($monitorLogPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
                    $fs.Seek($global:lastMonitorLogSize, [System.IO.SeekOrigin]::Begin) | Out-Null
                    $reader = New-Object System.IO.StreamReader($fs, [System.Text.Encoding]::UTF8)
                    $diff = $reader.ReadToEnd()
                    $reader.Close()
                    $global:lastMonitorLogSize = $currentSize
                }
            }
            if (-not [string]::IsNullOrWhiteSpace($diff)) {
                $promptParts += "VOICI CE QUI A ETE ECRIT DANS LE JOURNAL .monitor.log DEPUIS TON DERNIER REVEIL (ex: Ton précédent rapport). Prends ce contexte en compte :`n$diff"
            }
            
            $promptParts += "Tu peux consulter l'historique complet dans le fichier .monitor.log. Chemin : $monitorLogPath`n`nVoici le fichier de logs actuel pour la commande cluster run :`n$logFilePath"
            
            $promptParts += @"
INSTRUCTIONS IMPORTANTES DE DIAGNOSTIC :
Exécute une analyse critique approfondie et globale des logs de la commande :
1. Recherche des erreurs, avertissements ou comportements anormaux PARTOUT dans le log, et pas seulement à la fin.
2. Analyse les timings/horodatages des logs pour identifier des ralentissements suspects, des temps morts anormalement longs (freezes) ou des problèmes de vitesse d'exécution.
3. Rédige un diagnostic détaillé des performances et signale tout problème majeur.
4. Si tu détermines qu'il n'y a aucun problème et que tout se passe bien, tu n'as rien à faire : termine simplement ton intervention sans rien modifier. NE MODIFIE PAS DU CODE POUR MODIFIER DU CODE. Corrige SEULEMENT les problèmes critiques ou les ralentissements anormaux notoires. Toute modification de code va invalider les étapes du pipeline qui en dépendent et ralentira inutilement notre processus à la prochaine exécution.
5. Si tu as identifié un problème majeur qui nécessite absolument un redémarrage (ex: blocage, ralentissement extrême, résultats faussés qui vont contaminer toute la pipeline - bref, uniquement des cas bloquants où redémarrer nous fera QUE gagner du temps par rapport à laisser tourner), utilise tes outils d'écriture de fichier pour créer un fichier vide nommé `".restart_cluster`" à la racine du projet. Le script détectera ce fichier et redémarrera la commande. N'oublie pas que je ne peux pas lire tes messages textes à cause de l'animation de la CLI, tu DOIS utiliser tes outils pour interagir !
6. Inclus TOUJOURS dans ta réponse une analyse claire de l'état de la pipeline pour indiquer où en est l'exécution actuellement. Écris impérativement cette analyse à la fin du fichier `.monitor.log` en utilisant tes outils d'écriture de fichier (ex: ajout de texte à la fin du fichier). Utilise STRICTEMENT ce format de liste à puces pour rendre ça beau, clair et lisible :
   - ✅ Nom de l'étape 1 : Tout s'est passé correctement.
   - ⚠️ Nom de l'étape 2 : Ralentissement détecté.
   - 🔄 Nom de l'étape 3 : En cours d'exécution.

CONSIGNES DE SÉCURITÉ :
- SOIS EXTRÊMEMENT PRUDENT lors des modifications de code : ne modifie jamais rien sans avoir enquêté en profondeur dans le reste du code pour vérifier si la modification est réellement justifiée. On ne veut JAMAIS casser un comportement qui était intentionnel ou souhaité ! AUCUNE hypothèse. Toujours vérifier en détails (via tes outils ou des sous-agents) si le code actuel n'était pas intentionnel, si le bug est vraiment lié à ça et rien qu'à ça. Ne jamais assumer quelque chose comme étant vrai sans vérifier. TOUJOURS vérifier.
- La commande suit actuellement son cours. Tes modifications éventuelles de code seront prises en compte automatiquement lors du prochain run de la commande par le script de monitoring.
- INTERDICTION ABSOLUE de lancer toi-même la commande 'cluster-run', de compiler, de tester ou d'exécuter des processus. Le script de monitoring / le cluster s'en charge automatiquement. Ton rôle est uniquement de diagnostiquer, de modifier le code source si nécessaire, et de t'arrêter proprement.
"@
            
            $prompt = $promptParts -join "`n`n---`n`n"
            $safePrompt = $prompt -replace '"', '\"'
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            Add-Content -Path $monitorLogPath -Value "`n=== Periodic Check: $timestamp ===" -Encoding UTF8
            
            try {
                $agentOutput = & agy --dangerously-skip-permissions --model "$selectedModel" --print "$safePrompt"
                $agentOutputString = $agentOutput | Out-String
                Write-Host "`n=== [RETOUR AGENT: VERIFICATION PERIODIQUE] ===" -ForegroundColor Cyan
                Write-Host $agentOutputString -ForegroundColor Cyan
                Write-Host "==============================================`n" -ForegroundColor Cyan
                
                if (Test-Path ".restart_cluster") {
                    Remove-Item ".restart_cluster" -Force -ErrorAction SilentlyContinue
                    Write-Host "[Monitor] Agent requested a restart via .restart_cluster file! Terminating current process..." -ForegroundColor Yellow
                    $isAgentRestart = $true
                    taskkill /F /T /PID $process.Id *>$null
                    Start-Sleep -Seconds 1
                    break
                }
            } catch {
                Write-Host "[Monitor] Failed to invoke agy check: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
    
    # 3. Process has exited. Handle exit codes
    $exitCode = $process.ExitCode
    Write-Host "[Monitor] Process exited with code: $exitCode" -ForegroundColor Yellow
    
    if ($isAgentRestart) {
        Write-Host "[Monitor] Redémarrage automatique déclenché par l'agent..." -ForegroundColor Cyan
        Start-Sleep -Seconds 1
    } elseif ($null -ne $exitCode -and $exitCode -ne 0) {
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
        
        $diff = ""
        if (Test-Path $monitorLogPath) {
            $currentSize = (Get-Item $monitorLogPath).Length
            if ($currentSize -gt $global:lastMonitorLogSize) {
                $fs = [System.IO.File]::Open($monitorLogPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
                $fs.Seek($global:lastMonitorLogSize, [System.IO.SeekOrigin]::Begin) | Out-Null
                $reader = New-Object System.IO.StreamReader($fs, [System.Text.Encoding]::UTF8)
                $diff = $reader.ReadToEnd()
                $reader.Close()
                $global:lastMonitorLogSize = $currentSize
            }
        }
        if (-not [string]::IsNullOrWhiteSpace($diff)) {
            $promptParts += "VOICI CE QUI A ETE ECRIT DANS LE JOURNAL .monitor.log DEPUIS TON DERNIER REVEIL (ex: Ton précédent rapport). Prends ce contexte en compte :`n$diff"
        }
        
        $promptParts += "Tu peux consulter l'historique complet dans le fichier .monitor.log. Chemin : $monitorLogPath`n`nLa commande cluster run s'est arrêtée avec une erreur (code de sortie $exitCode).`nVoici les 100 dernières lignes de logs de la commande :`n$lastLogs"
        
        $promptParts += @"
INSTRUCTIONS IMPORTANTES DE CORRECTION :
Analyse ces logs et corrige l'erreur directement dans les fichiers de code source concernés :
1. Recherche l'origine de l'erreur dans l'ensemble des logs fournis, pas seulement sur la dernière ligne.
2. Analyse les timings/horodatages des logs pour identifier si l'erreur est liée à un freeze, un timeout ou un temps mort anormal.
3. Corrige le code source pour régler ce problème.
4. Inclus TOUJOURS dans ta réponse une analyse claire de l'état de la pipeline. Précise à quelle étape exacte le crash s'est produit. Écris impérativement cette analyse à la fin du fichier `.monitor.log` en utilisant tes outils d'écriture de fichier. Utilise STRICTEMENT ce format de liste à puces pour rendre ça beau, clair et lisible :
   - ✅ Nom de l'étape 1 : Terminée avec succès.
   - ❌ Nom de l'étape 2 : Crash survenu à ce niveau (explication courte).

CONSIGNES DE SÉCURITÉ :
- SOIS EXTRÊMEMENT PRUDENT lors des modifications de code : ne modifie jamais rien sans avoir enquêté en profondeur dans le reste du code pour vérifier si la modification est réellement justifiée. On ne veut JAMAIS casser un comportement qui était intentionnel ou souhaité ! AUCUNE hypothèse. Toujours vérifier en détails (via tes outils ou des sous-agents) si le code actuel n'était pas intentionnel, si le bug est vraiment lié à ça et rien qu'à ça. Ne jamais assumer quelque chose comme étant vrai sans vérifier. TOUJOURS vérifier.
- Tes modifications de code seront prises en compte lors du prochain run.
- INTERDICTION ABSOLUE de lancer toi-même la commande 'cluster-run', de compiler, de tester ou d'exécuter des processus. Ton unique rôle est de modifier le code source pour corriger le problème et de t'arrêter proprement en expliquant ce que tu as fait. Le script de monitoring se charge de relancer la commande après ton arrêt.
"@
        
        $prompt = $promptParts -join "`n`n---`n`n"
        $safePrompt = $prompt -replace '"', '\"'
        
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -Path $monitorLogPath -Value "`n=== Crash Repair: $timestamp ===" -Encoding UTF8
        
        try {
            $agentOutput = & agy --dangerously-skip-permissions --model "$selectedModel" --print "$safePrompt"
            $agentOutputString = $agentOutput | Out-String
            Write-Host "`n=== [RETOUR AGENT: REPARATION CRASH] ===" -ForegroundColor Red
            Write-Host $agentOutputString -ForegroundColor Red
            Write-Host "==============================================`n" -ForegroundColor Red
            

            
            Write-Host "[Monitor] Agent repair finished. Restarting cluster-run..." -ForegroundColor Green
        } catch {
            Write-Host "[Monitor] Failed to run agy repair agent: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "[Monitor] Waiting 10 seconds before restarting..." -ForegroundColor Yellow
            Start-Sleep -Seconds 10
        }
    } else {
        # Process completed successfully
        Write-Host "[Monitor] Process completed successfully! Waking up agent for final validation..." -ForegroundColor Green
        
        $promptParts = @()
        if (-not [string]::IsNullOrWhiteSpace($userPromptContext)) {
            $promptParts += "CONTEXTE UTILISATEUR :`n$userPromptContext"
        }
        
        $diff = ""
        if (Test-Path $monitorLogPath) {
            $currentSize = (Get-Item $monitorLogPath).Length
            if ($currentSize -gt $global:lastMonitorLogSize) {
                $fs = [System.IO.File]::Open($monitorLogPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
                $fs.Seek($global:lastMonitorLogSize, [System.IO.SeekOrigin]::Begin) | Out-Null
                $reader = New-Object System.IO.StreamReader($fs, [System.Text.Encoding]::UTF8)
                $diff = $reader.ReadToEnd()
                $reader.Close()
                $global:lastMonitorLogSize = $currentSize
            }
        }
        if (-not [string]::IsNullOrWhiteSpace($diff)) {
            $promptParts += "VOICI CE QUI A ETE ECRIT DANS LE JOURNAL .monitor.log DEPUIS TON DERNIER REVEIL (ex: Ton précédent rapport). Prends ce contexte en compte :`n$diff"
        }
        
        $promptParts += "Tu peux consulter l'historique complet dans le fichier .monitor.log. Chemin : $monitorLogPath`n`nLa commande cluster run vient de se terminer avec succès !`nVoici le fichier de logs complet pour la commande : $logFilePath"
        
        $promptParts += @"
INSTRUCTIONS IMPORTANTES DE VALIDATION FINALE :
La pipeline vient de se terminer. Ton rôle est de vérifier les résultats finaux pour t'assurer que tout est correct, cohérent et correspond aux attentes.
1. Recherche des avertissements finaux ou des résultats anormaux dans les logs.
2. Si tout est bon, rédige un dernier rapport de succès détaillé dans le fichier `.monitor.log` (en utilisant tes outils d'écriture de fichier).
3. Si (et seulement si) tu détectes un problème GRAVE nécessitant absolument d'invalider cette exécution, apporte ta solution (modification du code) et relance la pipeline en créant le fichier vide `".restart_cluster`" à la racine du projet. Sois extrêmement prudent avec ça, ne relance que si c'est strictement indispensable.
4. N'oublie pas que je ne peux pas lire tes messages textes à cause de l'animation de la CLI, tu DOIS écrire ton diagnostic final dans le fichier `.monitor.log` !
"@
        
        $prompt = $promptParts -join "`n`n---`n`n"
        $safePrompt = $prompt -replace '"', '\"'
        
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Add-Content -Path $monitorLogPath -Value "`n=== Final Validation: $timestamp ===" -Encoding UTF8
        
        try {
            $agentOutput = & agy --dangerously-skip-permissions --model "$selectedModel" --print "$safePrompt"
            $agentOutputString = $agentOutput | Out-String
            Write-Host "`n=== [RETOUR AGENT: VALIDATION FINALE] ===" -ForegroundColor Green
            Write-Host $agentOutputString -ForegroundColor Green
            Write-Host "==============================================`n" -ForegroundColor Green
            
            if (Test-Path ".restart_cluster") {
                Remove-Item ".restart_cluster" -Force -ErrorAction SilentlyContinue
                Write-Host "[Monitor] Agent requested a restart during final validation via .restart_cluster file! Restarting..." -ForegroundColor Yellow
                $isAgentRestart = $true
                continue
            }
        } catch {
            Write-Host "[Monitor] Failed to run agy final validation agent: $($_.Exception.Message)" -ForegroundColor Red
        }

        Write-Host ""
        $choice = Read-Host "La validation finale est terminee. [R]elancer, ou [Q]uitter le script ? (R/Q)"
        if ($choice -match '^[qQ]') {
            Write-Host "Fin de la supervision." -ForegroundColor Green
            $running = $false
        } else {
            Write-Host "Relancement..." -ForegroundColor Cyan
        }
    }
    }
} finally {
    if ($null -ne $process -and -not $process.HasExited) {
        Write-Host "`n[Monitor] Arret du processus cluster-run en arriere-plan suite a l'interruption (Ctrl+C)..." -ForegroundColor Yellow
        taskkill /F /T /PID $process.Id *>$null
    }
}
