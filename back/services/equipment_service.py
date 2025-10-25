"""
Service spécialisé pour la gestion de l'équipement des personnages.
Respect du SRP - Responsabilité unique : achat/vente d'équipement et gestion de l'argent.
"""

from back.models.domain.character import Character
from back.models.domain.equipment_manager import EquipmentManager
from back.services.character_data_service import CharacterDataService
from back.utils.logger import log_debug


class EquipmentService:
    """
    ### EquipmentService
    **Description:** Service spécialisé dans la gestion de l'équipement des personnages.
    **Responsabilité unique:** Achat/vente d'équipement et gestion de l'argent.
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
        equipment_cost = equipment_details.get('cost', 0)
        if character.gold < equipment_cost:
            raise ValueError("Pas assez d'argent pour acheter cet équipement")
        
        # Initialiser la liste d'équipement si nécessaire
        if character.equipment is None:
            character.equipment = []
        
        # Ajouter l'équipement à la liste
        if equipment_name not in character.equipment:
            character.equipment.append(equipment_name)
        
        # Débiter l'argent
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
        
        # Vérifier que l'équipement est dans l'inventaire
        if not character.equipment or equipment_name not in character.equipment:
            raise ValueError(f"L'équipement '{equipment_name}' n'est pas dans l'inventaire")
        
        # Retirer l'équipement de la liste
        character.equipment.remove(equipment_name)
        
        # Rembourser l'argent (50% du prix d'achat)
        equipment_cost = equipment_details.get('cost', 0)
        refund_amount = equipment_cost * 0.5  # 50% de remboursement
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
        return character.equipment or []
    
    def get_equipment_details(self, character: Character) -> list:
        """
        ### get_equipment_details
        **Description:** Récupère les détails complets des équipements du personnage.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        **Retour:** Liste des détails d'équipements
        """
        if not character.equipment:
            return []
        
        equipment_details = []
        for equipment_name in character.equipment:
            details = self.equipment_manager.get_equipment_by_name(equipment_name)
            if details:
                equipment_details.append({
                    'name': equipment_name,
                    **details
                })
        
        return equipment_details
    
    def calculate_total_weight(self, character: Character) -> float:
        """
        ### calculate_total_weight
        **Description:** Calcule le poids total de l'équipement.
        **Paramètres:**
        - `character` (Character): Personnage à analyser
        **Retour:** Poids total en kilogrammes
        """
        if not character.equipment:
            return 0.0
        
        total_weight = 0.0
        for equipment_name in character.equipment:
            details = self.equipment_manager.get_equipment_by_name(equipment_name)
            if details:
                total_weight += details.get('weight', 0)
        
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
        
        equipment_cost = equipment_details.get('cost', 0)
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
