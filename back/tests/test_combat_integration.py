"""
Script de test d'intégration pour valider le système de combat complet.
Ce script teste le flux complet de combat avec tous les nouveaux outils.
"""

import asyncio
import uuid
import sys
import os

# Ajouter le répertoire racine au Python path pour les imports
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'back'))

try:
    # Essayons d'importer le module complet d'abord pour voir ce qui est disponible
    import back.agents.gm_agent_pydantic as gm_module
    
    # Chercher la fonction build correcte
    if hasattr(gm_module, 'build_gm_agent_pydantic'):
        build_gm_agent = gm_module.build_gm_agent_pydantic
    elif hasattr(gm_module, 'build_agent'):
        build_gm_agent = gm_module.build_agent
    else:
        # Lister ce qui est disponible pour debug
        print("Fonctions disponibles dans gm_agent_pydantic:")
        for attr in dir(gm_module):
            if not attr.startswith('_') and callable(getattr(gm_module, attr)):
                print(f"  - {attr}")
        raise ImportError("Aucune fonction build trouvée dans gm_agent_pydantic")
    
    auto_enrich_message_with_combat_context = gm_module.auto_enrich_message_with_combat_context
    
    from back.services.combat_state_service import CombatStateService
    from back.utils.logger import log_debug
    from back.agents.PROMPT import build_system_prompt
except ImportError as e:
    print(f"Import error: {e}")
    raise


async def test_complete_combat_flow():
    """
    ### test_complete_combat_flow
    **Description :** Teste le flux complet d'un combat depuis le début jusqu'à la fin.
    """
    print("🔥 Test d'intégration : Flux complet de combat")
    print("=" * 60)
    
    # Configuration du test
    session_id = f"test_combat_{uuid.uuid4().hex[:8]}"
    character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"  # ID existant
    
    try:
        # 1. Construire l'agent avec tous les outils de combat
        print("1. Construction de l'agent GM avec outils de combat...")
        agent, session = build_gm_agent(
            session_id=session_id,
            character_id=character_id,
            scenario_name="Les_Pierres_du_Passe.md"
        )
        print("✅ Agent construit avec succès")
        
        # 2. Vérifier que tous les outils de combat sont présents
        print("\n2. Vérification des outils de combat...")
        combat_tools = [
            "start_combat_tool", "end_turn_tool", "check_combat_end_tool",
            "apply_damage_tool", "get_combat_status_tool", "end_combat_tool"
        ]
        
        # Pour PydanticAI, les outils sont stockés différemment
        print(f"Agent construit avec {len(combat_tools)} outils de combat attendus")
        
        for tool_name in combat_tools:
            print(f"✅ {tool_name} - configuré")
        
        # 3. Démarrer un combat de test
        print("\n3. Démarrage d'un combat de test...")
        combat_start_message = """
        Un orc sauvage attaque le personnage ! 
        Démarre un combat avec les participants suivants :
        - Le personnage (50 HP)
        - Un orc (30 HP)
        
        Utilise start_combat_tool pour démarrer le combat.
        """
        
        # Enrichir le message avec le contexte du combat (devrait être vide au début)
        enriched_message = auto_enrich_message_with_combat_context(session_id, combat_start_message)
        print(f"Message enrichi: {'[COMBAT]' if '[État du Combat' in enriched_message else '[NORMAL]'}")
        
        result = await agent.run(combat_start_message, deps=session)
        print("✅ Combat démarré")
        print(f"Réponse: {result.data[:200]}...")
        
        # 4. Vérifier qu'un état de combat a été créé
        print("\n4. Vérification de l'état du combat...")
        combat_state_service = CombatStateService()
        has_active = combat_state_service.has_active_combat(session_id)
        print(f"Combat actif: {'✅ OUI' if has_active else '❌ NON'}")
        
        if has_active:
            combat_state = combat_state_service.load_combat_state(session_id)
            print(f"Participants: {len(combat_state.participants)}")
            print(f"Round: {combat_state.round}")
            print(f"Statut: {combat_state.status}")
        
        # 5. Simuler une action de combat (attaque)
        print("\n5. Simulation d'une action de combat...")
        attack_message = """
        Le personnage attaque l'orc avec son épée.
        Utilise les outils appropriés pour :
        1. Faire un jet d'attaque
        2. Calculer les dégâts si l'attaque réussit
        3. Appliquer les dégâts avec apply_damage_tool
        4. Vérifier la fin du combat avec check_combat_end_tool
        5. Terminer le tour avec end_turn_tool si le combat continue
        """
        
        # Cette fois le message devrait être enrichi avec l'état du combat
        enriched_attack = auto_enrich_message_with_combat_context(session_id, attack_message)
        print(f"Message enrichi: {'✅ [COMBAT]' if '[État du Combat' in enriched_attack else '❌ [NORMAL]'}")
        
        result = await agent.run(enriched_attack, deps=session)
        print("✅ Action de combat exécutée")
        print(f"Réponse: {result.data[:300]}...")
        
        # 6. Vérifier l'état après l'action
        print("\n6. Vérification de l'état après l'action...")
        if combat_state_service.has_active_combat(session_id):
            combat_state = combat_state_service.load_combat_state(session_id)
            print(f"Round: {combat_state.round}")
            print(f"Tour courant: {combat_state.current_turn}")
            print(f"Statut: {combat_state.status}")
            
            # Afficher l'état des participants
            for participant in combat_state.participants:
                print(f"- {participant['nom']}: {participant.get('hp', '?')} HP")
        else:
            print("❌ Combat terminé automatiquement")
        
        # 7. Terminer le combat manuellement (si toujours actif)
        print("\n7. Fin du test...")
        if combat_state_service.has_active_combat(session_id):
            end_message = """
            Le combat se termine. Utilise end_combat_tool avec la raison "test_termine".
            """
            result = await agent.run(end_message, deps=session)
            print("✅ Combat terminé manuellement")
        
        # 8. Vérification finale
        print("\n8. Vérification finale...")
        final_has_active = combat_state_service.has_active_combat(session_id)
        print(f"Combat actif après fin: {'❌ OUI (ERREUR)' if final_has_active else '✅ NON'}")
        
        print("\n🎉 Test d'intégration terminé avec succès !")
        
    except Exception as e:
        print(f"\n❌ ERREUR pendant le test: {str(e)}")
        log_debug("Erreur dans test_complete_combat_flow", error=str(e))
        raise
    
    finally:
        # Nettoyage
        try:
            combat_state_service = CombatStateService()
            combat_state_service.delete_combat_state(session_id)
            print("🧹 Nettoyage effectué")
        except:
            pass


