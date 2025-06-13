"""
Agent GM utilisant PydanticAI pour la gestion des sessions de jeu de rôle.
Migration progressive de Haystack vers PydanticAI.
"""

import os
import pathlib
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pydantic_ai import Agent
import json

from back.services.session_service import SessionService
from back.storage.pydantic_jsonl_store import PydanticJsonlStore
from back.models.domain.character import Character
from back.agents.PROMPT import build_system_prompt

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
api_base_url = os.getenv("DEEPSEEK_API_BASE_URL")
api_model = os.getenv("DEEPSEEK_API_MODEL")


class GMAgentDependencies:
    """
    ### GMAgentDependencies
    **Description :** Classe contenant les dépendances nécessaires à l'agent GM PydanticAI.
    **Attributs :**
    - `session_id` (str) : Identifiant de session
    - `character_data` (Character) : Données du personnage (modèle typé)
    - `store` (PydanticJsonlStore) : Store pour l'historique des messages
    - `message_history` (List[ModelMessage]) : Historique des messages PydanticAI
    """
    
    def __init__(self, session_id: str, character_data: Optional[Character] = None):
        self.session_id = session_id
        self.character_data = character_data
        # Initialiser le store pour l'historique
        project_root = pathlib.Path(__file__).parent.parent.parent
        if not os.path.isabs(session_id):
            history_path = str(project_root / "data" / "sessions" / f"{session_id}.jsonl")
        else:
            history_path = session_id + ".jsonl"
        self.store = PydanticJsonlStore(history_path)    

def build_gm_agent_pydantic(session_id: str, scenario_name: str = "Les_Pierres_du_Passe.md", character_id: Optional[str] = None):
    """
    ### build_gm_agent_pydantic
    **Description :** Construit l'agent GM avec PydanticAI et retourne l'agent et ses dépendances.
    **Paramètres :**
    - `session_id` (str) : Identifiant de la session
    - `scenario_name` (str) : Nom du fichier scénario (utilisé uniquement lors de la création d'une nouvelle session)
    - `character_id` (Optional[str]) : ID du personnage pour créer une nouvelle session
    **Retour :** Tuple (Agent PydanticAI configuré, SessionService).
    """
    # Créer le service de session
    try:
        # Essayer de charger une session existante
        session = SessionService(session_id)
    except ValueError:
        # Si la session n'existe pas et qu'on a fourni un character_id, créer une nouvelle session
        if character_id:
            session = SessionService(session_id, character_id=character_id, scenario_name=scenario_name)
        else:
            raise ValueError(f"Session {session_id} n'existe pas et aucun character_id fourni pour la créer")
      # Utiliser le scénario de la session (on ne peut pas le changer)
    scenario_name = session.scenario_name
    
    # Construire le prompt système avec scénario et règles
    system_prompt = build_system_prompt(scenario_name)
    
    # Créer l'agent avec la configuration DeepSeek
    from pydantic_ai.models.openai import OpenAIModel
    from pydantic_ai.providers.openai import OpenAIProvider
    provider = OpenAIProvider(
        base_url=api_base_url,
        api_key=api_key
    )
    
    model = OpenAIModel(
        model_name=api_model,
        provider=provider
    )
    from back.tools.character_tools import character_apply_xp, character_add_gold, character_take_damage
    from back.tools.combat_tools import (
        roll_initiative_tool, perform_attack_tool, resolve_attack_tool, calculate_damage_tool, 
        end_combat_tool, end_turn_tool, check_combat_end_tool, apply_damage_tool, 
        get_combat_status_tool, start_combat_tool
    )
    from back.tools.inventory_tools import inventory_add_item, inventory_remove_item
    from back.tools.skill_tools import skill_check_with_character
    
    agent = Agent(
        model=model,
        system_prompt=system_prompt,
        deps_type=SessionService,
        tools=[
            character_apply_xp,
            character_add_gold,
            character_take_damage,
            inventory_add_item,
            inventory_remove_item,
            skill_check_with_character,
            # Outils de combat complets
            start_combat_tool,
            roll_initiative_tool,
            perform_attack_tool,
            resolve_attack_tool,
            calculate_damage_tool,
            apply_damage_tool,
            get_combat_status_tool,
            check_combat_end_tool,
            end_turn_tool,
            end_combat_tool
        ])
    
    return agent, session


