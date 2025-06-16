"""
Service dédié à la création de personnage pour le jeu de rôle.
Ce service gère l'allocation automatique des caractéristiques, la vérification des règles,
et fournit les listes de professions, races, compétences, cultures, équipements et sorts.
"""

from back.models.domain.characteristics_manager import CharacteristicsManager
from back.models.domain.skills_manager import SkillsManager
from back.models.domain.races_manager import RacesManager
from back.models.domain.spells_manager import SpellsManager
from back.models.domain.professions_manager import ProfessionsManager
from back.models.domain.equipment_manager import EquipmentManager

class CharacterCreationService:
    """
    Service pour la gestion de la création de personnage.
    """

    @staticmethod
    def allocate_attributes_auto(profession: str, race: str) -> dict:
        """
        ### allocate_attributes_auto
        **Description:** Alloue automatiquement les caractéristiques d'un personnage selon sa profession et sa race, en optimisant la répartition selon les recommandations métier et en intégrant les bonus raciaux dans le calcul du budget, sans boucle infinie.
        **Parameters:**
        - `profession` (str): La profession du personnage.
        - `race` (str): La race du personnage.
        **Returns:** Un dictionnaire des caractéristiques allouées.
        """
        characteristics_manager = CharacteristicsManager()
        races_manager = RacesManager()
          # Obtenir les noms des caractéristiques et le budget
        char_names = list(characteristics_manager.get_all_characteristics().keys())
        starting_points = characteristics_manager.starting_points
        
        # Bonus raciaux à intégrer dans la répartition
        race_data = races_manager.get_race_by_name(race)
        racial_bonuses = race_data.get("characteristic_bonuses", {}) if race_data else {}
        
        # 1. On part d'une base minimale (50 partout)
        values = {name: 50 for name in char_names}
          # 2. Pour simplifier, on distribue équitablement le budget restant
        remaining_budget = starting_points - sum(values.values())
        
        # 3. Distribution équitable avec priorité aux caractéristiques principales de la profession
        professions_manager = ProfessionsManager()
        profession_data = professions_manager.get_profession_by_name(profession)
        primary_chars = profession_data.get("primary_characteristics", []) if profession_data else []
        
        # Distribution prioritaire aux caractéristiques principales
        chars_to_improve = primary_chars + [name for name in char_names if name not in primary_chars]
        
        # Amélioration progressive jusqu'à épuisement du budget
        while remaining_budget > 0 and any(values[name] < 90 for name in char_names):
            improved = False
            for char_name in chars_to_improve:
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
        
        return values    @staticmethod
    def check_attributes_points(attributes: dict) -> bool:
        """
        ### check_attributes_points
        **Description:** Vérifie que les points de caractéristiques respectent les règles de création (budget, limites, etc.).
        **Parameters:**
        - `attributes` (dict): Dictionnaire des caractéristiques du personnage.
        **Returns:** Un booléen indiquant si les points sont valides.
        """    @staticmethod
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
        
        # Vérifie les bornes (1-100)
        for v in attributes.values():
            if v < 1 or v > 100:
                return False
        return True

    @staticmethod
    def get_professions() -> list:
        """
        ### get_professions
        **Description:** Retourne la liste des professions disponibles (noms uniquement).        **Parameters:**
        - Aucun
        **Returns:** Une liste de professions (str).
        """
        professions_manager = ProfessionsManager()
        return professions_manager.get_profession_names()

    @staticmethod
    def get_professions_full() -> list:
        """
        ### get_professions_full
        **Description:** Retourne la liste complète des objets professions (toutes les infos).
        **Parameters:**
        - Aucun
        **Returns:** Une liste de dictionnaires représentant chaque profession.
        """
        professions_manager = ProfessionsManager()
        return professions_manager.get_all_professions()    @staticmethod
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
        **Description:** Retourne le dictionnaire brut des groupes de compétences (structure du JSON centralisé).
        **Parameters:**
        - Aucun
        **Returns:** Un dictionnaire {groupe: [compétences]}.
        """
        skills_manager = SkillsManager()
        return skills_manager.get_all_skill_groups()    @staticmethod
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
        return all_spells    @staticmethod
    def check_skills_points(skills: dict, profession: str) -> bool:
        """
        ### check_skills_points
        **Description:** Vérifie que la répartition des points de compétences respecte les règles (budget, maximum par compétence, groupes favoris, etc.), en s'appuyant sur les nouveaux managers.
        **Parameters:**
        - `skills` (dict): Dictionnaire {nom_compétence: rangs}
        - `profession` (str): Profession du personnage (pour les groupes favoris)
        **Returns:** True si la répartition est valide, False sinon.
        """
        professions_manager = ProfessionsManager()
        skills_manager = SkillsManager()
        
        MAX_RANK = 6
        BUDGET = 40
        
        profession_data = professions_manager.get_profession_by_name(profession)
        if not profession_data:
            return False
        
        skill_groups = profession_data.get("skill_groups", {})
        total_cost = 0
        
        for skill_name, ranks in skills.items():
            if not (0 <= ranks <= MAX_RANK):
                return False
            
            skill_data = skills_manager.get_skill_by_name(skill_name)
            if not skill_data:
                return False
            
            skill_group = skill_data.get("group", "")
            is_favored = skill_group in skill_groups
            
            # Calcul du coût: si favori, coût réduit de moitié pour les premiers rangs
            if is_favored and skill_group in skill_groups:
                favored_info = skill_groups[skill_group]
                favored_ranks = min(ranks, favored_info.get("ranks", 0))
                cost_per_rank = favored_info.get("cost_per_rank", 3)
                regular_ranks = max(0, ranks - favored_ranks)
                total_cost += favored_ranks * cost_per_rank + regular_ranks * 3
            else:
                total_cost += ranks * 3  # Coût standard
        
        return total_cost <= BUDGET    @staticmethod
    def calculate_skills_cost(skills: dict, profession: str) -> int:
        """
        ### calculate_skills_cost
        **Description:** Calcule le coût total en PdP de la répartition des compétences, en s'appuyant sur les nouveaux managers.
        **Parameters:**
        - `skills` (dict): Dictionnaire {nom_compétence: rangs}
        - `profession` (str): Profession du personnage
        **Returns:** Le coût total (int).
        """
        professions_manager = ProfessionsManager()
        skills_manager = SkillsManager()
        
        profession_data = professions_manager.get_profession_by_name(profession)
        if not profession_data:
            return 0
        
        skill_groups = profession_data.get("skill_groups", {})
        total_cost = 0
        
        for skill_name, ranks in skills.items():
            skill_data = skills_manager.get_skill_by_name(skill_name)
            if not skill_data:
                continue
            
            skill_group = skill_data.get("group", "")
            is_favored = skill_group in skill_groups
            
            # Calcul du coût: si favori, coût réduit de moitié pour les premiers rangs
            if is_favored and skill_group in skill_groups:
                favored_info = skill_groups[skill_group]
                favored_ranks = min(ranks, favored_info.get("ranks", 0))
                cost_per_rank = favored_info.get("cost_per_rank", 3)
                regular_ranks = max(0, ranks - favored_ranks)
                total_cost += favored_ranks * cost_per_rank + regular_ranks * 3
            else:
                total_cost += ranks * 3  # Coût standard
                
        return total_cost
