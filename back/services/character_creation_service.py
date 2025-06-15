"""
Service dédié à la création de personnage pour le jeu de rôle.
Ce service gère l'allocation automatique des caractéristiques, la vérification des règles,
et fournit les listes de professions, races, compétences, cultures, équipements et sorts.
"""

from back.models.domain.competences import Competences
from back.models.domain.equipements import Equipements
from back.models.domain.magie import Magie
from back.config import get_data_dir
import json
import os

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
        from back.models.domain.caracteristiques import Caracteristiques
        from back.models.domain.races import Races
        caracs = Caracteristiques()
        base_names = caracs.NAMES
        budget = 550
        # Bonus raciaux à intégrer dans la répartition
        races = Races().RACES_DATA
        race_obj = races.get(race)
        racial_bonuses = race_obj.characteristic_bonuses if race_obj else {}
        # 1. On part d'une base minimale (50 partout)
        values = {name: 50 for name in base_names}
        # 2. On prépare la liste d'ordre de priorité
        recos = caracs.get_profession_recommendations().get(profession, {})
        main_stats = recos.get("principales", [])
        ordered_stats = main_stats + [n for n in base_names if n not in main_stats]
        # 3. On incrémente chaque stat dans l'ordre, en tenant compte du bonus racial, jusqu'à épuisement du budget
        while True:
            improved = False
            for stat in ordered_stats:
                bonus = racial_bonuses.get(stat, 0)
                # On ne dépasse jamais 90 au total (valeur brute + bonus racial)
                if values[stat] + bonus < 90:
                    # On simule l'incrément
                    test_values = {k: values[k] + racial_bonuses.get(k, 0) for k in base_names}
                    test_values[stat] += 1
                    if caracs.calculate_cost(test_values) <= budget:
                        values[stat] += 1
                        improved = True
            if not improved:
                break
        # 4. On applique les bonus raciaux pour le résultat final
        for stat in base_names:
            if stat in racial_bonuses:
                values[stat] += racial_bonuses[stat]
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
        from back.models.domain.caracteristiques import Caracteristiques
        caracs = Caracteristiques()
        # Vérifie le budget total
        if not caracs.validate_distribution(attributes):
            return False
        # Vérifie les bornes (1-105)
        for v in attributes.values():
            if v < 1 or v > 105:
                return False
        return True

    @staticmethod
    def get_professions() -> list:
        """
        ### get_professions
        **Description:** Retourne la liste des professions disponibles (noms uniquement).
        **Parameters:**
        - Aucun
        **Returns:** Une liste de professions (str).
        """
        data_path = os.path.join(get_data_dir(), 'professions.json')
        with open(data_path, encoding='utf-8') as f:
            professions = json.load(f)
        return [p['name'] for p in professions]

    @staticmethod
    def get_professions_full() -> list:
        """
        ### get_professions_full
        **Description:** Retourne la liste complète des objets professions (toutes les infos).
        **Parameters:**
        - Aucun
        **Returns:** Une liste de dictionnaires représentant chaque profession.
        """
        data_path = os.path.join(get_data_dir(), 'professions.json')
        with open(data_path, encoding='utf-8') as f:
            professions = json.load(f)
        return professions

    @staticmethod
    def get_races() -> list:
        """
        ### get_races
        **Description:** Retourne la liste complète des races disponibles avec toutes leurs informations (cultures, bonus, etc).
        **Parameters:**
        - Aucun
        **Returns:** Une liste d'objets RaceData (structure complète issue du JSON).
        """
        from back.models.domain.races import Races
        return Races().RACES_DATA

    @staticmethod
    def get_skills() -> dict:
        """
        ### get_skills
        **Description:** Retourne le dictionnaire brut des groupes de compétences (structure du JSON centralisé).
        **Parameters:**
        - Aucun
        **Returns:** Un dictionnaire {groupe: [compétences]}.
        """
        return Competences().SKILL_GROUPS

    @staticmethod
    def get_equipments() -> list:
        """
        ### get_equipments
        **Description:** Retourne la liste des équipements disponibles.
        **Parameters:**
        - Aucun
        **Returns:** Une liste d'équipements (str).
        """
        return list(Equipements().equipment.keys())

    @staticmethod
    def get_spells() -> list:
        """
        ### get_spells
        **Description:** Retourne la liste des sorts disponibles.
        **Parameters:**
        - Aucun
        **Returns:** Une liste de sorts (str).
        """
        return list(Magie().spells.keys())

    @staticmethod
    def check_skills_points(skills: dict, profession: str) -> bool:
        """
        ### check_skills_points
        **Description:** Vérifie que la répartition des points de compétences respecte les règles (budget, maximum par compétence, groupes favoris, etc.), en s'appuyant sur le modèle Competences.
        **Parameters:**
        - `skills` (dict): Dictionnaire {nom_compétence: rangs}
        - `profession` (str): Profession du personnage (pour les groupes favoris)
        **Returns:** True si la répartition est valide, False sinon.
        """
        from back.models.domain.professions import Professions
        from back.models.domain.competences import Competences
        MAX_RANK = 6
        BUDGET = 40
        prof = Professions().PROFESSIONS_DATA.get(profession)
        if not prof:
            return False
        favored_groups = prof.favored_skill_groups.keys()
        comp = Competences()
        total_cost = 0
        for skill, ranks in skills.items():
            skill_obj = comp.get_skill(skill)
            if not skill_obj:
                return False
            if not (0 <= ranks <= MAX_RANK):
                return False
            is_favored = skill_obj.group in favored_groups
            total_cost += comp.calculate_development_cost(skill, ranks, is_favored)
        return total_cost <= BUDGET

    @staticmethod
    def calculate_skills_cost(skills: dict, profession: str) -> int:
        """
        ### calculate_skills_cost
        **Description:** Calcule le coût total en PdP de la répartition des compétences, en s'appuyant sur le modèle Competences.
        **Parameters:**
        - `skills` (dict): Dictionnaire {nom_compétence: rangs}
        - `profession` (str): Profession du personnage
        **Returns:** Le coût total (int).
        """
        from back.models.domain.professions import Professions
        from back.models.domain.competences import Competences
        prof = Professions().PROFESSIONS_DATA.get(profession)
        if not prof:
            return 0
        favored_groups = prof.favored_skill_groups.keys()
        comp = Competences()
        total_cost = 0
        for skill, ranks in skills.items():
            skill_obj = comp.get_skill(skill)
            if not skill_obj:
                continue
            is_favored = skill_obj.group in favored_groups
            total_cost += comp.calculate_development_cost(skill, ranks, is_favored)
        return total_cost
