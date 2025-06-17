from typing import Dict, List, Optional
from pydantic import BaseModel
from .base import RaceData, CultureData

class Character(BaseModel):
    """
    ### Character
    **Description :** Modèle de données représentant un personnage joueur ou non-joueur du JdR. Utilisé pour typer `character_data` lors de l'initialisation de `GMAgentDependencies`.
    **Attributs :**
    - `concept` (str) : Concept ou archétype du personnage
    - `race` (RaceData) : Objet race complet avec tous les bonus et détails
    - `culture` (CultureData) : Objet culture complet avec tous les bonus et détails
    - `profession` (str) : Profession principale
    - `caracteristiques` (Dict[str, int]) : Caractéristiques principales (Force, Constitution, etc.)
    - `competences` (Dict[str, int]) : Compétences et leur niveau
    - `talents` (List[str]) : Liste des talents
    - `equipment` (List[str]) : Liste des équipements
    - `spells` (List[str]) : Liste des sorts connus
    - `current_step` (str) : Étape courante de création ou d'évolution
    - `equipment_summary` (Dict[str, float]) : Synthèse de l'équipement (coût, poids, argent restant, etc.)
    - `culture_bonuses` (Dict[str, int]) : Bonus liés à la culture
    - `name` (str) : Nom du personnage
    - `bonus_race` (Dict[str, int]) : Bonus liés à la race
    - `hp` (int) : Points de vie
    - `xp` (int) : Expérience accumulée
    - `background` (str) : Histoire du personnage (background narratif)
    - `physical_description` (str) : Description physique du personnage
    - `created_at` (Optional[str]) : Date de création (ISO)
    - `last_update` (Optional[str]) : Date de dernière mise à jour (ISO)
    """
    concept: str
    race: RaceData
    culture: CultureData
    profession: str
    caracteristiques: Dict[str, int]
    competences: Dict[str, int]
    talents: List[str]
    equipment: List[str]
    spells: List[str]
    current_step: str
    equipment_summary: Dict[str, float]
    culture_bonuses: Dict[str, int]
    name: str
    bonus_race: Dict[str, int]
    hp: int
    xp: int
    background: str
    physical_description: str
    created_at: Optional[str] = None
    last_update: Optional[str] = None
