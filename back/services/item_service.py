"""
Service de gestion des objets et de l'inventaire.
Permet de convertir les noms d'équipement en objets Item complets.
"""

import csv
import os
from typing import Dict, List, Optional
from uuid import uuid4
from back.models.schema import Item, ItemType
from back.utils.logger import log_debug

class ItemService:
    """Service pour la gestion des objets et de l'inventaire"""
    
    def __init__(self):
        self._items_data: Optional[Dict[str, Dict]] = None
        self._load_items_data()
    
    def _load_items_data(self) -> None:
        """
        ### _load_items_data
        **Description:** Charge les données des objets depuis le fichier CSV equipements.csv
        **Paramètres:** Aucun
        **Retour:** None (stocke les données dans self._items_data)
        """
        try:
            # Chemin vers le fichier CSV
            base_path = os.path.dirname(os.path.dirname(__file__))
            csv_path = os.path.join(base_path, "..", "data", "game", "equipements.csv")
            
            self._items_data = {}
            
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    item_name = row.get('Nom', '').strip()
                    if item_name:
                        self._items_data[item_name] = {
                            'type': row.get('Type', 'Materiel'),
                            'price_pc': int(row.get('Prix_PC', 0)),
                            'weight_kg': float(row.get('Poids_KG', 0)),
                            'description': row.get('Description', ''),
                            'category': row.get('Categorie', ''),
                            'crafting_time': row.get('Temps_Fabrication', '')
                        }
            
            log_debug(f"Données d'objets chargées", action="load_items_data", count=len(self._items_data))
            
        except Exception as e:
            log_debug(f"Erreur lors du chargement des données d'objets: {str(e)}", 
                     action="load_items_data_error", error=str(e))
            self._items_data = {}
    
    def get_item_data(self, item_name: str) -> Optional[Dict]:
        """
        ### get_item_data
        **Description:** Récupère les données d'un objet par son nom
        **Paramètres:**
        - `item_name` (str): Nom de l'objet à rechercher
        **Retour:** Dict avec les données de l'objet ou None si non trouvé
        """
        if self._items_data is None:
            self._load_items_data()
        
        return self._items_data.get(item_name)
    
    def create_item_from_name(self, item_name: str, quantity: int = 1, is_equipped: bool = False) -> Optional[Item]:
        """
        ### create_item_from_name
        **Description:** Crée un objet Item complet à partir d'un nom d'équipement
        **Paramètres:**
        - `item_name` (str): Nom de l'objet (ex: "Coutelas")
        - `quantity` (int): Quantité de l'objet (défaut: 1)
        - `is_equipped` (bool): Si l'objet est équipé (défaut: False)        **Retour:** Objet Item complet ou None si l'objet n'est pas trouvé
        """
        item_data = self.get_item_data(item_name)
        
        if not item_data:
            log_debug(f"Objet non trouvé dans les données: {item_name}", 
                     action="create_item_from_name_error", item_name=item_name)
            # Créer un objet générique si non trouvé dans les données
            generic_item = Item(
                id=str(uuid4()),
                name=item_name,
                item_type=ItemType.MATERIEL,
                price_pc=0,
                weight_kg=0.0,
                description=f"Objet générique: {item_name}",
                quantity=quantity,
                is_equipped=is_equipped
            )
            log_debug(f"Objet générique créé: {item_name}", 
                     action="create_item_from_name_generic", item_name=item_name)
            return generic_item
        
        # Déterminer le type d'objet
        try:
            item_type = ItemType(item_data['type'])
        except ValueError:
            item_type = ItemType.MATERIEL
        
        # Créer l'objet Item
        item = Item(
            id=str(uuid4()),
            name=item_name,
            item_type=item_type,
            price_pc=item_data['price_pc'],
            weight_kg=item_data['weight_kg'],
            description=item_data['description'],
            category=item_data['category'],
            quantity=quantity,
            is_equipped=is_equipped,
            crafting_time=item_data['crafting_time'] if item_data['crafting_time'] else None
        )
        
        # Ajouter des propriétés spécifiques selon le type
        if item_type == ItemType.ARME:
            item.damage = self._get_weapon_damage(item_name, item_data['category'])
        elif item_type == ItemType.ARMURE:
            item.protection = self._get_armor_protection(item_name, item_data['category'])
            item.armor_type = item_data['category']
        
        log_debug(f"Objet créé: {item_name}", action="create_item_from_name", 
                 item_id=item.id, item_type=item_type.value)
        
        return item
    
    def _get_weapon_damage(self, weapon_name: str, category: str) -> str:
        """
        ### _get_weapon_damage
        **Description:** Détermine les dégâts d'une arme basés sur son nom et sa catégorie
        **Paramètres:**
        - `weapon_name` (str): Nom de l'arme
        - `category` (str): Catégorie de l'arme
        **Retour:** String des dégâts (ex: "1d6+2")
        """
        # Table de dégâts basique - peut être étendue avec un fichier CSV séparé
        damage_table = {
            'Couteau': '1d4',
            'Epee': '1d8',
            'Arc': '1d6',
            'Arbalete': '1d8',
            'Baton': '1d6',
            'Fouet': '1d3',
            'Arts_Martiaux': '1d3'
        }
        
        return damage_table.get(category, '1d4')  # Défaut: 1d4
    
    def _get_armor_protection(self, armor_name: str, category: str) -> int:
        """
        ### _get_armor_protection  
        **Description:** Détermine la protection d'une armure basée sur son nom et sa catégorie
        **Paramètres:**
        - `armor_name` (str): Nom de l'armure
        - `category` (str): Catégorie de l'armure
        **Retour:** Points de protection (int)
        """
        # Table de protection basique - peut être étendue avec un fichier CSV séparé
        protection_table = {
            'Tissu': 1,
            'Cuir': 2, 
            'Maille': 4,
            'Plates': 6
        }
        
        return protection_table.get(category, 0)  # Défaut: 0
    
    def convert_equipment_list_to_inventory(self, equipment_names: List[str]) -> List[Item]:
        """
        ### convert_equipment_list_to_inventory
        **Description:** Convertit une liste de noms d'équipement en inventaire d'objets Item
        **Paramètres:**
        - `equipment_names` (List[str]): Liste des noms d'équipement (format ancien)
        **Retour:** Liste d'objets Item (format nouveau)
        """
        inventory = []
        
        for equipment_name in equipment_names:
            item = self.create_item_from_name(equipment_name, is_equipped=True)
            if item:
                inventory.append(item)
            else:
                # Créer un objet générique si non trouvé dans les données
                generic_item = Item(
                    id=str(uuid4()),
                    name=equipment_name,
                    item_type=ItemType.MATERIEL,
                    price_pc=0,
                    weight_kg=0.0,
                    description=f"Objet générique: {equipment_name}",
                    quantity=1,
                    is_equipped=True
                )
                inventory.append(generic_item)
                log_debug(f"Objet générique créé pour: {equipment_name}", 
                         action="convert_equipment_generic", item_name=equipment_name)
        
        log_debug(f"Équipement converti en inventaire", 
                 action="convert_equipment_to_inventory", 
                 original_count=len(equipment_names), 
                 converted_count=len(inventory))
        
        return inventory
    
    def get_equipped_items(self, inventory: List[Item]) -> List[Item]:
        """
        ### get_equipped_items
        **Description:** Filtre les objets équipés de l'inventaire
        **Paramètres:**
        - `inventory` (List[Item]): Inventaire complet
        **Retour:** Liste des objets équipés
        """
        return [item for item in inventory if item.is_equipped]
    
    def calculate_total_weight(self, inventory: List[Item]) -> float:
        """
        ### calculate_total_weight
        **Description:** Calcule le poids total de l'inventaire
        **Paramètres:**
        - `inventory` (List[Item]): Inventaire à calculer
        **Retour:** Poids total en kg (float)
        """
        return sum(item.weight_kg * item.quantity for item in inventory)
    
    def calculate_total_value(self, inventory: List[Item]) -> int:
        """
        ### calculate_total_value
        **Description:** Calcule la valeur totale de l'inventaire
        **Paramètres:**
        - `inventory` (List[Item]): Inventaire à calculer
        **Retour:** Valeur totale en pièces de cuivre (int)
        """
        return sum(item.price_pc * item.quantity for item in inventory)
