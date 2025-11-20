from pydantic_ai import RunContext
from back.utils.dice import roll_attack
from back.utils.logger import log_debug
from back.services.combat_service import CombatService
from back.services.combat_state_service import CombatStateService
from back.services.game_session_service import GameSessionService
from back.models.domain.combat_state import CombatantType
import uuid

combat_service = CombatService()
combat_state_service = CombatStateService()

def roll_initiative_tool(ctx: RunContext[GameSessionService], characters: list[dict]) -> list:
    """
    Calculates the initiative order of characters.

    Args:
        characters (list[dict]): List of characters participating in combat.
    
    Returns:
        list: List sorted by initiative.
    """
    log_debug("Tool roll_initiative_tool called", tool="roll_initiative_tool", characters=characters)
    # Ensure each character has an 'id' for CombatState
    for c in characters:
        if 'id' not in c:
            c['id'] = str(uuid.uuid4())
    
    # Use CombatService for initiative
    # Pass session service to help resolve player character
    state = combat_service.start_combat(characters, session_service=ctx.deps)
    state = combat_service.roll_initiative(state)
    
    # Return the sorted list of characters by initiative order
    sorted_combatants = []
    for uid in state.turn_order:
        combatant = state.get_combatant(uid)
        if combatant:
            sorted_combatants.append({
                "id": str(combatant.id),
                "name": combatant.name,
                "initiative": combatant.initiative_roll
            })
            
    return sorted_combatants

def perform_attack_tool(ctx: RunContext[GameSessionService], dice: str) -> int:
    """
    Performs an attack roll.

    Args:
        dice (str): Dice notation to roll. E.g.: "1d20".
    
    Returns:
        int: Result of the attack roll.
    """
    log_debug("Tool perform_attack_tool called", tool="perform_attack_tool", dice=dice)
    return roll_attack(dice)

def resolve_attack_tool(ctx: RunContext[GameSessionService], attack_roll: int, defense_roll: int) -> bool:
    """
    Resolves an attack by comparing attack and defense rolls.

    Args:
        attack_roll (int): Result of the attack roll.
        defense_roll (int): Result of the defense roll.
    
    Returns:
        bool: True if the attack succeeds, False otherwise.
    """
    log_debug("Tool resolve_attack_tool called", tool="resolve_attack_tool", attack_roll=attack_roll, defense_roll=defense_roll)
    return attack_roll > defense_roll

def calculate_damage_tool(ctx: RunContext[GameSessionService], base_damage: int, bonus: int = 0) -> int:
    """
    Calculates damage dealt taking modifiers into account.

    Args:
        base_damage (int): Base damage of the attack.
        bonus (int): Damage bonus/malus. Default: 0.
    
    Returns:
        int: Final damage dealt.
    """
    log_debug("Tool calculate_damage_tool called", tool="calculate_damage_tool", base_damage=base_damage, bonus=bonus)
    # Use CombatService for damage calculation
    return max(0, base_damage + bonus)

def end_combat_tool(ctx: RunContext[GameSessionService], combat_id: str, reason: str) -> dict:
    """
    Explicitly ends a combat by specifying the reason.

    Args:
        combat_id (str): Combat identifier.
        reason (str): Reason for ending the combat (flee, surrender, victory, etc.).
    
    Returns:
        dict: Dictionary containing the final combat status.
    """
    try:
        session_id = uuid.UUID(ctx.deps.session_id)
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if combat_state and str(combat_state.id) == combat_id:
            combat_state = combat_service.end_combat(combat_state, reason)
            combat_state_service.save_combat_state(session_id, combat_state)
            
            # Delete the combat state since it's finished
            combat_state_service.delete_combat_state(session_id)
            
            return combat_service.get_combat_summary(combat_state)
        else:
            return {"combat_id": combat_id, "status": "ended", "end_reason": reason, "error": "Combat not found"}
    except Exception as e:
        log_debug("Error in end_combat_tool", error=str(e), combat_id=combat_id)
        return {"combat_id": combat_id, "status": "ended", "end_reason": reason, "error": str(e)}


def end_turn_tool(ctx: RunContext[GameSessionService], combat_id: str) -> dict:
    """
    Explicitly ends the current turn and moves to the next.
    
    Args:
        combat_id (str): Combat identifier.
    
    Returns:
        dict: Updated state with the next player.
    """
    log_debug("Tool end_turn_tool called", tool="end_turn_tool", combat_id=combat_id)
    
    try:
        session_id = uuid.UUID(ctx.deps.session_id)
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if not combat_state or str(combat_state.id) != combat_id:
            return {"error": "Combat not found", "combat_id": combat_id}
        
        if not combat_state.is_active:
            return {"error": "Combat not active", "combat_id": combat_id, "status": "ended"}
        
        # End the current turn
        combat_state = combat_service.end_turn(combat_state)
        
        # Save the updated state
        combat_state_service.save_combat_state(session_id, combat_state)
        
        # Return the state with the next participant
        summary = combat_service.get_combat_summary(combat_state)
        
        current_participant = combat_state.get_current_combatant()
        
        summary["current_participant"] = {
            "id": str(current_participant.id),
            "name": current_participant.name
        } if current_participant else None
        
        summary["message"] = f"Turn ended. It's now {current_participant.name if current_participant else 'Unknown'}'s turn"
        
        return summary
        
    except Exception as e:
        log_debug("Error in end_turn_tool", error=str(e), combat_id=combat_id)
        return {"error": str(e), "combat_id": combat_id}


