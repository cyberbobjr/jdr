import json
from typing import Optional, List, Dict
from .base import Skill

class Competences:
    """Gestion des compétences (chargement depuis skill_groups.json)"""

    def __init__(self):
        self.SKILL_GROUPS = self._load_skill_groups()
        self.skills = {}
        self.ranks = {}  # rangs par compétence
        self.adolescence_ranks = {}  # rangs d'adolescence

    def _load_skill_groups(self) -> Dict[str, List[dict]]:
        """
        ### _load_skill_groups
        **Description:** Charge les groupes de compétences depuis le fichier JSON centralisé.
        **Parameters:**
        - Aucun
        **Returns:**
        - (Dict[str, List[dict]]) : Dictionnaire des groupes de compétences et leurs descriptions.
        """
        import os
        from back.config import get_data_dir
        json_path = os.path.join(get_data_dir(), 'skill_groups.json')
        with open(json_path, encoding='utf-8') as f:
            return json.load(f)

    # Ajout pour compatibilité API : alias de get_skill
    def get_competence(self, skill_name: str):
        return self.get_skill(skill_name)
    
    def calculate_skill_bonus(self, skill_name: str, characteristics) -> int:
        """Calcule le bonus total d'une compétence"""
        skill = self.get_skill(skill_name)
        if not skill:
            return 0
            
        # Bonus des rangs (premiers 10 rangs = +5 chacun)
        total_ranks = self.get_total_ranks(skill_name)
        rank_bonus = min(total_ranks, 10) * 5
        if total_ranks > 10:
            rank_bonus += (total_ranks - 10) * 2  # Après 10 rangs, +2 par rang
            
        # Bonus des caractéristiques
        char1_bonus = characteristics.get_bonus(skill.characteristics[0])
        char2_bonus = characteristics.get_bonus(skill.characteristics[1])
        
        return rank_bonus + char1_bonus + char2_bonus
    
    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """Récupère une compétence par son nom"""
        # Recherche la compétence et sa description
        for group, skills in self.SKILL_GROUPS.items():
            for skill in skills:
                if isinstance(skill, dict) and skill.get("name") == skill_name:
                    # Les caractéristiques, type, etc. peuvent être enrichis ici si besoin
                    return Skill(skill_name, group, ("Raisonnement", "Volonté"), "Tout-ou-rien", skill.get("description", ""))
        return None
    
    def get_total_ranks(self, skill_name: str) -> int:
        """Retourne le total des rangs (développement + adolescence)"""
        dev_ranks = self.ranks.get(skill_name, 0)
        adol_ranks = self.adolescence_ranks.get(skill_name, 0)
        return dev_ranks + adol_ranks
    
    def calculate_development_cost(self, skill_name: str, ranks: int, is_favored: bool) -> int:
        """Calcule le coût en PdD pour développer une compétence"""
        cost_per_rank = 2 if is_favored else 4
        return ranks * cost_per_rank
    
    def get_group_skills(self, group_name: str) -> List[str]:
        """Retourne les compétences d'un groupe"""
        # Retourne la liste des noms de compétences du groupe
        return [s["name"] for s in self.SKILL_GROUPS.get(group_name, [])]
