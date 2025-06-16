"""
Tests unitaires pour RacesManager (version corrigée).
"""
from back.models.domain.races_manager import RacesManager

class TestRacesManagerFixed:
    def test_races_manager_initialization(self):
        """Test l'initialisation du manager des races."""
        manager = RacesManager()
        assert manager is not None
        assert hasattr(manager, 'races_data')

    def test_get_all_races(self):
        """Test la récupération de toutes les races."""
        manager = RacesManager()
        races = manager.get_all_races()
        
        assert isinstance(races, list)
        assert len(races) > 0
        
        # Vérifier que tous les éléments sont des noms de races (strings)
        for race_name in races:
            assert isinstance(race_name, str)

    def test_get_race_names(self):
        """Test la récupération des noms de races."""
        manager = RacesManager()
        race_names = manager.get_race_names()
        
        assert isinstance(race_names, list)
        assert len(race_names) > 0
        
        # Vérifier que tous les éléments sont des strings
        for name in race_names:
            assert isinstance(name, str)

    def test_get_race_by_name(self):
        """Test la récupération d'une race par nom."""
        manager = RacesManager()
        races = manager.get_all_races()
        
        if races:
            first_race_name = races[0]
            race_data = manager.get_race_by_name(first_race_name)
            
            assert race_data is not None
            assert isinstance(race_data, dict)
            assert "name" in race_data
            assert race_data["name"] == first_race_name

    def test_get_cultures_for_race(self):
        """Test la récupération des cultures d'une race."""
        manager = RacesManager()
        races = manager.get_all_races()
        
        if races:
            first_race_name = races[0]
            cultures = manager.get_cultures_for_race(first_race_name)
            
            assert isinstance(cultures, list)
            # Peut être vide si la race n'a pas de cultures
            for culture in cultures:
                assert isinstance(culture, dict)

    def test_get_characteristic_bonuses(self):
        """Test la récupération des bonus de caractéristiques."""
        manager = RacesManager()
        races = manager.get_all_races()
        
        if races:
            first_race_name = races[0]
            bonuses = manager.get_characteristic_bonuses(first_race_name)
            
            assert isinstance(bonuses, dict)
            # Vérifier que toutes les valeurs sont des entiers
            for char_name, bonus in bonuses.items():
                assert isinstance(char_name, str)
                assert isinstance(bonus, int)

    def test_get_all_races_data(self):
        """Test la récupération de toutes les données de races."""
        manager = RacesManager()
        races_data = manager.get_all_races_data()
        
        assert isinstance(races_data, list)
        assert len(races_data) > 0
        
        # Vérifier la structure de base
        for race in races_data:
            assert isinstance(race, dict)
            assert "name" in race
