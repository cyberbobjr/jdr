import yaml
import os
from typing import Dict, List, Optional
from ...config import get_data_dir

class SkillsManager:
    """Gestionnaire des compétences utilisant le nouveau système JSON pour l'agent LLM"""
    
    def __init__(self):
        self._load_skills_data()
    
    def _load_skills_data(self):
        """Load skills data from YAML file"""
        data_path = os.path.join(get_data_dir(), "skills_for_llm.yaml")
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            self.skills_data = data["skills_for_llm"]
            self.skill_groups = self.skills_data["skill_groups"]
            
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Skills data file not found: {data_path}. "
                f"Please ensure the file exists and contains valid YAML data with 'skills_for_llm' and 'skill_groups' keys."
            )
        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"Invalid YAML in skills file {data_path}: {str(e)}. "
                f"Please check the file format and syntax."
            )

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


    def search_skills_by_keyword(self, keyword: str) -> List[Dict]:
        """Recherche des compétences par mot-clé dans le nom ou la description"""
        keyword_lower = keyword.lower()
        matching_skills = []
        
        for group_name, skills in self.skill_groups.items():
            for skill in skills:
                if (keyword_lower in skill["name"].lower() or
                    keyword_lower in skill["description"].lower()):
                    skill_copy = skill.copy()
                    skill_copy["group"] = group_name
                    matching_skills.append(skill_copy)
        
        return matching_skills
