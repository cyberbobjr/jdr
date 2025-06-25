"""
Service dédié à la création de personnage pour le jeu de rôle.
Ce service gère l'allocation automatique des caractéristiques, la vérification des règles,
et fournit les listes de races, compétences, cultures, équipements et sorts.
"""

from back.models.domain.characteristics_manager import CharacteristicsManager
from back.models.domain.skills_manager import SkillsManager
from back.models.domain.races_manager import RacesManager
from back.models.domain.spells_manager import SpellsManager
from back.models.domain.equipment_manager import EquipmentManager
from back.models.schema import RaceData

class CharacterCreationService:
    """
    Service pour la gestion de la création de personnage.
    """

    @staticmethod
    def allocate_attributes_auto(race_data: RaceData) -> dict:
        """
        ### allocate_attributes_auto
        **Description:** Alloue automatiquement les caractéristiques d'un personnage selon sa race, en optimisant la répartition selon les recommandations métier et en intégrant les bonus raciaux dans le calcul du budget, sans boucle infinie.
        **Parameters:**
        - `race_data` (RaceData): L'objet race complet du personnage.
        **Returns:** Un dictionnaire des caractéristiques allouées.
        """
        characteristics_manager = CharacteristicsManager()
          # Obtenir les noms des caractéristiques et le budget
        char_names = list(characteristics_manager.get_all_characteristics().keys())
        starting_points = characteristics_manager.starting_points
        
        # Bonus raciaux à intégrer dans la répartition
        racial_bonuses = race_data.characteristic_bonuses if race_data else {}
        
        # 1. On part d'une base minimale (50 partout)
        values = {name: 50 for name in char_names}
          # 2. Pour simplifier, on distribue équitablement le budget restant
        remaining_budget = starting_points - sum(values.values())
        
        # 3. Distribution équitable
        while remaining_budget > 0 and any(values[name] < 90 for name in char_names):
            improved = False
            for char_name in char_names:
                if remaining_budget > 0 and values[char_name] < 90:
                    values[char_name] += 1
                    remaining_budget -= 1
                    improved = True
            if not improved:
                break
        
        # 4. On applique les bonus raciaux pour le résultat final
        for char_name in char_names:
            if char_name in racial_bonuses:
                values[char_name] += racial_bonuses[char_name]
        
        return values

    @staticmethod
    def check_attributes_points(attributes: dict) -> bool:
        """
        ### check_attributes_points
        **Description:** Vérifie que les points de caractéristiques respectent les règles de création (budget, limites, etc.).
        **Parameters:**
        - `attributes` (dict): Dictionnaire des caractéristiques du personnage.
        **Returns:** Un booléen indiquant si les points sont valides.
        """
        characteristics_manager = CharacteristicsManager()
        
        # Vérifie le budget total
        total_cost = characteristics_manager.calculate_cost(attributes)
        if total_cost > characteristics_manager.starting_points:
            return False
          # Vérifie les bornes (1-105)
        for v in attributes.values():
            if v < 1 or v > 105:
                return False
        return True
    
    @staticmethod
    def get_races() -> list:
        """
        ### get_races
        **Description:** Retourne la liste complète des races disponibles avec toutes leurs informations (cultures, bonus, etc).
        **Parameters:**
        - Aucun
        **Returns:** Une liste d'objets RaceData (structure complète issue du JSON).
        """
        races_manager = RacesManager()
        return races_manager.get_all_races_data()

    @staticmethod
    def get_skills() -> dict:
        """
        ### get_skills
        **Description:** Retourne la structure complète du fichier skills_for_llm.json (groupes, compétences, niveaux de difficulté, etc.) pour documentation Swagger et frontend.
        **Parameters:**
        - Aucun
        **Returns:** Un dictionnaire détaillé conforme à skills_for_llm.json.
        """
        skills_manager = SkillsManager()
        return skills_manager.skills_data

    @staticmethod
    def check_skills_points(skills: dict) -> bool:
        """
        ### check_skills_points
        **Description:** Vérifie la validité de la répartition des points de compétences.
        **Parameters:**
        - `skills` (dict): Dictionnaire des compétences et points attribués.
        **Returns:** True si la répartition est valide, False sinon.
        """
        # Logique simple : chaque compétence doit être entre 0 et 6, total max 40
        if not isinstance(skills, dict):
            return False
        total = 0
        for v in skills.values():
            if not (0 <= v <= 6):
                return False
            total += v
        return total <= 40

    @staticmethod
    def calculate_skills_cost(skills: dict) -> int:
        """
        ### calculate_skills_cost
        **Description:** Calcule le coût total de la répartition des compétences.
        **Parameters:**
        - `skills` (dict): Dictionnaire des compétences et points attribués.
        **Returns:** Le coût total (int).
        """
        if not isinstance(skills, dict):
            return 0
        return sum(skills.values())

    @staticmethod
    def get_equipments() -> list:
        """
        ### get_equipments
        **Description:** Retourne la liste des équipements disponibles.
        **Parameters:**
        - Aucun
        **Returns:** Une liste d'équipements (str).
        """
        equipment_manager = EquipmentManager()
        return equipment_manager.get_equipment_names()

    @staticmethod
    def get_spells() -> list:
        """
        ### get_spells
        **Description:** Retourne la liste des sorts disponibles.
        **Parameters:**
        - Aucun
        **Returns:** Une liste de sorts (str).
        """
        spells_manager = SpellsManager()
        all_spells = []
        for sphere_data in spells_manager.get_all_spells().values():
            all_spells.extend([spell["name"] for spell in sphere_data])
        return all_spells
