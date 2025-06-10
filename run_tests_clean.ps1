# Script PowerShell pour executer les tests avec nettoyage automatique
# Fichier: run_tests_clean.ps1

param(
    [string]$TestPattern = "back/tests/agents/test_gm_agent_consolidated.py",
    [switch]$CleanBefore,
    [switch]$CleanAfter,
    [switch]$Verbose
)

Write-Host "Tests avec nettoyage automatique" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Nettoyage avant les tests si demande
if ($CleanBefore) {
    Write-Host "Nettoyage AVANT les tests..." -ForegroundColor Yellow
    python back/tests/cleanup_test_sessions.py
}

# Compter les fichiers et répertoires de test avant
$sessionsBefore = @()
$dirsBefore = @()
if (Test-Path "data/sessions") {
    $sessionsBefore = Get-ChildItem "data/sessions" -Filter "*.jsonl" | Where-Object { $_.Name -match "^test_" }
    $dirsBefore = Get-ChildItem "data/sessions" -Directory | Where-Object { $_.Name -match "^test_" }
}
Write-Host "Fichiers de test presents AVANT: $($sessionsBefore.Count)" -ForegroundColor Blue
Write-Host "Repertoires de test presents AVANT: $($dirsBefore.Count)" -ForegroundColor Blue

# Executer les tests
Write-Host "Execution des tests..." -ForegroundColor Green
if ($Verbose) {
    python -m pytest $TestPattern -v --tb=short
} else {
    python -m pytest $TestPattern
}

$testExitCode = $LASTEXITCODE

# Compter les fichiers et répertoires de test après
$sessionsAfter = @()
$dirsAfter = @()
if (Test-Path "data/sessions") {
    $sessionsAfter = Get-ChildItem "data/sessions" -Filter "*.jsonl" | Where-Object { $_.Name -match "^test_" }
    $dirsAfter = Get-ChildItem "data/sessions" -Directory | Where-Object { $_.Name -match "^test_" }
}
Write-Host "Fichiers de test presents APRES: $($sessionsAfter.Count)" -ForegroundColor Blue
Write-Host "Repertoires de test presents APRES: $($dirsAfter.Count)" -ForegroundColor Blue

# Afficher les nouveaux éléments créés
$newFiles = $sessionsAfter | Where-Object { $_.Name -notin $sessionsBefore.Name }
$newDirs = $dirsAfter | Where-Object { $_.Name -notin $dirsBefore.Name }

if ($newFiles.Count -gt 0) {
    Write-Host "Nouveaux fichiers crees:" -ForegroundColor Magenta
    foreach ($file in $newFiles) {
        Write-Host "   • $($file.Name)" -ForegroundColor White
    }
}

if ($newDirs.Count -gt 0) {
    Write-Host "Nouveaux repertoires crees:" -ForegroundColor Magenta
    foreach ($dir in $newDirs) {
        Write-Host "   • $($dir.Name)/" -ForegroundColor White
    }
}

# Nettoyage apres les tests si demande
if ($CleanAfter) {
    Write-Host "Nettoyage APRES les tests..." -ForegroundColor Yellow
    python back/tests/cleanup_test_sessions.py
}

# Resume final
Write-Host "" 
Write-Host "RESUME" -ForegroundColor Cyan
Write-Host "======" -ForegroundColor Cyan
if ($testExitCode -eq 0) {
    Write-Host "Tests: REUSSIS" -ForegroundColor Green
} else {
    Write-Host "Tests: ECHOUES (code $testExitCode)" -ForegroundColor Red
}
Write-Host "Fichiers crees: $($newFiles.Count)" -ForegroundColor Blue
Write-Host "Repertoires crees: $($newDirs.Count)" -ForegroundColor Blue
Write-Host "Nettoyage automatique: $(if ($CleanAfter -or $CleanBefore) { "ACTIVE" } else { "DESACTIVE" })" -ForegroundColor Yellow

# Conseils d'utilisation
$totalCreated = $newFiles.Count + $newDirs.Count
if ($totalCreated -gt 0 -and -not $CleanAfter) {
    Write-Host ""
    Write-Host "CONSEIL: Utilisez -CleanAfter pour nettoyer automatiquement" -ForegroundColor Yellow
    Write-Host "   Exemple: .\run_tests_clean.ps1 -CleanAfter" -ForegroundColor Gray
}

exit $testExitCode
