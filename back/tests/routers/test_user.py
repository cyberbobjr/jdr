import pytest
from fastapi.testclient import TestClient
from back.app import app
from back.services.settings_service import SettingsService
from back.models.domain.preferences import UserPreferences

client = TestClient(app)

class TestUserRouter:
    """
    Test suite for User Router (/user/preference).
    """

    @pytest.fixture(autouse=True)
    def clean_preferences(self):
        """Clean up preferences file before each test."""
        service = SettingsService()
        if service.preferences_file.exists():
            service.preferences_file.unlink()
        yield
        if service.preferences_file.exists():
            service.preferences_file.unlink()

    def test_get_preferences(self):
        """
        Test GET /user/preference
        """
        response = client.get("/user/preference")
        assert response.status_code == 200
        data = response.json()
        assert "language" in data
        assert data["language"] == "English"  # Default

    def test_update_preferences(self):
        """
        Test PUT /user/preference
        """
        payload = {"language": "French"}
        response = client.put("/user/preference", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "French"
        
        # Verify persistence via GET
        response = client.get("/user/preference")
        assert response.json()["language"] == "French"
