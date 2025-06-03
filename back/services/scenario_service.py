# Logique métier unitaire (SRP)

import os
from uuid import UUID
from uuid import uuid4
from typing import List
from back.models.schema import ScenarioStatus
from back.utils.logger import log_debug
from back.services.character_service import CharacterService


class ScenarioService:
    """
    ### list_scenarios
    **Description:** Liste les scénarios disponibles et ceux en cours.
    **Parameters:** Aucun.
    **Returns:** Liste de `ScenarioStatus`, incluant le nom, le statut et l'ID de session (le cas échéant).
    """
    @staticmethod
    def list_scenarios() -> List[ScenarioStatus]:
        # Définir les chemins vers les dossiers scenarios et sessions
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
        scenarios_dir = os.path.join(base_dir, "scenarios")
        sessions_dir = os.path.join(base_dir, "sessions")

        # Scénarios disponibles (*.md dans data/scenarios)
        available = []
        if os.path.isdir(scenarios_dir):
            for fname in os.listdir(scenarios_dir):
                if fname.endswith(".md"):
                    available.append(ScenarioStatus(name=fname, status="available"))        # Scénarios en cours (dossiers UUID dans data/sessions)
        in_progress = []
        if os.path.isdir(sessions_dir):
            for d in os.listdir(sessions_dir):
                dir_path = os.path.join(sessions_dir, d)
                if os.path.isdir(dir_path):
                    try:
                        session_id = UUID(d)
                        
                        # Enrichir avec les noms explicites
                        scenario_name = None
                        character_name = None
                        try:
                            session_info = ScenarioService.get_session_info(str(session_id))
                            scenario_name = session_info.get("scenario_name")
                            character_id = session_info.get("character_id")
                            
                            # Récupérer le nom du personnage
                            if character_id:
                                character = CharacterService.get_character(character_id)
                                character_name = character.name
                                
                        except Exception as e:
                            log_debug("Impossible de récupérer les infos enrichies pour la session", 
                                    action="list_scenarios", session_id=str(session_id), error=str(e))
                        
                        # Créer un nom d'affichage plus explicite
                        display_name = str(session_id)
                        if scenario_name and character_name:
                            display_name = f"{scenario_name} - {character_name}"
                        elif scenario_name:
                            display_name = f"{scenario_name} - Session {str(session_id)[:8]}"
                        
                        in_progress.append(ScenarioStatus(
                            name=display_name, 
                            status="in_progress", 
                            session_id=session_id,
                            scenario_name=scenario_name,
                            character_name=character_name
                        ))
                    except Exception:
                        continue

        log_debug("Liste des scénarios demandée", action="list_scenarios", available=len(available), in_progress=len(in_progress))
        return available + in_progress

    @staticmethod
    def get_scenario_details(scenario_file: str) -> str:
        """
        Récupère le contenu d'un scénario (fichier Markdown) à partir de son nom de fichier.
        
        Parameters:
        - scenario_file (str): Le nom du fichier du scénario (ex: Les_Pierres_du_Passe.md).
        
        Returns:
        - str: Le contenu du fichier Markdown du scénario.
        
        Raises:
        - FileNotFoundError: Si le fichier n'existe pas.
        """
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/scenarios"))
        scenario_path = os.path.join(base_dir, scenario_file)
        if not os.path.isfile(scenario_path):
            raise FileNotFoundError(f"Le scénario '{scenario_file}' n'existe pas.")
        with open(scenario_path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def get_all_scenarios() -> list:
        """
        Liste tous les scénarios disponibles (obsolète, tool supprimé).

        Returns:
        - list: Une liste des scénarios disponibles.
        """
        # Cette méthode est conservée pour compatibilité, mais n'utilise plus de tool.
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/scenarios"))
        return [f for f in os.listdir(base_dir) if f.endswith(".md")]    @staticmethod
    def start_scenario(scenario_name: str, character_id: UUID) -> dict:
        """
        ### start_scenario
        **Description:** Démarre un scénario avec un personnage spécifique et crée une session unique.
        **Parameters:**
        - `scenario_name` (str): Le nom du scénario à démarrer.
        - `character_id` (UUID): L'identifiant du personnage.
        **Returns:**
        - dict: Un dictionnaire contenant l'id de session, le nom du scénario, l'id du personnage et un message de confirmation.
        **Raises:**
        - ValueError: Si une session existe déjà avec le même scénario et personnage.
        """
        # Vérifier s'il existe déjà une session avec le même scénario et personnage
        if ScenarioService.check_existing_session(scenario_name, str(character_id)):
            raise ValueError(f"Une session existe déjà pour le scénario '{scenario_name}' avec le personnage {character_id}.")
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
        scenarios_dir = os.path.join(base_dir, "scenarios")
        sessions_dir = os.path.join(base_dir, "sessions")

        # Vérifie si le scénario existe
        scenario_path = os.path.join(scenarios_dir, scenario_name)
        if not os.path.exists(scenario_path):
            raise FileNotFoundError(f"Le scénario '{scenario_name}' n'existe pas.")

        # Crée une session pour le scénario
        session_id = str(uuid4())
        session_dir = os.path.join(sessions_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)

        # Associe le personnage à la session
        with open(os.path.join(session_dir, "character.txt"), "w") as f:
            f.write(str(character_id))
        
        # Stocke le nom du scénario dans la session
        with open(os.path.join(session_dir, "scenario.txt"), "w") as f:
            f.write(scenario_name)

        return {
            "session_id": session_id,
            "scenario_name": scenario_name,
            "character_id": str(character_id),
            "message": f"Scénario '{scenario_name}' démarré avec succès pour le personnage {character_id}."
        }

    @staticmethod
    def get_session_info(session_id: str) -> dict:
        """
        ### get_session_info
        **Description:** Récupère les informations d'une session (character_id et scenario_name) à partir de son ID.
        **Paramètres:**
        - `session_id` (str): L'identifiant de la session.
        **Retour:**
        - dict: Un dictionnaire contenant character_id et scenario_name, ou lève une exception si la session n'existe pas.
        """
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
        session_dir = os.path.join(base_dir, "sessions", session_id)
        
        if not os.path.isdir(session_dir):
            raise FileNotFoundError(f"La session '{session_id}' n'existe pas.")
        
        # Récupérer l'ID du personnage
        character_file = os.path.join(session_dir, "character.txt")
        if not os.path.exists(character_file):
            raise FileNotFoundError(f"Fichier character.txt manquant pour la session '{session_id}'.")
        
        with open(character_file, "r") as f:
            character_id = f.read().strip()
        
        # Récupérer le nom du scénario
        scenario_file = os.path.join(session_dir, "scenario.txt")
        if not os.path.exists(scenario_file):
            raise FileNotFoundError(f"Fichier scenario.txt manquant pour la session '{session_id}'.")
        
        with open(scenario_file, "r") as f:
            scenario_name = f.read().strip()
        
        log_debug("Informations de session récupérées", action="get_session_info", session_id=session_id, character_id=character_id, scenario_name=scenario_name)
        return {
            "character_id": character_id,
            "scenario_name": scenario_name
        }

    @staticmethod
    def check_existing_session(scenario_name: str, character_id: str) -> bool:
        """
        ### check_existing_session
        **Description:** Vérifie s'il existe déjà une session avec le même scénario et personnage.
        **Parameters:**
        - `scenario_name` (str): Le nom du scénario.
        - `character_id` (str): L'identifiant du personnage.
        **Returns:**
        - bool: True si une session existe déjà, False sinon.
        """
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
        sessions_dir = os.path.join(base_dir, "sessions")
        
        if not os.path.isdir(sessions_dir):
            return False
            
        # Parcourir tous les dossiers de session
        for session_folder in os.listdir(sessions_dir):
            session_path = os.path.join(sessions_dir, session_folder)
            
            # Vérifier que c'est un dossier et qu'il a la structure d'une session UUID
            if os.path.isdir(session_path):
                try:
                    # Vérifier que c'est un UUID valide
                    UUID(session_folder)
                    
                    # Vérifier les fichiers scenario.txt et character.txt
                    scenario_file = os.path.join(session_path, "scenario.txt")
                    character_file = os.path.join(session_path, "character.txt")
                    
                    if os.path.exists(scenario_file) and os.path.exists(character_file):
                        with open(scenario_file, "r", encoding="utf-8") as f:
                            existing_scenario = f.read().strip()
                        with open(character_file, "r", encoding="utf-8") as f:
                            existing_character = f.read().strip()
                            
                        # Comparer avec les paramètres fournis
                        if existing_scenario == scenario_name and existing_character == character_id:
                            log_debug("Session existante trouvée", 
                                    action="check_existing_session", 
                                    session_id=session_folder,
                                    scenario_name=scenario_name, 
                                    character_id=character_id)
                            return True
                            
                except (ValueError, FileNotFoundError):
                    # Ignorer les dossiers invalides ou les erreurs de lecture
                    continue
        
        return False
