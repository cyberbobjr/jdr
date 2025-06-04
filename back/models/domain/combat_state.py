from typing import List, Dict, Optional
from pydantic import BaseModel

class CombatState(BaseModel):
    """
    ### CombatState
    **Description :** Classe centrale pour stocker l’état courant du combat (participants, initiative, round, statut, etc.).
    **Attributs :**
    - `combat_id` (str) : Identifiant unique du combat.
    - `round` (int) : Numéro du round en cours.
    - `participants` (List[Dict]) : Liste des participants (id, nom, PV, statut, initiative, etc.).
    - `initiative_order` (List[str]) : Ordre d’initiative (liste d’IDs).
    - `current_turn` (int) : Index du participant dont c’est le tour.
    - `log` (List[str]) : Historique des actions du combat.
    - `status` (str) : Statut du combat ("en_cours", "termine", etc.).
    - `end_reason` (Optional[str]) : Raison de la fin du combat (victoire, fuite, reddition, etc.).
    """
    combat_id: str
    round: int = 1
    participants: List[Dict]
    initiative_order: List[str]
    current_turn: int = 0
    log: List[str] = []
    status: str = "en_cours"
    end_reason: Optional[str] = None
