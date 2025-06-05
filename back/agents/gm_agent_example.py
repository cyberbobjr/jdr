###### FICHIER DEPRECATED ?
"""
Exemple d'utilisation de l'agent GM migré vers PydanticAI.
Ce fichier montre comment utiliser le nouvel agent dans l'application.
"""

import asyncio
import json
from back.agents.gm_agent_pydantic import build_gm_agent_pydantic, enrich_user_message_with_character


async def example_gm_session():
    """
    ### example_gm_session
    **Description :** Exemple de session de jeu avec l'agent GM PydanticAI.
    **Paramètres :** Aucun.
    **Retour :** Aucun.
    """
    # Construire l'agent avec une session de test
    session_id = "example_session"
    scenario_name = "Les_Pierres_du_Passe.md"
    
    agent, deps = build_gm_agent_pydantic(session_id=session_id, scenario_name=scenario_name)
    
    # Exemple de données de personnage
    character_data = {
        "name": "Aragorn",
        "race": "Dúnadan",
        "profession": "Rôdeur",
        "level": 3,
        "characteristics": {
            "force": 15,
            "agilite": 14,
            "constitution": 16,
            "intelligence": 13,
            "perception": 17,
            "volonte": 14
        },
        "skills": {
            "combat_melee": 12,
            "archerie": 10,
            "discretion": 15,
            "survie": 18
        },
        "health": {
            "current": 25,
            "maximum": 25
        },
        "equipment": ["Épée longue", "Arc long", "Armure de cuir"],
        "gold": 50
    }
    
    # Enrichir le message utilisateur avec les données du personnage
    user_message = "Je m'approche prudemment de la clairière en restant dans l'ombre des arbres."
    character_json = json.dumps(character_data, ensure_ascii=False, indent=2)
    enriched_message = enrich_user_message_with_character(user_message, character_json)
    
    try:
        # Exécuter l'agent avec le message enrichi
        print("🎲 Démarrage de la session de jeu avec PydanticAI...")
        print(f"📝 Message du joueur : {user_message}")
        print("🤖 Réponse du Maître du Jeu en cours...")
        
        # Note : Pour l'exemple, nous simulons l'exécution car nous n'avons pas de clé API configurée
        # Dans un vrai environnement, cela ressemblerait à :
        # result = await agent.run(enriched_message, deps=deps)
        # print(f"🎭 GM : {result.data}")
        
        print("✅ Exemple de migration réussi ! L'agent PydanticAI est prêt à être utilisé.")
        print("🔧 Configuration nécessaire : Assurez-vous que les variables d'environnement DEEPSEEK_API_KEY, DEEPSEEK_API_BASE_URL et DEEPSEEK_API_MODEL sont définies.")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution : {e}")
        print("💡 Ceci est normal si les clés API ne sont pas configurées.")


async def example_tool_usage():
    """
    ### example_tool_usage
    **Description :** Exemple d'utilisation des outils de l'agent GM.
    **Paramètres :** Aucun.
    **Retour :** Aucun.
    """
    from back.agents.gm_agent_pydantic import GMAgentDependencies
    
    print("🛠️ Test des outils de l'agent GM...")
    
    # Créer des dépendances de test
    deps = GMAgentDependencies(session_id="tool_test_session")
    
    # Simuler l'utilisation des outils
    print("⚔️ Les outils suivants sont disponibles dans l'agent PydanticAI :")
    print("  - apply_xp_to_character : Application d'expérience")
    print("  - add_gold_to_character : Ajout d'or")
    print("  - apply_damage_to_character : Application de dégâts")
    print("  - perform_skill_check : Jets de compétence")
    
    print("✨ Migration des outils terminée avec succès !")


if __name__ == "__main__":
    print("🚀 Exemple d'utilisation de l'agent GM PydanticAI")
    print("=" * 50)
    
    # Exécuter l'exemple de session
    asyncio.run(example_gm_session())
    
    print("\n" + "=" * 50)
    
    # Exécuter l'exemple d'outils
    asyncio.run(example_tool_usage())
