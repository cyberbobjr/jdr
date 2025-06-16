import json
from typing import Dict, List, Optional
from pathlib import Path

class SkillsManager:
    """Gestionnaire des compétences utilisant le nouveau système JSON pour l'agent LLM"""
    
    def __init__(self):
        self._load_skills_data()
    
    def _load_skills_data(self):
        """Charge les données depuis le fichier JSON"""
        data_path = Path(__file__).parent.parent.parent.parent / "data" / "skills_for_llm.json"
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.skills_data = data["skills_for_llm"]
            self.skill_groups = self.skills_data["skill_groups"]
            self.difficulty_levels = self.skills_data["difficulty_levels"]
            
        except FileNotFoundError:
            # Fallback vers un système minimal
            self._load_fallback_data()
    
    def _load_fallback_data(self):
        """Données de fallback si le fichier JSON n'est pas trouvé"""
        self.skill_groups = {
            "Général": [
                {
                    "name": "Perception",
                    "description": "Capacité à remarquer des détails",
                    "characteristics": ["Intuition", "Volonté"],
                    "examples": ["Repérer un piège", "Entendre des pas"]
                }
            ]
        }
        self.difficulty_levels = {
            "Moyenne": {"modifier": 0, "description": "Difficulté standard"}
        }

    def get_skill_by_name(self, skill_name: str) -> Optional[Dict]:
        """Trouve une compétence par son nom dans tous les groupes"""
        for group_name, skills in self.skill_groups.items():
            for skill in skills:
                if skill["name"] == skill_name:
                    skill_copy = skill.copy()
                    skill_copy["group"] = group_name
                    return skill_copy
        return None

    def get_all_skills(self) -> List[Dict]:
        """Retourne toutes les compétences avec leur groupe"""
        all_skills = []
        for group_name, skills in self.skill_groups.items():
            for skill in skills:
                skill_copy = skill.copy()
                skill_copy["group"] = group_name
                all_skills.append(skill_copy)
        return all_skills

    def get_skills_by_group(self, group_name: str) -> List[Dict]:
        """Retourne les compétences d'un groupe spécifique"""
        return self.skill_groups.get(group_name, [])

    def get_difficulty_modifier(self, difficulty_name: str) -> int:
        """Retourne le modificateur pour un niveau de difficulté"""
        difficulty = self.difficulty_levels.get(difficulty_name, {})
        return difficulty.get("modifier", 0)

    def get_all_difficulty_levels(self) -> Dict[str, Dict]:
        """Retourne tous les niveaux de difficulté"""
        return self.difficulty_levels

    def search_skills_by_keyword(self, keyword: str) -> List[Dict]:
        """Recherche des compétences par mot-clé dans le nom ou la description"""
        keyword_lower = keyword.lower()
        matching_skills = []
        
        for group_name, skills in self.skill_groups.items():
            for skill in skills:
                if (keyword_lower in skill["name"].lower() or 
                    keyword_lower in skill["description"].lower() or
                    any(keyword_lower in example.lower() for example in skill.get("examples", []))):
                    skill_copy = skill.copy()
                    skill_copy["group"] = group_name
                    matching_skills.append(skill_copy)
        
        return matching_skills

    def get_skills_by_characteristic(self, characteristic: str) -> List[Dict]:
        """Retourne les compétences qui utilisent une caractéristique donnée"""
        matching_skills = []
        
        for group_name, skills in self.skill_groups.items():
            for skill in skills:
                if characteristic in skill.get("characteristics", []):
                    skill_copy = skill.copy()
                    skill_copy["group"] = group_name
                    matching_skills.append(skill_copy)
        
        return matching_skills

    def suggest_skill_for_action(self, action_description: str) -> List[Dict]:
        """Suggère des compétences appropriées pour une action donnée"""
        # Simple recherche par mots-clés dans la description
        action_lower = action_description.lower()
        suggestions = []
        
        # Mots-clés spécifiques pour suggérer des compétences
        keyword_mapping = {
            "combat": ["Maniement d'Arme", "Arts Martiaux"],
            "attaque": ["Maniement d'Arme", "Arts Martiaux"],
            "voir": ["Perception"],
            "entendre": ["Perception"],
            "repérer": ["Perception"],
            "grimper": ["Escalade"],
            "escalader": ["Escalade"],
            "nager": ["Natation"],
            "cacher": ["Discrétion"],
            "furtif": ["Discrétion"],
            "silencieux": ["Discrétion"],
            "convaincre": ["Diplomatie"],
            "négocier": ["Diplomatie"],
            "menacer": ["Intimidation"],
            "effrayer": ["Intimidation"],
            "voler": ["Vol à la Tire"],
            "subtiliser": ["Vol à la Tire"],
            "crocheter": ["Crochetage"],
            "ouvrir": ["Crochetage"],
            "serrure": ["Crochetage"]
        }
        
        for keyword, skill_names in keyword_mapping.items():
            if keyword in action_lower:
                for skill_name in skill_names:
                    skill = self.get_skill_by_name(skill_name)
                    if skill and skill not in suggestions:
                        suggestions.append(skill)
        
        return suggestions
