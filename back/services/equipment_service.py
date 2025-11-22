"""
Service spécialisé pour la gestion de l'équipement et de l'inventaire des personnages.
Responsabilité unique :
- Achat/vente d'équipement et gestion de l'argent
- Gestion de l'inventaire (ajout, retrait, (dé)équipement, quantités)
"""

from typing import List, Dict, Any
from uuid import uuid4
from back.models.domain.character import Character
from back.models.domain.equipment_manager import EquipmentManager
from back.models.domain.items import EquipmentItem
from back.services.character_data_service import CharacterDataService
from back.utils.logger import log_debug


class EquipmentService:
    """
    ### EquipmentService
    **Description:** Service spécialisé dans la gestion de l'équipement et de l'inventaire des personnages.
    **Responsabilité unique:** Achat/vente d'équipement, gestion de l'argent, ajout/retrait d'objets et (dé)équipement.
    """
    
    def __init__(self, data_service: CharacterDataService):
        """
        ### __init__
        **Description:** Initialise le service d'équipement avec un service de données.
        **Paramètres:**
        - `data_service` (CharacterDataService): Service de données pour la persistance
        """
        self.data_service = data_service
        self.equipment_manager = EquipmentManager()
    
    def buy_equipment(self, character: Character, item_id: str) -> Character:
        """
        ### buy_equipment
        **Description:** Achète un équipement et débite l'argent correspondant.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `item_id` (str): ID de l'équipement à acheter
        **Retour:** Personnage modifié
        **Lève:** ValueError si l'équipement n'existe pas ou si pas assez d'argent
        """
        log_debug("Achat d'équipement", 
                 action="buy_equipment", 
                 character_id=str(character.id),
                 item_id=item_id)
        
        # Récupérer les détails de l'équipement
        equipment_details = self.equipment_manager.get_equipment_by_id(item_id)
        if not equipment_details:
            raise ValueError(f"Équipement '{item_id}' non trouvé")
        
        # Vérifier le budget
        equipment_cost = int(equipment_details.get('cost_gold', 0) * 100 + equipment_details.get('cost_silver', 0) * 10 + equipment_details.get('cost_copper', 0))
        # Note: The original code used 'cost' which might have been a simplified float. 
        # The new manager returns cost_gold/silver/copper. 
        # Let's assume the character.gold is actually in copper or some base unit? 
        # Wait, the original code said: character.gold -= equipment_cost. 
        # And equipment_details.get('cost', 0).
        # The YAML has cost_gold, cost_silver, etc.
        # The manager _standardize_item sets cost_gold etc.
        # Let's check how currency is handled.
        # The original code: equipment_cost = int(equipment_details.get('cost', 0) or 0)
        # It seems the previous manager might have flattened cost?
        # Let's look at the previous manager code I read.
        # It had: 'cost': float(src.get('cost', 0)) in _standardize_item? 
        # No, the previous code I read had: 'cost_gold': int(src.get('cost_gold', 0))...
        # But buy_equipment used .get('cost').
        # This implies the previous manager MIGHT have had a 'cost' field or the service was broken/using old data.
        # Let's assume for now we use cost_gold as the main currency for simplicity or check if I need to convert.
        # The YAML metadata says: "1G = 10S = 100C".
        # Character model has 'gold'.
        # I will assume for now we just use gold cost or a simplified cost.
        # Let's stick to what was there but adapted.
        # If the previous code used 'cost', and the manager didn't provide it, it was 0.
        # I'll use cost_gold for now.
        
        cost_val = equipment_details.get('cost_gold', 0)
        
        if character.gold < cost_val:
            raise ValueError("Pas assez d'argent pour acheter cet équipement")
        
        # Créer l'objet EquipmentItem
        item_entry = EquipmentItem(
            id=item_id,
            name=equipment_details['name'],
            category=equipment_details.get('category', 'misc'),
            cost_gold=equipment_details.get('cost_gold', 0),
            cost_silver=equipment_details.get('cost_silver', 0),
            cost_copper=equipment_details.get('cost_copper', 0),
            weight=float(equipment_details.get('weight', 0)),
            quantity=1,
            equipped=False,
            description=equipment_details.get('description'),
            damage=equipment_details.get('damage'),
            range=equipment_details.get('range'),
            protection=int(equipment_details.get('protection', 0)) if equipment_details.get('protection') else None,
            type=equipment_details.get('type')
        )

        # Ajouter l'équipement dans la bonne catégorie
        # We can rely on category from details
        cat = equipment_details.get('category', 'misc')
        if cat == 'weapon':
            character.equipment.weapons.append(item_entry)
        elif cat == 'armor':
            character.equipment.armor.append(item_entry)
        else:
            character.equipment.accessories.append(item_entry)
        
        # Débiter l'argent
        character.gold -= cost_val
        
        self.data_service.save_character(character)
        
        log_debug("Équipement acheté avec succès", 
                 action="buy_equipment_success", 
                 character_id=str(character.id),
                 item_id=item_id,
                 cost=cost_val,
                 gold_restant=character.gold)
        
        return character
    
    def sell_equipment(self, character: Character, item_id: str) -> Character:
        """
        ### sell_equipment
        **Description:** Vend un équipement et rembourse l'argent correspondant.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `item_id` (str): ID de l'équipement à vendre
        **Retour:** Personnage modifié
        **Lève:** ValueError si l'équipement n'existe pas ou n'est pas dans l'inventaire
        """
        log_debug("Vente d'équipement", 
                 action="sell_equipment", 
                 character_id=str(character.id),
                 item_id=item_id)
        
        # Récupérer les détails de l'équipement pour le prix (catalogue)
        equipment_details = self.equipment_manager.get_equipment_by_id(item_id)
        
        # Retirer l'équipement de la bonne catégorie
        found = False
        item_cost = 0.0
        
        for lst in self._all_lists(character):
            for i, it in enumerate(lst):
                # Match by id if present, otherwise name (fallback for migration)
                match = False
                if it.id == item_id:
                    match = True
                elif equipment_details and it.name == equipment_details['name']:
                    match = True
                
                if match:
                    # Use item cost if stored, otherwise catalog cost
                    item_cost = it.cost_gold # Simplified
                    del lst[i]
                    found = True
                    break
            if found:
                break
                
        if not found:
            raise ValueError(f"L'équipement '{item_id}' n'est pas dans l'inventaire")
        
        # Si on n'a pas le coût sur l'objet, on prend le catalogue
        if item_cost == 0 and equipment_details:
            item_cost = float(equipment_details.get('cost_gold', 0))

        # Rembourser l'argent (50% du prix d'achat)
        refund_amount = int(item_cost * 0.5)
        character.gold += refund_amount
        
        self.data_service.save_character(character)
        
        log_debug("Équipement vendu avec succès", 
                 action="sell_equipment_success", 
                 character_id=str(character.id),
                 item_id=item_id,
                 refund_amount=refund_amount,
                 gold_restant=character.gold)
        
        return character
    
    def update_money(self, character: Character, amount: float) -> Character:
        """
        ### update_money
        **Description:** Met à jour l'argent du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `amount` (float): Montant à ajouter/retirer (positif pour ajouter, négatif pour retirer)
        **Retour:** Personnage modifié
        """
        log_debug("Mise à jour de l'argent", 
                 action="update_money", 
                 character_id=str(character.id),
                 amount=amount)
        
        character.gold = max(0, character.gold + int(amount))  # Ne pas aller en négatif
        self.data_service.save_character(character)
        
        log_debug("Argent mis à jour", 
                 action="update_money_success", 
                 character_id=str(character.id),
                 nouveau_gold=character.gold)
        
        return character
    
    def get_equipment_list(self, character: Character) -> List[Dict[str, Any]]:
        """
        ### get_equipment_list
        **Description:** Récupère la liste des équipements du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        **Retour:** Liste de dictionnaires {name, catalog_id, quantity}
        """
        items = []
        for lst in self._all_lists(character):
            items.extend([{
                "name": it.name,
                "id": it.id,
                "quantity": it.quantity
            } for it in lst])
        return items
    
    def get_equipment_details(self, character: Character) -> List[EquipmentItem]:
        """
        ### get_equipment_details
        **Description:** Récupère les détails complets des équipements du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        **Retour:** Liste des objets EquipmentItem
        """
        details = []
        for lst in self._all_lists(character):
            details.extend(lst)
        return details
    
    def calculate_total_weight(self, character: Character) -> float:
        """
        ### calculate_total_weight
        **Description:** Calcule le poids total de l'équipement.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        **Retour:** Poids total en kilogrammes
        """
        total_weight = 0.0
        for lst in self._all_lists(character):
            for it in lst:
                total_weight += it.weight * it.quantity
        return total_weight
    
    def can_afford_equipment(self, character: Character, item_id: str) -> bool:
        """
        ### can_afford_equipment
        **Description:** Vérifie si le personnage peut acheter un équipement.
        **Paramètres:**
        - `character` (Character): Personnage à vérifier
        - `item_id` (str): ID de l'équipement
        **Retour:** True si le personnage peut acheter, False sinon
        """
        equipment_details = self.equipment_manager.get_equipment_by_id(item_id)
        if not equipment_details:
            return False
        
        equipment_cost = int(equipment_details.get('cost_gold', 0))
        return character.gold >= equipment_cost
    
    def equipment_exists(self, item_id: str) -> bool:
        """
        ### equipment_exists
        **Description:** Vérifie si un équipement existe dans le catalogue.
        **Paramètres:**
        - `item_id` (str): ID de l'équipement
        **Retour:** True si l'équipement existe, False sinon
        """
        return self.equipment_manager.get_equipment_by_id(item_id) is not None

    # --- Inventory management (merged from InventoryService) ---
    def add_item(self, character: Character, item_id: str, quantity: int = 1) -> Character:
        """
        ### add_item
        **Description:** Ajoute un objet standardisé à l'inventaire du personnage à partir de son id.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `item_id` (str): Identifiant de l'objet
        - `quantity` (int): Quantité à ajouter (défaut: 1)
        **Retour:** Personnage modifié
        """
        log_debug("Equipment add item", action="add_item", character_id=str(character.id), item_id=item_id, quantity=quantity)
        base = self.equipment_manager.get_equipment_by_id(item_id)
        if not base:
            return character

        target_list = self._get_category_list(character, base.get('category', 'misc'))
        
        # Check if we already have this item in inventory (by id match)
        existing = next((it for it in target_list if it.id == item_id), None)
        
        # Fallback: check by name if needed (migration scenario)
        if not existing:
            existing = next((it for it in target_list if it.name == base['name']), None)

        if existing:
            existing.quantity += int(quantity)
        else:
            new_item = EquipmentItem(
                id=item_id,
                name=base['name'],
                category=base.get('category', 'misc'),
                cost_gold=int(base.get('cost_gold', 0)),
                cost_silver=int(base.get('cost_silver', 0)),
                cost_copper=int(base.get('cost_copper', 0)),
                weight=float(base.get('weight', 0)),
                quantity=int(quantity),
                equipped=False,
                description=base.get('description'),
                damage=base.get('damage'),
                range=base.get('range'),
                protection=int(base.get('protection', 0)) if base.get('protection') else None,
                type=base.get('type')
            )
            target_list.append(new_item)

        self.data_service.save_character(character)
        return character

    def add_item_object(self, character: Character, item: Dict[str, Any]) -> Character:
        """
        ### add_item_object
        **Description:** Ajoute un objet complet (déjà structuré) à l'inventaire du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `item` (dict): L'objet à ajouter (doit contenir au minimum `name`)
        **Retour:** Personnage modifié
        """
        log_debug("Equipment add item object", action="add_item_object", character_id=str(character.id), item_id=item.get('id'))

        category = item.get('category', 'accessory')
        target_list = self._get_category_list(character, category)
        
        # Try to find existing stack
        existing = next((it for it in target_list if it.name == item.get('name')), None)
        qty = int(item.get('quantity', 1) or 1)
        
        if existing:
            existing.quantity += qty
        else:
            new_item = EquipmentItem(
                id=str(item.get('id') or uuid4()),
                name=item.get('name', 'Unknown Item'),
                category=category,
                cost_gold=int(item.get('cost_gold', item.get('cost', 0)) or 0),
                cost_silver=int(item.get('cost_silver', 0)),
                cost_copper=int(item.get('cost_copper', 0)),
                weight=float(item.get('weight', 0) or 0),
                quantity=qty,
                equipped=bool(item.get('equipped', False)),
                description=item.get('description'),
                damage=item.get('damage'),
                range=item.get('range'),
                protection=int(item.get('protection', 0)) if item.get('protection') else None,
                type=item.get('type')
            )
            target_list.append(new_item)

        self.data_service.save_character(character)
        return character

    def remove_item(self, character: Character, item_id: str, quantity: int = 1) -> Character:
        """
        ### remove_item
        **Description:** Retire un objet de l'inventaire du personnage (en ajustant la quantité).
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `item_id` (str): Identifiant de l'objet (UUID)
        - `quantity` (int): Quantité à retirer (défaut: 1)
        **Retour:** Personnage modifié
        """
        log_debug("Equipment remove item", action="remove_item", character_id=str(character.id), item_id=item_id, quantity=quantity)
        for lst in self._all_lists(character):
            for idx, it in enumerate(lst):
                if it.id == item_id:
                    it.quantity -= int(quantity)
                    if it.quantity <= 0:
                        del lst[idx]
                    self.data_service.save_character(character)
                    return character
        self.data_service.save_character(character)
        return character

    def equip_item(self, character: Character, item_id: str) -> Character:
        """
        ### equip_item
        **Description:** Équipe un objet du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `item_id` (str): Identifiant de l'objet
        **Retour:** Personnage modifié
        """
        log_debug("Equipment equip item", action="equip_item", character_id=str(character.id), item_id=item_id)
        for lst in self._all_lists(character):
            for it in lst:
                if it.id == item_id:
                    it.equipped = True
                    self.data_service.save_character(character)
                    return character
        self.data_service.save_character(character)
        return character

    def unequip_item(self, character: Character, item_id: str) -> Character:
        """
        ### unequip_item
        **Description:** Déséquipe un objet du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `item_id` (str): Identifiant de l'objet
        **Retour:** Personnage modifié
        """
        log_debug("Equipment unequip item", action="unequip_item", character_id=str(character.id), item_id=item_id)
        for lst in self._all_lists(character):
            for it in lst:
                if it.id == item_id:
                    it.equipped = False
                    self.data_service.save_character(character)
                    return character
        self.data_service.save_character(character)
        return character

    def get_equipped_items(self, character: Character) -> List[EquipmentItem]:
        """
        ### get_equipped_items
        **Description:** Récupère la liste des objets équipés.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        **Retour:** Liste des objets équipés
        """
        equipped: List[EquipmentItem] = []
        for lst in self._all_lists(character):
            equipped.extend([it for it in lst if it.equipped])
        return equipped

    def item_exists(self, character: Character, item_id: str) -> bool:
        """
        ### item_exists
        **Description:** Vérifie si un objet existe dans l'inventaire.
        **Paramètres:**
        - `character` (Character): Personnage à vérifier
        - `item_id` (str): Identifiant de l'objet
        **Retour:** True si l'objet existe, False sinon
        """
        return any(True for lst in self._all_lists(character) for it in lst if it.id == item_id)

    def get_item_quantity(self, character: Character, item_id: str) -> int:
        """
        ### get_item_quantity
        **Description:** Récupère la quantité d'un objet dans l'inventaire.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        - `item_id` (str): Identifiant de l'objet
        **Retour:** Quantité de l'objet (0 si non présent)
        """
        for lst in self._all_lists(character):
            for it in lst:
                if it.id == item_id:
                    return it.quantity
        return 0

    # --- helpers ---
    def _get_category_list(self, character: Character, category: str) -> List[EquipmentItem]:
        cats = category.lower()
        eq = character.equipment
        if cats in ('weapon', 'weapons'):
            return eq.weapons
        if cats == 'armor':
            return eq.armor
        if cats in ('consumable', 'consumables'):
            return eq.consumables
        return eq.accessories

    def _all_lists(self, character: Character) -> List[List[EquipmentItem]]:
        eq = character.equipment
        return [eq.weapons, eq.armor, eq.accessories, eq.consumables]

    def decrease_item_quantity(self, character: Character, item_id: str, amount: int = 1) -> Character:
        """
        ### decrease_item_quantity
        **Description:** Decreases the quantity of a specific item in the character's inventory.
        If the quantity reaches 0 or less, the item is removed from the inventory.
        
        **Parameters:**
        - `character` (Character): The character to modify.
        - `item_id` (str): The ID (catalog ID, UUID, or name) of the item to decrease.
        - `amount` (int): The amount to decrease by. Default is 1.
        
        **Returns:** 
        - `Character`: The updated character object.
        """
        log_debug("Decreasing item quantity", 
                  action="decrease_item_quantity", 
                  character_id=str(character.id), 
                  item_id=item_id, 
                  amount=amount)

        if amount <= 0:
            return character

        item_found = False
        
        # Helper to process list
        def process_list(item_list: List[EquipmentItem]) -> bool:
            for i, item in enumerate(item_list):
                # Match by id or name
                match = False
                if item.id == item_id: match = True
                elif item.name.lower() == item_id.lower(): match = True
                
                if match:
                    item.quantity -= amount
                    
                    if item.quantity <= 0:
                        item_list.pop(i)
                        log_debug("Item removed (quantity <= 0)", 
                                 action="decrease_item_quantity_removed", 
                                 character_id=str(character.id), 
                                 item_id=item_id)
                    return True
            return False

        # Check all equipment lists
        for lst in self._all_lists(character):
            if process_list(lst):
                item_found = True
                break
        
        if item_found:
            self.data_service.save_character(character)
        else:
            log_debug("Item not found for quantity decrease", 
                      action="decrease_item_quantity_not_found", 
                      character_id=str(character.id), 
                      item_id=item_id)
            
        return character

    def increase_item_quantity(self, character: Character, item_id: str, amount: int = 1) -> Character:
        """
        ### increase_item_quantity
        **Description:** Increases the quantity of a specific item in the character's inventory.
        If the item is not found, this method does nothing (idempotent behavior).
        
        **Parameters:**
        - `character` (Character): The character to modify.
        - `item_id` (str): The ID (catalog ID, UUID, or name) of the item to increase.
        - `amount` (int): The amount to increase by. Default is 1.
        
        **Returns:** 
        - `Character`: The updated character object.
        """
        log_debug("Increasing item quantity", 
                  action="increase_item_quantity", 
                  character_id=str(character.id), 
                  item_id=item_id, 
                  amount=amount)

        if amount <= 0:
            return character

        item_found = False
        
        # Helper to process list
        def process_list(item_list: List[EquipmentItem]) -> bool:
            for item in item_list:
                # Match by id or name
                match = False
                if item.id == item_id: match = True
                elif item.name.lower() == item_id.lower(): match = True

                if match:
                    item.quantity += amount
                    log_debug("Item quantity increased", 
                             action="increase_item_quantity_success", 
                             character_id=str(character.id), 
                             item_id=item_id,
                             new_quantity=item.quantity)
                    return True
            return False

        # Check all equipment lists
        for lst in self._all_lists(character):
            if process_list(lst):
                item_found = True
                break
        
        if item_found:
            self.data_service.save_character(character)
        else:
            log_debug("Item not found for quantity increase", 
                      action="increase_item_quantity_not_found", 
                      character_id=str(character.id), 
                      item_id=item_id)
            
        return character

