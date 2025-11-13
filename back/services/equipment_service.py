"""
Service spécialisé pour la gestion de l'équipement et de l'inventaire des personnages.
Responsabilité unique :
- Achat/vente d'équipement et gestion de l'argent
- Gestion de l'inventaire (ajout, retrait, (dé)équipement, quantités)
"""

from typing import List, Dict, Any
from back.models.domain.character_v2 import CharacterV2 as Character
from back.models.domain.equipment_manager import EquipmentManager
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
    
    def buy_equipment(self, character: Character, equipment_name: str) -> Character:
        """
        ### buy_equipment
        **Description:** Achète un équipement et débite l'argent correspondant.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `equipment_name` (str): Nom de l'équipement à acheter
        **Retour:** Personnage modifié
        **Lève:** ValueError si l'équipement n'existe pas ou si pas assez d'argent
        """
        log_debug("Achat d'équipement", 
                 action="buy_equipment", 
                 character_id=str(character.id),
                 equipment_name=equipment_name)
        
        # Récupérer les détails de l'équipement
        equipment_details = self.equipment_manager.get_equipment_by_name(equipment_name)
        if not equipment_details:
            raise ValueError(f"Équipement '{equipment_name}' non trouvé")
        
        # Vérifier le budget
        equipment_cost = int(equipment_details.get('cost', 0) or 0)
        if character.gold < equipment_cost:
            raise ValueError("Pas assez d'argent pour acheter cet équipement")
        
        # Ajouter l'équipement dans la bonne catégorie
        weapons = self.equipment_manager.get_weapons()
        armor = self.equipment_manager.get_armor()
        item_entry = {"name": equipment_name, **equipment_details}
        if equipment_name in weapons:
            character.equipment.weapons.append(item_entry)
        elif equipment_name in armor:
            character.equipment.armor.append(item_entry)
        else:
            # Catégorie générique -> accessories
            character.equipment.accessories.append(item_entry)
        
        # Débiter l'argent (maps to equipment.gold via compat property)
        character.gold -= equipment_cost
        
        self.data_service.save_character(character)
        
        log_debug("Équipement acheté avec succès", 
                 action="buy_equipment_success", 
                 character_id=str(character.id),
                 equipment_name=equipment_name,
                 cost=equipment_cost,
                 gold_restant=character.gold)
        
        return character
    
    def sell_equipment(self, character: Character, equipment_name: str) -> Character:
        """
        ### sell_equipment
        **Description:** Vend un équipement et rembourse l'argent correspondant.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `equipment_name` (str): Nom de l'équipement à vendre
        **Retour:** Personnage modifié
        **Lève:** ValueError si l'équipement n'existe pas ou n'est pas dans l'inventaire
        """
        log_debug("Vente d'équipement", 
                 action="sell_equipment", 
                 character_id=str(character.id),
                 equipment_name=equipment_name)
        
        # Récupérer les détails de l'équipement
        equipment_details = self.equipment_manager.get_equipment_by_name(equipment_name)
        if not equipment_details:
            raise ValueError(f"Équipement '{equipment_name}' non trouvé")
        
        # Retirer l'équipement de la bonne catégorie
        found = False
        for lst in (character.equipment.weapons, character.equipment.armor, character.equipment.accessories, character.equipment.consumables):
            for i, it in enumerate(lst):
                if it.get("name") == equipment_name:
                    del lst[i]
                    equipment_details = equipment_details or it
                    found = True
                    break
            if found:
                break
        if not found:
            raise ValueError(f"L'équipement '{equipment_name}' n'est pas dans l'inventaire")
        
        # Rembourser l'argent (50% du prix d'achat)
        equipment_cost = int(equipment_details.get('cost', 0) or 0)
        refund_amount = int(equipment_cost * 0.5)  # 50% de remboursement
        character.gold += refund_amount
        
        self.data_service.save_character(character)
        
        log_debug("Équipement vendu avec succès", 
                 action="sell_equipment_success", 
                 character_id=str(character.id),
                 equipment_name=equipment_name,
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
        
        character.gold = max(0, character.gold + amount)  # Ne pas aller en négatif
        self.data_service.save_character(character)
        
        log_debug("Argent mis à jour", 
                 action="update_money_success", 
                 character_id=str(character.id),
                 nouveau_gold=character.gold)
        
        return character
    
    def get_equipment_list(self, character: Character) -> list:
        """
        ### get_equipment_list
        **Description:** Récupère la liste des équipements du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        **Retour:** Liste des noms d'équipements
        """
        names = []
        for lst in (character.equipment.weapons, character.equipment.armor, character.equipment.accessories, character.equipment.consumables):
            names.extend([it.get("name") for it in lst if isinstance(it, dict) and it.get("name")])
        return names
    
    def get_equipment_details(self, character: Character) -> list:
        """
        ### get_equipment_details
        **Description:** Récupère les détails complets des équipements du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        **Retour:** Liste des détails d'équipements
        """
        details = []
        for lst in (character.equipment.weapons, character.equipment.armor, character.equipment.accessories, character.equipment.consumables):
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
        for lst in (character.equipment.weapons, character.equipment.armor, character.equipment.accessories, character.equipment.consumables):
            for it in lst:
                qty = int(it.get('quantity', 1) or 1)
                total_weight += float(it.get('weight', 0) or 0) * qty
        return total_weight
    
    def can_afford_equipment(self, character: Character, equipment_name: str) -> bool:
        """
        ### can_afford_equipment
        **Description:** Vérifie si le personnage peut acheter un équipement.
        **Paramètres:**
        - `character` (Character): Personnage à vérifier
        - `equipment_name` (str): Nom de l'équipement
        **Retour:** True si le personnage peut acheter, False sinon
        """
        equipment_details = self.equipment_manager.get_equipment_by_name(equipment_name)
        if not equipment_details:
            return False
        
        equipment_cost = int(equipment_details.get('cost', 0) or 0)
        return character.gold >= equipment_cost
    
    def equipment_exists(self, equipment_name: str) -> bool:
        """
        ### equipment_exists
        **Description:** Vérifie si un équipement existe dans le catalogue.
        **Paramètres:**
        - `equipment_name` (str): Nom de l'équipement
        **Retour:** True si l'équipement existe, False sinon
        """
        return self.equipment_manager.get_equipment_by_name(equipment_name) is not None

    # --- Inventory management (merged from InventoryService) ---
    def add_item(self, character: Character, item_id: str, quantity: int = 1) -> Character:
        """
        ### add_item
        **Description:** Ajoute un objet standardisé à l'inventaire du personnage à partir de son id/nom.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `item_id` (str): Identifiant (slug) ou nom exact de l'objet
        - `quantity` (int): Quantité à ajouter (défaut: 1)
        **Retour:** Personnage modifié
        """
        log_debug("Equipment add item", action="add_item", character_id=str(character.id), item_id=item_id, quantity=quantity)
        base = self.equipment_manager.get_equipment_by_id(item_id)
        if not base:
            return character

        target_list = self._get_category_list(character, base['category'])
        existing = next((it for it in target_list if it.get('id') == base['id']), None)
        if existing:
            existing['quantity'] = int(existing.get('quantity', 1)) + int(quantity)
        else:
            new_item = dict(base)
            new_item['quantity'] = int(quantity)
            target_list.append(new_item)

        self.data_service.save_character(character)
        return character

    def add_item_object(self, character: Character, item: Dict[str, Any]) -> Character:
        """
        ### add_item_object
        **Description:** Ajoute un objet complet (déjà structuré) à l'inventaire du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `item` (dict): L'objet à ajouter (doit contenir au minimum `id`, `name`)
        **Retour:** Personnage modifié
        """
        log_debug("Equipment add item object", action="add_item_object", character_id=str(character.id), item_id=item.get('id'))

        category = item.get('category', 'accessory')
        target_list = self._get_category_list(character, category)
        existing = next((it for it in target_list if it.get('id') == item.get('id')), None)
        qty = int(item.get('quantity', 1) or 1)
        if existing:
            existing['quantity'] = int(existing.get('quantity', 1)) + qty
        else:
            payload = {
                'id': item.get('id'),
                'name': item.get('name'),
                'category': category,
                'cost': float(item.get('cost', 0) or 0),
                'weight': float(item.get('weight', 0) or 0),
                'quantity': qty,
                'equipped': bool(item.get('equipped', False)),
            }
            for k in ('damage', 'range', 'protection', 'description', 'type'):
                if k in item:
                    payload[k] = item[k]
            target_list.append(payload)

        self.data_service.save_character(character)
        return character

    def remove_item(self, character: Character, item_id: str, quantity: int = 1) -> Character:
        """
        ### remove_item
        **Description:** Retire un objet de l'inventaire du personnage (en ajustant la quantité).
        **Paramètres:**
        - `character` (Character): Personnage à modifier
        - `item_id` (str): Identifiant de l'objet
        - `quantity` (int): Quantité à retirer (défaut: 1)
        **Retour:** Personnage modifié
        """
        log_debug("Equipment remove item", action="remove_item", character_id=str(character.id), item_id=item_id, quantity=quantity)
        for lst in self._all_lists(character):
            for idx, it in enumerate(lst):
                if it.get('id') == item_id:
                    it['quantity'] = int(it.get('quantity', 1)) - int(quantity)
                    if it['quantity'] <= 0:
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
                if it.get('id') == item_id:
                    it['equipped'] = True
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
                if it.get('id') == item_id:
                    it['equipped'] = False
                    self.data_service.save_character(character)
                    return character
        self.data_service.save_character(character)
        return character

    def get_equipped_items(self, character: Character) -> List[Dict[str, Any]]:
        """
        ### get_equipped_items
        **Description:** Récupère la liste des objets équipés.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        **Retour:** Liste des objets équipés
        """
        equipped: List[Dict[str, Any]] = []
        for lst in self._all_lists(character):
            equipped.extend([it for it in lst if bool(it.get('equipped', False))])
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
        return any(True for lst in self._all_lists(character) for it in lst if it.get('id') == item_id)

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
                if it.get('id') == item_id:
                    return int(it.get('quantity', 1))
        return 0

    # --- helpers ---
    def _get_category_list(self, character: Character, category: str) -> List[Dict[str, Any]]:
        cats = category.lower()
        eq = character.equipment
        if cats in ('weapon', 'weapons'):
            return eq.weapons
        if cats == 'armor':
            return eq.armor
        if cats in ('consumable', 'consumables'):
            return eq.consumables
        return eq.accessories

    def _all_lists(self, character: Character) -> List[List[Dict[str, Any]]]:
        eq = character.equipment
        return [eq.weapons, eq.armor, eq.accessories, eq.consumables]
