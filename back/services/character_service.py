# filepath: c:\Users\benjamin\IdeaProjects\jdr\back\services\character_service.py
# Logique métier unitaire (SRP)

import os
from typing import List, Dict
from back.models.schema import Character, Item
from back.utils.logger import log_debug
from back.services.character_persistence_service import CharacterPersistenceService
from back.services.item_service import ItemService
from back.config import get_data_dir

class CharacterService:
    
    def __init__(self, character_id: str):
        """
        ### __init__
        **Description:** Initialise le service de personnage pour un personnage spécifique
        **Paramètres:**
        - `character_id` (str): Identifiant du personnage à gérer
        **Retour:** Aucun
        """
        self.character_id = character_id
        self.character_data = self._load_character()
    def _load_character(self) -> Character:
        """
        ### _load_character
        **Description:** Charge les données du personnage depuis le stockage persistant
        **Retour:** Objet Character chargé
        """
        character_data = CharacterPersistenceService.load_character_data(self.character_id)
        # On prend directement la racine du JSON
        state_data = character_data
        # Convertir l'ancien format equipment vers inventory si nécessaire
        self._convert_equipment_to_inventory(state_data)
        # Ajouter les champs manquants avec des valeurs par défaut
        state_data.setdefault("xp", 0)
        state_data.setdefault("gold", 0)
        state_data.setdefault("hp", 100)
        # L'ID est le nom du fichier (sans .json)
        state_data["id"] = self.character_id
        log_debug("Chargement du personnage", action="_load_character", character_id=self.character_id)
        return Character(**state_data)
    
    def save_character(self) -> None:
        """
        ### save_character
        **Description:** Sauvegarde les données du personnage vers le stockage persistant
        **Retour:** Aucun
        """
        character_dict = self.character_data.model_dump()
        # Retirer l'ID car il ne doit pas être dans le fichier
        character_dict.pop('id', None)
        CharacterPersistenceService.save_character_data(self.character_id, character_dict)
        log_debug("Sauvegarde du personnage", action="save_character", character_id=self.character_id)
    
    def get_character(self) -> Character:
        """
        ### get_character
        **Description:** Retourne l'objet Character actuellement chargé
        **Retour:** Objet Character
        """
        return self.character_data
    
    def get_character_json(self) -> str:
        """
        ### get_character_json
        **Description:** Retourne les données du personnage au format JSON
        **Retour:** String JSON des données du personnage
        """
        return self.character_data.model_dump_json()

    @staticmethod
    def _convert_equipment_to_inventory(state_data: dict) -> None:
        """
        ### _convert_equipment_to_inventory
        **Description:** Convertit l'ancien format 'equipment' vers le nouveau format 'inventory'
        **Paramètres:**
        - `state_data` (dict): Données d'état du personnage à convertir
        **Retour:** None (modifie state_data in-place)
        """
        item_service = ItemService()
        
        # Si on a un ancien format 'equipment' mais pas d'inventory
        if 'equipment' in state_data and 'inventory' not in state_data:
            equipment_names = state_data.get('equipment', [])
            if equipment_names:
                # Convertir les noms d'équipement en objets Item
                inventory = item_service.convert_equipment_list_to_inventory(equipment_names)
                state_data['inventory'] = [item.model_dump() for item in inventory]
                log_debug("Équipement converti en inventaire", 
                         action="convert_equipment_to_inventory", 
                         character_equipment_count=len(equipment_names),
                         character_inventory_count=len(inventory))
            else:
                state_data['inventory'] = []
            
            # Supprimer l'ancien champ equipment après conversion
            del state_data['equipment']
        
        # Si on n'a ni equipment ni inventory, créer un inventaire vide
        elif 'inventory' not in state_data and 'equipment' not in state_data:
            state_data['inventory'] = []

    @staticmethod
    def get_all_characters() -> List[object]:
        """
        Récupère la liste de tous les personnages disponibles à partir des fichiers JSON.

        Returns:
            List[object]: Une liste d'objets Character ou de dicts bruts pour les personnages incomplets.
        """
        characters = []
        characters_dir = os.path.join(get_data_dir(), "characters")
        required_fields = ["name", "race", "culture", "profession", "caracteristiques", "competences"]
        
        for filename in os.listdir(characters_dir):
            if filename.endswith(".json"):
                character_id = filename[:-5]  # Retire l'extension .json
                try:
                    character_data = CharacterPersistenceService.load_character_data(character_id)
                    status = character_data.get("status", None)
                    if status == "en_cours":
                        # On ajoute le dict brut pour les personnages en cours de création
                        character_data["id"] = character_id
                        characters.append(character_data)
                        continue
                    if not all(field in character_data for field in required_fields):
                        log_debug("Personnage ignoré (champs manquants)", 
                                 action="get_all_characters", 
                                 filename=filename, 
                                 missing_fields=[field for field in required_fields if field not in character_data])
                        continue
                    # Convertir l'ancien format equipment vers inventory si nécessaire
                    CharacterService._convert_equipment_to_inventory(character_data)
                    # Ajouter les champs manquants avec des valeurs par défaut
                    character_data.setdefault("xp", 0)
                    character_data.setdefault("gold", 0)
                    character_data.setdefault("hp", 100)
                    # L'ID est le nom du fichier (sans .json)
                    character_data["id"] = character_id
                    characters.append(Character(**character_data))
                except (FileNotFoundError, ValueError) as e:
                    log_debug("Erreur lors du chargement du personnage", 
                             action="get_all_characters_error", 
                             filename=filename, 
                             error=str(e))
                    continue
        log_debug("Chargement de tous les personnages", action="get_all_characters", count=len(characters))
        return characters
    
    @staticmethod
    def get_character(character_id: str) -> dict:
        """
        ### get_character
        **Description :** Récupère un personnage à partir de son identifiant (UUID) depuis le dossier data/characters.
        **Paramètres :**
        - `character_id` (str) : Identifiant du personnage (UUID).
        **Retour :** Dictionnaire des données du personnage.
        """       
        try:
            character_data = CharacterPersistenceService.load_character_data(character_id)
            
            state_data = character_data
            # Convertir l'ancien format equipment vers inventory si nécessaire
            CharacterService._convert_equipment_to_inventory(state_data)
            
            # Ajouter les champs manquants avec des valeurs par défaut
            state_data.setdefault("xp", 0)
            state_data.setdefault("gold", 0)
            state_data.setdefault("hp", 100)
            
            # L'ID est le nom du fichier (sans .json)
            state_data["id"] = character_id
            
            log_debug("Chargement du personnage", action="get_character", character_id=character_id)
            return state_data
        except Exception as e:
            raise e
        state_data["id"] = character_id
        log_debug("Chargement du personnage", action="get_character", character_id=character_id)
        return Character(**state_data)

    def apply_xp(self, xp: int) -> None:
        """
        ### apply_xp
        **Description:** Ajoute de l'XP au personnage et met à jour ses données
        **Paramètres:**
        - `xp` (int): Points d'expérience à ajouter
        **Retour:** Aucun
        """
        current_xp = getattr(self.character_data, 'xp', 0)
        new_xp = current_xp + xp
        self.character_data.xp = new_xp
        self.save_character()
        log_debug("Ajout d'XP", action="apply_xp", player_id=self.character_id, xp_ajoute=xp, xp_total=new_xp)

    def add_gold(self, gold: int) -> None:
        """
        ### add_gold
        **Description:** Ajoute de l'or au portefeuille du personnage
        **Paramètres:**
        - `gold` (int): Montant d'or à ajouter
        **Retour:** Aucun
        """
        current_gold = getattr(self.character_data, 'gold', 0)
        new_gold = current_gold + gold
        self.character_data.gold = new_gold
        self.save_character()
        log_debug("Ajout d'or", action="add_gold", player_id=self.character_id, gold_ajoute=gold, gold_total=new_gold)

    def take_damage(self, amount: int, source: str = "combat") -> None:
        """
        ### take_damage
        **Description:** Diminue les points de vie du personnage
        **Paramètres:**
        - `amount` (int): Points de dégâts à appliquer
        - `source` (str): Source des dégâts (optionnel)
        **Retour:** Aucun
        """
        current_hp = getattr(self.character_data, 'hp', 0)
        new_hp = max(0, current_hp - amount)
        self.character_data.hp = new_hp
        self.save_character()
        log_debug("Application de dégâts", action="take_damage", player_id=self.character_id, 
                 amount=amount, hp_restant=new_hp, source=source)

    def instantiate_item_by_id(self, item_id: str, qty: int = 1) -> 'Item':
        """
        ### instantiate_item_by_id
        **Description:** Instancie un objet à partir de son identifiant en utilisant le service ItemService.
        **Paramètres:**
        - `item_id` (str): L'identifiant de l'objet à instancier.
        - `qty` (int): Quantité de l'objet (défaut: 1)
        **Retour:** Objet Item instancié.
        """
        item_service = ItemService()
        # On suppose que l'item_id correspond au nom de l'objet dans ItemService
        item = item_service.create_item_from_name(item_id, quantity=qty)
        return item

    def add_item_object(self, item: 'Item') -> Dict:
        """
        ### add_item_object
        **Description:** Ajoute un objet complet à l'inventaire du personnage.
        **Paramètres:**
        - `item` (Item): L'objet à ajouter à l'inventaire.
        **Retour:** dict - Résumé de l'inventaire mis à jour
        """
        if not hasattr(self.character_data, 'inventory') or self.character_data.inventory is None:
            self.character_data.inventory = []
        # Vérifie si l'objet existe déjà
        for inv_item in self.character_data.inventory:
            if hasattr(inv_item, 'id') and inv_item.id == item.id:
                inv_item.quantity += item.quantity
                self.save_character()
                return {"inventory": [i.model_dump() if hasattr(i, 'model_dump') else i for i in self.character_data.inventory]}
        # Sinon, ajoute l'objet
        self.character_data.inventory.append(item)
        self.save_character()
        return {"inventory": [i.model_dump() if hasattr(i, 'model_dump') else i for i in self.character_data.inventory]}

    def item_exists(self, item_id: str) -> bool:
        """
        ### item_exists
        **Description:** Vérifie si un objet avec l'identifiant donné existe dans l'inventaire du personnage.
        **Paramètres:**
        - `item_id` (str): L'identifiant de l'objet à vérifier.
        **Retour:** booléen indiquant la présence de l'objet dans l'inventaire.
        """
        if not hasattr(self.character_data, 'inventory') or self.character_data.inventory is None:
            return False
        for item in self.character_data.inventory:
            if hasattr(item, 'id') and item.id == item_id:
                return True
        return False

    def add_item(self, item_id: str, qty: int = 1) -> Dict:
        """
        ### add_item
        **Description:** Ajoute un objet à l'inventaire du personnage. Instancie l'objet si il n'existe pas.
        **Paramètres:**
        - `item_id` (str): L'identifiant de l'objet
        - `qty` (int): La quantité à ajouter (par défaut 1)
        **Retour:** dict - Résumé de l'inventaire mis à jour
        """
        log_debug("Ajout d'un objet à l'inventaire", action="add_item", player_id=self.character_id, item_id=item_id, qty=qty)
        if not hasattr(self.character_data, 'inventory') or self.character_data.inventory is None:
            self.character_data.inventory = []
        found = False
        for item in self.character_data.inventory:
            if hasattr(item, 'id') and item.id == item_id:
                item.quantity += qty
                found = True
                break
        if not found:
            # Instancie l'objet et l'ajoute à l'inventaire
            item = self.instantiate_item_by_id(item_id, qty)
            self.character_data.inventory.append(item)
        self.save_character()
        return {"inventory": [item.model_dump() if hasattr(item, 'model_dump') else item for item in self.character_data.inventory]}

    def remove_item(self, item_id: str, qty: int = 1) -> Dict:
        """
        ### remove_item
        **Description:** Retire un objet de l'inventaire du personnage
        **Paramètres:**
        - `item_id` (str): L'identifiant de l'objet
        - `qty` (int): La quantité à retirer (par défaut 1)
        **Retour:** dict - Résumé de l'inventaire mis à jour
        """
        log_debug("Retrait d'un objet de l'inventaire", action="remove_item", player_id=self.character_id, item_id=item_id, qty=qty)
        
        if hasattr(self.character_data, 'inventory') and self.character_data.inventory:
            for i, item in enumerate(self.character_data.inventory):
                if hasattr(item, 'id') and item.id == item_id:
                    item.quantity -= qty
                    if item.quantity <= 0:
                        del self.character_data.inventory[i]
                    break
        
        self.save_character()
        return {"inventory": [item.model_dump() if hasattr(item, 'model_dump') else item for item in self.character_data.inventory]}

    def equip_item(self, item_id: str) -> Dict:
        """
        ### equip_item
        **Description:** Équipe un objet pour le personnage
        **Paramètres:**
        - `item_id` (str): L'identifiant de l'objet
        **Retour:** dict - Résumé de l'inventaire mis à jour avec l'objet équipé
        """
        if hasattr(self.character_data, 'inventory') and self.character_data.inventory:
            for item in self.character_data.inventory:
                if hasattr(item, 'id') and item.id == item_id:
                    if hasattr(item, 'is_equipped'):
                        item.is_equipped = True
                    break
        
        self.save_character()
        return {"inventory": [item.model_dump() if hasattr(item, 'model_dump') else item for item in self.character_data.inventory]}

    def unequip_item(self, item_id: str) -> Dict:
        """
        ### unequip_item
        **Description:** Déséquipe un objet pour le personnage
        **Paramètres:**
        - `item_id` (str): L'identifiant de l'objet
        **Retour:** dict - Résumé de l'inventaire mis à jour avec l'objet déséquipé
        """
        if hasattr(self.character_data, 'inventory') and self.character_data.inventory:
            for item in self.character_data.inventory:
                if hasattr(item, 'id') and item.id == item_id:
                    if hasattr(item, 'is_equipped'):
                        item.is_equipped = False
                    break
        
        self.save_character()
        return {"inventory": [item.model_dump() if hasattr(item, 'model_dump') else item for item in self.character_data.inventory]}
