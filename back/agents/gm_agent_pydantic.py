"""
Agent GM utilisant PydanticAI pour la gestion des sessions de jeu de rôle.
Migration progressive de Haystack vers PydanticAI.
"""

from dotenv import load_dotenv
from pydantic_ai import Agent

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

from back.config import get_llm_config

# Configuration LLM centralisée
llm_config = get_llm_config()
api_key = llm_config["api_key"]
api_base_url = llm_config["api_endpoint"]
api_model = llm_config["model"]


def build_simple_gm_agent():
    """
    ### build_simple_gm_agent
    **Description :** Construit un agent GM simple sans contexte de session pour les tâches de génération (nom, background, description).
    **Paramètres :** Aucun
    **Retour :** Agent PydanticAI configuré sans dépendances de session.
    """
    # Prompt système simple pour la génération de contenu
    system_prompt = """Tu es un maître de jeu expert en jeu de rôle medieval-fantastique.
Tu aides à créer des personnages cohérents et immersifs.
Réponds toujours de manière concise et appropriée au contexte fourni."""
    
    # Créer l'agent avec la configuration DeepSeek
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider
    provider = OpenAIProvider(
        base_url=api_base_url,
        api_key=api_key
    )
    
    model = OpenAIChatModel(
        model_name=api_model,
        provider=provider
    )
    
    # Agent simple sans outils ni dépendances
    agent = Agent(
        model=model,
        system_prompt=system_prompt
    )
    
    return agent
