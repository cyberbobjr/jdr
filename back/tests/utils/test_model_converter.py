"""
Tests pour ModelConverter.
Vérifie la conversion cohérente entre objets Pydantic et dictionnaires.
"""

import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from back.utils.model_converter import ModelConverter
from back.models.schema import Item


class TestModelConverter:
    """Tests pour la classe ModelConverter."""

    def test_to_dict_with_pydantic_model(self):
        """Test la conversion d'un objet Pydantic en dict."""
        item = Item(id="sword", name="Épée", quantity=1, weight_kg=2.0)
        result = ModelConverter.to_dict(item)

        assert isinstance(result, dict)
        assert result["id"] == "sword"
        assert result["name"] == "Épée"
        assert result["quantity"] == 1
        assert result["weight_kg"] == 2.0

    def test_to_dict_with_dict(self):
        """Test la conversion d'un dict en dict (pas de changement)."""
        data = {"id": "sword", "name": "Épée"}
        result = ModelConverter.to_dict(data)

        assert result is data  # Doit retourner le même objet

    def test_to_dict_with_object_with_dict_method(self):
        """Test la conversion d'un objet avec méthode dict()."""
        class MockObject:
            def dict(self):
                return {"id": "shield", "name": "Bouclier"}

        obj = MockObject()
        result = ModelConverter.to_dict(obj)

        assert result == {"id": "shield", "name": "Bouclier"}

    def test_to_dict_with_standard_object(self):
        """Test la conversion d'un objet standard avec vars()."""
        class MockObject:
            def __init__(self):
                self.id = "armor"
                self.name = "Armure"

        obj = MockObject()
        result = ModelConverter.to_dict(obj)

        assert result == {"id": "armor", "name": "Armure"}

    def test_to_dict_with_invalid_object(self):
        """Test la conversion d'un objet invalide."""
        class MockObject:
            pass  # Pas de dict() ni model_dump()

        obj = MockObject()

        with pytest.raises(ValueError, match="Impossible de convertir"):
            ModelConverter.to_dict(obj)

    def test_to_json_with_pydantic_model(self):
        """Test la conversion en JSON d'un objet Pydantic."""
        item = Item(id="sword", name="Épée", quantity=1, weight_kg=2.0)
        result = ModelConverter.to_json(item)

        assert isinstance(result, str)
        # Vérifier que c'est du JSON valide
        import json
        parsed = json.loads(result)
        assert parsed["id"] == "sword"

    def test_to_json_with_dict(self):
        """Test la conversion en JSON d'un dict."""
        data = {"id": "sword", "name": "Épée"}
        result = ModelConverter.to_json(data)

        assert isinstance(result, str)
        import json
        parsed = json.loads(result)
        assert parsed == data