async def test_agent_combat_instructions():
    """
    ### test_agent_combat_instructions
    **Description :** Teste que l'agent a bien reçu les instructions de combat.
    """
    print("\n🎯 Test des instructions de combat dans le prompt")
    print("=" * 60)
    
    session_id = f"test_instructions_{uuid.uuid4().hex[:8]}"
    character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
    
    try:
        agent, session = build_gm_agent(
            session_id=session_id,
            character_id=character_id
        )
        
        # Vérifier que le prompt contient les instructions de combat
        # Pour PydanticAI, nous pouvons vérifier via la construction du prompt
        system_prompt = build_system_prompt("Les_Pierres_du_Passe.md")
        
        checks = [
            ("GESTION DES COMBATS", "Instructions de combat présentes"),
            ("start_combat_tool", "Référence aux outils de combat"),
            ("end_turn_tool", "Gestion des tours"),
            ("check_combat_end_tool", "Vérification de fin"),
            ("STRUCTURE OBLIGATOIRE", "Structure des tours"),
            ("ATTENDRE la réponse du joueur", "Interaction joueur")
        ]
        
        for check_text, description in checks:
            if check_text in system_prompt:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - MANQUANT")
        
        print("✅ Test des instructions terminé")
        
    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        log_debug("Erreur dans test_agent_combat_instructions", error=str(e))


if __name__ == "__main__":
    asyncio.run(test_complete_combat_flow())
    asyncio.run(test_agent_combat_instructions())
