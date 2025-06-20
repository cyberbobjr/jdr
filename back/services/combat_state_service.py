"""
### CombatStateService
**Description :** Service pour persister et charger l'état des combats en cours.
"""

import json
import pathlib
from typing import Optional
from back.models.domain.combat_state import CombatState
from back.utils.logger import log_debug
from back.config import get_data_dir


class CombatStateService:
    """
    ### CombatStateService
    **Description :** Service pour gérer la persistance de l'état des combats actifs.
    """
    
    def __init__(self):
        """
        ### __init__
        **Description :** Initialise le service avec le chemin vers le répertoire de données.
        """
        self.data_dir = pathlib.Path(get_data_dir()) / "combat"
        self.data_dir.mkdir(exist_ok=True, parents=True)
    
    def _get_combat_file_path(self, session_id: str) -> pathlib.Path:
        """
        ### _get_combat_file_path
        **Description :** Retourne le chemin du fichier de combat pour une session donnée.
        **Paramètres :**
        - `session_id` (str) : Identifiant de la session.        **Retour :** Chemin vers le fichier de combat.
        """
        return self.data_dir / f"{session_id}_combat.json"
    
    def save_combat_state(self, session_id: str, combat_state: CombatState) -> None:
        """
        ### save_combat_state
        **Description :** Sauvegarde l'état du combat dans un fichier JSON.
        **Paramètres :**
        - `session_id` (str) : Identifiant de la session.
        - `combat_state` (CombatState) : État du combat à sauvegarder.
        **Retour :** Aucun.
        """
        try:
            file_path = self._get_combat_file_path(session_id)
            # Créer le répertoire s'il n'existe pas
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(combat_state.model_dump(), f, ensure_ascii=False, indent=2)
            
            log_debug("État du combat sauvegardé", 
                     action="save_combat_state", 
                     session_id=session_id, 
                     combat_id=combat_state.combat_id,
                     round=combat_state.round,
                     status=combat_state.status)
        except Exception as e:
            log_debug("Erreur lors de la sauvegarde de l'état du combat", 
                     error=str(e), 
                     session_id=session_id)
            raise
    
    def load_combat_state(self, session_id: str) -> Optional[CombatState]:
        """
        ### load_combat_state
        **Description :** Charge l'état du combat depuis un fichier JSON.
        **Paramètres :**
        - `session_id` (str) : Identifiant de la session.
        **Retour :** État du combat chargé ou None si aucun combat actif.
        """
        try:
            file_path = self._get_combat_file_path(session_id)
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            combat_state = CombatState(**data)
            
            log_debug("État du combat chargé", 
                     action="load_combat_state", 
                     session_id=session_id, 
                     combat_id=combat_state.combat_id,
                     round=combat_state.round,
                     status=combat_state.status)
            
            return combat_state
        except Exception as e:
            log_debug("Erreur lors du chargement de l'état du combat", 
                     error=str(e), 
                     session_id=session_id)
            return None
    
    def delete_combat_state(self, session_id: str) -> None:
        """
        ### delete_combat_state
        **Description :** Supprime l'état du combat (combat terminé).
        **Paramètres :**
        - `session_id` (str) : Identifiant de la session.
        **Retour :** Aucun.
        """
        try:
            file_path = self._get_combat_file_path(session_id)
            if file_path.exists():
                file_path.unlink()
                log_debug("État du combat supprimé", 
                         action="delete_combat_state", 
                         session_id=session_id)
        except Exception as e:
            log_debug("Erreur lors de la suppression de l'état du combat", 
                     error=str(e), 
                     session_id=session_id)
    
    def has_active_combat(self, session_id: str) -> bool:
        """
        ### has_active_combat
        **Description :** Vérifie si une session a un combat actif.
        **Paramètres :**
        - `session_id` (str) : Identifiant de la session.
        **Retour :** True si un combat est actif, False sinon.
        """
        combat_state = self.load_combat_state(session_id)
        return combat_state is not None and combat_state.status == "en_cours"
