"""
Tests unitaires pour le router characters refactoré.
Teste les endpoints utilisant les nouveaux services spécialisés.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from back.routers.characters import router
from back.models.domain.character import Character
from back.services.character_data_service import CharacterDataService


# Créer un client de test
client = TestClient(router)


class TestCharactersRouterRefactored:
    """Tests pour le router characters refactoré avec les nouveaux services."""
    
    @pytest.fixture
    def mock_character(self):
        """Fixture pour un personnage de test."""
        return Character(
            id="test-character-123",
            name="Aragorn",
            race="Humain",
            culture="Gondor",
            status="complet",
            xp=100,
            gold=200.0,
            hp=85,
            caracteristiques={
                "Force": 85,
                "Constitution": 80,
                "Agilité": 70
            },
            competences={
                "Perception": 60,
                "Combat": 75
            },
            inventory=[],
            equipment=[],
            spells=[],
            culture_bonuses={
                "Combat": 5,
                "Influence": 3
            }
        )
    
    @pytest.fixture
    def mock_character_list(self, mock_character):
        """Fixture pour une liste de personnages."""
        character2 = mock_character.model_copy()
        character2.id = "test-character-456"
        character2.name = "Legolas"
        character2.race = "Elfe"
        return [mock_character, character2]
    
    def test_list_characters_success(self, mock_character_list):
        """Test de récupération réussie de la liste des personnages."""
        with patch.object(CharacterDataService, 'get_all_characters') as mock_get_all:
            mock_get_all.return_value = mock_character_list
            
            response = client.get("/")
            
            assert response.status_code == 200
            data = response.json()
            assert "characters" in data
            assert len(data["characters"]) == 2
            assert data["characters"][0]["name"] == "Aragorn"
            assert data["characters"][1]["name"] == "Legolas"
    
    def test_list_characters_empty(self):
        """Test de récupération de la liste des personnages quand elle est vide."""
        with patch.object(CharacterDataService, 'get_all_characters') as mock_get_all:
            mock_get_all.return_value = []
            
            response = client.get("/")
            
            assert response.status_code == 200
            data = response.json()
            assert "characters" in data
            assert len(data["characters"]) == 0
    
    def test_list_characters_error(self):
        """Test de gestion d'erreur lors de la récupération de la liste."""
        with patch.object(CharacterDataService, 'get_all_characters') as mock_get_all:
            mock_get_all.side_effect = Exception("Erreur de base de données")
            
            response = client.get("/")
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Erreur interne du serveur" in data["detail"]
    
    def test_get_character_detail_success(self, mock_character):
        """Test de récupération réussie des détails d'un personnage."""
        with patch.object(CharacterDataService, 'get_character_by_id') as mock_get_by_id:
            mock_get_by_id.return_value = mock_character
            
            response = client.get("/test-character-123")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "test-character-123"
            assert data["name"] == "Aragorn"
            assert data["race"] == "Humain"
            assert data["culture"] == "Gondor"
            assert data["xp"] == 100
            assert data["gold"] == 200.0
            assert data["hp"] == 85
    
    def test_get_character_detail_not_found(self):
        """Test de récupération d'un personnage qui n'existe pas."""
        with patch.object(CharacterDataService, 'get_character_by_id') as mock_get_by_id:
            mock_get_by_id.side_effect = FileNotFoundError("Personnage non trouvé")
            
            response = client.get("/non-existent-character")
            
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "Personnage non-existent-character non trouvé" in data["detail"]
    
    def test_get_character_detail_validation_error(self, mock_character):
        """Test de récupération avec erreur de validation."""
        with patch.object(CharacterDataService, 'get_character_by_id') as mock_get_by_id:
            # Simuler une erreur de validation Pydantic
            mock_get_by_id.side_effect = Exception("Erreur de validation")
            
            response = client.get("/invalid-character")
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "Erreur interne du serveur" in data["detail"]
    
    def test_character_detail_response_structure(self, mock_character):
        """Test de la structure de la réponse CharacterDetailResponse."""
        with patch.object(CharacterDataService, 'get_character_by_id') as mock_get_by_id:
            mock_get_by_id.return_value = mock_character
            
            response = client.get("/test-character-123")
            
            assert response.status_code == 200
            data = response.json()
            
            # Vérifier que tous les champs obligatoires sont présents
            required_fields = ["id", "name", "race", "culture", "status", "xp", "gold", "hp"]
            for field in required_fields:
                assert field in data
            
            # Vérifier les champs optionnels
            optional_fields = ["caracteristiques", "competences", "inventory", "equipment", "spells", "culture_bonuses"]
            for field in optional_fields:
                # Les champs doivent être présents mais peuvent être None
                assert field in data
    
    def test_character_list_response_structure(self, mock_character_list):
        """Test de la structure de la réponse CharacterListResponse."""
        with patch.object(CharacterDataService, 'get_all_characters') as mock_get_all:
            mock_get_all.return_value = mock_character_list
            
            response = client.get("/")
            
            assert response.status_code == 200
            data = response.json()
            
            # Vérifier la structure de base
            assert "characters" in data
            assert isinstance(data["characters"], list)
            assert len(data["characters"]) == 2
            
            # Vérifier que chaque personnage a les champs de base
            for character in data["characters"]:
                assert "id" in character
                assert "name" in character
                assert "race" in character
                assert "culture" in character


class TestCharactersRouterIntegration:
    """Tests d'intégration pour le router characters."""
    
    def test_router_registration(self):
        """Test que le router est correctement enregistré."""
        # Vérifier que le router a les routes attendues
        routes = [route for route in router.routes]
        assert len(routes) == 2  # GET / et GET /{character_id}
        
        # Vérifier les méthodes HTTP
        get_routes = [route for route in routes if route.methods == {"GET"}]
        assert len(get_routes) == 2
        
        # Vérifier les paths
        paths = [route.path for route in routes]
        assert "/" in paths
        assert "/{character_id}" in paths
