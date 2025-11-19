# Logique métier unitaire (SRP)

from typing import List, Dict
from back.models.schema import Item, CharacterStatus
from back.models.domain.character import Character
from back.utils.logger import log_debug, log_info, log_warning, get_logger
from back.utils.model_converter import ModelConverter
from back.services.character_data_service import CharacterDataService
from back.services.item_service import ItemService
from back.services.equipment_service import EquipmentService
from back.models.domain.equipment_manager import EquipmentManager

logger = get_logger(__name__)

class CharacterService:
    character_id: str
    strict_validation: bool
    character_data: Character
    data_service: CharacterDataService
    
    def __init__(self, character_id: str, strict_validation: bool = True) -> None:
        """
        ### __init__
        **Description:** Initialise le service de personnage pour un personnage spécifique
        **Paramètres:**
        - `character_id` (str): Identifiant du personnage à gérer
        - `strict_validation` (bool): Si True, valide strictement avec le modèle Character. Si False, accepte les personnages incomplets.
        **Retour:** Aucun
        """
        self.character_id = character_id
        self.strict_validation = strict_validation
        self.data_service = CharacterDataService()
        self.character_data = self._load_character()
        
    def _load_character(self) -> Character:
        """
        ### _load_character
        **Description:** Charge les données du personnage depuis le stockage persistant
        **Retour:** Objet CharacterV2 chargé
        """
        character: Character = self.data_service.load_character(self.character_id)

        # Vérifier si le personnage est complet
        is_incomplete = (
            character.name is None or
            character.status == CharacterStatus.IN_PROGRESS or
            character.status is None
        )

        log_debug("Chargement du personnage", action="_load_character", character_id=self.character_id, is_incomplete=is_incomplete)

        # Retourner l'objet CharacterV2 (Pydantic gère les valeurs par défaut)
        return character

    def save_character(self) -> None:
        """
        ### save_character
        **Description:** Sauvegarde les données du personnage vers le stockage persistant
        **Retour:** Aucun
        """
        self.data_service.save_character(self.character_data, self.character_id)
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
        return ModelConverter.to_json(self.character_data)
    
    @staticmethod
    def get_all_characters() -> List[Character]:
        """
        ### get_all_characters
        **Description:** Récupère la liste de tous les personnages disponibles à partir des fichiers JSON.
        **Retour:** Liste d'objets CharacterV2.
        """
        data_service = CharacterDataService()
        return data_service.get_all_characters()
    
    @staticmethod
    def get_character_by_id(character_id: str) -> Character:
        """
        ### get_character_by_id
        **Description:** Récupère un personnage à partir de son identifiant (UUID) depuis le dossier data/characters.
        **Paramètres:**
        - `character_id` (str): Identifiant du personnage (UUID).
        **Retour:** Objet CharacterV2 du personnage.
        """
        try:
            data_service = CharacterDataService()
            character: Character = data_service.load_character(character_id)

            log_debug("Chargement du personnage", action="get_character_by_id", character_id=character_id)
            return character
        except Exception as e:
            raise e

    # --- Business Logic Methods ---

    def apply_xp(self, xp: int) -> Character:
        """
        ### apply_xp
        **Description:** Ajoute de l'XP au personnage.
        **Paramètres:**
        - `xp` (int): Points d'expérience à ajouter
        **Retour:** Personnage modifié
        """
        self.character_data.xp += xp
        self.save_character()
        
        log_info("XP ajouté au personnage",
                   extra={"action": "apply_xp",
                          "character_id": str(self.character_data.id),
                          "xp_ajoute": xp,
                          "xp_total": self.character_data.xp})
        
        return self.character_data
    
    def add_gold(self, gold: float) -> Character:
        """
        ### add_gold
        **Description:** Ajoute de l'or au portefeuille du personnage.
        **Paramètres:**
        - `gold` (float): Montant d'or à ajouter (peut avoir des décimales)
        **Retour:** Personnage modifié
        """
        self.character_data.gold += int(gold)
        self.save_character()
        
        log_info("Or ajouté au personnage",
                   extra={"action": "add_gold",
                          "character_id": str(self.character_data.id),
                          "gold_ajoute": gold,
                          "gold_total": self.character_data.gold})
        
        return self.character_data
    
    def take_damage(self, amount: int, source: str = "combat") -> Character:
        """
        ### take_damage
        **Description:** Diminue les points de vie du personnage.
        **Paramètres:**
        - `amount` (int): Points de dégâts à appliquer
        - `source` (str): Source des dégâts (optionnel)
        **Retour:** Personnage modifié
        """
        # Delegate to combat stats to ensure consistency
        self.character_data.combat_stats.take_damage(int(amount))
        self.save_character()
        
        log_warning("Dégâts appliqués au personnage",
                      extra={"action": "take_damage",
                             "character_id": str(self.character_data.id),
                             "amount": amount,
                             "hp_restant": self.character_data.hp,
                             "source": source})
        
        return self.character_data
    
    def heal(self, amount: int, source: str = "soin") -> Character:
        """
        ### heal
        **Description:** Augmente les points de vie du personnage.
        **Paramètres:**
        - `amount` (int): Points de vie à restaurer
        - `source` (str): Source du soin (optionnel)
        **Retour:** Personnage modifié
        """
        max_hp = self.character_data.combat_stats.max_hit_points
        self.character_data.hp = min(max_hp, self.character_data.hp + int(amount))
        self.save_character()
        
        log_info("Soins appliqués au personnage",
                   extra={"action": "heal",
                          "character_id": str(self.character_data.id),
                          "amount": amount,
                          "hp_restant": self.character_data.hp,
                          "source": source})
        
        return self.character_data

    def calculate_max_hp(self) -> int:
        """
        ### calculate_max_hp
        **Description:** Calcule les PV maximums du personnage basés sur sa constitution.
        **Retour:** PV maximums calculés
        """
        # Simplified v2 formula based on character stats and level
        constitution = self.character_data.stats.constitution
        level = self.character_data.level
        return constitution * 10 + level * 5
    
    def is_alive(self) -> bool:
        """
        ### is_alive
        **Description:** Vérifie si le personnage est en vie.
        **Retour:** True si le personnage est en vie, False sinon
        """
        return self.character_data.combat_stats.is_alive()
    
    def get_level(self) -> int:
        """
        ### get_level
        **Description:** Calcule le niveau du personnage basé sur son XP.
        **Retour:** Niveau calculé
        """
        # In v2, level is tracked directly on the character
        return self.character_data.level

    # --- Item Management Methods ---

    def instantiate_item_by_id(self, item_id: str, qty: int = 1) -> 'Item':
        """
        ### instantiate_item_by_id
        **Description:** Instancie un objet à partir de son identifiant en utilisant le service ItemService.
        **Paramètres:**
        - `item_id` (str): L'identifiant de l'objet à instancier.
        - `qty` (int): Quantité de l'objet (défaut: 1)
        **Retour:** Objet Item instancié.
        """
        item_service: ItemService = ItemService()
        # On suppose que l'item_id correspond au nom de l'objet dans ItemService
        item: Item = item_service.create_item_from_name(item_id, quantity=qty)
        return item

    def add_item_object(self, item: 'Item') -> Dict:
        """
        ### add_item_object
        **Description:** Ajoute un objet complet à l'inventaire du personnage.
        **Paramètres:**
        - `item` (Item): L'objet à ajouter à l'inventaire.
        **Retour:** dict - Résumé de l'inventaire mis à jour
        """
        # Utiliser EquipmentService pour déléguer la logique
        equipment_service: EquipmentService = EquipmentService(self.data_service)
        character: Character = self.data_service.load_character(self.character_id)
        equipment_service.add_item_object(character, item)
        # Recharger les données
        self.character_data = self._load_character()
        return {"inventory": [ModelConverter.to_dict(i) for i in self.character_data.inventory]}

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
        found: bool = False
        for item in self.character_data.inventory:
            if hasattr(item, 'id') and item.id == item_id:
                item.quantity += qty
                found = True
                break
        if not found:
            # Instancie l'objet et l'ajoute à l'inventaire
            item: Item = self.instantiate_item_by_id(item_id, qty)
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
    
    def buy_equipment(self, equipment_name: str) -> Dict:
        """
        ### buy_equipment
        **Description:** Achète un équipement et débite l'argent correspondant du budget de création.
        **Paramètres:**
        - `equipment_name` (str): Nom de l'équipement à acheter
        **Retour:** dict - Résumé avec statut, argent restant, poids total et détails de l'équipement
        """
        log_debug("Achat d'équipement", action="buy_equipment", character_id=self.character_id, equipment_name=equipment_name)
        
        # Récupérer les détails de l'équipement
        equipment_manager: EquipmentManager = EquipmentManager()
        equipment_details: Dict[str, any] | None = equipment_manager.get_equipment_by_name(equipment_name)
        if not equipment_details:
            raise ValueError(f"Équipement '{equipment_name}' non trouvé")
        
        # Vérifier le budget avec la clé 'gold'
        # Gérer le cas où character_data est un dict ou un objet Character
        character_dict: Dict[str, any]
        if hasattr(self.character_data, 'model_dump'):
            character_dict = self.character_data.model_dump()
        else:
            character_dict = self.character_data.copy() if isinstance(self.character_data, dict) else self.character_data
            
        current_gold: float = character_dict.get('gold', 0)
        equipment_cost: float = equipment_details.get('cost', 0)
        
        if current_gold < equipment_cost:
            raise ValueError("Pas assez d'argent pour acheter cet équipement")
        
        # Ajouter l'équipement à la liste
        equipment_list: List[str] = character_dict.get('equipment', [])
        if equipment_name not in equipment_list:
            equipment_list.append(equipment_name)
        # Mettre à jour l'or du personnage
        new_gold: float = current_gold - equipment_cost
        
        # Calculer le poids total pour la réponse
        total_weight: float = 0
        for equipment_name_in_list in equipment_list:
            equipment_item: Dict[str, any] | None = equipment_manager.get_equipment_by_name(equipment_name_in_list)
            if equipment_item:
                total_weight += equipment_item.get('weight', 0)
        
        # Mettre à jour les données du personnage
        if hasattr(self.character_data, 'equipment'):
            self.character_data.equipment = equipment_list
        else:
            self.character_data['equipment'] = equipment_list
        
        if hasattr(self.character_data, 'gold'):
            self.character_data.gold = new_gold
        else:
            self.character_data['gold'] = new_gold
        
        self.save_character()
        
        return {
            'status': 'success',
            'gold': new_gold,
            'total_weight': total_weight,
            'equipment_added': {
                'name': equipment_name,
                **equipment_details
            }
        }

    def sell_equipment(self, equipment_name: str) -> Dict:
        """
        ### sell_equipment
        **Description:** Vend un équipement et rembourse l'argent correspondant au budget de création.
        **Paramètres:**
        - `equipment_name` (str): Nom de l'équipement à vendre
        **Retour:** dict - Résumé avec statut, argent restant, poids total et détails de l'équipement
        """
        log_debug("Vente d'équipement", action="sell_equipment", character_id=self.character_id, equipment_name=equipment_name)
        
        # Récupérer les détails de l'équipement
        equipment_manager: EquipmentManager = EquipmentManager()
        equipment_details: Dict[str, any] | None = equipment_manager.get_equipment_by_name(equipment_name)
        if not equipment_details:
            raise ValueError(f"Équipement '{equipment_name}' non trouvé")
        
        # Retirer l'équipement de la liste
        # Gérer le cas où character_data est un dict ou un objet Character
        character_dict: Dict[str, any]
        if hasattr(self.character_data, 'model_dump'):
            character_dict = self.character_data.model_dump()
        else:
            character_dict = self.character_data.copy() if isinstance(self.character_data, dict) else self.character_data
            
        equipment_list: List[str] = character_dict.get('equipment', [])
        if equipment_name not in equipment_list:
            raise ValueError(f"L'équipement '{equipment_name}' n'est pas dans l'inventaire")
            
        equipment_list.remove(equipment_name)
        
        # Rembourser l'or du personnage
        current_gold: float = character_dict.get('gold', 0)
        equipment_cost: float = equipment_details.get('cost', 0)
        new_gold: float = current_gold + equipment_cost
        
        # Calculer le poids total pour la réponse
        total_weight: float = 0
        for equipment_name_in_list in equipment_list:
            equipment_item: Dict[str, any] | None = equipment_manager.get_equipment_by_name(equipment_name_in_list)
            if equipment_item:
                total_weight += equipment_item.get('weight', 0)
        
        # Mettre à jour les données du personnage
        if hasattr(self.character_data, 'equipment'):
            self.character_data.equipment = equipment_list
        else:
            self.character_data['equipment'] = equipment_list
            
        if hasattr(self.character_data, 'gold'):
            self.character_data.gold = new_gold
        else:
            self.character_data['gold'] = new_gold
        self.save_character()
        
        return {
            'status': 'success',
            'gold': new_gold,
            'total_weight': total_weight,
            'equipment_removed': {
                'name': equipment_name,
                **equipment_details
            }
        }

    def update_money(self, amount: int) -> Dict:
        """
        ### update_money
        **Description:** Met à jour l'argent du personnage (positif pour ajouter, négatif pour retirer).
        **Paramètres:**
        - `amount` (int): Montant à ajouter/retirer
        **Retour:** dict - Résumé avec statut et nouvel argent
        """
        log_debug("Mise à jour de l'argent", action="update_money", character_id=self.character_id, amount=amount)
        # Mettre à jour l'argent avec la clé 'gold'
        # Gérer le cas où character_data est un dict ou un objet Character
        character_dict: Dict[str, any]
        if hasattr(self.character_data, 'model_dump'):
            character_dict = self.character_data.model_dump()
        else:
            character_dict = self.character_data.copy() if isinstance(self.character_data, dict) else self.character_data
            
        current_gold: float = character_dict.get('gold', 0)
        new_gold: float = max(0, current_gold + amount)  # Ne pas aller en négatif
        
        # Mettre à jour les données du personnage
        if hasattr(self.character_data, 'gold'):
            self.character_data.gold = new_gold
        else:
            self.character_data['gold'] = new_gold
        self.save_character()
        
        return {
            'status': 'success',
            'gold': new_gold
        }
