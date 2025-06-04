import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour permettre l'import du module back
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from back.app import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
