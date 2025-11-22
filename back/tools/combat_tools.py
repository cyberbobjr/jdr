from pydantic_ai import RunContext
from back.utils.logger import log_debug, log_error
from back.services.combat_service import CombatService
from back.services.combat_state_service import CombatStateService
from back.services.game_session_service import GameSessionService
from back.models.domain.combat_state import CombatantType
import uuid

combat_service = CombatService()
combat_state_service = CombatStateService()

def start_combat_tool(ctx: RunContext[GameSessionService], location: str, description: str, participants: list[dict]) -> dict:
    """
    Starts a new combat with the given participants.

    Args:
        location (str): Location of the combat.
        description (str): Description of the combat setup.
        participants (list[dict]): List of participants. Each participant should have:
            - name (str): Name of the participant.
            - role (str): "enemy" or "ally".
            - archetype (str): Description/Class (e.g., "Orc Warrior", "Goblin Archer").
            - level (int, optional): Level of the NPC if known/defined in scenario.
            - is_unique_npc (bool, optional): If this is a specific named NPC from the scenario.

    Returns:
        dict: Simplified CombatSeedPayload (combat_id, message).
    """
    log_debug("Tool start_combat_tool called", tool="start_combat_tool", location=location, description=description, participants=participants)
    
    try:
        session_id = uuid.UUID(ctx.deps.session_id)
        
        # Check that there's no active combat already
        if combat_state_service.has_active_combat(session_id):
            # If active combat exists, we might want to return it or error.
            # For robustness, let's error but provide info.
            return {"error": "A combat is already in progress for this session"}
        
        # Ensure player is included in participants
        has_player = any(p.get('role') == 'ally' or p.get('camp') == 'player' or p.get('is_player') for p in participants)
        if not has_player:
            participants.append({
                "name": "Player",
                "role": "ally",
                "camp": "player",
                "is_player": True
            })

        # Prepare participants data for service
        processed_participants = []
        for p in participants:
            p_data = p.copy()
            # Ensure camp is set based on role
            if 'role' in p_data:
                p_data['camp'] = 'player' if p_data['role'] == 'ally' else 'enemy'
            elif 'camp' not in p_data:
                p_data['camp'] = 'enemy'
            
            # Ensure ID
            if 'id' not in p_data:
                p_data['id'] = str(uuid.uuid4())
                
            processed_participants.append(p_data)
            
        # Create the initial combat state
        # Pass session_service (ctx.deps) to resolve player character
        combat_state = combat_service.start_combat(processed_participants, session_service=ctx.deps)
        
        # Save the initial state
        combat_state_service.save_combat_state(session_id, combat_state)
        
        # Return simplified payload for Narrative Agent
        return {
            "combat_id": str(combat_state.id),
            "message": f"Combat started at {location}. {description}"
        }
        
    except Exception as e:
        log_error(f"Error in start_combat_tool: {e}")
        return {"error": str(e)}

def execute_attack_tool(ctx: RunContext[GameSessionService], attacker_id: str, target_id: str) -> dict:
    """
    Executes a full attack action from one combatant to another.
    Handles weapon selection, attack roll, damage roll, and application.

    Args:
        attacker_id (str): ID of the attacker.
        target_id (str): ID of the target.

    Returns:
        dict: Result of the attack (message, updated state summary).
    """
    log_debug("Tool execute_attack_tool called", tool="execute_attack_tool", attacker_id=attacker_id, target_id=target_id)
    
    try:
        session_id = uuid.UUID(ctx.deps.session_id)
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if not combat_state:
            return {"error": "No active combat found"}
            
        # Execute attack
        combat_state, result_message = combat_service.execute_attack(combat_state, attacker_id, target_id)
        
        # Check for combat end
        is_ended = combat_service.check_combat_end(combat_state)
        auto_end_info = None
        
        if is_ended:
            players_alive = any(p.type == CombatantType.PLAYER and p.is_alive() for p in combat_state.participants)
            enemies_alive = any(p.type == CombatantType.NPC and p.is_alive() for p in combat_state.participants)
            
            if not players_alive:
                reason = "defeat"
            elif not enemies_alive:
                reason = "victory"
            else:
                reason = "draw"
            
            combat_state = combat_service.end_combat(combat_state, reason)
            auto_end_info = {"ended": True, "reason": reason}
            
            # Delete the combat state since it's finished
            combat_state_service.delete_combat_state(session_id)
        else:
            # Save the updated state
            combat_state_service.save_combat_state(session_id, combat_state)
            
        return {
            "message": result_message,
            "combat_state": combat_service.get_combat_summary(combat_state),
            "auto_ended": auto_end_info
        }

    except Exception as e:
        log_error(f"Error in execute_attack_tool: {e}")
        return {"error": str(e)}

