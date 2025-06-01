# Logique métier unitaire (SRP)

import os
from uuid import UUID
from uuid import uuid4
from typing import List
from back.models.schema import ScenarioStatus
from back.utils.logger import log_debug


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
                    available.append(ScenarioStatus(name=fname, status="available"))

        # Scénarios en cours (dossiers UUID dans data/sessions)
        in_progress = []
        if os.path.isdir(sessions_dir):
            for d in os.listdir(sessions_dir):
                dir_path = os.path.join(sessions_dir, d)
                if os.path.isdir(dir_path):
                    try:
                        session_id = UUID(d)
                        in_progress.append(ScenarioStatus(name=str(session_id), status="in_progress", session_id=session_id))
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
        return [f for f in os.listdir(base_dir) if f.endswith(".md")]

    @staticmethod
    def start_scenario(scenario_name: str, character_id: UUID) -> dict:
        """
        ### start_scenario
        **Description:** Démarre un scénario avec un personnage spécifique et crée une session unique.
        **Parameters:**
        - `scenario_name` (str): Le nom du scénario à démarrer.
        - `character_id` (UUID): L'identifiant du personnage.
        **Returns:**
        - dict: Un dictionnaire contenant l'id de session, le nom du scénario, l'id du personnage et un message de confirmation.
        """
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

        return {
            "session_id": session_id,
            "scenario_name": scenario_name,
            "character_id": str(character_id),
            "message": f"Scénario '{scenario_name}' démarré avec succès pour le personnage {character_id}."
        }
