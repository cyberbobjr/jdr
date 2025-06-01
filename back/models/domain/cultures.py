from typing import Optional, Dict
import csv
import os
from .base import Culture
from .races import Races

class Cultures:
    """Gestion des cultures"""
    
    def __init__(self):
        self.cultures = self._load_cultures()
    
    def _load_cultures(self) -> Dict[str, Culture]:
        """Charge toutes les cultures depuis le fichier CSV"""
        cultures = {}
        csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cultures.csv')
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Ignorer les lignes de commentaire
                    if row['Nom'].startswith('#'):
                        continue
                    
                    # Construire le dictionnaire des compétences d'adolescence
                    adolescence_skills = {}
                    skill_mapping = {
                        'Estimation': 'Estimation',
                        'Artisanat': 'Artisanat',
                        'Accord': 'Accord',
                        'Armure': 'Armure',
                        'Embuscade': 'Embuscade',
                        'Elevage': 'Élevage',
                        'Escalade': 'Escalade',
                        'Endurance': 'Endurance',
                        'Soins': 'Soins',
                        'Herboristerie': 'Herboristerie',
                        'Connaissance_Generale': 'Connaissance Générale',
                        'Sens_Orientation': 'Sens de l\'Orientation',
                        'Perception': 'Perception',
                        'Runes': 'Runes',
                        'Crochetage_Pieges': 'Crochetage & Pièges',
                        'Dissimulation': 'Dissimulation',
                        'Pistage': 'Pistage',
                        'Maniement_Arme': 'Maniement d\'Arme',
                        'Equitation': 'Équitation',
                        'Natation': 'Natation',
                        'Saut': 'Saut'
                    }
                    
                    for csv_key, skill_name in skill_mapping.items():
                        if csv_key in row and row[csv_key].isdigit():
                            value = int(row[csv_key])
                            if value > 0:
                                adolescence_skills[skill_name] = value
                    
                    # Créer l'objet Culture
                    culture = Culture(
                        name=row['Nom'],
                        description=row['Description'],
                        adolescence_skills=adolescence_skills
                    )
                    
                    cultures[row['Nom']] = culture
                    
        except FileNotFoundError:
            print(f"Erreur : Fichier CSV non trouvé à {csv_path}")
        except Exception as e:
            print(f"Erreur lors du chargement du fichier CSV : {e}")
            
        return cultures
    
    def get_culture(self, culture_name: str) -> Optional[Culture]:
        """Récupère une culture par son nom"""
        return self.cultures.get(culture_name)
    
    def get_all_cultures(self) -> Dict[str, Culture]:
        """Retourne toutes les cultures"""
        return self.cultures
    
    def get_culture_names(self) -> list:
        """Retourne la liste des noms de cultures"""
        return list(self.cultures.keys())
    
    def search_cultures(self, search_term: str) -> list:
        """Recherche des cultures par nom ou description"""
        results = []
        search_term = search_term.lower()
        
        for culture in self.cultures.values():
            if (search_term in culture.name.lower() or 
                search_term in culture.description.lower()):
                results.append(culture)
                
        return results
    
    def get_cultures_with_skill(self, skill_name: str) -> list:
        """Retourne les cultures qui donnent des bonus à une compétence"""
        results = []
        for culture in self.cultures.values():
            if skill_name in culture.adolescence_skills:
                results.append(culture)
        return results
    
    def validate_race_culture(self, race_name: str, culture_name: str) -> bool:
        """Valide si une culture est compatible avec une race"""
        races = Races()
        race = races.get_race(race_name)
        if not race:
            return False
        return culture_name in race.sub_cultures
    
    def get_compatible_cultures(self, race_name: str) -> list:
        """Retourne les cultures compatibles avec une race donnée"""
        races = Races()
        race = races.get_race(race_name)
        if not race:
            return []
        
        compatible_cultures = []
        for culture_name in race.sub_cultures:
            culture = self.get_culture(culture_name)
            if culture:
                compatible_cultures.append(culture)
        
        return compatible_cultures
    
    def get_total_adolescence_bonus(self, culture_name: str) -> int:
        """Calcule le total des bonus d'adolescence d'une culture"""
        culture = self.get_culture(culture_name)
        if not culture:
            return 0
        return sum(culture.adolescence_skills.values())
    
    def get_culture_statistics(self) -> Dict[str, int]:
        """Retourne des statistiques sur les cultures"""
        stats = {
            "total_cultures": len(self.cultures),
            "avg_adolescence_bonus": 0,
            "max_adolescence_bonus": 0,
            "min_adolescence_bonus": float('inf')
        }
        
        if self.cultures:
            bonuses = [self.get_total_adolescence_bonus(name) for name in self.cultures.keys()]
            stats["avg_adolescence_bonus"] = sum(bonuses) / len(bonuses)
            stats["max_adolescence_bonus"] = max(bonuses)
            stats["min_adolescence_bonus"] = min(bonuses)
        
        return stats
