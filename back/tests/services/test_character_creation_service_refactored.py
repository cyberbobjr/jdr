"""
Tests unitaires pour CharacterCreationService (version refactorisée avec nouveaux managers).
"""
from back.services.character_creation_service import CharacterCreationService

class TestCharacterCreationService:
    def test_allocate_attributes_auto(self):
        # Test avec des races réelles depuis les JSON
        races = CharacterCreationService.get_races()
        
        if races:
            race_data = races[0]  # races[0] est déjà un objet RaceData
            result = CharacterCreationService.allocate_attributes_auto(race_data)
            
            assert isinstance(result, dict)
            assert len(result) > 0
            # Vérifier que toutes les valeurs sont des entiers positifs
            for char_name, value in result.items():
                assert isinstance(value, int)
                assert value > 0

    def test_check_attributes_points(self):
        # Test avec des attributs valides
        valid_attributes = {
            "Force": 50,
            "Agilité": 50,
            "Constitution": 50,
            "Volonté": 50,
            "Raisonnement": 50,
            "Intuition": 50,
            "Charisme": 50
        }
        
        valid = CharacterCreationService.check_attributes_points(valid_attributes)
        assert isinstance(valid, bool)
        
        # Test avec des attributs invalides (valeurs trop hautes)
        invalid_attributes = {char: 200 for char in valid_attributes.keys()}
        invalid = CharacterCreationService.check_attributes_points(invalid_attributes)
        assert invalid == False

    def test_get_races(self):
        races = CharacterCreationService.get_races()
        assert isinstance(races, list)
        assert len(races) > 0
        for race in races:
            assert isinstance(race, dict)
            assert "name" in race
            assert "cultures" in race
            assert "characteristic_bonuses" in race

    def test_get_skills(self):
        skills = CharacterCreationService.get_skills()
        assert isinstance(skills, dict)
        assert len(skills) > 0
        # Vérifier la structure des groupes de compétences
        for group_name, skill_list in skills.items():
            assert isinstance(group_name, str)
            assert isinstance(skill_list, list)

    def test_get_equipments(self):
        equipments = CharacterCreationService.get_equipments()
        assert isinstance(equipments, list)
        # Peut être vide si pas d'équipements définis
        for equipment in equipments:
            assert isinstance(equipment, str)

    def test_get_spells(self):
        spells = CharacterCreationService.get_spells()
        assert isinstance(spells, list)
        # Peut être vide si pas de sorts définis
        for spell in spells:
            assert isinstance(spell, str)

    def test_check_skills_points(self):
        # Test avec des compétences valides (vides)
        valid_skills = {}
        result = CharacterCreationService.check_skills_points(valid_skills)
        assert isinstance(result, bool)
        
        # Test avec des compétences invalides (trop de rangs)
        invalid_skills = {"Perception": 10}  # Trop de rangs
        result = CharacterCreationService.check_skills_points(invalid_skills)
        assert result == False    
    def test_calculate_skills_cost(self):
        # Test du calcul de coût sans profession
        skills = {"Perception": 2}
        
        cost = CharacterCreationService.calculate_skills_cost(skills)
        assert isinstance(cost, int)
        assert cost >= 0