def check_combat_end_tool(ctx: RunContext[GameSessionService], combat_id: str) -> dict:
    """
    Automatically checks if the combat has ended.
    
    Args:
        combat_id (str): Combat identifier.
    
    Returns:
        dict: Combat status and automatic actions taken.
    """
    log_debug("Tool check_combat_end_tool called", tool="check_combat_end_tool", combat_id=combat_id)
    
    try:
        session_id = uuid.UUID(ctx.deps.session_id)
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if not combat_state or str(combat_state.id) != combat_id:
            return {"error": "Combat not found", "combat_id": combat_id}
        
        if not combat_state.is_active:
            return {"combat_ended": True, "status": "ended"}
        
        # Check if the combat has ended
        is_ended = combat_service.check_combat_end(combat_state)
        
        if is_ended:
            # Determine the reason for ending
            players_alive = any(p.type == CombatantType.PLAYER and p.is_alive() for p in combat_state.participants)
            enemies_alive = any(p.type == CombatantType.NPC and p.is_alive() for p in combat_state.participants)
            
            if not players_alive:
                reason = "defeat"
            elif not enemies_alive:
                reason = "victory"
            else:
                reason = "draw"
            
            # End the combat automatically
            combat_state = combat_service.end_combat(combat_state, reason)
            combat_state_service.save_combat_state(session_id, combat_state)
            
            # Delete the combat state since it's finished
            combat_state_service.delete_combat_state(session_id)
            
            return {
                "combat_ended": True,
                "status": "ended",
                "end_reason": reason,
                "message": f"Combat ended automatically: {reason}",
                "summary": combat_service.get_combat_summary(combat_state)
            }
        else:
            return {
                "combat_ended": False,
                "status": "ongoing",
                "message": "Combat ongoing"
            }
            
    except Exception as e:
        log_debug("Error in check_combat_end_tool", error=str(e), combat_id=combat_id)
        return {"error": str(e), "combat_id": combat_id}


def apply_damage_tool(ctx: RunContext[GameSessionService], combat_id: str, target_id: str, amount: int) -> dict:
    """
    Applies damage to a participant and checks combat state.
    
    Args:
        combat_id (str): Combat identifier.
        target_id (str): Target ID.
        amount (int): Damage points to apply.
    
    Returns:
        dict: Updated state after applying damage.
    """
    log_debug("Tool apply_damage_tool called", tool="apply_damage_tool", 
              combat_id=combat_id, target_id=target_id, amount=amount)
    
    try:
        session_id = uuid.UUID(ctx.deps.session_id)
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if not combat_state or str(combat_state.id) != combat_id:
            return {"error": "Combat not found", "combat_id": combat_id}
        
        if not combat_state.is_active:
            return {"error": "Combat not active", "combat_id": combat_id, "status": "ended"}
        
        # Apply the damage
        combat_state = combat_service.apply_damage(combat_state, target_id, amount)
        
        # Automatically check if the combat has ended
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
        
        # Save the updated state
        combat_state_service.save_combat_state(session_id, combat_state)
        
        # Find the target for return information
        target_uuid = uuid.UUID(target_id)
        target = combat_state.get_combatant(target_uuid)
        
        result = {
            "damage_applied": amount,
            "target": {
                "id": str(target.id),
                "name": target.name,
                "hp": target.current_hit_points
            } if target else None,
            "combat_state": combat_service.get_combat_summary(combat_state)
        }
        
        if auto_end_info:
            result["auto_ended"] = auto_end_info
        
        return result
        
    except Exception as e:
        log_debug("Error in apply_damage_tool", error=str(e), combat_id=combat_id, target_id=target_id)
        return {"error": str(e), "combat_id": combat_id}


