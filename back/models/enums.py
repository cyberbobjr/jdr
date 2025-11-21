"""
Shared enumerations for the JdR project.
"""
from enum import Enum

class CharacterStatus(str, Enum):
    """Character lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    IN_GAME = "in_game"

class ItemType(str, Enum):
    """Possible item types"""
    MATERIAL = "Materiel"
    WEAPON = "Arme" 
    ARMOR = "Armure"
    FOOD = "Nourriture"
    MAGIC_ITEM = "Objet_Magique"
