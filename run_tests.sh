#!/bin/zsh

# Script pour lancer tous les tests du projet avec pytest

# Se déplacer à la racine du projet si nécessaire
# SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
# cd "$SCRIPT_DIR/.."

# Ajouter le répertoire racine au PYTHONPATH
export PYTHONPATH=$(pwd)

# Lancer les tests
pytest --asyncio-mode=auto --rootdir=back/tests -v
