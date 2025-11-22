"""
Script de debug pour diagnostiquer le problème avec les outils de combat PydanticAI
"""

import asyncio
from back.agents.generic_agent import build_gm_agent_pydantic
from back.services.combat_state_service import CombatStateService
import uuid


async def debug_tools():
    """Teste les outils de combat avec des messages très explicites"""
    print("🔍 DEBUG: Test des outils de combat PydanticAI")
    print("=" * 60)
    
    session_id = f"debug_{uuid.uuid4().hex[:8]}"
    character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
    
    try:
        # 1. Construire l'agent
        print("1. Construction de l'agent...")
        agent, session = build_gm_agent_pydantic(
            session_id=session_id,
            character_id=character_id
        )
        print("✅ Agent construit")
        
        # 2. Test simple : demander à l'agent de lister ses outils
        print("\n2. Test: Demande à l'agent de lister ses outils...")
        list_tools_message = """
        Peux-tu me dire quels outils tu as à disposition pour gérer les combats ? 
        Utilise simplement tes connaissances, sans appeler d'outils.
        """
        
        result = await agent.run(list_tools_message, deps=session)
        print(f"Réponse: {result.output}")
        
        # 3. Test explicite : démarrer un combat avec un message très clair
        print("\n3. Test: Démarrage explicite d'un combat...")
        start_message = """
        INSTRUCTION TRÈS CLAIRE: Tu DOIS utiliser l'outil start_combat_tool maintenant.
        
        Démarre un combat avec ces participants exactement :
        [
            {"nom": "Héros", "hp": 50, "initiative": 15},
            {"nom": "Orc", "hp": 30, "initiative": 12}
        ]
        
        UTILISE start_combat_tool IMMÉDIATEMENT avec cette liste.
        """
        
        result = await agent.run(start_message, deps=session)
        print(f"Réponse: {result.output}")
        
        # 4. Vérifier si un combat a été créé
        print("\n4. Vérification de l'état du combat...")
        combat_state_service = CombatStateService()
        has_combat = combat_state_service.has_active_combat(session_id)
        print(f"Combat actif: {'✅ OUI' if has_combat else '❌ NON'}")
        
        if has_combat:
            print("✅ L'outil start_combat_tool a fonctionné !")
            combat_state = combat_state_service.load_combat_state(session_id)
            print(f"Combat ID: {combat_state.combat_id}")
            print(f"Participants: {len(combat_state.participants)}")
            
            # 5. Test end_combat_tool
            print("\n5. Test: Fin explicite du combat...")
            end_message = f"""
            INSTRUCTION TRÈS CLAIRE: Tu DOIS utiliser l'outil end_combat_tool maintenant.
            
            Termine le combat avec:
            - combat_id: "{combat_state.combat_id}"
            - reason: "test_debug_terminé"
            
            UTILISE end_combat_tool IMMÉDIATEMENT avec ces paramètres.
            """
            
            result = await agent.run(end_message, deps=session)
            print(f"Réponse: {result.output}")
            
            # Vérifier si le combat est terminé
            final_has_combat = combat_state_service.has_active_combat(session_id)
            print(f"Combat actif après end_combat_tool: {'❌ ÉCHEC' if final_has_combat else '✅ TERMINÉ'}")
        else:
            print("❌ L'outil start_combat_tool n'a pas fonctionné")
        
        print("\n🎯 Debug terminé")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Nettoyage
        try:
            combat_state_service = CombatStateService()
            combat_state_service.delete_combat_state(session_id)
            print("🧹 Nettoyage effectué")
        except:
            pass


if __name__ == "__main__":
    asyncio.run(debug_tools())
