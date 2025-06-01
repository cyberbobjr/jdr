from typing import Dict, Any, List, Optional
import csv
import os
from .base import Equipment

class Equipements:
    """Gestion de l'équipement, des armes et armures"""
    
    def __init__(self):
        self.equipment = self._load_equipment()
        self.weapons = self._load_weapons()
        self.armors = self._load_armors()
        self.shields = self._load_shields()
        self.services = self._load_services()
    
    def _load_equipment(self) -> Dict[str, Equipment]:
        """Charge l'équipement général depuis le fichier CSV"""
        equipment = {}
        # Ajustement du chemin pour pointer vers /data/game/equipements.csv depuis la racine du projet
        csv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'game', 'equipements.csv')
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Ignorer les lignes de commentaire
                    if row['Type'].startswith('#'):
                        continue
                    
                    # Créer l'objet Equipment avec les arguments corrects
                    item = Equipment(
                        name=row['Nom'],
                        price=int(row['Prix_PC']) if row['Prix_PC'].isdigit() else 0,
                        weight=float(row['Poids_KG']) if row['Poids_KG'].replace('.', '').isdigit() else 0.0,
                        description=row['Description'],
                        category=row['Categorie']
                        # Supprimer 'item_type' si non pris en charge
                    )
                    
                    equipment[row['Nom']] = item
                    
        except FileNotFoundError:
            print(f"Erreur : Fichier CSV non trouvé à {csv_path}")
        except Exception as e:
            print(f"Erreur lors du chargement du fichier CSV : {e}")
            
        return equipment
    
    def _load_weapons(self) -> Dict[str, Any]:
        """Charge les armes depuis le fichier CSV"""
        weapons = {}
        # Ajustement du chemin pour pointer vers /data/game/equipements.csv depuis la racine du projet
        csv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'game', 'equipements.csv')
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['Type'] == 'Arme':
                        weapon = {
                            'name': row['Nom'],
                            'price': int(row['Prix_PC']) if row['Prix_PC'].isdigit() else 0,
                            'weight': float(row['Poids_KG']) if row['Poids_KG'].replace('.', '').isdigit() else 0.0,
                            'crafting_time': row['Temps_Fabrication'],
                            'description': row['Description'],
                            'category': row['Categorie']
                        }
                        weapons[row['Nom']] = weapon
                        
        except Exception as e:
            print(f"Erreur lors du chargement des armes : {e}")
            
        return weapons
    
    def _load_armors(self) -> Dict[str, Any]:
        """Charge les armures depuis le fichier CSV"""
        armors = {}
        # Ajustement du chemin pour pointer vers /data/game/equipements.csv depuis la racine du projet
        csv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'game', 'equipements.csv')
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['Type'] == 'Armure':
                        armor = {
                            'name': row['Nom'],
                            'price': int(row['Prix_PC']) if row['Prix_PC'].isdigit() else 0,
                            'weight': float(row['Poids_KG']) if row['Poids_KG'].replace('.', '').isdigit() else 0.0,
                            'crafting_time': row['Temps_Fabrication'],
                            'description': row['Description'],
                            'category': row['Categorie']
                        }
                        armors[row['Nom']] = armor
                        
        except Exception as e:
            print(f"Erreur lors du chargement des armures : {e}")
            
        return armors
    
    def _load_shields(self) -> Dict[str, Any]:
        """Charge les boucliers depuis le fichier CSV"""
        shields = {}
        # Ajustement du chemin pour pointer vers /data/game/equipements.csv depuis la racine du projet
        csv_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'game', 'equipements.csv')
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['Type'] == 'Bouclier':
                        shield = {
                            'name': row['Nom'],
                            'price': int(row['Prix_PC']) if row['Prix_PC'].isdigit() else 0,
                            'weight': float(row['Poids_KG']) if row['Poids_KG'].replace('.', '').isdigit() else 0.0,
                            'crafting_time': row['Temps_Fabrication'],
                            'description': row['Description'],
                            'category': row['Categorie']
                        }
                        shields[row['Nom']] = shield
                        
        except Exception as e:
            print(f"Erreur lors du chargement des boucliers : {e}")
            
        return shields
    
    def _load_services(self) -> Dict[str, Any]:
        """Charge les services depuis les données hardcodées"""
        return {
            "Bibliothèque": {"price": 10, "unit": "par jour"},
            "Courtisane": {"price": 1000, "unit": "par nuit"},
            "Guide en ville": {"price": 20, "unit": "par jour"},
            "Lessive": {"price": 5, "unit": "par panier"},
            "Ménestrel": {"price": 500, "unit": "par soirée"},
            "Messager en ville": {"price": 5, "unit": "par message"},
            "Pleureuse": {"price": 5, "unit": "par veillée"},
            "Porte-flambeau": {"price": 30, "unit": "par nuit"},
            "Prostituée": {"price": 10, "unit": "par passe"},
            "Prostituée de luxe": {"price": 300, "unit": "par nuit"},
            "Scribe": {"price": 10, "unit": "par page"},
            "Diligence": {"price": 3, "unit": "par km"},
            "Droit de passage": {"price": 1, "unit": "par passage"},
            "Employé qualifié": {"price": 30, "unit": "par jour"},
            "Employé non qualifié": {"price": 10, "unit": "par jour"},
            "Messager": {"price": 2, "unit": "par km"},
            "Traversée en bateau": {"price": 10, "unit": "par km"}
        }
    
    def get_item(self, item_name: str) -> Optional[Equipment]:
        """Récupère un équipement par son nom"""
        return self.equipment.get(item_name)
    
    def get_weapon(self, weapon_name: str) -> Optional[Dict[str, Any]]:
        """Récupère une arme par son nom"""
        return self.weapons.get(weapon_name)
    
    def get_armor(self, armor_name: str) -> Optional[Dict[str, Any]]:
        """Récupère une armure par son nom"""
        return self.armors.get(armor_name)
    
    def get_shield(self, shield_name: str) -> Optional[Dict[str, Any]]:
        """Récupère un bouclier par son nom"""
        return self.shields.get(shield_name)
    
    def get_items_by_category(self, category: str) -> List[Equipment]:
        """Retourne tous les équipements d'une catégorie"""
        return [item for item in self.equipment.values() if item.category == category]
    
    def get_items_by_type(self, item_type: str) -> List[Equipment]:
        """Retourne tous les équipements d'un type"""
        return [item for item in self.equipment.values() if item.item_type == item_type]
    
    def get_weapons_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Retourne toutes les armes d'une catégorie"""
        return [weapon for weapon in self.weapons.values() if weapon.get('category') == category]
    
    def search_items(self, search_term: str) -> List[Equipment]:
        """Recherche des équipements par nom ou description"""
        results = []
        search_term = search_term.lower()
        
        for item in self.equipment.values():
            if (search_term in item.name.lower() or 
                search_term in item.description.lower()):
                results.append(item)
                
        return results
    
    def get_items_by_price_range(self, min_price: int, max_price: int) -> List[Equipment]:
        """Retourne les équipements dans une fourchette de prix"""
        return [item for item in self.equipment.values() 
                if min_price <= item.price <= max_price]
    
    def convert_price_to_coins(self, price_pc: int) -> Dict[str, int]:
        """Convertit un prix en pièces de cuivre vers différentes devises"""
        po = price_pc // 100
        pa = (price_pc % 100) // 10
        pc = price_pc % 10
        
        return {
            "po": po,  # pièces d'or
            "pa": pa,  # pièces d'argent
            "pc": pc   # pièces de cuivre
        }
    
    def convert_pc_to_po(self, price_pc: int) -> float:
        """Convertit un prix en pièces de cuivre vers pièces d'or"""
        return round(price_pc / 100, 2)
    
    def get_starting_money(self, social_class: str = "moyenne") -> int:
        """Calcule l'argent de départ selon la classe sociale (en pièces d'or)"""
        if social_class == "pauvre":
            return 5  # 5 pièces d'or (500 pc)
        elif social_class == "moyenne":
            return 20  # 20 pièces d'or (2000 pc)
        elif social_class == "riche":
            return 100  # 100 pièces d'or (10000 pc)
        return 20
    
    def get_equipment_categories(self) -> List[str]:
        """Retourne la liste de toutes les catégories d'équipement"""
        categories = set()
        for item in self.equipment.values():
            categories.add(item.category)
        return sorted(list(categories))
    
    def get_weapon_categories(self) -> List[str]:
        """Retourne la liste de toutes les catégories d'armes"""
        categories = set()
        for weapon in self.weapons.values():
            categories.add(weapon.get('category', 'Autre'))
        return sorted(list(categories))
    
    def get_all_equipment(self) -> Dict[str, Any]:
        """Retourne tous les équipements (général + armes + armures + boucliers)"""
        all_equipment = {}
        
        # Ajouter l'équipement général
        for name, item in self.equipment.items():
            all_equipment[name] = {
                "name": item.name,
                "price": self.convert_pc_to_po(item.price),  # Conversion pc -> po
                "weight": item.weight,
                "description": item.description,
                "category": item.category
            }
        
        # Ajouter les armes
        for name, weapon in self.weapons.items():
            all_equipment[name] = {
                **weapon,
                "price": self.convert_pc_to_po(weapon.get('price', 0))  # Conversion pc -> po
            }
        
        # Ajouter les armures
        for name, armor in self.armors.items():
            all_equipment[name] = {
                **armor,
                "price": self.convert_pc_to_po(armor.get('price', 0))  # Conversion pc -> po
            }
        
        # Ajouter les boucliers
        for name, shield in self.shields.items():
            all_equipment[name] = {
                **shield,
                "price": self.convert_pc_to_po(shield.get('price', 0))  # Conversion pc -> po
            }
        
        return all_equipment
    
    def calculate_equipment_cost(self, equipment_list: List[str]) -> Dict[str, Any]:
        """Calcule le coût total et le poids d'une liste d'équipements"""
        total_cost = 0.0
        total_weight = 0.0
        equipment_details = []
        
        all_equipment = self.get_all_equipment()
        
        for item_name in equipment_list:
            if item_name in all_equipment:
                item = all_equipment[item_name]
                total_cost += item["price"]
                total_weight += item["weight"]
                equipment_details.append({
                    "name": item_name,
                    "price": item["price"],
                    "weight": item["weight"],
                    "category": item["category"]
                })
            else:
                print(f"Équipement non trouvé : {item_name}")
        
        return {
            "total_cost": total_cost,
            "total_weight": total_weight,
            "equipment_details": equipment_details,
            "item_count": len(equipment_details)
        }
    
    def validate_equipment_purchase(self, equipment_list: List[str], available_money: float) -> Dict[str, Any]:
        """Valide un achat d'équipement selon l'argent disponible"""
        cost_summary = self.calculate_equipment_cost(equipment_list)
        
        remaining_money = available_money - cost_summary["total_cost"]
        
        return {
            **cost_summary,
            "available_money": available_money,
            "remaining_money": remaining_money,
            "can_afford": remaining_money >= 0,
            "missing_money": max(0, -remaining_money)
        }
    
    def get_recommended_equipment_by_profession(self, profession: str) -> List[str]:
        """Retourne l'équipement recommandé selon la profession"""
        recommendations = {
            "Guerrier": ["Épée longue", "Armure de cuir", "Bouclier rond", "Casque de cuir"],
            "Paladin": ["Épée longue", "Armure de mailles", "Bouclier", "Symbole sacré"],
            "Voleur": ["Épée courte", "Armure de cuir souple", "Dague", "Outils de crochetage"],
            "Ranger": ["Arc long", "Épée longue", "Armure de cuir", "Carquois"],
            "Mage": ["Bâton", "Grimoire", "Composants magiques", "Robe"],
            "Animiste": ["Bâton", "Herbes médicinales", "Cristal de focalisation", "Robe naturelle"],
            "Barde": ["Épée courte", "Instrument de musique", "Armure de cuir souple"],
            "Clerc": ["Masse d'armes", "Bouclier", "Armure de mailles", "Symbole sacré"],
            "Druide": ["Gourdin", "Armure de cuir", "Herbes", "Bourse en cuir"],
            "Sorcier": ["Dague", "Orbe magique", "Grimoire", "Composants magiques"]
        }
        
        # Cherche par nom exact ou par inclusion
        for prof_key, equipment in recommendations.items():
            if prof_key.lower() in profession.lower() or profession.lower() in prof_key.lower():
                return equipment
        
        # Équipement de base si profession non reconnue
        return ["Épée courte", "Armure de cuir", "Sac à dos", "Rations"]
