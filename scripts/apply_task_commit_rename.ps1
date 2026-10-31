<#
.SYNOPSIS
Wrapper 1-clic pour apply_task_commit_rename.py supportant -DryRun et -Apply.
#>
[CmdletBinding()]
param (
    [string]$VaultDir = "c:\Users\Jamet\Documents\VoiceNotes",
    [switch]$Apply,
    [switch]$DryRun,
    [string]$DiffOutput = ""
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$pyScript = Join-Path $scriptDir "apply_task_commit_rename.py"
if (-not (Test-Path $pyScript)) {
    $altPy = "C:\Users\Jamet\.gemini\antigravity-cli\brain\f26aba91-5383-4dd3-ac8e-a736047a5b7c\apply_task_commit_rename.py"
    if (Test-Path $altPy) {
        $pyScript = $altPy
    }
}

$pyArgs = @($pyScript, "--vault-dir", $VaultDir)
if ($Apply) {
    $pyArgs += "--apply"
} else {
    $pyArgs += "--dry-run"
}

if ($DiffOutput -ne "") {
    $pyArgs += @("--diff-output", $DiffOutput)
}

Write-Host "Exécution de apply_task_commit_rename.py avec Python..." -ForegroundColor Cyan
& python @pyArgs
exit $LASTEXITCODE
