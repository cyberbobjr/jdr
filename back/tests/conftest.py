import pytest
import shutil
import os
from pathlib import Path
from typing import List, Generator
from fastapi.testclient import TestClient
from back.config import get_data_dir


@pytest.fixture
def client():
    """
    ### client
    **Description :** Fixture pour créer un client de test FastAPI.
    **Paramètres :** Aucun
    **Retour :** TestClient configuré pour l'application FastAPI.
    """
    from back.app import app
    return TestClient(app)


class SessionManager:
    """
    ### SessionManager
    **Description :** Gestionnaire de sessions de test qui suit et nettoie automatiquement les sessions créées pendant les tests.
    """
    
    def __init__(self):
        self.created_sessions: List[str] = []
        self.sessions_base_path = Path(get_data_dir()) / "sessions"
    
    def track_session(self, session_id: str):
        """
        ### track_session
        **Description :** Ajoute un ID de session à la liste des sessions à nettoyer.
        **Paramètres :**
        - `session_id` (str) : L'ID de la session à suivre.
        **Retour :** None
        """
        self.created_sessions.append(session_id)
    
    def cleanup_sessions(self):
        """
        ### cleanup_sessions
        **Description :** Supprime toutes les sessions trackées des répertoires de données.
        **Paramètres :** Aucun
        **Retour :** None
        """
        for session_id in self.created_sessions:
            session_dir = self.sessions_base_path / session_id
            if session_dir.exists():
                shutil.rmtree(session_dir)
            
            # Nettoyer aussi les fichiers .jsonl de session
            session_file = self.sessions_base_path / f"{session_id}.jsonl"
            if session_file.exists():
                session_file.unlink()
        
        self.created_sessions.clear()


@pytest.fixture
def session_manager() -> Generator[SessionManager, None, None]:
    """
    ### session_manager
    **Description :** Fixture pour gérer automatiquement le nettoyage des sessions de test.
    **Paramètres :** Aucun
    **Retour :** SessionManager configuré pour nettoyer automatiquement à la fin du test.
    """
    manager = SessionManager()
    yield manager
    # Nettoyage automatique à la fin du test
    manager.cleanup_sessions()


@pytest.fixture
def isolated_data_dir(tmp_path, monkeypatch) -> Path:
    """
    ### isolated_data_dir
    **Description :** Fixture pour créer un environnement de données isolé pour les tests.
    """
    # Créer la structure de dossiers nécessaire
    scenarios_dir = tmp_path / "scenarios"
    scenarios_dir.mkdir()
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()
    characters_dir = tmp_path / "characters"
    characters_dir.mkdir()
    # Créer un scénario de test par défaut
    (scenarios_dir / "Les_Pierres_du_Passe.md").write_text(
        "# Les Pierres du Passé\n\nScénario de test pour les tests d'intégration.",
        encoding="utf-8"
    )
    # Créer un autre scénario de test
    (scenarios_dir / "TestScenario.md").write_text(
        "# Test Scénario\nCeci est un scénario de test pour la validation des tests unitaires.\n",
        encoding="utf-8"
    )
    # Patch global de get_data_dir dans tous les modules de service et de test connus
    monkeypatch.setattr("back.config.get_data_dir", lambda: str(tmp_path))
    monkeypatch.setattr("back.services.scenario_service.get_data_dir", lambda: str(tmp_path))
    monkeypatch.setattr("back.services.character_persistence_service.get_data_dir", lambda: str(tmp_path))
    # Patch aussi dans les tests qui importent directement get_data_dir
    monkeypatch.setattr("back.tests.agents.test_prompt.get_data_dir", lambda: str(tmp_path))
    monkeypatch.setattr("back.tests.cleanup_test_sessions.get_data_dir", lambda: str(tmp_path))
    monkeypatch.setattr("back.tests.conftest.get_data_dir", lambda: str(tmp_path))
    monkeypatch.setattr("back.services.character_service.get_data_dir", lambda: str(tmp_path))
    # Patch d'environnement pour garantir l'isolation même en cas d'import précoce
    os.environ['JDR_DATA_DIR'] = str(tmp_path)
    return tmp_path


