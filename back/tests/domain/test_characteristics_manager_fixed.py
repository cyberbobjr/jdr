"""
Tests pour CharacteristicsManager (adapté à l'implémentation existante)
"""

from back.models.domain.characteristics_manager import CharacteristicsManager

def test_characteristics_manager_initialization():
    """Test l'initialisation du manager des caractéristiques."""
    manager = CharacteristicsManager()
    assert manager is not None
    
    # Vérifier que les données sont chargées
    chars = manager.get_all_characteristics()
    assert len(chars) > 0

def test_get_all_characteristics():
    """Test la récupération de toutes les caractéristiques."""
    manager = CharacteristicsManager()
    chars = manager.get_all_characteristics()
    
    assert isinstance(chars, dict)
    assert len(chars) > 0
    
    # Vérifier la structure des données selon l'implémentation réelle
    for char_name, char_data in chars.items():
        assert isinstance(char_name, str)
        assert isinstance(char_data, dict)
        assert "name" in char_data
        assert "description" in char_data
        assert "value" in char_data
        assert "info" in char_data

def test_get_description():
    """Test la récupération de la description d'une caractéristique."""
    manager = CharacteristicsManager()
    
    # Test avec une caractéristique qui devrait exister
    description = manager.get_description("Force")
    assert isinstance(description, str)

def test_get_bonus():
    """Test le calcul des bonus selon la valeur."""
    manager = CharacteristicsManager()
    
    # Test avec des valeurs connues
    manager.set_value("Force", 50)
    bonus = manager.get_bonus("Force")
    assert isinstance(bonus, int)

def test_calculate_cost():
    """Test le calcul du coût total d'une distribution."""
    manager = CharacteristicsManager()
    
    # Distribution de test
    distribution = {
        "Force": 60,
        "Agilité": 70,
        "Constitution": 50,
        "Volonté": 80
    }
    
    total_cost = manager.calculate_cost(distribution)
    assert isinstance(total_cost, int)
    assert total_cost > 0

def test_set_value():
    """Test la définition d'une valeur de caractéristique."""
    manager = CharacteristicsManager()
    
    manager.set_value("Force", 70)
    chars = manager.get_all_characteristics()
    assert chars["Force"]["value"] == 70

def test_set_racial_bonus():
    """Test la définition d'un bonus racial."""
    manager = CharacteristicsManager()
    
    manager.set_racial_bonus("Force", 5)
    chars = manager.get_all_characteristics()
    assert chars["Force"]["racial_bonus"] == 5

def test_starting_points():
    """Test l'accès aux points de départ."""
    manager = CharacteristicsManager()
    
    assert hasattr(manager, 'starting_points')
    assert isinstance(manager.starting_points, int)
    assert manager.starting_points > 0
