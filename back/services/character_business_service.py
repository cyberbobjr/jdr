"""
Service spécialisé pour la logique métier des personnages.
Respect du SRP - Responsabilité unique : logique métier (XP, or, dégâts).
"""

from back.models.domain.character import Character
from back.services.character_data_service import CharacterDataService
from back.config import get_logger

logger = get_logger(__name__)


class CharacterBusinessService:
    """
    ### CharacterBusinessService
    **Description:** Service spécialisé dans la logique métier des personnages.
    **Responsabilité unique:** Gestion de la logique métier (XP, or, dégâts).
    """
    
    def __init__(self, data_service: CharacterDataService):
        """
        ### __init__
        **Description:** Initialise le service de logique métier avec un service de données.
        **Paramètres:**
        - `data_service` (CharacterDataService): Service de données pour la persistance
        """
        self.data_service = data_service
    
    def apply_xp(self, character: Character, xp: int) -> Character:
        """
        ### apply_xp
        **Description:** Ajoute de l'XP au personnage.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `xp` (int): Points d'expérience à ajouter
        **Retour:** Personnage modifié
        """
        character.xp += xp
        self.data_service.save_character(character)
        
        logger.info("XP ajouté au personnage",
                   extra={"action": "apply_xp",
                          "character_id": str(character.id),
                          "xp_ajoute": xp,
                          "xp_total": character.xp})
        
        return character
    
    def add_gold(self, character: Character, gold: float) -> Character:
        """
        ### add_gold
        **Description:** Ajoute de l'or au portefeuille du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `gold` (float): Montant d'or à ajouter (peut avoir des décimales)
        **Retour:** Personnage modifié
        """
        character.gold += gold
        self.data_service.save_character(character)
        
        logger.info("Or ajouté au personnage",
                   extra={"action": "add_gold",
                          "character_id": str(character.id),
                          "gold_ajoute": gold,
                          "gold_total": character.gold})
        
        return character
    
    def take_damage(self, character: Character, amount: int, source: str = "combat") -> Character:
        """
        ### take_damage
        **Description:** Diminue les points de vie du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `amount` (int): Points de dégâts à appliquer
        - `source` (str): Source des dégâts (optionnel)
        **Retour:** Personnage modifié
        """
        character.hp = max(0, character.hp - amount)
        self.data_service.save_character(character)
        
        logger.warning("Dégâts appliqués au personnage",
                      extra={"action": "take_damage",
                             "character_id": str(character.id),
                             "amount": amount,
                             "hp_restant": character.hp,
                             "source": source})
        
        return character
    
    def heal(self, character: Character, amount: int, source: str = "soin") -> Character:
        """
        ### heal
        **Description:** Augmente les points de vie du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `amount` (int): Points de vie à restaurer
        - `source` (str): Source du soin (optionnel)
        **Retour:** Personnage modifié
        """
        # TODO: Définir les PV maximums selon la constitution
        max_hp = 100  # Valeur temporaire
        character.hp = min(max_hp, character.hp + amount)
        self.data_service.save_character(character)
        
        logger.info("Soins appliqués au personnage",
                   extra={"action": "heal",
                          "character_id": str(character.id),
                          "amount": amount,
                          "hp_restant": character.hp,
                          "source": source})
        
        return character
    
    def calculate_max_hp(self, character: Character) -> int:
        """
        ### calculate_max_hp
        **Description:** Calcule les PV maximums du personnage basés sur sa constitution.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        **Retour:** PV maximums calculés
        """
        # TODO: Implémenter la formule de calcul des PV basée sur la constitution
        constitution = character.stats.get("Constitution", 50)
        base_hp = 50  # PV de base
        constitution_bonus = (constitution - 50) // 10  # +1 PV tous les 10 points de constitution
        
        return base_hp + constitution_bonus
    
    def is_alive(self, character: Character) -> bool:
        """
        ### is_alive
        **Description:** Vérifie si le personnage est en vie.
        **Paramètres:**
        - `character` (Character): Personnage à vérifier
        **Retour:** True si le personnage est en vie, False sinon
        """
        return character.hp > 0
    
    def get_level(self, character: Character) -> int:
        """
        ### get_level
        **Description:** Calcule le niveau du personnage basé sur son XP.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        **Retour:** Niveau calculé
        """
        # TODO: Implémenter la table de progression par niveau
        xp = character.xp
        
        if xp < 1000:
            return 1
        elif xp < 3000:
            return 2
        elif xp < 6000:
            return 3
        elif xp < 10000:
            return 4
        elif xp < 15000:
            return 5
        else:
            return 6 + (xp - 15000) // 5000  # +1 niveau tous les 5000 XP après niveau 5