def apply_direct_damage_tool(ctx: RunContext[GameSessionService], target_id: str, amount: int, reason: str = "effect") -> dict:
    """
    Applies direct damage to a target (e.g., from a spell, trap, or environment).
    Does NOT perform an attack roll.

    Args:
        target_id (str): ID of the target.
        amount (int): Amount of damage to apply.
        reason (str): Source/reason for the damage (optional).

    Returns:
        dict: Result of the damage application.
    """
    log_debug("Tool apply_direct_damage_tool called", tool="apply_direct_damage_tool", target_id=target_id, amount=amount)
    
    try:
        session_id = uuid.UUID(ctx.deps.session_id)
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if not combat_state:
            return {"error": "No active combat found"}
            
        # Apply damage
        combat_state = combat_service.apply_direct_damage(combat_state, target_id, amount, is_attack=False)
        combat_state.add_log_entry(f"Damage applied to target {target_id}: {amount} ({reason})")
        
        # Check for combat end
        is_ended = combat_service.check_combat_end(combat_state)
        auto_end_info = None
        
        if is_ended:
            players_alive = any(p.type == CombatantType.PLAYER and p.is_alive() for p in combat_state.participants)
            enemies_alive = any(p.type == CombatantType.NPC and p.is_alive() for p in combat_state.participants)
            
            if not players_alive:
                reason = "defeat"
            elif not enemies_alive:
                reason = "victory"
            else:
                reason = "draw"
            
            combat_state = combat_service.end_combat(combat_state, reason)
            auto_end_info = {"ended": True, "reason": reason}
            
            combat_state_service.delete_combat_state(session_id)
        else:
            combat_state_service.save_combat_state(session_id, combat_state)
            
        return {
            "message": f"Applied {amount} damage to {target_id}.",
            "combat_state": combat_service.get_combat_summary(combat_state),
            "auto_ended": auto_end_info
        }

    except Exception as e:
        log_error(f"Error in apply_direct_damage_tool: {e}")
        return {"error": str(e)}

def end_turn_tool(ctx: RunContext[GameSessionService], combat_id: str) -> dict:
    """
    Ends the current turn and moves to the next combatant.

    Args:
        combat_id (str): Combat identifier.

    Returns:
        dict: Updated combat summary.
    """
    log_debug("Tool end_turn_tool called", tool="end_turn_tool", combat_id=combat_id)
    
    try:
        session_id = uuid.UUID(ctx.deps.session_id)
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if not combat_state or str(combat_state.id) != combat_id:
            return {"error": "Combat not found", "combat_id": combat_id}
        
        combat_state = combat_service.end_turn(combat_state)
        combat_state_service.save_combat_state(session_id, combat_state)
        
        summary = combat_service.get_combat_summary(combat_state)
        current_participant = combat_state.get_current_combatant()
        
        summary["message"] = f"Turn ended. It's now {current_participant.name if current_participant else 'Unknown'}'s turn"
        
        return summary
        
    except Exception as e:
        log_error(f"Error in end_turn_tool: {e}")
        return {"error": str(e)}

def check_combat_end_tool(ctx: RunContext[GameSessionService], combat_id: str) -> dict:
    """
    Checks if the combat has ended and performs cleanup if so.

    Args:
        combat_id (str): Combat identifier.

    Returns:
        dict: Status of the combat.
    """
    log_debug("Tool check_combat_end_tool called", tool="check_combat_end_tool", combat_id=combat_id)
    
    try:
        session_id = uuid.UUID(ctx.deps.session_id)
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if not combat_state or str(combat_state.id) != combat_id:
            return {"error": "Combat not found", "combat_id": combat_id}
            
        is_ended = combat_service.check_combat_end(combat_state)
        
        if is_ended:
            players_alive = any(p.type == CombatantType.PLAYER and p.is_alive() for p in combat_state.participants)
            enemies_alive = any(p.type == CombatantType.NPC and p.is_alive() for p in combat_state.participants)
            
            if not players_alive:
                reason = "defeat"
            elif not enemies_alive:
                reason = "victory"
            else:
                reason = "draw"
            
            combat_state = combat_service.end_combat(combat_state, reason)
            combat_state_service.delete_combat_state(session_id)
            
            return {
                "combat_ended": True,
                "status": "ended",
                "end_reason": reason,
                "message": f"Combat ended: {reason}",
                "summary": combat_service.get_combat_summary(combat_state)
            }
        else:
            return {
                "combat_ended": False,
                "status": "ongoing",
                "message": "Combat ongoing"
            }
            
    except Exception as e:
        log_error(f"Error in check_combat_end_tool: {e}")
        return {"error": str(e)}

def end_combat_tool(ctx: RunContext[GameSessionService], combat_id: str, reason: str) -> dict:
    """
    Forcefully ends the combat.

    Args:
        combat_id (str): Combat identifier.
        reason (str): Reason for ending.

    Returns:
        dict: Final summary.
    """
    log_debug("Tool end_combat_tool called", tool="end_combat_tool", combat_id=combat_id, reason=reason)
    
    try:
        session_id = uuid.UUID(ctx.deps.session_id)
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if combat_state and str(combat_state.id) == combat_id:
            combat_state = combat_service.end_combat(combat_state, reason)
            combat_state_service.delete_combat_state(session_id)
            return combat_service.get_combat_summary(combat_state)
        else:
            return {"error": "Combat not found", "combat_id": combat_id}
            
    except Exception as e:
        log_error(f"Error in end_combat_tool: {e}")
        return {"error": str(e)}

def get_combat_status_tool(ctx: RunContext[GameSessionService], combat_id: str) -> dict:
    """
    Retrieves the current status of the combat.

    Args:
        combat_id (str): Combat identifier.

    Returns:
        dict: Combat summary.
    """
    log_debug("Tool get_combat_status_tool called", tool="get_combat_status_tool", combat_id=combat_id)
    
    try:
        session_id = uuid.UUID(ctx.deps.session_id)
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if not combat_state or str(combat_state.id) != combat_id:
            return {"error": "Combat not found", "combat_id": combat_id}
            
        return combat_service.get_combat_summary(combat_state)
        
    except Exception as e:
        log_error(f"Error in get_combat_status_tool: {e}")
        return {"error": str(e)}
