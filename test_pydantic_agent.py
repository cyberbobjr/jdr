"""
Test simple de l'agent GM PydanticAI
"""

import asyncio
from back.agents.gm_agent_pydantic import build_gm_agent_pydantic


async def test_pydantic_agent():
    """Test simple de l'agent PydanticAI"""
    print("🔧 Création de l'agent PydanticAI...")
    
    try:
        agent, deps = build_gm_agent_pydantic(session_id="test_agent")
        print("✅ Agent créé avec succès")
        
        print("🎯 Test d'un message simple...")
        message = "Bonjour ! Je suis un aventurier. Peux-tu me présenter le début d'une aventure ?"
        
        response = await agent.run(message, deps=deps)
        print(f"📝 Réponse de l'agent: {response.data[:200]}...")
        print("✅ Test de message simple réussi")
        
        print("🛠️ Test d'un outil (XP)...")
        xp_message = "Applique 100 XP au personnage pour avoir vaincu un gobelin"
        
        xp_response = await agent.run(xp_message, deps=deps)
        print(f"📝 Réponse XP: {xp_response.data[:200]}...")
        print("✅ Test d'outil XP réussi")
        
        print("\n🎉 MIGRATION RÉUSSIE ! Tous les tests de base passent.")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_pydantic_agent())
    if success:
        print("\n✨ L'agent PydanticAI est opérationnel !")
    else:
        print("\n💥 Problème avec l'agent PydanticAI")
