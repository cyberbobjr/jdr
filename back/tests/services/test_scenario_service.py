import pytest
from back.services.scenario_service import ScenarioService
from back.models.schema import ScenarioStatus


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
    # Création d'un fichier scénario temporaire
    scenario_name = "test_scenario.md"
    scenario_content = "# Titre\nContenu du scénario."
    scenarios_dir = tmp_path / "scenarios"
    scenarios_dir.mkdir()
    scenario_path = scenarios_dir / scenario_name
    scenario_path.write_text(scenario_content, encoding="utf-8")

    # Patch le chemin de base pour pointer sur le dossier temporaire
    import os

    original_abspath = os.path.abspath

    def fake_abspath(path):
        if "data/scenarios" in path:
            return str(scenarios_dir)
        return original_abspath(path)

    os.path.abspath = fake_abspath

    # Test lecture OK
    result = ScenarioService.get_scenario_details(scenario_name)
    assert result == scenario_content

    # Test fichier inexistant
    try:
        ScenarioService.get_scenario_details("not_found.md")
        assert False, "Une exception aurait dû être levée pour un fichier inexistant."
    except FileNotFoundError:
        pass

    # Nettoyage
    os.path.abspath = original_abspath
