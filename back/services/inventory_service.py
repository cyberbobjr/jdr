"""
Service spécialisé pour la gestion de l'inventaire des personnages.
Respect du SRP - Responsabilité unique : gestion des objets d'inventaire.
"""

from typing import List
from back.models.domain.character import Character
from back.models.schema import Item
from back.services.character_data_service import CharacterDataService
from back.services.item_service import ItemService
from back.config import get_logger

logger = get_logger(__name__)


class InventoryService:
    """
    ### InventoryService
    **Description:** Service spécialisé dans la gestion de l'inventaire des personnages.
    **Responsabilité unique:** Gestion des objets d'inventaire (ajout, retrait, équipement).
    """
    
    def __init__(self, data_service: CharacterDataService):
        """
        ### __init__
        **Description:** Initialise le service d'inventaire avec un service de données.
        **Paramètres:**
        - `data_service` (CharacterDataService): Service de données pour la persistance
        """
        self.data_service = data_service
    
    def add_item(self, character: Character, item_id: str, quantity: int = 1) -> Character:
        """
        ### add_item
        **Description:** Ajoute un objet à l'inventaire du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `item_id` (str): Identifiant de l'objet
        - `quantity` (int): Quantité à ajouter (défaut: 1)
        **Retour:** Personnage modifié
        """
        logger.info("Objet ajouté à l'inventaire",
                   extra={"action": "add_item",
                          "character_id": str(character.id),
                          "item_id": item_id,
                          "quantity": quantity})
        
        # Initialiser l'inventaire si nécessaire
        if character.inventory is None:
            character.inventory = []
        
        # Vérifier si l'objet existe déjà
        existing_item = self._find_item_by_id(character, item_id)
        
        if existing_item:
            existing_item.quantity += quantity
        else:
            # Créer un nouvel objet
            item_service = ItemService()
            new_item = item_service.create_item_from_name(item_id, quantity=quantity)
            character.inventory.append(new_item)
        
        self.data_service.save_character(character)
        return character
    
    def remove_item(self, character: Character, item_id: str, quantity: int = 1) -> Character:
        """
        ### remove_item
        **Description:** Retire un objet de l'inventaire du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `item_id` (str): Identifiant de l'objet
        - `quantity` (int): Quantité à retirer (défaut: 1)
        **Retour:** Personnage modifié
        """
        logger.info("Objet retiré de l'inventaire",
                   extra={"action": "remove_item",
                          "character_id": str(character.id),
                          "item_id": item_id,
                          "quantity": quantity})
        
        if not character.inventory:
            return character
        
        for i, item in enumerate(character.inventory):
            if item.id == item_id:
                item.quantity -= quantity
                if item.quantity <= 0:
                    del character.inventory[i]
                break
        
        self.data_service.save_character(character)
        return character
    
    def equip_item(self, character: Character, item_id: str) -> Character:
        """
        ### equip_item
        **Description:** Équipe un objet pour le personnage.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `item_id` (str): Identifiant de l'objet
        **Retour:** Personnage modifié
        """
        logger.info("Objet équipé",
                   extra={"action": "equip_item",
                          "character_id": str(character.id),
                          "item_id": item_id})
        
        if not character.inventory:
            return character
        
        for item in character.inventory:
            if item.id == item_id:
                item.is_equipped = True
                break
        
        self.data_service.save_character(character)
        return character
    
    def unequip_item(self, character: Character, item_id: str) -> Character:
        """
        ### unequip_item
        **Description:** Déséquipe un objet pour le personnage.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `item_id` (str): Identifiant de l'objet
        **Retour:** Personnage modifié
        """
        logger.info("Objet déséquipé",
                   extra={"action": "unequip_item",
                          "character_id": str(character.id),
                          "item_id": item_id})
        
        if not character.inventory:
            return character
        
        for item in character.inventory:
            if item.id == item_id:
                item.is_equipped = False
                break
        
        self.data_service.save_character(character)
        return character
    
    def get_equipped_items(self, character: Character) -> List[Item]:
        """
        ### get_equipped_items
        **Description:** Récupère la liste des objets équipés.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        **Retour:** Liste des objets équipés
        """
        if not character.inventory:
            return []
        
        return [item for item in character.inventory if item.is_equipped]
    
    def item_exists(self, character: Character, item_id: str) -> bool:
        """
        ### item_exists
        **Description:** Vérifie si un objet existe dans l'inventaire.
        **Paramètres:**
        - `character` (Character): Personnage à vérifier
        - `item_id` (str): Identifiant de l'objet
        **Retour:** True si l'objet existe, False sinon
        """
        return self._find_item_by_id(character, item_id) is not None
    
    def get_item_quantity(self, character: Character, item_id: str) -> int:
        """
        ### get_item_quantity
        **Description:** Récupère la quantité d'un objet dans l'inventaire.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        - `item_id` (str): Identifiant de l'objet
        **Retour:** Quantité de l'objet (0 si non présent)
        """
        item = self._find_item_by_id(character, item_id)
        return item.quantity if item else 0
    
    def calculate_total_weight(self, character: Character) -> float:
        """
        ### calculate_total_weight
        **Description:** Calcule le poids total de l'inventaire.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        **Retour:** Poids total en kilogrammes
        """
        if not character.inventory:
            return 0.0
        
        total_weight = 0.0
        for item in character.inventory:
            total_weight += item.weight_kg * item.quantity
        
        return total_weight
    
    def _find_item_by_id(self, character: Character, item_id: str) -> Item | None:
        """
        ### _find_item_by_id
        **Description:** Recherche un objet par son identifiant dans l'inventaire.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        - `item_id` (str): Identifiant de l'objet
        **Retour:** Objet trouvé ou None
        """
        if not character.inventory:
            return None
        
        for item in character.inventory:
            if item.id == item_id:
                return item
        
        return None
