from typing import List, Dict, Any
from uuid import UUID, uuid4
import random
from back.models.domain.combat_state import CombatState, Combatant, CombatantType
from back.models.domain.combat_system_manager import CombatSystemManager
from back.models.domain.character import Stats, Skills, Equipment, CombatStats, Spells
from back.models.domain.npc import NPC
from back.utils.logger import log_debug

class CombatService:
    def __init__(self):
        self.manager = CombatSystemManager()

    def start_combat(self, participants_data: List[Dict[str, Any]], session_service: Any = None) -> CombatState:
        """
        Initialize a new combat state with the given participants.
        """
        participants = []
        for p_data in participants_data:
            # Determine type
            is_player = p_data.get('camp') == 'player' or p_data.get('is_player', False)
            c_type = CombatantType.PLAYER if is_player else CombatantType.NPC
            
            character_ref = None
            npc_ref = None

            if c_type == CombatantType.PLAYER:
                if session_service and session_service.character_data:
                    character_ref = session_service.character_data
                elif p_data.get('character'):
                     character_ref = p_data.get('character')
            else:
                if p_data.get('npc'):
                    npc_ref = p_data.get('npc')
                else:
                    npc_ref = self._create_dummy_npc(p_data.get('name', p_data.get('nom', 'Unknown')))

            combatant = Combatant(
                id=UUID(str(p_data.get('id'))) if p_data.get('id') else uuid4(),
                name=p_data.get('name', p_data.get('nom', 'Unknown')),
                type=c_type,
                current_hit_points=p_data.get('hp', 10),
                max_hit_points=p_data.get('max_hp', p_data.get('hp', 10)),
                armor_class=p_data.get('ac', 10),
                initiative_roll=p_data.get('initiative', 0),
                character_ref=character_ref,
                npc_ref=npc_ref
            )
            participants.append(combatant)

        state = CombatState(
            participants=participants,
            is_active=True,
            log=["Combat started."]
        )
        return state

    def _create_dummy_npc(self, name: str) -> NPC:
        return NPC(
            name=name,
            archetype="Generic Enemy",
            stats=Stats(strength=10, constitution=10, agility=10, intelligence=10, wisdom=10, charisma=10),
            skills=Skills(),
            equipment=Equipment(),
            combat_stats=CombatStats(max_hit_points=10, current_hit_points=10, armor_class=10, attack_bonus=0),
            spells=Spells()
        )

    def roll_initiative(self, state: CombatState) -> CombatState:
        """
        Roll initiative for all participants and set turn order.
        """
        for p in state.participants:
            # Simple d20 + agi mod (if available)
            # For now, just d20
            roll = random.randint(1, 20)
            p.initiative_roll = roll
            state.add_log_entry(f"{p.name} rolled {roll} for initiative.")

        # Sort participants by initiative (descending)
        sorted_participants = sorted(state.participants, key=lambda p: p.initiative_roll, reverse=True)
        state.turn_order = [p.id for p in sorted_participants]
        
        if state.turn_order:
            state.current_turn_combatant_id = state.turn_order[0]
            
        return state

    def end_combat(self, state: CombatState, reason: str) -> CombatState:
        state.is_active = False
        state.add_log_entry(f"Combat ended: {reason}")
        return state

    def get_combat_summary(self, state: CombatState) -> Dict[str, Any]:
        return {
            "combat_id": str(state.id),
            "round": state.round_number,
            "participants": [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "hp": p.current_hit_points,
                    "max_hp": p.max_hit_points,
                    "camp": "player" if p.type == CombatantType.PLAYER else "enemy"
                } for p in state.participants
            ],
            "turn_order": [str(uid) for uid in state.turn_order],
            "current_turn": str(state.current_turn_combatant_id) if state.current_turn_combatant_id else None,
            "status": "ongoing" if state.is_active else "ended",
            "log": state.log[-5:] # Last 5 entries
        }

    def end_turn(self, state: CombatState) -> CombatState:
        if not state.turn_order:
            return state
            
        try:
            if state.current_turn_combatant_id is None:
                raise ValueError("Current turn combatant ID is None")

            current_idx = state.turn_order.index(state.current_turn_combatant_id)
            next_idx = (current_idx + 1) % len(state.turn_order)
            state.current_turn_combatant_id = state.turn_order[next_idx]
            
            if next_idx == 0:
                state.round_number += 1
                state.add_log_entry(f"Round {state.round_number} started.")
                
            next_combatant = state.get_combatant(state.current_turn_combatant_id)
            if next_combatant:
                state.add_log_entry(f"It is now {next_combatant.name}'s turn.")
                
        except ValueError:
            # Current combatant not in turn order (maybe died/removed?)
            if state.turn_order:
                state.current_turn_combatant_id = state.turn_order[0]
        
        return state

    def check_combat_end(self, state: CombatState) -> bool:
        players_alive = any(p.type == CombatantType.PLAYER and p.is_alive() for p in state.participants)
        enemies_alive = any(p.type == CombatantType.NPC and p.is_alive() for p in state.participants)
        return not players_alive or not enemies_alive

    def apply_damage(self, state: CombatState, target_id: str, amount: int) -> CombatState:
        try:
            target_uuid = UUID(target_id)
            combatant = state.get_combatant(target_uuid)
            if combatant:
                actual_damage = combatant.take_damage(amount)
                state.add_log_entry(f"{combatant.name} took {actual_damage} damage. HP: {combatant.current_hit_points}/{combatant.max_hit_points}")
                if not combatant.is_alive():
                    state.add_log_entry(f"{combatant.name} has been defeated!")
        except ValueError:
            log_debug(f"Invalid UUID for target_id: {target_id}")
        return state
