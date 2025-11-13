import yaml
import os
from typing import Dict, List, Optional
from ...config import get_data_dir

class SpellsManager:
    """Spells manager using the new simplified YAML system for the LLM agent"""
    
    def __init__(self):
        self._load_spells_data()
    
    def _load_spells_data(self):
        """Load data from YAML file"""
        data_path = os.path.join(get_data_dir(), "spells.yaml")
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            self.magic_system = data["magic_system"]
            self.spheres = self.magic_system["spheres"]
            
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Spells data file not found: {data_path}. "
                f"Please ensure that file exists and contains valid YAML data with 'magic_system' and 'spheres' keys."
            )
        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"Invalid YAML in spells file {data_path}: {str(e)}. "
                f"Please check the file format and syntax."
            )

    def get_all_spheres(self) -> List[str]:
        """Retourne la liste de toutes les sphères de magie"""
        return [sphere["name"] for sphere in self.spheres]

    def get_sphere_by_name(self, sphere_name: str) -> Optional[Dict]:
        """Retourne les données d'une sphère par son nom"""
        for sphere in self.spheres:
            if sphere["name"] == sphere_name:
                return sphere
        return None

    def get_spells_by_sphere(self, sphere_name: str) -> List[Dict]:
        """Retourne tous les sorts d'une sphère"""
        sphere = self.get_sphere_by_name(sphere_name)
        if sphere:
            return sphere.get("spells", [])
        return []

    def get_spell_by_name(self, spell_name: str) -> Optional[Dict]:
        """Trouve un sort par son nom dans toutes les sphères"""
        for sphere in self.spheres:
            for spell in sphere.get("spells", []):
                if spell["name"] == spell_name:
                    spell_copy = spell.copy()
                    spell_copy["sphere"] = sphere["name"]
                    return spell_copy
        return None

    def get_all_spells(self) -> List[Dict]:
        """Retourne tous les sorts avec leur sphère"""
        all_spells = []
        for sphere in self.spheres:
            for spell in sphere.get("spells", []):
                spell_copy = spell.copy()
                spell_copy["sphere"] = sphere["name"]
                all_spells.append(spell_copy)
        return all_spells

    def get_spells_by_power_cost(self, max_cost: int) -> List[Dict]:
        """Retourne tous les sorts coûtant au maximum X points de pouvoir"""
        affordable_spells = []
        for sphere in self.spheres:
            for spell in sphere.get("spells", []):
                if spell.get("power_cost", 0) <= max_cost:
                    spell_copy = spell.copy()
                    spell_copy["sphere"] = sphere["name"]
                    affordable_spells.append(spell_copy)
        return affordable_spells

    def search_spells_by_keyword(self, keyword: str) -> List[Dict]:
        """Recherche des sorts par mot-clé dans le nom ou la description"""
        keyword_lower = keyword.lower()
        matching_spells = []
        
        for sphere in self.spheres:
            for spell in sphere.get("spells", []):
                if (keyword_lower in spell["name"].lower() or 
                    keyword_lower in spell["description"].lower()):
                    spell_copy = spell.copy()
                    spell_copy["sphere"] = sphere["name"]
                    matching_spells.append(spell_copy)
        
        return matching_spells

    def get_sphere_description(self, sphere_name: str) -> str:
        """Retourne la description d'une sphère"""
        sphere = self.get_sphere_by_name(sphere_name)
        if sphere:
            return sphere.get("description", "")
        return ""

    def suggest_spells_for_situation(self, situation: str) -> List[Dict]:
        """Suggère des sorts appropriés pour une situation donnée"""
        situation_lower = situation.lower()
        suggestions = []
        
        # Mots-clés spécifiques pour suggérer des sorts
        keyword_mapping = {
            "soigner": ["Soins Mineurs", "Soins Majeurs", "Régénération"],
            "guérir": ["Soins Mineurs", "Soins Majeurs", "Purification"],
            "attaque": ["Projectile Magique", "Boule de Feu", "Éclair"],
            "combat": ["Arme Élémentaire", "Bouclier Magique", "Force de la Nature"],
            "défense": ["Bouclier Magique", "Amélioration d'Armure", "Peau d'Acier"],
            "voir": ["Lumière", "Infravision", "Détection de la Magie"],
            "éclairage": ["Lumière"],
            "charmer": ["Charme", "Voix Envoutante"],
            "convaincre": ["Charme", "Voix Envoutante"],
            "confondre": ["Confusion", "Distractions"],
            "calmer": ["Quiétude", "Sommeil"],
            "animal": ["Dialectes de la Nature", "Mutation Animale"],
            "nature": ["Force de la Nature", "Dialectes de la Nature"],
            "feu": ["Embrasement", "Boule de Feu"],
            "froid": ["Congélation"],
            "barrière": ["Mur d'Épines"],
            "téléporter": ["Téléportation"],
            "langue": ["Langages"]
        }
        
        for keyword, spell_names in keyword_mapping.items():
            if keyword in situation_lower:
                for spell_name in spell_names:
                    spell = self.get_spell_by_name(spell_name)
                    if spell and spell not in suggestions:
                        suggestions.append(spell)
        
        return suggestions

    def get_spells_for_character_spheres(self, character_spheres: List[str]) -> Dict[str, List[Dict]]:
        """Retourne tous les sorts disponibles pour les sphères d'un personnage"""
        available_spells = {}
        
        for sphere_name in character_spheres:
            sphere_spells = self.get_spells_by_sphere(sphere_name)
            if sphere_spells:
                available_spells[sphere_name] = sphere_spells
        
        return available_spells
