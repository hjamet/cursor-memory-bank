param(
    [string]$Goal
)

$ErrorActionPreference = "Stop"

# Fix character encoding issues in Windows Console
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
} catch {}
$OutputEncoding = [System.Text.Encoding]::UTF8

# Déterminer les chemins
if (Test-Path (Join-Path $PSScriptRoot "workflows\monitor.md")) {
    # Exécution depuis le dossier caché .agent/
    $monitorPath = Join-Path $PSScriptRoot "workflows\monitor.md"
    $continuePath = Join-Path $PSScriptRoot "workflows\continue.md"
} else {
    # Exécution depuis utils/ dans le dépôt de développement
    $monitorPath = Join-Path $PSScriptRoot "..\src\commands\monitor.md"
    $continuePath = Join-Path $PSScriptRoot "..\src\commands\continue.md"
}
$convsDir = "$env:USERPROFILE\.gemini\antigravity\conversations"


# Charger les instructions en UTF-8
if (-not (Test-Path $monitorPath)) {
    Write-Error "Fichier d'instruction Monitor introuvable : $monitorPath"
    exit 1
}
if (-not (Test-Path $continuePath)) {
    Write-Error "Fichier d'instruction Continue introuvable : $continuePath"
    exit 1
}

$monitorInstructionRaw = Get-Content -Path $monitorPath -Raw -Encoding UTF8
$continueInstructionRaw = Get-Content -Path $continuePath -Raw -Encoding UTF8

# Fonction pour retirer le frontmatter YAML
function Remove-Frontmatter([string]$text) {
    $trimmed = $text.Trim()
    if ($trimmed.StartsWith("---")) {
        # Trouver la seconde occurrence de "---" après le premier index
        $firstIndex = $trimmed.IndexOf("---")
        $secondIndex = $trimmed.IndexOf("---", $firstIndex + 3)
        if ($secondIndex -ne -1) {
            return $trimmed.Substring($secondIndex + 3).Trim()
        }
    }
    return $trimmed
}

$monitorInstruction = Remove-Frontmatter $monitorInstructionRaw
$continueInstruction = Remove-Frontmatter $continueInstructionRaw

# Saisir le but si non fourni en paramètre (support multi-ligne)
if ([string]::IsNullOrWhiteSpace($Goal)) {
    Write-Host "=== Antigravity Monitor Loop ===" -ForegroundColor Cyan
    Write-Host "Saisissez le but (Goal) de la supervision." -ForegroundColor Cyan
    Write-Host "Collez votre texte et entrez 'EOF' sur une nouvelle ligne (ou double entree sur ligne vide) pour valider :" -ForegroundColor Gray
    
    $GoalLines = @()
    while ($true) {
        $line = Read-Host
        if ($line.Trim() -eq 'EOF') {
            break
        }
        if ([string]::IsNullOrEmpty($line) -and $GoalLines.Count -gt 0 -and $GoalLines[-1] -eq "") {
            # Double entree sur ligne vide pour terminer (on retire le premier vide)
            $GoalLines = $GoalLines[0..($GoalLines.Count-2)]
            break
        }
        if ([string]::IsNullOrEmpty($line) -and $GoalLines.Count -eq 0) {
            break
        }
        $GoalLines += $line
    }
    
    $Goal = $GoalLines -join "`n"
    if ([string]::IsNullOrWhiteSpace($Goal)) {
        Write-Error "Le but ne peut pas etre vide."
        exit 1
    }
}

# Prompt d'initialisation propre avec instructions complètes en UTF-8 (sans frontmatter)
$initialPrompt = @"
$monitorInstruction

---

🎯 GOAL À ATTEINDRE :
$Goal

---
IMPORTANT DIRECTIVE : L'objectif ci-dessus est le but fourni par l'utilisateur. Tu es le Superviseur (Monitor). Formule ce goal en une phrase précise, note-le et passe immédiatement à l'étape 2 (Lancement du Teamwork Coordinator) en invoquant le sous-agent comme décrit dans le workflow. Ne me demande pas de clarifier le but, il est entièrement décrit ci-dessus. Démarre dès maintenant.
"@

# Prompt de relance propre avec instructions complètes en UTF-8 (sans frontmatter)
$continuePrompt = @"
$continueInstruction

---
IMPORTANT DIRECTIVE : L'IDE a planté. Applique immédiatement ce workflow de reprise pour restaurer l'état et relancer les tâches/sous-agents en cours.
"@

$isFirstRun = $true
$convId = $null

Write-Host ""
Write-Host "Demarrage de la boucle de monitoring..." -ForegroundColor Cyan
Write-Host "Le script surveillera l'execution et relancera la conversation en cas de plantage." -ForegroundColor Gray
Write-Host "Appuyez sur Ctrl+C dans ce terminal externe pour interrompre la surveillance." -ForegroundColor Gray
Write-Host ""

while ($true) {
    if ($isFirstRun) {
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host " Lancement initial de la supervision" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        
        # Execution interactive initiale en contournant la limite de 8191 caracteres de cmd.exe
        Start-Process -FilePath "agy" -ArgumentList "--dangerously-skip-permissions", "--prompt-interactive", $initialPrompt -NoNewWindow -Wait
        $isFirstRun = $false
    } else {
        Write-Host "==========================================" -ForegroundColor Yellow
        Write-Host " Relance post-crash de la conversation" -ForegroundColor Yellow
        Write-Host " Conversation ID : $convId" -ForegroundColor Yellow
        Write-Host "==========================================" -ForegroundColor Yellow
        
        # Relance de la conversation en contournant la limite de 8191 caracteres de cmd.exe
        Start-Process -FilePath "agy" -ArgumentList "--dangerously-skip-permissions", "--conversation", $convId, "--prompt-interactive", $continuePrompt -NoNewWindow -Wait
    }

    # Recuperer le code de retour d'agy
    $exitCode = $LASTEXITCODE
    Write-Host "Processus agy arrete avec le code de sortie : $exitCode" -ForegroundColor Gray

    # Si le code est 0, c'est un arret volontaire/propre
    if ($exitCode -eq 0) {
        Write-Host ""
        $choice = Read-Host "L'agent s'est arrete proprement. [R]elancer la conversation, ou [Q]uitter le script ? (R/Q)"
        if ($choice -match '^[qQ]') {
            Write-Host "Fin de la supervision." -ForegroundColor Green
            break
        } elseif ($choice -match '^[rR]') {
            # Identifier la derniere conversation
            $latestDb = Get-ChildItem -Path $convsDir -Filter "*.db" -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending |
                Select-Object -First 1
            if ($latestDb) {
                $convId = $latestDb.BaseName
                Write-Host "Relance de la derniere conversation : $convId" -ForegroundColor Cyan
            } else {
                Write-Warning "Aucune conversation existante trouvee. Relancement complet."
                $isFirstRun = $true
            }
        }
    } else {
        # Arret anormal/crash (code non nul)
        Write-Host "Arret anormal de agy detecte (possible crash d'IDE/Language Server)." -ForegroundColor Red
        
        # Attendre un peu que le LS redemarre
        Write-Host "Attente de 15 secondes pour laisser le Language Server se reinitialiser..." -ForegroundColor Yellow
        Start-Sleep -Seconds 15

        # Identifier la derniere conversation active
        $latestDb = Get-ChildItem -Path $convsDir -Filter "*.db" -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if ($latestDb) {
            $convId = $latestDb.BaseName
            Write-Host "Derniere conversation identifiee pour la reprise : $convId" -ForegroundColor Cyan
        } else {
            Write-Warning "Aucune conversation trouvee pour la relance. Reprise impossible."
            break
        }
    }
}

