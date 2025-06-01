import random

# Jets de dés

def roll_attack(dice: str) -> int:
    """
    Effectue un jet d'attaque en lançant les dés spécifiés.

    Parameters:
    - dice (str): La notation des dés à lancer (ex: "1d20").

    Returns:
    - int: Le résultat du jet d'attaque.
    """
    num, sides = map(int, dice.lower().split('d'))
    return sum(random.randint(1, sides) for _ in range(num))
