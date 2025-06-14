#!/usr/bin/env python3
"""
### cleanup_test_sessions.py
**Description :** Script de nettoyage des sessions de test créées par les tests automatisés.
Supprime automatiquement les fichiers de session temporaires générés pendant les tests.
"""

from back.config import get_data_dir
from pathlib import Path
import re
from datetime import datetime

def cleanup_test_sessions():
    """
    ### cleanup_test_sessions
    **Description :** Nettoie les fichiers ET répertoires de session de test dans le répertoire data/sessions.
    Supprime les fichiers et dossiers qui correspondent aux patterns de test.
    """
    sessions_dir = Path(get_data_dir()) / "sessions"
    if not sessions_dir.exists():
        print("📁 Répertoire data/sessions non trouvé")
        return
    
    # Patterns pour identifier les fichiers et répertoires de test
    test_patterns = [
        r"^test_.*",                   # test_* (fichiers et dossiers)
        r"^.*_test.*",                 # *_test* (fichiers et dossiers)
        r"^test-.*",                   # test-* (fichiers et dossiers)
        r"^.*_tools.*",                # *_tools* (fichiers et dossiers)
        r"^.*_integration.*",          # *_integration* (fichiers et dossiers)
        r"^.*_deps.*",                 # *_deps* (fichiers et dossiers)
        r"^.*_concurrent.*",           # *_concurrent* (fichiers et dossiers)
        r"^.*_memory.*",               # *_memory* (fichiers et dossiers)
        r"^.*_error.*",                # *_error* (fichiers et dossiers)
        r"^.*_config.*",               # *_config* (fichiers et dossiers)
        r"^.*_session.*",              # *_session* (fichiers et dossiers)
    ]
    
    deleted_files = []
    deleted_dirs = []
    kept_files = []
    kept_dirs = []
    
    # Nettoyer les fichiers .jsonl
    for file_path in sessions_dir.glob("*.jsonl"):
        file_name = file_path.name
        is_test_file = any(re.match(pattern, file_name) for pattern in test_patterns)
        
        if is_test_file:
            try:
                file_path.unlink()
                deleted_files.append(file_name)
                print(f"🗑️  Fichier supprimé: {file_name}")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression du fichier {file_name}: {e}")
        else:
            kept_files.append(file_name)
    
    # Nettoyer les répertoires de test
    for dir_path in sessions_dir.iterdir():
        if dir_path.is_dir():
            dir_name = dir_path.name
            is_test_dir = any(re.match(pattern, dir_name) for pattern in test_patterns)
            
            if is_test_dir:
                try:
                    # Supprimer récursivement le répertoire et son contenu
                    import shutil
                    shutil.rmtree(dir_path)
                    deleted_dirs.append(dir_name)
                    print(f"📁🗑️ Répertoire supprimé: {dir_name}/")
                except Exception as e:
                    print(f"❌ Erreur lors de la suppression du répertoire {dir_name}/: {e}")
            else:
                kept_dirs.append(dir_name)
    
    print(f"\n📊 Résumé du nettoyage:")
    print(f"   • {len(deleted_files)} fichiers de test supprimés")
    print(f"   • {len(deleted_dirs)} répertoires de test supprimés")
    print(f"   • {len(kept_files)} fichiers conservés")
    print(f"   • {len(kept_dirs)} répertoires conservés")
    
    if kept_files or kept_dirs:
        print(f"\n📋 Éléments conservés (sessions réelles):")
        for file_name in sorted(kept_files):
            print(f"   • {file_name}")
        for dir_name in sorted(kept_dirs):
            print(f"   • {dir_name}/")

def cleanup_old_sessions(days=7):
    """
    ### cleanup_old_sessions
    **Description :** Supprime les sessions ET répertoires plus anciens que le nombre de jours spécifié.
    **Paramètres :**
    - `days` (int) : Nombre de jours après lesquels supprimer les sessions.
    """
    sessions_dir = Path(get_data_dir()) / "sessions"
    if not sessions_dir.exists():
        return
    
    cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
    old_files = []
    old_dirs = []
    
    # Nettoyer les anciens fichiers
    for file_path in sessions_dir.glob("*.jsonl"):
        if file_path.stat().st_mtime < cutoff_time:
            try:
                file_path.unlink()
                old_files.append(file_path.name)
                print(f"🕰️  Fichier supprimé (ancien): {file_path.name}")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression de {file_path.name}: {e}")
    
    # Nettoyer les anciens répertoires
    for dir_path in sessions_dir.iterdir():
        if dir_path.is_dir() and dir_path.stat().st_mtime < cutoff_time:
            try:
                import shutil
                shutil.rmtree(dir_path)
                old_dirs.append(dir_path.name)
                print(f"🕰️📁 Répertoire supprimé (ancien): {dir_path.name}/")
            except Exception as e:
                print(f"❌ Erreur lors de la suppression du répertoire {dir_path.name}/: {e}")
    
    if old_files or old_dirs:
        print(f"\n🕰️  {len(old_files)} anciens fichiers et {len(old_dirs)} anciens répertoires supprimés (>{days} jours)")

if __name__ == "__main__":
    print("🧹 Nettoyage des sessions de test...")
    cleanup_test_sessions()
    print("\n🕰️ Nettoyage des anciennes sessions...")
    cleanup_old_sessions(7)
    print("\n✅ Nettoyage terminé !")
