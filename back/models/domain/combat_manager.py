from back.utils.dice import roll_attack
from back.tools.skill_tools import skill_check

class CombatManager:
    """
    Gère les combats en suivant les règles définies dans la section 6 du guide.
    """

    def __init__(self):
        self.initiative_order = []
        self.current_turn = -1  # Initialisation à -1 pour que le premier appel à next_turn commence au premier personnage

    def roll_initiative(self, characters):
        """
        Calcule l'ordre d'initiative des personnages.

        Parameters:
        - characters (list): Liste des personnages avec leurs initiatives.

        Returns:
        - list: Liste triée des personnages avec leurs initiatives.
        """
        self.initiative_order = sorted(
            characters,
            key=lambda char: char['initiative'],
            reverse=True
        )
        return [{"name": char['name'], "initiative": char['initiative']} for char in self.initiative_order]

    def next_turn(self):
        """
        Passe au tour suivant dans l'ordre d'initiative.

        Returns:
        - object: Le personnage dont c'est le tour.
        """
        if not self.initiative_order:
            raise ValueError("L'ordre d'initiative n'a pas été défini.")

        self.current_turn = (self.current_turn + 1) % len(self.initiative_order)
        return self.initiative_order[self.current_turn]

    def reset_combat(self):
        """
        Réinitialise le combat.
        """
        self.initiative_order = []
        self.current_turn = -1  # Réinitialisation à -1

    def calculate_initiative(self, character_stats):
        """
        Calcule l'initiative d'un personnage en utilisant les outils appropriés.

        Parameters:
        - character_stats (dict): Statistiques du personnage (AGI, PER, etc.).

        Returns:
        - int: Résultat de l'initiative.
        """
        dice_result = roll_attack("1d20")
        initiative = dice_result + character_stats['AGI'] + (character_stats['PER'] // 3)
        return initiative

    def resolve_attack(self, attack_roll, defense_roll):
        """
        Résout une attaque en comparant les jets d'attaque et de défense.

        Parameters:
        - attack_roll (int): Jet d'attaque.
        - defense_roll (int): Jet de défense.

        Returns:
        - bool: True si l'attaque réussit, False sinon.
        """
        return attack_roll > defense_roll

    def calculate_damage(self, base_damage, modifiers):
        """
        Calcule les dégâts infligés en tenant compte des modificateurs.

        Parameters:
        - base_damage (int): Dégâts de base de l'attaque.
        - modifiers (dict): Modificateurs de dégâts (ex: bonus d'arme).

        Returns:
        - int: Dégâts finaux infligés.
        """
        damage = base_damage + modifiers.get('bonus', 0)
        return max(0, damage)

    def perform_attack(self, dice: str) -> int:
        """
        Effectue un jet d'attaque en utilisant l'outil roll_attack.

        Parameters:
        - dice (str): La notation des dés à lancer (ex: "1d20").

        Returns:
        - int: Le résultat du jet d'attaque.
        """
        return roll_attack(dice)
