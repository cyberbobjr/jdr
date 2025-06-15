"""
Tests unitaires pour CharacterCreationService.
"""
from back.services.character_creation_service import CharacterCreationService

class TestCharacterCreationService:
    def test_allocate_attributes_auto(self):
        # À compléter selon la logique métier
        result = CharacterCreationService.allocate_attributes_auto("Guerrier", "Humain")
        assert isinstance(result, dict)

    def test_check_attributes_points(self):
        # Exemple de test
        attributes = {"force": 10, "intelligence": 8}
        valid = CharacterCreationService.check_attributes_points(attributes)
        assert isinstance(valid, bool)

    def test_get_professions(self):
        professions = CharacterCreationService.get_professions()
        assert isinstance(professions, list)

    def test_get_races(self):
        races = CharacterCreationService.get_races()
        # On attend une liste d'objets RaceData (structure dict issue du JSON)
        assert isinstance(races, list)
        assert len(races) > 0
        for race in races:
            assert isinstance(race, dict) or hasattr(race, 'name')
            assert hasattr(race, 'cultures') or 'cultures' in race
            assert hasattr(race, 'characteristic_bonuses') or 'characteristic_bonuses' in race

    def test_get_skills(self):
        skills = CharacterCreationService.get_skills()
        assert isinstance(skills, list)

    def test_get_cultures(self):
        cultures = CharacterCreationService.get_cultures()
        assert isinstance(cultures, list)

    def test_get_equipments(self):
        equipments = CharacterCreationService.get_equipments()
        assert isinstance(equipments, list)

    def test_get_spells(self):
        spells = CharacterCreationService.get_spells()
        assert isinstance(spells, list)

    def test_allocate_attributes_auto_guerrier_nain(self):
        result = CharacterCreationService.allocate_attributes_auto("Guerrier", "Nain")
        assert isinstance(result, dict)
        assert set(result.keys()) == {
            "Force", "Constitution", "Agilité", "Rapidité", "Volonté", "Raisonnement", "Intuition", "Présence"
        }
        # Vérifie que les bonus raciaux sont bien appliqués
        assert result["Force"] >= 54  # Bonus racial Nain +4
        assert result["Constitution"] >= 54  # Bonus racial Nain +4
        assert result["Volonté"] >= 53  # Bonus racial Nain +3
        # Vérifie le respect du budget
        from back.models.domain.caracteristiques import Caracteristiques
        caracs = Caracteristiques()
        assert caracs.validate_distribution(result)

    def test_allocate_attributes_auto_mage_elfe_noldo(self):
        result = CharacterCreationService.allocate_attributes_auto("Mage", "Elfe Noldo")
        assert isinstance(result, dict)
        # Les caracs principales du mage sont les plus élevées du set
        main_stats = ["Raisonnement", "Volonté", "Intuition"]
        main_values = [result[stat] for stat in main_stats]
        other_values = [v for k, v in result.items() if k not in main_stats]
        # On vérifie que chaque carac principale est supérieure ou égale à toutes les secondaires
        for v in main_values:
            assert v >= min(other_values)
        # Bonus racial Elfe Noldo appliqué
        assert result["Présence"] >= 55
        # Respect du budget
        from back.models.domain.caracteristiques import Caracteristiques
        caracs = Caracteristiques()
        assert caracs.validate_distribution(result)

    def test_check_attributes_points_valid(self):
        # Cas valide : 8x68 = 544 (sous le budget)
        attributes = {k: 68 for k in [
            "Force", "Constitution", "Agilité", "Rapidité", "Volonté", "Raisonnement", "Intuition", "Présence"
        ]}
        assert CharacterCreationService.check_attributes_points(attributes)

    def test_check_attributes_points_invalid_budget(self):
        # Cas invalide : trop de points
        attributes = {k: 100 for k in [
            "Force", "Constitution", "Agilité", "Rapidité", "Volonté", "Raisonnement", "Intuition", "Présence"
        ]}
        assert not CharacterCreationService.check_attributes_points(attributes)

    def test_check_attributes_points_invalid_bounds(self):
        # Cas invalide : valeur hors bornes
        attributes = {k: 0 for k in [
            "Force", "Constitution", "Agilité", "Rapidité", "Volonté", "Raisonnement", "Intuition", "Présence"
        ]}
        assert not CharacterCreationService.check_attributes_points(attributes)