def get_combat_status_tool(ctx: RunContext[GameSessionService], combat_id: str) -> dict:
    """
    Returns the complete combat state for injection into the prompt.
    
    Args:
        combat_id (str): Combat identifier.
    
    Returns:
        dict: Structured summary of the combat (round, who is playing, HP, etc.).
    """
    log_debug("Tool get_combat_status_tool called", tool="get_combat_status_tool", combat_id=combat_id)
    
    try:
        session_id = uuid.UUID(ctx.deps.session_id)
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if not combat_state or str(combat_state.id) != combat_id:
            return {"error": "Combat not found", "combat_id": combat_id}
        
        summary = combat_service.get_combat_summary(combat_state)
        
        # Add enriched information
        current_participant = combat_state.get_current_combatant()
        
        summary["current_participant"] = {
            "id": str(current_participant.id),
            "name": current_participant.name
        } if current_participant else None
        
        summary["alive_participants"] = [
            {"id": str(p.id), "name": p.name, "hp": p.current_hit_points} 
            for p in combat_state.participants if p.is_alive()
        ]
        summary["dead_participants"] = [
            {"id": str(p.id), "name": p.name} 
            for p in combat_state.participants if not p.is_alive()
        ]
        
        return summary
        
    except Exception as e:
        log_debug("Error in get_combat_status_tool", error=str(e), combat_id=combat_id)
        return {"error": str(e), "combat_id": combat_id}


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
        dict: CombatSeedPayload structure (location, participants, description).
    """
    log_debug("Tool start_combat_tool called", tool="start_combat_tool", location=location, description=description, participants=participants)
    
    try:
        session_id = uuid.UUID(ctx.deps.session_id)
        
        # Check that there's no active combat already
        if combat_state_service.has_active_combat(session_id):
            return {"error": "A combat is already in progress for this session"}
        
        # Process and normalize participants
        processed_participants = []
        
        # Always add the player if not present (usually handled by the agent, but good to ensure)
        # However, the agent might not include the player in the list if it assumes the player is always there.
        # For now, we assume the agent provides the list of *opponents* and allies, and we inject the player?
        # Or the agent provides everyone? The prompt says "list of participants".
        # Let's assume the agent provides everyone including the player if they are part of the context, 
        # but usually the player is implicit in the session. 
        # Actually, CombatService.start_combat usually expects a list of dicts.
        # Let's look at how we handled it before: "The first participant is often the player".
        # We should probably ensure the player is added by the service if not in the list, 
        # or we explicitly add the player here.
        # Let's stick to the plan: "participant generator logic".
        
        for p in participants:
            # Basic normalization
            p_data = p.copy()
            
            if 'id' not in p_data:
                p_data['id'] = str(uuid.uuid4())
            
            # Map fields to what CombatService expects
            if 'name' in p_data:
                p_data['nom'] = p_data['name']
            
            # Determine stats based on archetype/level
            level = p_data.get('level', 1)
            archetype = p_data.get('archetype', 'Unknown').lower()
            is_unique = p_data.get('is_unique_npc', False)
            
            # Simple generator logic (placeholder for more complex logic)
            # In a real system, we would query a database of monsters/NPCs
            base_hp = 10
            base_ac = 10
            initiative_bonus = 0
            
            if 'orc' in archetype:
                base_hp = 15 + (level * 5)
                base_ac = 13
                initiative_bonus = 1
            elif 'goblin' in archetype:
                base_hp = 8 + (level * 4)
                base_ac = 12
                initiative_bonus = 2
            elif 'troll' in archetype:
                base_hp = 40 + (level * 10)
                base_ac = 15
                initiative_bonus = -1
            elif 'boss' in archetype or is_unique:
                base_hp = 50 + (level * 10)
                base_ac = 16
                initiative_bonus = 3
            else:
                # Generic scaling
                base_hp = 10 + (level * 5)
            
            # Set stats if not provided
            if 'hp' not in p_data and 'health' not in p_data:
                p_data['hp'] = base_hp
            
            # Ensure camp is set
            if 'role' in p_data:
                p_data['camp'] = 'player' if p_data['role'] == 'ally' else 'enemy'
            elif 'camp' not in p_data:
                p_data['camp'] = 'enemy'

            # Initiative (will be rolled by service, but we can set a bonus)
            if 'initiative' not in p_data:
                p_data['initiative'] = 10 + initiative_bonus

            processed_participants.append(p_data)
        
        # Ensure the player is included? 
        # The previous code said: "The first participant is often the player".
        # If the agent follows instructions, it might list the player. 
        # If not, CombatService.start_combat might need to handle it.
        # Let's check CombatService.start_combat signature. 
        # It takes `participants: list[dict]`.
        # And `session_service` to resolve player character.
        # So we just pass the processed list.
        
        # Create the initial combat state
        combat_state = combat_service.start_combat(processed_participants, session_service=ctx.deps)
        
        # Calculate initiative
        combat_state = combat_service.roll_initiative(combat_state)
        
        # Save the initial state
        combat_state_service.save_combat_state(session_id, combat_state)
        
        # Return CombatSeedPayload structure
        # We need to convert the combat_state back to a dict of participants for the payload?
        # Or just return what we constructed?
        # CombatSeedPayload has: location, participants (Dict[str, Any]), description
        # The participants dict in CombatSeedPayload seems to be a map of ID -> data?
        # Let's check CombatSeedPayload definition again.
        # participants: Dict[str, Any]
        
        participants_payload = {}
        for p in combat_state.participants:
            participants_payload[str(p.id)] = {
                "name": p.name,
                "hp": p.current_hit_points,
                "max_hp": p.max_hit_points,
                "camp": p.camp.value if hasattr(p.camp, 'value') else str(p.camp),
                "type": p.type.value if hasattr(p.type, 'value') else str(p.type)
            }

        return {
            "location": location,
            "description": description,
            "participants": participants_payload
        }
        
    except Exception as e:
        log_debug("Error in start_combat_tool", error=str(e))
        return {"error": str(e)}
