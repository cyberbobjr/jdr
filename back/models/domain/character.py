from typing import Dict, List, Optional
from pydantic import BaseModel
from uuid import UUID

from back.models.schema import Item, RaceData, CultureData, CharacterStatus

class Character(BaseModel):
    """
    ### Character
    **Description :** Modèle de données représentant un personnage joueur ou non-joueur du JdR. Utilise la définition correcte du schéma principal.
    **Attributs :**
    - `id` (UUID) : Identifiant unique du personnage
    - `name` (str) : Nom du personnage
    - `race` (RaceData) : Objet race complet avec tous les bonus et détails
    - `culture` (CultureData) : Objet culture complet avec tous les bonus et détails
    - `caracteristiques` (Dict[str, int]) : Caractéristiques principales (Force, Constitution, etc.)
    - `competences` (Dict[str, int]) : Compétences et leur niveau
    - `hp` (int) : Points de vie (calculé à partir de Constitution)
    - `xp` (int) : Points d'expérience
    - `gold` (float) : Or possédé (peut avoir des décimales)
    - `inventory` (List[Item]) : Inventaire détaillé avec objets complets
    - `spells` (List[str]) : Liste des sorts connus
    - `culture_bonuses` (Dict[str, int]) : Bonus liés à la culture
    - `background` (str) : Histoire du personnage (background narratif)
    - `physical_description` (str) : Description physique du personnage
    - `status` (CharacterStatus) : Statut du personnage
    """
    id: UUID
    name: str
    race: RaceData
    culture: CultureData
    caracteristiques: Dict[str, int]
    competences: Dict[str, int]
    hp: int = 100  # calculé à partir de Constitution
    xp: int = 0  # Points d'expérience
    gold: float = 0.0  # Or possédé (peut avoir des décimales)
    inventory: List[Item] = []  # Inventaire détaillé avec objets complets
    spells: List[str] = []
    culture_bonuses: Dict[str, int]
    background: str = None  # Histoire du personnage
    physical_description: str = None  # Description physique
    status: CharacterStatus = None  # Statut du personnage
    last_update: Optional[str] = None  # Date de la dernière mise à jour
    
    @staticmethod
    def is_character_finalized(character_dict: Dict) -> bool:
        """
        ### is_character_finalized
        **Description :** Vérifie si un personnage passé sous forme de dictionnaire contient tous les champs obligatoires pour être considéré comme finalisé.
        **Parameters :**
        - `character_dict` (Dict) : Dictionnaire représentant un personnage
        **Returns :** bool - True si le personnage est finalisé, False sinon
        """
        required_fields = [
            'id', 'name', 'race', 'culture', 'caracteristiques', 
            'competences', 'culture_bonuses'
        ]
        
        # Vérifier que tous les champs obligatoires sont présents et non None
        for field in required_fields:
            if field not in character_dict or character_dict[field] is None:
                return False
        
        # Vérifications spécifiques pour certains champs
        # Race doit avoir un nom
        if 'name' not in character_dict.get('race', {}) or not character_dict['race']['name']:
            return False
            
        # Culture doit avoir un nom
        if 'name' not in character_dict.get('culture', {}) or not character_dict['culture']['name']:
            return False
            
        # Les caractéristiques doivent contenir les attributs de base
        required_characteristics = ['Force', 'Constitution', 'Dextérité', 'Intelligence', 'Perception', 'Charisme']
        caracteristiques = character_dict.get('caracteristiques', {})
        for char in required_characteristics:
            if char not in caracteristiques:
                return False
                
        # Les compétences ne peuvent pas être vides
        if not character_dict.get('competences', {}):
            return False
            
        return True