@pytest.fixture
def mock_llm_response():
    """
    ### mock_llm_response
    **Description :** Fixture pour mocker les réponses LLM dans les tests.
    **Paramètres :** Aucun
    **Retour :** Dict contenant une réponse LLM simulée.
    """
    return {
        "response": "Bienvenue dans cette aventure ! Vous vous trouvez à l'entrée d'une caverne mystérieuse...",
        "session_id": None,  # Sera remplacé par l'ID réel dans les tests
        "character_name": "Test Hero",
        "scenario_name": "Les_Pierres_du_Passe.md"
    }


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_files():
    """
    ### cleanup_test_files
    **Description :** Fixture de session qui nettoie automatiquement tous les fichiers ET répertoires de test créés pendant la session de test.
    """
    sessions_dir = Path(get_data_dir()) / "sessions"
    
    # Enregistrer l'état initial (fichiers et répertoires)
    initial_files = set()
    initial_dirs = set()
    if sessions_dir.exists():
        initial_files = {f.name for f in sessions_dir.glob("*.jsonl")}
        initial_dirs = {d.name for d in sessions_dir.iterdir() if d.is_dir()}
    
    yield  # Tous les tests s'exécutent ici
    
    # Nettoyage final de tous les fichiers et répertoires de test créés pendant la session
    if sessions_dir.exists():
        current_files = {f.name for f in sessions_dir.glob("*.jsonl")}
        current_dirs = {d.name for d in sessions_dir.iterdir() if d.is_dir()}
        
        test_files = current_files - initial_files
        test_dirs = current_dirs - initial_dirs
        
        if test_files or test_dirs:
            print(f"\n🧹 Nettoyage de session: {len(test_files)} fichiers et {len(test_dirs)} répertoires de test à supprimer")
            
            # Supprimer les fichiers de test
            for file_name in test_files:
                file_path = sessions_dir / file_name
                if file_path.exists():
                    try:
                        file_path.unlink()
                        print(f"   ✅ 📄 {file_name}")
                    except Exception as e:
                        print(f"   ❌ 📄 {file_name}: {e}")
            
            # Supprimer les répertoires de test
            for dir_name in test_dirs:
                dir_path = sessions_dir / dir_name
                if dir_path.exists():
                    try:
                        shutil.rmtree(dir_path)
                        print(f"   ✅ 📁 {dir_name}/")
                    except Exception as e:
                        print(f"   ❌ 📁 {dir_name}/: {e}")

def pytest_sessionfinish(session, exitstatus):
    """
    ### pytest_sessionfinish
    **Description :** Hook exécuté à la fin de la session de tests pour un nettoyage final.
    """
    try:
        from back.tests.cleanup_test_sessions import cleanup_test_sessions
        
        if exitstatus == 0:  # Tests réussis
            print("\n🎉 Tous les tests ont réussi !")
        else:
            print(f"\n⚠️ Tests terminés avec le code de sortie : {exitstatus}")
        
        print("🧹 Nettoyage final des fichiers de test...")
        cleanup_test_sessions()
    except ImportError:
        print("⚠️ Script de nettoyage non trouvé")
    except Exception as e:
        print(f"⚠️ Erreur lors du nettoyage : {e}")

@pytest.fixture
def character_79e55c14(isolated_data_dir):
    """
    Fixture qui crée le fichier du personnage 79e55c14-7dd5-4189-b209-ea88f6d067eb dans le dossier characters du répertoire isolé.
    Le JSON contient les champs à la racine ET dans 'state' pour compatibilité maximale.
    """
    import json
    from uuid import UUID
    character_data = {
        "id": "79e55c14-7dd5-4189-b209-ea88f6d067eb",
        "name": "Galadhwen",
        "race": "Elfe Sylvain",
        "culture": "Rurale",
        "profession": "Aventurier",
        "caracteristiques": {
            "Force": 69,
            "Constitution": 69,
            "Agilité": 69,
            "Rapidité": 69,
            "Volonté": 69,
            "Raisonnement": 69,
            "Intuition": 68,
            "Présence": 68
        },
        "competences": {"Comédie": 21, "Perception": 42, "Survie": 33},
        "hp": 102,
        "xp": 0,
        "gold": 0,
        "inventory": [],
        "equipment": ["Bandoulière", "Coutelas", "Bottes de cuir", "Gants de cuir"],
        "talents": [],
        "notes": "",
        "background": "",        "spells": [],
        "culture_bonuses": {},
        "physical_description": "",
    }
    characters_dir = isolated_data_dir / "characters"
    characters_dir.mkdir(exist_ok=True)
    file_path = characters_dir / "79e55c14-7dd5-4189-b209-ea88f6d067eb.json"
    # Format hybride : racine + state
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({**character_data, "state": character_data}, f, ensure_ascii=False, indent=2)
    return file_path
