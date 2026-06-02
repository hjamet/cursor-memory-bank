param(
    [string]$Goal
)

$ErrorActionPreference = "Stop"

# Fix character encoding issues in Windows Console
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

# Déterminer les chemins des workflows dans le workspace courant pour vérification
$monitorWorkflowPath = ".agent/workflows/monitor.md"
$continueWorkflowPath = ".agent/workflows/continue.md"

# Saisir le but si non fourni en paramètre (support multi-ligne)
if ([string]::IsNullOrWhiteSpace($Goal)) {
    Write-Host "=== Antigravity Monitor Loop ===" -ForegroundColor Cyan
    Write-Host "Saisissez le but (Goal) de la supervision." -ForegroundColor Cyan
    Write-Host "Collez votre texte et entrez 'EOF' sur une nouvelle ligne (ou double entrée sur ligne vide) pour valider :" -ForegroundColor Gray
    
    $GoalLines = @()
    while ($true) {
        $line = Read-Host
        if ($line.Trim() -eq 'EOF') {
            break
        }
        if ([string]::IsNullOrEmpty($line) -and $GoalLines.Count -gt 0 -and $GoalLines[-1] -eq "") {
            # Double entrée sur ligne vide pour terminer (on retire le premier vide)
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
        Write-Error "Le but ne peut pas être vide."
        exit 1
    }
}

# Prompt d'initialisation propre sans frontmatter
$initialPrompt = @"
Applique le workflow de supervision défini dans le fichier de workflow de ton espace de travail : $monitorWorkflowPath.

🎯 GOAL À ATTEINDRE :
$Goal

---
IMPORTANT DIRECTIVE : L'objectif ci-dessus est le but fourni par l'utilisateur. Tu es le Superviseur (Monitor). Formule ce goal en une phrase précise, note-le et passe immédiatement à l'étape 2 (Lancement du Teamwork Coordinator) en invoquant le sous-agent comme décrit dans le workflow. Ne me demande pas de clarifier le but, il est entièrement décrit ci-dessus. Démarre dès maintenant.
"@

# Prompt de relance propre sans frontmatter
$continuePrompt = @"
Applique le workflow de reprise défini dans le fichier de workflow de ton espace de travail : $continueWorkflowPath suite au crash de l'IDE.

Restaure immédiatement l'état et relance les tâches/sous-agents en cours comme décrit dans le workflow.
"@

$convsDir = "$env:USERPROFILE\.gemini\antigravity\conversations"
$isFirstRun = $true
$convId = $null

Write-Host ""
Write-Host "Démarrage de la boucle de monitoring..." -ForegroundColor Cyan
Write-Host "Le script surveillera l'exécution et relancera la conversation en cas de plantage." -ForegroundColor Gray
Write-Host "Appuyez sur Ctrl+C dans ce terminal externe pour interrompre la surveillance." -ForegroundColor Gray
Write-Host ""

while ($true) {
    if ($isFirstRun) {
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host " Lancement initial de la supervision" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        
        # Exécution interactive initiale avec --dangerously-skip-permissions
        & agy --dangerously-skip-permissions --prompt-interactive "$initialPrompt"
        $isFirstRun = $false
    } else {
        Write-Host "==========================================" -ForegroundColor Yellow
        Write-Host " Relance post-crash de la conversation" -ForegroundColor Yellow
        Write-Host " Conversation ID : $convId" -ForegroundColor Yellow
        Write-Host "==========================================" -ForegroundColor Yellow
        
        # Relance avec l'instruction continue.md et --dangerously-skip-permissions
        & agy --dangerously-skip-permissions --conversation $convId --prompt-interactive "$continuePrompt"
    }

    # Récupérer le code de retour d'agy
    $exitCode = $LASTEXITCODE
    Write-Host "Processus agy arrêté avec le code de sortie : $exitCode" -ForegroundColor Gray

    # Si le code est 0, c'est un arrêt volontaire/propre
    if ($exitCode -eq 0) {
        Write-Host ""
        $choice = Read-Host "L'agent s'est arrêté proprement. [R]elancer la conversation, ou [Q]uitter le script ? (R/Q)"
        if ($choice -match '^[qQ]') {
            Write-Host "Fin de la supervision." -ForegroundColor Green
            break
        } elseif ($choice -match '^[rR]') {
            # Identifier la dernière conversation
            $latestDb = Get-ChildItem -Path $convsDir -Filter "*.db" -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending |
                Select-Object -First 1
            if ($latestDb) {
                $convId = $latestDb.BaseName
                Write-Host "Relance de la dernière conversation : $convId" -ForegroundColor Cyan
            } else {
                Write-Warning "Aucune conversation existante trouvée. Relancement complet."
                $isFirstRun = $true
            }
        }
    } else {
        # Arrêt anormal/crash (code non nul)
        Write-Host "Arrêt anormal de agy détecté (possible crash d'IDE/Language Server)." -ForegroundColor Red
        
        # Attendre un peu que le LS redémarre
        Write-Host "Attente de 15 secondes pour laisser le Language Server se réinitialiser..." -ForegroundColor Yellow
        Start-Sleep -Seconds 15

        # Identifier la dernière conversation active
        $latestDb = Get-ChildItem -Path $convsDir -Filter "*.db" -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1
        if ($latestDb) {
            $convId = $latestDb.BaseName
            Write-Host "Dernière conversation identifiée pour la reprise : $convId" -ForegroundColor Cyan
        } else {
            Write-Warning "Aucune conversation trouvée pour la relance. Reprise impossible."
            break
        }
    }
}
