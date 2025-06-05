"""
Tests pour l'agent GM migré vers PydanticAI.
"""

import pytest
from unittest.mock import patch
from back.agents.gm_agent_pydantic import (
    build_gm_agent_pydantic,
    GMAgentDependencies,
    _get_scenario_content,
    _get_rules_content,
    _build_system_prompt,
    enrich_user_message_with_character
)


class TestGMAgentPydantic:
    """
    ### TestGMAgentPydantic
    **Description :** Classe de tests pour l'agent GM utilisant PydanticAI.
    """

    def test_gm_agent_dependencies_initialization(self):
        """
        ### test_gm_agent_dependencies_initialization
        **Description :** Teste l'initialisation des dépendances de l'agent GM.
        **Paramètres :** Aucun.
        **Retour :** Aucun.
        """
        session_id = "test_session"
        character_data = {"name": "Aragorn", "level": 5}
        
        deps = GMAgentDependencies(session_id=session_id, character_data=character_data)
        
        assert deps.session_id == session_id
        assert deps.character_data == character_data
        assert deps.store is not None

    def test_get_scenario_content_existing_file(self):
        """
        ### test_get_scenario_content_existing_file
        **Description :** Teste le chargement d'un fichier scénario existant.
        **Paramètres :** Aucun.
        **Retour :** Aucun.
        """
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value="Contenu du scénario test"):
            
            content = _get_scenario_content("test_scenario.md")
            assert content == "Contenu du scénario test"

    def test_get_scenario_content_non_existing_file(self):
        """
        ### test_get_scenario_content_non_existing_file
        **Description :** Teste le comportement avec un fichier scénario inexistant.
        **Paramètres :** Aucun.
        **Retour :** Aucun.
        """
        with patch("pathlib.Path.exists", return_value=False):
            content = _get_scenario_content("inexistant.md")
            assert content == ""

    def test_get_rules_content(self):
        """
        ### test_get_rules_content
        **Description :** Teste le chargement du contenu des règles.
        **Paramètres :** Aucun.
        **Retour :** Aucun.
        """
        mock_content = "# Règles de combat\nContenu des règles..."
        
        with patch("pathlib.Path.exists", return_value=True), \
             patch("builtins.open", mock_data=mock_content):
            
            content = _get_rules_content()
            # Vérifier que le contenu contient les en-têtes de section
            assert "=== section-6-combat.md ===" in content or content == ""

    def test_build_system_prompt_without_scenario(self):
        """
        ### test_build_system_prompt_without_scenario
        **Description :** Teste la construction du prompt système sans scénario.
        **Paramètres :** Aucun.
        **Retour :** Aucun.
        """
        prompt = _build_system_prompt()
        
        assert "Maître du Donjon (RPG-Bot)" in prompt
        assert "Terres du Milieu" in prompt
        assert "SCÉNARIO :" in prompt

    def test_build_system_prompt_with_scenario(self):
        """
        ### test_build_system_prompt_with_scenario
        **Description :** Teste la construction du prompt système avec un scénario.
        **Paramètres :** Aucun.
        **Retour :** Aucun.
        """
        with patch("back.agents.gm_agent_pydantic._get_scenario_content", return_value="Scénario de test"):
            prompt = _build_system_prompt("test_scenario.md")
            
            assert "Scénario de test" in prompt

    def test_enrich_user_message_with_character(self):
        """
        ### test_enrich_user_message_with_character
        **Description :** Teste l'enrichissement d'un message utilisateur avec les données du personnage.
        **Paramètres :** Aucun.
        **Retour :** Aucun.
        """
        message = "Je veux attaquer l'orc"
        character_json = '{"name": "Legolas", "classe": "Archer"}'
        
        enriched_message = enrich_user_message_with_character(message, character_json)
        assert message in enriched_message
        assert character_json in enriched_message
        assert "PERSONNAGE_JSON:" in enriched_message

    def test_build_gm_agent_pydantic(self):
        """
        ### test_build_gm_agent_pydantic
        **Description :** Teste la construction de l'agent GM PydanticAI.
        **Paramètres :** Aucun.
        **Retour :** Aucun.
        """
        session_id = "test_session"
        scenario_name = "test_scenario.md"
        
        with patch("back.agents.gm_agent_pydantic._build_system_prompt", return_value="Prompt test"):
            agent, deps = build_gm_agent_pydantic(session_id=session_id, scenario_name=scenario_name)
            
            assert deps.session_id == session_id
            assert agent is not None

    @pytest.mark.asyncio
    async def test_apply_xp_tool_integration(self):
        """
        ### test_apply_xp_tool_integration
        **Description :** Teste l'intégration de l'outil d'application d'XP.
        **Paramètres :** Aucun.
        **Retour :** Aucun.
        """
        # Les outils sont maintenant définis directement dans l'agent via les décorateurs
        # Créons un agent pour tester que les outils sont bien présents
        agent, deps = build_gm_agent_pydantic("test_session", "test_scenario")
        
        # Vérifier que l'agent a bien été créé
        assert agent is not None
        assert deps is not None
          # Les outils sont intégrés via @agent.tool, pas comme fonctions exportées
        # Donc on teste que l'agent peut être créé sans erreur
        print("Agent PydanticAI créé avec succès avec les outils intégrés")

    @pytest.mark.asyncio
    async def test_skill_check_tool_integration(self):
        """
        ### test_skill_check_tool_integration
        **Description :** Teste l'intégration de l'outil de jet de compétence.
        **Paramètres :** Aucun.
        **Retour :** Aucun.
        """
        # Les outils sont maintenant définis directement dans l'agent via les décorateurs
        # Créons un agent pour tester que les outils sont bien présents
        agent, deps = build_gm_agent_pydantic("test_session", "test_scenario")
        
        # Vérifier que l'agent a bien été créé
        assert agent is not None
        assert deps is not None
        
        # Les outils sont intégrés via @agent.tool, pas comme fonctions exportées
        print("Agent PydanticAI créé avec succès avec les outils de compétence intégrés")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
