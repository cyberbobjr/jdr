from typing import Dict
from .base import CharacteristicBonus

class Caracteristiques:
    """Gestion des 8 caractéristiques et leurs bonus"""
    
    # Noms et descriptions des caractéristiques
    CHARACTERISTICS_INFO = {
        "Force": "Ne représente pas simplement la force brutale, mais permet aussi d'évaluer la carrure et la structure musculaire. Les personnages possédant une Force importante peuvent utiliser leur puissance physique à son potentiel maximal. Favorisée par les Guerriers.",
        "Constitution": "Reflète la santé et le bien-être global, la vigueur, la résistance aux poisons et aux maladies, et la capacité à survivre à la fatigue et aux blessures subies lors des combats.",
        "Agilité": "Les personnages qui accomplissent des exploits exceptionnels de dextérité manuelle ont une Agilité élevée. Favorisée par les Aventuriers et les Voleurs.",
        "Rapidité": "Mesure les réflexes et la coordination, détermine le temps de réaction. Les personnages avec des valeurs élevées se déplacent rapidement et sont à même d'esquiver des coups. Favorisée par les Guerriers et les Moines.",
        "Volonté": "Symbolise la résolution, le dévouement et l'obstination. Détermine la résistance aux tentatives de manipulations par autrui. Les Moines favorisent le plus une haute Volonté.",
        "Raisonnement": "La capacité à montrer une pensée logique, rationnelle et analytique. Les personnages avec de nombreux points semblent particulièrement astucieux, pleins de bon sens et capables d'appliquer de sains jugements. Estimé par les Mages et les Guerriers-Mages.",
        "Intuition": "Couvre les facultés intuitives, la capacité à discerner la vraie nature d'une situation. Définit le lien avec le monde qui entoure le personnage et sa compréhension. Estimée par les Prêtres.",
        "Présence": "Le contrôle, la confiance en soi et la contenance. Ceux possédant une Présence élevée sont pleins de charme et d'esprit, avec une évidente force de personnalité. Détermine la capacité à interagir et influencer les autres. Valorisée par les Bardes."
    }
    
    NAMES = list(CHARACTERISTICS_INFO.keys())
    
    # Table des bonus de caractéristiques
    BONUS_TABLE = {
        range(1, 6): -18, range(6, 11): -16, range(11, 16): -14, range(16, 21): -12,
        range(21, 26): -10, range(26, 31): -8, range(31, 36): -6, range(36, 41): -4,
        range(41, 46): -2, range(46, 51): 0, range(51, 56): 1, range(56, 61): 2,
        range(61, 66): 3, range(66, 71): 4, range(71, 76): 5, range(76, 81): 6,
        range(81, 86): 7, range(86, 91): 8, range(91, 96): 9, range(96, 101): 10,
        101: 11, 102: 12, 103: 13, 104: 14, 105: 15
    }
    
    # Coûts d'achat des caractéristiques
    COST_TABLE = {
        range(1, 91): 1, range(91, 96): 2, range(96, 101): 3, range(101, 106): 10
    }
    
    # Recommandations de caractéristiques par profession (basées sur le fichier markdown)
    PROFESSION_RECOMMENDATIONS = {
        "Animiste": {
            "principales": ["Raisonnement", "Volonté", "Constitution", "Agilité"],
            "description": "Privilégiez Raisonnement et Volonté pour la magie, Constitution pour la survie en nature"
        },
        "Aventurier": {
            "principales": ["Volonté", "Raisonnement", "Intuition", "Force", "Agilité"],
            "description": "Répartition équilibrée recommandée pour faire face à toutes situations"
        },
        "Barbare": {
            "principales": ["Constitution", "Agilité", "Force"],
            "description": "Maximisez Constitution et Force pour la survie et les dégâts au combat"
        },
        "Barde": {
            "principales": ["Volonté", "Présence", "Raisonnement", "Intuition"],
            "description": "Présence élevée pour l'influence, Volonté et Raisonnement pour la magie"
        },
        "Guérisseur": {
            "principales": ["Raisonnement", "Volonté", "Intuition"],
            "description": "Concentrez-vous sur Raisonnement et Volonté pour maximiser vos sorts de soin"
        },
        "Guerrier": {
            "principales": ["Force", "Constitution", "Agilité", "Rapidité"],
            "description": "Force et Constitution pour les dégâts et la survie, Agilité et Rapidité pour l'esquive"
        },
        "Guerrier-Mage": {
            "principales": ["Raisonnement", "Volonté", "Force", "Agilité"],
            "description": "Équilibrez les caractéristiques magiques et martiales"
        },
        "Mage": {
            "principales": ["Raisonnement", "Volonté", "Intuition"],
            "description": "Maximisez Raisonnement et Volonté pour la puissance magique"
        },
        "Mentaliste": {
            "principales": ["Raisonnement", "Volonté", "Intuition"],
            "description": "Similaire au Mage, avec un accent sur l'Intuition pour la perception"
        },
        "Moine": {
            "principales": ["Intuition", "Volonté", "Rapidité"],
            "description": "Intuition et Volonté pour le Ki, Rapidité pour l'esquive et l'initiative"
        },
        "Rôdeur": {
            "principales": ["Volonté", "Intuition", "Raisonnement", "Force", "Agilité"],
            "description": "Équilibrez magie de la nature et capacités martiales"
        },
        "Thaumaturge": {
            "principales": ["Raisonnement", "Volonté", "Intuition"],
            "description": "Focus sur les caractéristiques mentales pour la manipulation magique"
        },
        "Voleur": {
            "principales": ["Intuition", "Force", "Agilité"],
            "description": "Agilité pour la discrétion, Intuition pour la perception, Force pour l'escalade"
        }
    }
    
    def __init__(self):
        self.values = {name: 50 for name in self.NAMES}
        self.racial_bonuses = {name: 0 for name in self.NAMES}
    
    def get_description(self, characteristic: str) -> str:
        """Retourne la description d'une caractéristique"""
        return self.CHARACTERISTICS_INFO.get(characteristic, "")
    
    def get_bonus(self, characteristic: str) -> int:
        """Calcule le bonus final d'une caractéristique (valeur + bonus racial)"""
        base_value = self.values[characteristic]
        base_bonus = self._get_base_bonus(base_value)
        racial_bonus = self.racial_bonuses[characteristic]
        return base_bonus + racial_bonus
    
    def _get_base_bonus(self, value: int) -> int:
        """Récupère le bonus de base selon la table"""
        if value in [101, 102, 103, 104, 105]:
            return self.BONUS_TABLE[value]
        
        for value_range, bonus in self.BONUS_TABLE.items():
            if isinstance(value_range, range) and value in value_range:
                return bonus
        return 0
    
    def calculate_cost(self, values: Dict[str, int]) -> int:
        """Calcule le coût total des caractéristiques"""
        total_cost = 0
        
        for value in values.values():
            # Pour chaque caractéristique, on calcule le coût total depuis 0
            cost = 0
            
            # De 1 à 90 : 1 point par niveau
            if value <= 90:
                cost = value
            else:
                # D'abord, les 90 premiers points coûtent 90
                cost = 90
                
                # De 91 à 95 : 2 points par niveau
                if value <= 95:
                    cost += (value - 90) * 2
                else:
                    # Les 5 niveaux de 91 à 95 coûtent 10 points (5 × 2)
                    cost += 10
                    
                    # De 96 à 100 : 3 points par niveau
                    if value <= 100:
                        cost += (value - 95) * 3
                    else:
                        # Les 5 niveaux de 96 à 100 coûtent 15 points (5 × 3)
                        cost += 15
                        
                        # De 101 à 105 : 10 points par niveau
                        cost += (value - 100) * 10
            
            total_cost += cost
        
        return total_cost
    
    def validate_distribution(self, values: Dict[str, int], budget: int = 550) -> bool:
        """Valide la répartition des caractéristiques"""
        return self.calculate_cost(values) <= budget
    
    def get_profession_recommendations(self) -> Dict[str, Dict]:
        """Retourne les recommandations de caractéristiques par profession"""
        return self.PROFESSION_RECOMMENDATIONS
