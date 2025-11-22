from typing import List, Dict, Any, Tuple
from uuid import UUID, uuid4
import random
import re
from back.models.domain.combat_state import CombatState, Combatant, CombatantType
from back.models.domain.character import Stats, Skills, Equipment, CombatStats, Spells
from back.models.domain.items import EquipmentItem
from back.models.domain.npc import NPC
from back.services.character_service import CharacterService
from back.utils.logger import log_debug, log_error

class CombatService:
    def __init__(self):
        """
        Initializes the CombatService.

        Purpose:
            Prepares the combat service for managing combat encounters.
            This service handles all combat-related operations including participant
            management, attack resolution, damage application, and turn progression.
        """

    def start_combat(self, participants_data: List[Dict[str, Any]], session_service: Any = None) -> CombatState:
        """
        Initializes a new combat state with the given participants.

        Purpose:
            Creates a new combat session, generates participants (including NPCs with default equipment),
            and rolls initial initiative.

        Args:
            participants_data (List[Dict[str, Any]]): A list of dictionaries containing participant data.
                Each dict should contain keys like 'name', 'camp', 'hp', etc.
            session_service (Any, optional): The GameSessionService instance to access player character data.
                Defaults to None.

        Returns:
            CombatState: The newly created and initialized combat state.
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
                    # Generate NPC with equipment
                    npc_ref = self._create_npc_with_equipment(p_data.get('name', p_data.get('nom', 'Unknown')), p_data)

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
        
        # Auto-roll initiative
        state = self.roll_initiative(state)
        
        return state

    def _create_npc_with_equipment(self, name: str, data: Dict[str, Any]) -> NPC:
        """
        Creates an NPC and assigns default equipment based on archetype/data.

        Purpose:
            Generates a fully populated NPC object with stats and equipment suitable for combat,
            handling cases where explicit NPC data is missing.

        Args:
            name (str): The name of the NPC.
            data (Dict[str, Any]): The raw data dictionary for the NPC.

        Returns:
            NPC: The constructed NPC object with equipment.
        """
        archetype = data.get('archetype', 'Generic Enemy')
        
        # Default stats
        stats = Stats(strength=10, constitution=10, agility=10, intelligence=10, wisdom=10, charisma=10)
        
        # Default equipment generation logic
        equipment = Equipment()
        
        def create_item(name: str, category: str, **kwargs) -> EquipmentItem:
            return EquipmentItem(
                id=str(uuid4()),
                name=name,
                category=category,
                cost_gold=0,
                cost_silver=0,
                cost_copper=0,
                weight=1.0,
                quantity=1,
                equipped=True,
                **kwargs
            )
        
        # Simple logic to assign weapons based on name/archetype
        # This could be expanded with a proper lookup table
        if "goblin" in name.lower() or "goblin" in archetype.lower():
            equipment.weapons.append(create_item("Scimitar", "weapons", damage="1d6", type="melee"))
            equipment.armor.append(create_item("Leather Armor", "armor", protection=2))
        elif "orc" in name.lower() or "orc" in archetype.lower():
            equipment.weapons.append(create_item("Greataxe", "weapons", damage="1d12", type="melee"))
            equipment.armor.append(create_item("Hide Armor", "armor", protection=3))
        elif "skeleton" in name.lower():
            equipment.weapons.append(create_item("Shortsword", "weapons", damage="1d6", type="melee"))
        elif "archer" in name.lower() or "bandit" in name.lower():
             equipment.weapons.append(create_item("Shortbow", "weapons", damage="1d6", type="ranged"))
             equipment.armor.append(create_item("Leather Armor", "armor", protection=2))
        else:
            # Fallback weapon
            equipment.weapons.append(create_item("Claws/Slam", "weapons", damage="1d4", type="melee"))

        return NPC(
            name=name,
            archetype=archetype,
            stats=stats,
            skills=Skills(),
            equipment=equipment,
            combat_stats=CombatStats(
                max_hit_points=data.get('max_hp', 10), 
                current_hit_points=data.get('hp', 10), 
                armor_class=data.get('ac', 10), 
                attack_bonus=data.get('attack_bonus', 2)
            ),
            spells=Spells()
        )

    def roll_initiative(self, state: CombatState) -> CombatState:
        """
        Rolls initiative for all participants and sets the turn order.

        Purpose:
            Calculates initiative for every participant based on their stats and a d20 roll,
            then sorts them to determine the turn order.

        Args:
            state (CombatState): The current combat state.

        Returns:
            CombatState: The updated combat state with assigned initiative rolls and turn order.
        """
        for p in state.participants:
            # Get initiative bonus
            bonus = 0
            if p.character_ref:
                bonus = p.character_ref.calculate_initiative()
            elif p.npc_ref:
                # Simplified NPC initiative (usually just Dex mod, here 0 or from data)
                bonus = 0 
            
            roll = random.randint(1, 20)
            total = roll + bonus
            p.initiative_roll = total
            state.add_log_entry(f"{p.name} rolled {total} ({roll}+{bonus}) for initiative.")

        # Sort participants by initiative (descending)
        sorted_participants = sorted(state.participants, key=lambda p: p.initiative_roll, reverse=True)
        state.turn_order = [p.id for p in sorted_participants]
        
        if state.turn_order:
            state.current_turn_combatant_id = state.turn_order[0]
            
        return state

    def execute_attack(self, state: CombatState, attacker_id: str, target_id: str) -> Tuple[CombatState, str]:
        """
        Executes a full attack sequence between two combatants.

        Purpose:
            Handles the mechanics of an attack: validating participants, calculating attack rolls,
            determining hits/misses/crits, rolling damage, and applying it to the target.

        Args:
            state (CombatState): The current combat state.
            attacker_id (str): The UUID string of the attacking combatant.
            target_id (str): The UUID string of the target combatant.

        Returns:
            Tuple[CombatState, str]: A tuple containing the updated combat state and a narrative result message.
        """
        try:
            attacker_uuid = UUID(attacker_id)
            target_uuid = UUID(target_id)
        except ValueError:
            return state, "Invalid ID format."

        attacker = state.get_combatant(attacker_uuid)
        target = state.get_combatant(target_uuid)

        if not attacker or not target:
            return state, "Attacker or Target not found."

        if not attacker.is_alive():
            return state, f"{attacker.name} is unconscious and cannot attack."

        # 1. Get Weapon and Bonuses
        weapon = self._get_equipped_weapon(attacker)
        attack_bonus = self._get_attack_bonus(attacker)
        
        weapon_name = weapon.get("name", "Unarmed Strike")
        damage_dice = weapon.get("damage", "1")

        # 2. Attack Roll
        d20 = random.randint(1, 20)
        total_attack = d20 + attack_bonus
        
        is_crit = d20 == 20
        is_auto_miss = d20 == 1
        
        log_msg = f"{attacker.name} attacks {target.name} with {weapon_name}. Roll: {d20} + {attack_bonus} = {total_attack} vs AC {target.armor_class}."
        
        # 3. Resolve Hit
        hits = (total_attack >= target.armor_class and not is_auto_miss) or is_crit
        
        result_msg = ""
        if hits:
            # 4. Roll Damage
            damage = self._roll_dice(damage_dice)
            if is_crit:
                damage += self._roll_dice(damage_dice) # Simple crit: roll twice
                log_msg += " CRITICAL HIT!"
            
            # Add ability mod to damage (simplified: same as attack bonus for now, or 0)
            damage_mod = attack_bonus # Often Str/Dex mod is added
            total_damage = max(1, damage + damage_mod)
            
            # 5. Apply Damage
            state = self.apply_direct_damage(state, target_id, total_damage, is_attack=True)
            
            result_msg = f"Hit! {attacker.name} deals {total_damage} damage to {target.name}."
            if not target.is_alive():
                result_msg += f" {target.name} is defeated!"
        else:
            result_msg = f"Miss! {attacker.name} missed {target.name}."
            state.add_log_entry(f"{attacker.name} missed {target.name} with {weapon_name}.")

        return state, result_msg

    def _get_equipped_weapon(self, combatant: Combatant) -> Dict[str, Any]:
        """
        Retrieves the equipped weapon for a combatant.

        Purpose:
            Helper method to find the active weapon for a combatant, falling back to an unarmed strike
            if no weapon is equipped.

        Args:
            combatant (Combatant): The combatant to check.

        Returns:
            Dict[str, Any]: A dictionary representing the weapon (name, damage, type).
        """
        equipment = None
        if combatant.character_ref:
            equipment = combatant.character_ref.equipment
        elif combatant.npc_ref:
            equipment = combatant.npc_ref.equipment
            
        if equipment and equipment.weapons:
            # TODO: Check for 'equipped' flag. For now, take the first one.
            # In a real implementation, we would filter by w.get('equipped', True)
            weapon = equipment.weapons[0]
            if isinstance(weapon, EquipmentItem):
                return weapon.model_dump()
            return weapon
            
        return {"name": "Unarmed Strike", "damage": "1", "type": "melee"}

    def _get_attack_bonus(self, combatant: Combatant) -> int:
        """
        Calculates the attack bonus for a combatant.

        Purpose:
            Helper method to retrieve the attack bonus from the underlying character or NPC reference.

        Args:
            combatant (Combatant): The combatant to check.

        Returns:
            int: The calculated attack bonus.
        """
        if combatant.character_ref:
            return combatant.character_ref.combat_stats.attack_bonus
        elif combatant.npc_ref:
            return combatant.npc_ref.combat_stats.attack_bonus
        return 0

    def _roll_dice(self, dice_str: str) -> int:
        """
        Parses and rolls a dice string (e.g., '1d8', '2d6+1').

        Purpose:
            Utility method to simulate dice rolls based on standard RPG notation.

        Args:
            dice_str (str): The dice string to roll.

        Returns:
            int: The total result of the roll.
        """
        try:
            # Remove whitespace
            dice_str = dice_str.replace(" ", "")
            
            # Check for static number
            if dice_str.isdigit():
                return int(dice_str)
                
            # Parse XdY+Z
            match = re.match(r"(\d+)d(\d+)(?:([+-])(\d+))?", dice_str)
            if match:
                count = int(match.group(1))
                sides = int(match.group(2))
                modifier_sign = match.group(3)
                modifier = int(match.group(4)) if match.group(4) else 0
                
                total = sum(random.randint(1, sides) for _ in range(count))
                
                if modifier_sign == '-':
                    total -= modifier
                elif modifier_sign == '+':
                    total += modifier
                    
                return max(1, total)
            return 1 # Fallback
        except Exception as e:
            log_error(f"Error rolling dice {dice_str}: {e}")
            return 1

    def apply_direct_damage(self, state: CombatState, target_id: str, amount: int, is_attack: bool = False) -> CombatState:
        """
        Applies damage directly to a target and syncs with CharacterService if applicable.

        Purpose:
            Reduces a combatant's HP, logs the event, checks for death, and ensures player HP
            is synchronized with persistent storage.

        Args:
            state (CombatState): The current combat state.
            target_id (str): The UUID string of the target combatant.
            amount (int): The amount of damage to apply.
            is_attack (bool, optional): Whether the damage is from an attack (affects logging). Defaults to False.

        Returns:
            CombatState: The updated combat state.
        """
        try:
            target_uuid = UUID(target_id)
            combatant = state.get_combatant(target_uuid)
            if combatant:
                actual_damage = combatant.take_damage(amount)
                source_str = "Attack" if is_attack else "Effect"
                state.add_log_entry(f"{combatant.name} took {actual_damage} damage ({source_str}). HP: {combatant.current_hit_points}/{combatant.max_hit_points}")
                
                if not combatant.is_alive():
                    state.add_log_entry(f"{combatant.name} has been defeated!")

                # IMMEDIATE SYNC FOR PLAYERS
                if combatant.type == CombatantType.PLAYER and combatant.character_ref:
                    self._sync_player_hp(combatant)
                
                # TODO: Implement Status Effects (e.g., Poison, Stun) here.
                # Future improvement: Add a 'status_effects' list to Combatant and process them.

        except ValueError:
            log_debug(f"Invalid UUID for target_id: {target_id}")
        return state

    def _sync_player_hp(self, combatant: Combatant) -> None:
        """
        Synchronizes the combatant's HP back to the persistent Character storage.

        Purpose:
            Ensures that damage taken during combat is immediately reflected in the player's
            persistent character record to prevent data loss.

        Args:
            combatant (Combatant): The combatant (must be a player) to sync.

        Returns:
            None
        """
        try:
            if not combatant.character_ref:
                return

            # Persist via CharacterService
            # We instantiate a fresh service to ensure clean state handling
            char_service = CharacterService(str(combatant.character_ref.id))
            
            # Update the loaded character data with the current combat HP
            # We trust the combat state as the source of truth for HP during combat
            # Ensure we don't exceed max HP (though combat logic should handle this, safety first)
            new_hp = combatant.current_hit_points
            char_service.character_data.combat_stats.current_hit_points = new_hp
            
            # Save the updated character
            char_service.save_character()
            
            # Update the local reference to keep it in sync with the "real" character
            combatant.character_ref = char_service.character_data
            
            log_debug(f"Synced HP for player {combatant.name} to {combatant.current_hit_points}")
            
        except Exception as e:
            log_error(f"Failed to sync player HP for {combatant.name}: {e}")

    def end_combat(self, state: CombatState, reason: str) -> CombatState:
        """
        Ends the combat session.

        Purpose:
            Marks the combat as inactive, logs the reason, and performs a final HP sync for all players.

        Args:
            state (CombatState): The current combat state.
            reason (str): The reason for ending the combat (e.g., "Victory", "Fled").

        Returns:
            CombatState: The updated (inactive) combat state.
        """
        state.is_active = False
        state.add_log_entry(f"Combat ended: {reason}")
        
        # Final sync for all players
        for p in state.participants:
            if p.type == CombatantType.PLAYER:
                self._sync_player_hp(p)
                
        return state

    def get_combat_summary(self, state: CombatState) -> Dict[str, Any]:
        """
        Generates a summary of the current combat state.

        Purpose:
            Provides a simplified view of the combat for UI display or AI context, including
            participants, turn order, and recent logs.

        Args:
            state (CombatState): The current combat state.

        Returns:
            Dict[str, Any]: A dictionary containing the combat summary.
        """
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
        """
        Advances the combat to the next turn.

        Purpose:
            Updates the current turn holder, increments the round counter if necessary, and logs the transition.

        Args:
            state (CombatState): The current combat state.

        Returns:
            CombatState: The updated combat state with the new turn holder.
        """
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
        """
        Checks if the combat should end.

        Purpose:
            Determines if one side has been completely defeated (no living members).

        Args:
            state (CombatState): The current combat state.

        Returns:
            bool: True if the combat should end, False otherwise.
        """
        players_alive = any(p.type == CombatantType.PLAYER and p.is_alive() for p in state.participants)
        enemies_alive = any(p.type == CombatantType.NPC and p.is_alive() for p in state.participants)
        return not players_alive or not enemies_alive

