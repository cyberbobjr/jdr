"""
Service de gestion des sessions de jeu de rôle.
Gère le chargement et la sauvegarde de l'historique, ainsi que les données de personnage et de scénario.
"""

import os
import pathlib
from typing import Dict, Any, Optional, List

from back.services.character_service import CharacterService
from back.storage.pydantic_jsonl_store import PydanticJsonlStore
from back.config import get_data_dir


class SessionService:
    """
    ### SessionService
    **Description :** Service de gestion des sessions de jeu, incluant l'historique des messages,
    les données du personnage et du scénario.
    **Attributs :**
    - `session_id` (str) : Identifiant de la session
    - `character_data` (Dict[str, Any]) : Données du personnage de la session
    - `scenario_name` (str) : Nom du scénario associé à la session
    - `store` (PydanticJsonlStore) : Store pour l'historique des messages
    """
    def __init__(self, session_id: str, character_id: Optional[str] = None, scenario_name: Optional[str] = None):
        """
        ### __init__
        **Description :** Initialise le service de session avec un identifiant.
        **Paramètres :**
        - `session_id` (str) : Identifiant unique de la session
        - `character_id` (Optional[str]) : ID du personnage pour créer une nouvelle session
        - `scenario_name` (Optional[str]) : Nom du scénario pour créer une nouvelle session
        """
        self.session_id = session_id
        self.character_id = character_id
        self.character_data: Dict[str, Any] = {}
        self.scenario_name: str = ""
        self.character_service: Optional[CharacterService] = None        
        # Initialiser le store pour l'historique
        if not os.path.isabs(session_id):
            history_path = os.path.join(get_data_dir(), "sessions", f"{session_id}.jsonl")
        else:
            history_path = session_id + ".jsonl"
        self.store = PydanticJsonlStore(history_path)
        
        # Charger les données de session ou créer une nouvelle session
        if not self._load_session_data():
            # Si la session n'existe pas et qu'on a fourni les paramètres, créer une nouvelle session
            if character_id and scenario_name:
                self._create_session(character_id, scenario_name)
            else:
                raise ValueError(f"Session {session_id} n'existe pas et les paramètres de création ne sont pas fournis")
            
    def _load_session_data(self) -> bool:
        """
        ### _load_session_data
        **Description :** Charge les données de session (personnage et scénario) depuis les fichiers.
        **Retour :** True si la session existe, False sinon.        """
        session_dir = pathlib.Path(get_data_dir()) / "sessions" / self.session_id
        if session_dir.exists() and session_dir.is_dir():
            # Charger l'ID du personnage
            character_file = session_dir / "character.txt"
            if character_file.exists():
                character_id = character_file.read_text(encoding='utf-8').strip()
                
                self.character_id = character_id  # Important: définir l'attribut character_id
                
                # Créer l'instance CharacterService pour ce personnage
                try:
                    self.character_service = CharacterService(character_id)
                    self.character_data = self.character_service.character_data.model_dump()
                except FileNotFoundError:
                    raise ValueError(f"Personnage {character_id} introuvable")
            
            # Charger le nom du scénario
            scenario_file = session_dir / "scenario.txt"
            if scenario_file.exists():
                self.scenario_name = scenario_file.read_text(encoding='utf-8').strip()
            else:
                self.scenario_name = 'Les_Pierres_du_Passe.md'  # Scénario par défaut
            
            return True
        
        return False
    def _create_session(self, character_id: str, scenario_name: str):
        """
        ### _create_session
        **Description :** Crée une nouvelle session avec l'ID du personnage et le nom du scénario.
        **Paramètres :**        - `character_id` (str) : ID du personnage
        - `scenario_name` (str) : Nom du scénario
        """
        session_dir = pathlib.Path(get_data_dir()) / "sessions" / self.session_id
        
        # Créer le répertoire de session
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarder l'ID du personnage
        character_file = session_dir / "character.txt"
        character_file.write_text(character_id, encoding='utf-8')
        
        # Sauvegarder le nom du scénario
        scenario_file = session_dir / "scenario.txt"
        scenario_file.write_text(scenario_name, encoding='utf-8')
          # Définir l'attribut character_id
        self.character_id = character_id
        
        # Créer l'instance CharacterService pour ce personnage
        try:
            self.character_service = CharacterService(character_id)
            self.character_data = self.character_service.character_data.model_dump()
        except FileNotFoundError:
            raise ValueError(f"Personnage {character_id} introuvable")
        
        self.scenario_name = scenario_name
    
    @staticmethod
    def list_all_sessions() -> List[Dict[str, Any]]:
        """
        ### list_all_sessions        **Description :** Récupère la liste de toutes les sessions avec les informations du scénario et du personnage.
        **Retour :** Liste de dictionnaires contenant les informations de chaque session
        """
        sessions_dir = pathlib.Path(get_data_dir()) / "sessions"
        
        all_sessions = []
        
        if sessions_dir.exists() and sessions_dir.is_dir():
            for session_path in sessions_dir.iterdir():
                if session_path.is_dir():
                    # Charger l'ID du personnage
                    character_file = session_path / "character.txt"
                    if character_file.exists():
                        character_id = character_file.read_text(encoding='utf-8').strip()
                    else:
                        character_id = "Inconnu"
                    
                    # Charger le nom du scénario
                    scenario_file = session_path / "scenario.txt"
                    if scenario_file.exists():
                        scenario_name = scenario_file.read_text(encoding='utf-8').strip()
                    else:
                        scenario_name = "Inconnu"
                    
                    all_sessions.append({
                        "session_id": session_path.name,
                        "character_id": character_id,
                        "scenario_name": scenario_name
                    })
        
        return all_sessions

    # Les méthodes suivantes sont supprimées car elles ne sont utilisées que dans les tests :
    # - load_history
    # - save_history
    # - update_character_data
