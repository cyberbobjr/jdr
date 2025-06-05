import unittest
from back.agents.gm_agent import build_gm_agent
from haystack.components.agents import Agent

class TestGmAgent(unittest.TestCase):
    def test_build_gm_agent(self):
        """
        ### test_build_gm_agent
        **Description :** Vérifie que la fonction build_gm_agent retourne bien un Agent Haystack configuré.
        **Paramètres :** Aucun.
        **Retour :** None (assertions sur le type et les attributs de l'agent).
        """
        agent = build_gm_agent()
        self.assertIsInstance(agent, Agent)
        self.assertTrue(hasattr(agent, '_chat_history'))
        self.assertTrue(hasattr(agent, '_store'))

if __name__ == "__main__":
    unittest.main()
