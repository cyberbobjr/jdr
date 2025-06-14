import pytest
from back.services.scenario_service import ScenarioService
from back.models.schema import ScenarioStatus
from unittest.mock import patch


def test_list_scenarios_available():
    # Appel de la méthode list_scenarios
    scenarios = ScenarioService.list_scenarios()
    # Vérifier qu'au moins un scénario disponible existe
    available = [s for s in scenarios if s.status == "available"]
    assert available, "Il devrait y avoir au moins un scénario disponible"
    # Vérifier le type des éléments
    assert all(isinstance(s, ScenarioStatus) for s in available)


@pytest.mark.usefixtures("tmp_path")
def test_get_scenario_details(tmp_path):
    # Création d'un fichier scénario temporaire dans un dossier unique
    scenario_name = "test_scenario_tmp.md"
    scenario_content = "# Titre\nContenu du scénario."
    scenarios_dir = tmp_path / "scenarios"
    scenarios_dir.mkdir()
    scenario_path = scenarios_dir / scenario_name
    scenario_path.write_text(scenario_content, encoding="utf-8")

    # Patch get_data_dir utilisé dans scenario_service (et non dans config)
    with patch("back.services.scenario_service.get_data_dir", return_value=str(tmp_path)):
        # Test lecture OK
        result = ScenarioService.get_scenario_details(scenario_name)
        assert result == scenario_content

        # Test fichier inexistant
        with pytest.raises(FileNotFoundError):
            ScenarioService.get_scenario_details("not_found.md")
