from back.models.domain.races import Races
from back.models.domain.base import RaceData, CultureData


def test_load_races_data_structure():
    """
    Teste que la méthode _load_races_data charge bien toutes les races et cultures depuis le JSON,
    et que la structure correspond aux dataclasses RaceData et CultureData.
    """
    races = Races()._load_races_data()
    assert isinstance(races, list)
    assert len(races) > 0
    for race in races:
        assert isinstance(race, RaceData)
        assert isinstance(race.name, str)
        assert isinstance(race.characteristic_bonuses, dict)
        assert isinstance(race.destiny_points, int)
        assert isinstance(race.special_abilities, list)
        assert isinstance(race.base_languages, list)
        assert isinstance(race.optional_languages, list)
        assert isinstance(race.cultures, list)
        for culture in race.cultures:
            assert isinstance(culture, CultureData)
            assert isinstance(culture.name, str)
            assert isinstance(culture.bonus, str)
            assert isinstance(culture.traits, str)


def test_races_data_content():
    """
    Vérifie que certaines races et cultures attendues sont bien présentes dans le JSON chargé.
    """
    races = Races()._load_races_data()
    race_names = [r.name for r in races]
    assert "Humains" in race_names
    assert "Elfes" in race_names
    humains = next(r for r in races if r.name == "Humains")
    culture_names = [c.name for c in humains.cultures]
    assert "Gondoriens" in culture_names
    assert "Rohirrim" in culture_names