def enrich_user_message_with_character(user_message: str, character_data: Dict[str, Any]) -> str:
    """
    ### enrich_user_message_with_character
    **Description :** Enrichit le message utilisateur avec les données du personnage.
    **Paramètres :**
    - `user_message` (str) : Message original de l'utilisateur
    - `character_data` (Dict[str, Any]) : Données du personnage
    **Retour :** Message enrichi avec contexte du personnage.
    """
    if not character_data:
        return user_message
    
    character_context = f"""<PERSONNAGE JOUEUR>
{json.dumps(character_data, indent=2, ensure_ascii=False)}
<PERSONNAGE JOUEUR>
"""
    return character_context + user_message


def enrich_user_message_with_combat_state(user_message: str, combat_state: Optional[Dict]) -> str:
    """
    ### enrich_user_message_with_combat_state
    **Description :** Enrichit le message avec l'état du combat actuel.
    **Paramètres :**
    - `user_message` (str) : Message original de l'utilisateur
    - `combat_state` (Optional[Dict]) : État du combat actuel
    **Retour :** Message enrichi avec contexte du combat.
    """
    if not combat_state or combat_state.get('status') != 'en_cours':
        return user_message
    
    current_participant = combat_state.get('current_participant', {})
    alive_participants = combat_state.get('alive_participants', [])
    
    combat_context = f"""[État du Combat Actuel:
Combat ID: {combat_state.get('combat_id', 'Inconnu')}
Round: {combat_state.get('round', 1)}
Tour de: {current_participant.get('nom', 'Inconnu')} (HP: {current_participant.get('hp', '?')})
Statut: {combat_state.get('status', 'en_cours')}
Participants vivants: {len(alive_participants)}
]

"""
    return combat_context + user_message


def auto_enrich_message_with_combat_context(session_id: str, user_message: str) -> str:
    """
    ### auto_enrich_message_with_combat_context
    **Description :** Enrichit automatiquement le message avec l'état du combat s'il y en a un actif.
    **Paramètres :**
    - `session_id` (str) : Identifiant de la session
    - `user_message` (str) : Message original de l'utilisateur
    **Retour :** Message enrichi avec contexte du combat si applicable.
    """
    try:
        from back.services.combat_state_service import CombatStateService
        from back.services.combat_service import CombatService
        
        combat_state_service = CombatStateService()
        combat_service = CombatService()
        
        # Vérifier s'il y a un combat actif
        if not combat_state_service.has_active_combat(session_id):
            return user_message
        
        # Charger l'état du combat
        combat_state = combat_state_service.load_combat_state(session_id)
        if not combat_state:
            return user_message
        
        # Obtenir le résumé enrichi
        combat_summary = combat_service.get_combat_summary(combat_state)
        
        # Ajouter des informations enrichies
        current_participant = None
        if combat_state.current_turn < len(combat_state.initiative_order):
            current_id = combat_state.initiative_order[combat_state.current_turn]
            current_participant = next((p for p in combat_state.participants if p['id'] == current_id), None)
        
        combat_summary["current_participant"] = current_participant
        combat_summary["alive_participants"] = [p for p in combat_state.participants if p.get('hp', 1) > 0]
        
        return enrich_user_message_with_combat_state(user_message, combat_summary)
        
    except Exception as e:
        # En cas d'erreur, retourner le message original sans crash
        return user_message

    # La gestion de l'historique (messages) doit être assurée directement par le store ou l'agent, et non par SessionService.
    # Les méthodes load_history, save_history et update_character_data ne sont plus utilisées ni exposées.
