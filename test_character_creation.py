#!/usr/bin/env python3
"""
Test rapide pour vérifier que Character peut être créé avec les bonnes propriétés
"""
import sys
import uuid

# Ajouter le projet au path
sys.path.insert(0, '/Users/benjaminmarchand/IdeaProjects/jdr')

from back.models.domain.character import Character
from back.models.schema import RaceData, CultureData, CharacterStatus

def test_character_creation():
    race_data = RaceData(
        name="Humain",
        characteristic_bonuses={"Force": 1, "Constitution": 1},
        destiny_points=3,
        special_abilities=["Adaptabilité"],
        base_languages=["Langue commune"],
        optional_languages=["Elfe", "Nain"]
    )
    
    culture_data = CultureData(
        name="Royaume de Fer",
        description="Culture guerrière",
        skill_bonuses={"Survie": 2},
        characteristic_bonuses={},
        free_skill_points=10,
        traits="Courageux"
    )
    
    character = Character(
        id=uuid.uuid4(),
        name="Test Character",
        race=race_data,
        culture=culture_data,
        caracteristiques={
            "Force": 14,
            "Constitution": 13,
            "Dextérité": 12,
            "Intelligence": 10,
            "Perception": 11,
            "Charisme": 9
        },
        competences={
            "Armes blanches": 85,
            "Combat": 75
        },
        culture_bonuses={"Survie": 2},
        status=CharacterStatus.DONE
    )
    
    print("✅ Character créé avec succès !")
    print(f"Nom: {character.name}")
    print(f"Race: {character.race.name}")
    print(f"Culture: {character.culture.name}")
    print(f"HP: {character.hp}")
    print(f"Or: {character.gold}")
    print(f"Statut: {character.status}")
    
    # Test de la validation
    character_dict = character.model_dump()
    # Conversion UUID -> string pour le test de validation
    character_dict['id'] = str(character_dict['id'])
    
    is_valid = Character.is_character_finalized(character_dict)
    print(f"✅ Personnage valide: {is_valid}")

if __name__ == "__main__":
    test_character_creation()
