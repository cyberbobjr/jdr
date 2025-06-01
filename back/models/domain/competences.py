from typing import Optional, List, Dict
from .base import Skill

class Competences:
    """Gestion des compétences"""

    # SKILL_GROUPS enrichi avec descriptions (extraites du markdown)
    SKILL_GROUPS = {
        "Artistique": [
            {"name": "Comédie", "description": "Capacité à jouer un rôle et imiter les actions d'autres personnes. Ne modifie pas l'apparence physique."},
            {"name": "Danse", "description": "Art de maîtriser les mouvements rythmiques et de reproduire ou créer des danses."},
            {"name": "Imitation", "description": "Talent pour reproduire voix et sons de manière convaincante."},
            {"name": "Musique - Chant", "description": "Maîtrise de la voix pour le chant et l'interprétation musicale."},
            {"name": "Musique - Instrument", "description": "Capacité à jouer d'un instrument de musique spécifique."},
            {"name": "Narration", "description": "Art de conter des histoires de manière captivante et mémorable."}
        ],
        "Arts de la Magie": [
            {"name": "Accord", "description": "Permet de s'accorder aux objets magiques et d'utiliser leurs pouvoirs."},
            {"name": "Alchimie", "description": "Art de créer des potions et substances magiques à partir d'ingrédients spéciaux."},
            {"name": "Artisanat des Charmes", "description": "Création d'objets magiques mineurs et temporaires."},
            {"name": "Connaissance Ésotérique", "description": "Savoir approfondi sur des sujets mystiques et magiques spécifiques."},
            {"name": "Cristaux Runiques", "description": "Utilisation et création de runes magiques sur des pierres précieuses."},
            {"name": "Développement PP", "description": "Mesure la capacité à accumuler et gérer l'énergie magique."},
            {"name": "Divination", "description": "Art de prédire l'avenir par diverses méthodes mystiques."},
            {"name": "Incantation de Sort", "description": "Capacité à lancer des sorts spécifiques."},
            {"name": "Projection de Pouvoir", "description": "Permet de transférer l'énergie magique dans des objets."},
            {"name": "Runes", "description": "Lecture et création d'inscriptions magiques."},
            {"name": "Tours de Magie", "description": "Maîtrise de la magie mineure et des sorts basiques."}
        ],
        "Athlétique": [
            {"name": "Acrobatie", "description": "Capacité à effectuer des mouvements complexes et acrobatiques, incluant la gestion des chutes."},
            {"name": "Contorsion", "description": "Art de se contorsionner pour passer dans des espaces étroits ou se libérer de liens."},
            {"name": "Escalade", "description": "Aptitude à grimper sur diverses surfaces verticales."}
        ],
        "Combat": [
            {"name": "Arts Martiaux - Balayages", "description": "Techniques de combat basées sur les projections et les déséquilibres."},
            {"name": "Arts Martiaux - Coups", "description": "Combat à mains nues focalisé sur les coups directs et percutants."},
            {"name": "Arts Martiaux - Style", "description": "Maîtrise de formes spécifiques et avancées d'arts martiaux."},
            {"name": "Bagarre", "description": "Combat de rue sans règles utilisant tout ce qui est disponible."},
            {"name": "Maniement d'Arme", "description": "Capacité à utiliser efficacement un type d'arme spécifique."},
            {"name": "Style de Combat", "description": "Techniques avancées de combat avec des armes."}
        ],
        "Concentration": [
            {"name": "Concentration Ki", "description": "Canalisation de l'énergie interne pour améliorer les capacités physiques."},
            {"name": "Concentration Mentale", "description": "Focalisation mentale pour améliorer une action spécifique."},
            {"name": "Défense Ki", "description": "Utilisation de l'énergie interne pour améliorer ses défenses sans armure."},
            {"name": "Force Ki", "description": "Augmentation temporaire de la force physique par l'énergie interne."},
            {"name": "Vitesse Ki", "description": "Accélération des mouvements permettant des actions supplémentaires."}
        ],
        "Général": [
            {"name": "Artisanat", "description": "Capacité à créer et réparer des objets dans un domaine spécifique."},
            {"name": "Connaissance Générale", "description": "Savoir théorique et pratique dans un domaine spécifique."},
            {"name": "Communication par Signaux", "description": "Capacité à transmettre des messages via des moyens non-verbaux."},
            {"name": "Estimation", "description": "Évaluation de la valeur marchande d'objets et de biens."},
            {"name": "Herboristerie", "description": "Connaissance des plantes et de leurs utilisations."},
            {"name": "Langage", "description": "Maîtrise d'une langue spécifique, parlée et/ou écrite."},
            {"name": "Maîtrise des Cordes", "description": "Expertise dans la manipulation des cordes et la création de nœuds."},
            {"name": "Perception", "description": "Capacité à remarquer des détails et détecter des choses cachées."},
            {"name": "Résistance du Corps", "description": "Capacité à résister aux effets physiques et aux poisons."},
            {"name": "Résistance de l'Esprit", "description": "Protection contre les effets mentaux et psychiques."},
            {"name": "Résistance à la Magie", "description": "Capacité à résister aux effets magiques."},
            {"name": "Soins", "description": "Capacité à traiter les blessures et les maladies."}
        ],
        "Influence": [
            {"name": "Baratin", "description": "Art de la persuasion et de la manipulation verbale."},
            {"name": "Éloquence en Public", "description": "Capacité à s'adresser et influencer des groupes."},
            {"name": "Marchandage", "description": "Art de la négociation commerciale et des échanges."}
        ],
        "Nature": [
            {"name": "Survie & Cueillette", "description": "Capacité à survivre et trouver des ressources en milieu naturel."},
            {"name": "Dressage", "description": "Art de communiquer et contrôler les animaux."},
            {"name": "Élevage", "description": "Soins et éducation des animaux domestiques."},
            {"name": "Équitation", "description": "Maîtrise du contrôle d'une monture spécifique."},
            {"name": "Horticulture", "description": "Art de cultiver et faire prospérer les plantes."},
            {"name": "Navigation", "description": "Pilotage et maintenance des embarcations."},
            {"name": "Pistage", "description": "Capacité à suivre et interpréter des traces."},
            {"name": "Sens de l'Orientation", "description": "Aptitude à se repérer et trouver son chemin."}
        ],
        "Physique": [
            {"name": "Armure", "description": "Capacité à se mouvoir efficacement en armure."},
            {"name": "Endurance", "description": "Mesure de la résistance physique et des Points de Vie."},
            {"name": "Natation", "description": "Capacité à se déplacer et survivre dans l'eau."},
            {"name": "Saut", "description": "Capacité à effectuer des sauts en hauteur et en longueur."}
        ],
        "Subterfuge": [
            {"name": "Connaissance de la Rue", "description": "Familiarité avec le milieu criminel et ses codes."},
            {"name": "Crochetage & Pièges", "description": "Manipulation de serrures et désarmement de pièges."},
            {"name": "Déguisement", "description": "Art de modifier son apparence physique."},
            {"name": "Détroussage", "description": "Art du vol à la tire et du pickpocket."},
            {"name": "Dissimulation", "description": "Capacité à se cacher et passer inaperçu."},
            {"name": "Embuscade", "description": "Art de l'attaque surprise au corps à corps."},
            {"name": "Tir Embusqué", "description": "Maîtrise de l'attaque surprise à distance."},
            {"name": "Tours de Passe-passe", "description": "Prestidigitation et manipulation fine."},
            {"name": "Utilisation des Poisons", "description": "Connaissance et manipulation sécurisée des toxiques."}
        ]
    }

    def __init__(self):
        self.skills = {}
        self.ranks = {}  # rangs par compétence
        self.adolescence_ranks = {}  # rangs d'adolescence

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
