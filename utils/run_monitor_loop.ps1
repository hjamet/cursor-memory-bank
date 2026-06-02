param(
    [string]$Goal
)

$ErrorActionPreference = "Stop"

# Déterminer les chemins
$monitorPath = Join-Path $PSScriptRoot "..\src\commands\monitor.md"
$continuePath = Join-Path $PSScriptRoot "..\src\commands\continue.md"
$convsDir = "$env:USERPROFILE\.gemini\antigravity\conversations"

# Charger les instructions
if (-not (Test-Path $monitorPath)) {
    Write-Error "Fichier d'instruction Monitor introuvable : $monitorPath"
    exit 1
}
if (-not (Test-Path $continuePath)) {
    Write-Error "Fichier d'instruction Continue introuvable : $continuePath"
    exit 1
}

$monitorInstruction = Get-Content -Path $monitorPath -Raw
$continueInstruction = Get-Content -Path $continuePath -Raw

# Saisir le but si non fourni en paramètre
if ([string]::IsNullOrWhiteSpace($Goal)) {
    Write-Host "=== Antigravity Monitor Loop ===" -ForegroundColor Cyan
    $Goal = Read-Host "Saisissez le but (Goal) de la supervision"
    if ([string]::IsNullOrWhiteSpace($Goal)) {
        Write-Error "Le but ne peut pas être vide."
        exit 1
    }
}

$initialPrompt = @"
$monitorInstruction

🎯 GOAL À ATTEINDRE :
$Goal
"@

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
        
        # Exécution interactive initiale
        & agy --prompt-interactive $initialPrompt
        $isFirstRun = $false
    } else {
        Write-Host "==========================================" -ForegroundColor Yellow
        Write-Host " Relance post-crash de la conversation" -ForegroundColor Yellow
        Write-Host " Conversation ID : $convId" -ForegroundColor Yellow
        Write-Host "==========================================" -ForegroundColor Yellow
        
        # Relance avec l'instruction continue.md
        & agy --conversation $convId --prompt-interactive $continueInstruction
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
