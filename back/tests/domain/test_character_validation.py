"""
Test unitaire pour la méthode is_character_finalized
"""
import uuid
from back.models.domain.character import Character

class TestCharacterValidation:
    """Tests pour la méthode de validation de Character."""
    
    def test_is_character_finalized_valid_character(self):
        """Teste la validation avec un personnage complet et valide."""
        valid_character = {
            "id": str(uuid.uuid4()),
            "name": "Guerrier",
            "race": {
                "name": "Humain",
                "characteristic_bonuses": {"Force": 1},
                "destiny_points": 3,
                "special_abilities": [],
                "base_languages": ["Langue commune"],
                "optional_languages": []
            },
            "culture": {
                "name": "Royaume de Fer",
            },
            "caracteristiques": {
                "Force": 14,
                "Constitution": 13,
                "Dextérité": 12,
                "Intelligence": 10,
                "Perception": 11,
                "Charisme": 9
            },
            "competences": {
                "Armes blanches": 85,
                "Combat": 75
            },
            "culture_bonuses": {"Survie": 2}
        }
        
        assert Character.is_character_finalized(valid_character) is True
    
    def test_is_character_finalized_missing_required_field(self):
        """Teste la validation avec un champ obligatoire manquant."""
        invalid_character = {
            "id": str(uuid.uuid4()),
            "name": "Guerrier",
            "race": {
                "name": "Humain",
            },
            # culture manquante
            "caracteristiques": {
                "Force": 14,
                "Constitution": 13,
                "Dextérité": 12,
                "Intelligence": 10,
                "Perception": 11,
                "Charisme": 9
            },
            "competences": {
                "Armes blanches": 85,
            },
            "culture_bonuses": {}
        }
        
        assert Character.is_character_finalized(invalid_character) is False
    
    def test_is_character_finalized_incomplete_characteristics(self):
        """Teste la validation avec des caractéristiques incomplètes."""
        invalid_character = {
            "id": str(uuid.uuid4()),
            "name": "Guerrier",
            "race": {
                "name": "Humain",
            },
            "culture": {
                "name": "Royaume de Fer",
            },
            "caracteristiques": {
                "Force": 14,
                # Manque Constitution, Dextérité, etc.
            },
            "competences": {
                "Armes blanches": 85,
            },
            "culture_bonuses": {}
        }
        
        assert Character.is_character_finalized(invalid_character) is False
    
    def test_is_character_finalized_empty_competences(self):
        """Teste la validation avec des compétences vides."""
        invalid_character = {
            "id": str(uuid.uuid4()),
            "name": "Guerrier",
            "race": {
                "name": "Humain",
            },
            "culture": {
                "name": "Royaume de Fer",
            },
            "caracteristiques": {
                "Force": 14,
                "Constitution": 13,
                "Dextérité": 12,
                "Intelligence": 10,
                "Perception": 11,
                "Charisme": 9
            },
            "competences": {},  # Vide
            "culture_bonuses": {}
        }
        
        assert Character.is_character_finalized(invalid_character) is False
    
    def test_is_character_finalized_race_without_name(self):
        """Teste la validation avec une race sans nom."""
        invalid_character = {
            "id": str(uuid.uuid4()),
            "name": "Guerrier",
            "race": {
                # pas de "name"
            },
            "culture": {
                "name": "Royaume de Fer",
            },
            "caracteristiques": {
                "Force": 14,
                "Constitution": 13,
                "Dextérité": 12,
                "Intelligence": 10,
                "Perception": 11,
                "Charisme": 9
            },
            "competences": {
                "Armes blanches": 85,
            },
            "culture_bonuses": {}
        }
        
        assert Character.is_character_finalized(invalid_character) is False
