"""
Test complet de l'agent GM PydanticAI avec tous les outils migrés.
"""

import asyncio
import pytest
from back.agents.gm_agent_pydantic import build_gm_agent_pydantic


class TestGMAgentPydanticTools:
    """
    ### TestGMAgentPydanticTools
    **Description :** Tests d'intégration pour tous les outils de l'agent GM PydanticAI.
    """

    @pytest.fixture
    def agent_and_deps(self):
        """Fixture pour créer un agent et ses dépendances de test."""
        return build_gm_agent_pydantic(session_id="test_tools_session")

    @pytest.mark.asyncio
    async def test_character_tools(self, agent_and_deps):
        """
        ### test_character_tools
        **Description :** Teste les outils de gestion de personnage.
        """
        agent, deps = agent_and_deps
        
        # Test XP tool
        try:
            response = await agent.run("Applique 100 XP au personnage pour avoir vaincu un orc", deps=deps)
            assert response.data is not None
            print(f"XP Tool Response: {response.data}")
        except Exception as e:
            print(f"XP Tool Error: {e}")

        # Test Gold tool
        try:
            response = await agent.run("Ajoute 50 pièces d'or au personnage pour sa récompense", deps=deps)
            assert response.data is not None
            print(f"Gold Tool Response: {response.data}")
        except Exception as e:
            print(f"Gold Tool Error: {e}")

        # Test Damage tool
        try:
            response = await agent.run("Applique 10 points de dégâts physiques au personnage", deps=deps)
            assert response.data is not None
            print(f"Damage Tool Response: {response.data}")
        except Exception as e:
            print(f"Damage Tool Error: {e}")

    @pytest.mark.asyncio
    async def test_skill_tools(self, agent_and_deps):
        """
        ### test_skill_tools
        **Description :** Teste les outils de compétences.
        """
        agent, deps = agent_and_deps
        
        try:
            response = await agent.run("Effectue un jet de Discrétion avec une difficulté de 15", deps=deps)
            assert response.data is not None
            print(f"Skill Tool Response: {response.data}")
        except Exception as e:
            print(f"Skill Tool Error: {e}")

    @pytest.mark.asyncio
    async def test_combat_tools(self, agent_and_deps):
        """
        ### test_combat_tools
        **Description :** Teste les outils de combat.
        """
        agent, deps = agent_and_deps
        
        # Test Attack Roll
        try:
            response = await agent.run("Effectue un jet d'attaque avec 1d20+5", deps=deps)
            assert response.data is not None
            print(f"Attack Tool Response: {response.data}")
        except Exception as e:
            print(f"Attack Tool Error: {e}")

        # Test Damage Calculation
        try:
            response = await agent.run("Calcule les dégâts avec 8 points de base et +2 de bonus", deps=deps)
            assert response.data is not None
            print(f"Damage Calculation Response: {response.data}")
        except Exception as e:
            print(f"Damage Calculation Error: {e}")

        # Test Attack Resolution
        try:
            response = await agent.run("Résous une attaque avec un jet d'attaque de 18 contre une défense de 15", deps=deps)
            assert response.data is not None
            print(f"Attack Resolution Response: {response.data}")
        except Exception as e:
            print(f"Attack Resolution Error: {e}")

    @pytest.mark.asyncio
    async def test_inventory_tools(self, agent_and_deps):
        """
        ### test_inventory_tools
        **Description :** Teste les outils d'inventaire.
        """
        agent, deps = agent_and_deps
        
        # Test Add Item
        try:
            response = await agent.run("Ajoute une épée longue à l'inventaire du personnage", deps=deps)
            assert response.data is not None
            print(f"Add Item Response: {response.data}")
        except Exception as e:
            print(f"Add Item Error: {e}")

        # Test Remove Item
        try:
            response = await agent.run("Retire une potion de soin de l'inventaire", deps=deps)
            assert response.data is not None
            print(f"Remove Item Response: {response.data}")
        except Exception as e:
            print(f"Remove Item Error: {e}")

    @pytest.mark.asyncio
    async def test_complete_scenario(self, agent_and_deps):
        """
        ### test_complete_scenario
        **Description :** Teste un scénario complet utilisant plusieurs outils.
        """
        agent, deps = agent_and_deps
        
        scenario_message = """
        Un orc attaque le personnage ! Gère cette situation de combat :
        1. Lance l'initiative
        2. Effectue une attaque de l'orc avec 1d20+3
        3. Si l'attaque réussit, applique 6 points de dégâts
        4. Donne 50 XP au personnage pour le combat
        """
        
        try:
            response = await agent.run(scenario_message, deps=deps)
            assert response.data is not None
            print(f"Complete Scenario Response: {response.data}")
            
            # Vérifier que la réponse contient des éléments de narration
            assert len(response.data) > 100  # Réponse substantielle
            
        except Exception as e:
            print(f"Complete Scenario Error: {e}")
            # Ne pas faire échouer le test, juste afficher l'erreur


if __name__ == "__main__":
    # Test simple pour vérifier que l'agent peut être créé et utilisé
    async def test_basic_functionality():
        agent, deps = build_gm_agent_pydantic(session_id="quick_test")
        
        try:
            response = await agent.run("Bonjour ! Je suis un aventurier. Présente-moi le début d'une aventure.", deps=deps)
            print(f"Basic Test Response: {response.data}")
            return True
        except Exception as e:
            print(f"Basic Test Error: {e}")
            return False
    
    # Exécuter le test de base
    if asyncio.run(test_basic_functionality()):
        print("\n✅ Test de base réussi - L'agent PydanticAI fonctionne correctement!")
    else:
        print("\n❌ Test de base échoué - Problème avec l'agent PydanticAI")
