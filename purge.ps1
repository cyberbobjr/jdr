# Chemin du répertoire courant
$rootDirectory = Get-Location

# Recherche tous les dossiers __pycache__ de façon récursive
$pycacheDirs = Get-ChildItem -Path $rootDirectory -Recurse -Directory -Filter "__pycache__"

foreach ($dir in $pycacheDirs) {
    try {
        Remove-Item -Path $dir.FullName -Recurse -Force
        Write-Host "Supprimé : $($dir.FullName)"
    } catch {
        Write-Warning "Impossible de supprimer : $($dir.FullName). Erreur : $_"
    }
}
