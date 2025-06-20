from typing import Optional, List, Dict
import csv
import os
from .base import Spell
from ...config import get_data_dir

class Magie:
    """Gestion de la magie et des sorts"""
    
    def __init__(self):
        self.spheres = ["Universelle", "Animiste", "Aventurier", "Barde", "Elémentaliste", "Guérisseur", "Guerrier-Mage", "Haute Magie", "Magicien", "Mentaliste"]
        self.spells = self._load_spells()
    
    def _load_spells(self) -> Dict[str, Spell]:
        """Charge tous les sorts depuis le fichier CSV"""
        spells = {}
        csv_path = os.path.join(get_data_dir(), 'sorts.csv')
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Ignorer les lignes de commentaire
                    if row['Sphere'].startswith('#'):
                        continue
                    
                    # Créer l'objet Spell avec les arguments corrects
                    spell = Spell(
                        name=row['Nom'],
                        sphere=row['Sphere'],
                        description=row['Description'],
                        duration=row['Duree'] if row['Duree'] != '-' else None,
                        cost=int(row['Cout_PP']) if row['Cout_PP'].isdigit() else 0,
                        range=row['Portee'],
                        resistance=row['Jet_Resistance'] if row['Jet_Resistance'] != '-' else None,
                        level=int(row['Niveau']) if 'Niveau' in row and row['Niveau'].isdigit() else 1,  # Initialisation du niveau
                        bonus=row['Bonus'] if row['Bonus'] != '-' else None,
                        malus=row['Malus'] if row['Malus'] != '-' else None,
                        dice_rolls=row['Jets_Des'] if row['Jets_Des'] != '-' else None
                    )
                    spells[row['Nom']] = spell
                    
        except FileNotFoundError:
            print(f"Erreur : Fichier CSV non trouvé à {csv_path}")
        except Exception as e:
            print(f"Erreur lors du chargement du fichier CSV : {e}")
            
        return spells
    
    def get_spell(self, spell_name: str) -> Optional[Spell]:
        """Récupère un sort par son nom"""
        return self.spells.get(spell_name)
    
    def get_spells_by_sphere(self, sphere: str) -> List[Spell]:
        """Retourne tous les sorts d'une sphère"""
        return [spell for spell in self.spells.values() if spell.sphere == sphere]
    
    def search_spells(self, search_term: str) -> List[Spell]:
        """Recherche des sorts par nom ou description"""
        results = []
        search_term = search_term.lower()
        
        for spell in self.spells.values():
            if (search_term in spell.name.lower() or 
                search_term in spell.description.lower()):
                results.append(spell)
                
        return results
    
    def get_spells_by_cost_range(self, min_cost: int, max_cost: int) -> List[Spell]:
        """Retourne les sorts dans une fourchette de coût en PP"""
        return [spell for spell in self.spells.values() 
                if min_cost <= spell.pp_cost <= max_cost]
    
    def calculate_pp_cost(self, base_cost: int, improvements: List[str] = None) -> int:
        """Calcule le coût total en PP d'un sort avec améliorations"""
        total_cost = base_cost
        if improvements:
            for improvement in improvements:
                if "Portée" in improvement:
                    total_cost += 2
                elif "Durée" in improvement:
                    total_cost += 4
                elif "Puissance" in improvement:
                    total_cost += 6
        return total_cost
    
    def get_all_spheres(self) -> List[str]:
        """Retourne la liste de toutes les sphères"""
        return self.spheres
    
    def get_spell_count_by_sphere(self) -> Dict[str, int]:
        """Retourne le nombre de sorts par sphère"""
        count = {}
        for sphere in self.spheres:
            count[sphere] = len(self.get_spells_by_sphere(sphere))
        return count
