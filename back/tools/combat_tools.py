from pydantic_ai import RunContext
from back.utils.dice import roll_attack
from back.utils.logger import log_debug
from back.services.combat_service import CombatService
from back.services.combat_state_service import CombatStateService
from back.services.game_session_service import GameSessionService
import uuid

combat_service = CombatService()
combat_state_service = CombatStateService()

def roll_initiative_tool(ctx: RunContext[GameSessionService], characters: list[dict]) -> list:
    """
    Calcule l'ordre d'initiative des personnages.

    Args:
        characters (list[dict]): Liste des personnages participant au combat.
    
    Returns:
        list: Liste triée selon l'initiative.
    """
    log_debug("Tool roll_initiative_tool appelé", tool="roll_initiative_tool", characters=characters)
    # Ensure each character has an 'id' for CombatState
    for c in characters:
        if 'id' not in c:
            c['id'] = str(uuid.uuid4())
    # Utilisation de CombatService pour l'initiative
    state = combat_service.start_combat(characters)
    state = combat_service.roll_initiative(state)
    # Retourne la liste triée des personnages selon l'ordre d'initiative
    return [p for cid in state.initiative_order for p in state.participants if p['id'] == cid]

# Tool definition removed - now handled directly by PydanticAI agent

def perform_attack_tool(ctx: RunContext[GameSessionService], dice: str) -> int:
    """
    Effectue un jet d'attaque.

    Args:
        dice (str): Notation des dés à lancer. Ex. : "1d20".
    
    Returns:
        int: Résultat du jet d'attaque.
    """
    log_debug("Tool perform_attack_tool appelé", tool="perform_attack_tool", dice=dice)
    return roll_attack(dice)

# Tool definition removed - now handled directly by PydanticAI agent

def resolve_attack_tool(ctx: RunContext[GameSessionService], attack_roll: int, defense_roll: int) -> bool:
    """
    Résout une attaque en comparant les jets d'attaque et de défense.

    Args:
        attack_roll (int): Résultat du jet d'attaque.
        defense_roll (int): Résultat du jet de défense.
    
    Returns:
        bool: True si l'attaque réussit, False sinon.
    """
    log_debug("Tool resolve_attack_tool appelé", tool="resolve_attack_tool", attack_roll=attack_roll, defense_roll=defense_roll)
    return attack_roll > defense_roll

# Tool definition removed - now handled directly by PydanticAI agent

def calculate_damage_tool(ctx: RunContext[GameSessionService], base_damage: int, bonus: int = 0) -> int:
    """
    Calcule les dégâts infligés en tenant compte des modificateurs.

    Args:
        base_damage (int): Dégâts de base de l'attaque.
        bonus (int): Bonus/malus de dégâts. Par défaut : 0.
    
    Returns:
        int: Dégâts finaux infligés.
    """
    log_debug("Tool calculate_damage_tool appelé", tool="calculate_damage_tool", base_damage=base_damage, bonus=bonus)
    # Utilisation de CombatService pour le calcul des dégâts
    return max(0, base_damage + bonus)

# Tool definition removed - now handled directly by PydanticAI agent

def end_combat_tool(ctx: RunContext[GameSessionService], combat_id: str, reason: str) -> dict:
    """
    Termine explicitement un combat en précisant la raison.

    Args:
        combat_id (str): Identifiant du combat.
        reason (str): Raison de la fin du combat (fuite, reddition, victoire, etc.).
    
    Returns:
        dict: Dictionnaire contenant le statut final du combat.
    """
    try:
        session_id = ctx.deps.session_id
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if combat_state and combat_state.combat_id == combat_id:
            combat_state = combat_service.end_combat(combat_state, reason)
            combat_state_service.save_combat_state(session_id, combat_state)
            
            # Supprimer l'état du combat car il est terminé
            combat_state_service.delete_combat_state(session_id)
            
            return combat_service.get_combat_summary(combat_state)
        else:
            return {"combat_id": combat_id, "status": "termine", "end_reason": reason, "error": "Combat non trouvé"}
    except Exception as e:
        log_debug("Erreur dans end_combat_tool", error=str(e), combat_id=combat_id)
        return {"combat_id": combat_id, "status": "termine", "end_reason": reason, "error": str(e)}


def end_turn_tool(ctx: RunContext[GameSessionService], combat_id: str) -> dict:
    """
    Termine explicitement le tour courant et passe au suivant.
    
    Args:
        combat_id (str): Identifiant du combat.
    
    Returns:
        dict: État mis à jour avec le joueur suivant.
    """
    log_debug("Tool end_turn_tool appelé", tool="end_turn_tool", combat_id=combat_id)
    
    try:
        session_id = ctx.deps.session_id
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if not combat_state or combat_state.combat_id != combat_id:
            return {"error": "Combat non trouvé", "combat_id": combat_id}
        
        if combat_state.status != "en_cours":
            return {"error": "Combat non actif", "combat_id": combat_id, "status": combat_state.status}
        
        # Terminer le tour courant
        combat_state = combat_service.end_turn(combat_state)
        
        # Sauvegarder l'état mis à jour
        combat_state_service.save_combat_state(session_id, combat_state)
        
        # Retourner l'état avec le participant suivant
        summary = combat_service.get_combat_summary(combat_state)
        current_participant = None
        if combat_state.current_turn < len(combat_state.initiative_order):
            current_id = combat_state.initiative_order[combat_state.current_turn]
            current_participant = next((p for p in combat_state.participants if p['id'] == current_id), None)
        
        summary["current_participant"] = current_participant
        summary["message"] = f"Tour terminé. C'est maintenant au tour de {current_participant['nom'] if current_participant else 'Inconnu'}"
        
        return summary
        
    except Exception as e:
        log_debug("Erreur dans end_turn_tool", error=str(e), combat_id=combat_id)
        return {"error": str(e), "combat_id": combat_id}


def check_combat_end_tool(ctx: RunContext[GameSessionService], combat_id: str) -> dict:
    """
    Vérifie automatiquement si le combat est terminé.
    
    Args:
        combat_id (str): Identifiant du combat.
    
    Returns:
        dict: Statut du combat et actions automatiques prises.
    """
    log_debug("Tool check_combat_end_tool appelé", tool="check_combat_end_tool", combat_id=combat_id)
    
    try:
        session_id = ctx.deps.session_id
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if not combat_state or combat_state.combat_id != combat_id:
            return {"error": "Combat non trouvé", "combat_id": combat_id}
        
        if combat_state.status != "en_cours":
            return {"combat_ended": True, "status": combat_state.status, "end_reason": combat_state.end_reason}
        
        # Vérifier si le combat est terminé
        is_ended = combat_service.check_combat_end(combat_state)
        
        if is_ended:
            # Déterminer la raison de la fin
            players_alive = any(p.get('camp') == 'joueur' and p.get('hp', 1) > 0 for p in combat_state.participants)
            enemies_alive = any(p.get('camp') == 'adversaire' and p.get('hp', 1) > 0 for p in combat_state.participants)
            
            if not players_alive:
                reason = "défaite"
            elif not enemies_alive:
                reason = "victoire"
            else:
                reason = "match_nul"
            
            # Terminer automatiquement le combat
            combat_state = combat_service.end_combat(combat_state, reason)
            combat_state_service.save_combat_state(session_id, combat_state)
            
            # Supprimer l'état du combat car il est terminé
            combat_state_service.delete_combat_state(session_id)
            
            return {
                "combat_ended": True,
                "status": "termine",
                "end_reason": reason,
                "message": f"Combat terminé automatiquement : {reason}",
                "summary": combat_service.get_combat_summary(combat_state)
            }
        else:
            return {
                "combat_ended": False,
                "status": "en_cours",
                "message": "Combat en cours"
            }
            
    except Exception as e:
        log_debug("Erreur dans check_combat_end_tool", error=str(e), combat_id=combat_id)
        return {"error": str(e), "combat_id": combat_id}


def apply_damage_tool(ctx: RunContext[GameSessionService], combat_id: str, target_id: str, amount: int) -> dict:
    """
    Applique des dégâts à un participant et vérifie l'état du combat.
    
    Args:
        combat_id (str): Identifiant du combat.
        target_id (str): ID de la cible.
        amount (int): Points de dégâts à appliquer.
    
    Returns:
        dict: État mis à jour après application des dégâts.
    """
    log_debug("Tool apply_damage_tool appelé", tool="apply_damage_tool", 
              combat_id=combat_id, target_id=target_id, amount=amount)
    
    try:
        session_id = ctx.deps.session_id
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if not combat_state or combat_state.combat_id != combat_id:
            return {"error": "Combat non trouvé", "combat_id": combat_id}
        
        if combat_state.status != "en_cours":
            return {"error": "Combat non actif", "combat_id": combat_id, "status": combat_state.status}
        
        # Appliquer les dégâts
        combat_state = combat_service.apply_damage(combat_state, target_id, amount)
        
        # Vérifier automatiquement si le combat est terminé
        is_ended = combat_service.check_combat_end(combat_state)
        auto_end_info = None
        
        if is_ended:
            players_alive = any(p.get('camp') == 'joueur' and p.get('hp', 1) > 0 for p in combat_state.participants)
            enemies_alive = any(p.get('camp') == 'adversaire' and p.get('hp', 1) > 0 for p in combat_state.participants)
            
            if not players_alive:
                reason = "défaite"
            elif not enemies_alive:
                reason = "victoire"
            else:
                reason = "match_nul"
            
            combat_state = combat_service.end_combat(combat_state, reason)
            auto_end_info = {"ended": True, "reason": reason}
            
            # Supprimer l'état du combat car il est terminé
            combat_state_service.delete_combat_state(session_id)
        
        # Sauvegarder l'état mis à jour
        combat_state_service.save_combat_state(session_id, combat_state)
        
        # Trouver la cible pour les informations de retour
        target = next((p for p in combat_state.participants if p['id'] == target_id), None)
        
        result = {
            "damage_applied": amount,
            "target": target,
            "combat_state": combat_service.get_combat_summary(combat_state)
        }
        
        if auto_end_info:
            result["auto_ended"] = auto_end_info
        
        return result
        
    except Exception as e:
        log_debug("Erreur dans apply_damage_tool", error=str(e), combat_id=combat_id, target_id=target_id)
        return {"error": str(e), "combat_id": combat_id}


def get_combat_status_tool(ctx: RunContext[GameSessionService], combat_id: str) -> dict:
    """
    Retourne l'état complet du combat pour injection dans le prompt.
    
    Args:
        combat_id (str): Identifiant du combat.
    
    Returns:
        dict: Résumé structuré du combat (round, qui joue, HP, etc.).
    """
    log_debug("Tool get_combat_status_tool appelé", tool="get_combat_status_tool", combat_id=combat_id)
    
    try:
        session_id = ctx.deps.session_id
        combat_state = combat_state_service.load_combat_state(session_id)
        
        if not combat_state or combat_state.combat_id != combat_id:
            return {"error": "Combat non trouvé", "combat_id": combat_id}
        
        summary = combat_service.get_combat_summary(combat_state)
        
        # Ajouter des informations enrichies
        current_participant = None
        if combat_state.current_turn < len(combat_state.initiative_order):
            current_id = combat_state.initiative_order[combat_state.current_turn]
            current_participant = next((p for p in combat_state.participants if p['id'] == current_id), None)
        
        summary["current_participant"] = current_participant
        summary["alive_participants"] = [p for p in combat_state.participants if p.get('hp', 1) > 0]
        summary["dead_participants"] = [p for p in combat_state.participants if p.get('hp', 1) <= 0]
        
        return summary
        
    except Exception as e:
        log_debug("Erreur dans get_combat_status_tool", error=str(e), combat_id=combat_id)
        return {"error": str(e), "combat_id": combat_id}


def start_combat_tool(ctx: RunContext[GameSessionService], participants: list[dict]) -> dict:
    """
    Démarre un nouveau combat avec les participants donnés.
    
    Args:
        participants (list[dict]): Liste des participants (joueur et adversaires).
    
    Returns:
        dict: État initial du combat.
    """
    log_debug("Tool start_combat_tool appelé", tool="start_combat_tool", participants=participants)
    
    try:
        session_id = ctx.deps.session_id
        
        # Vérifier qu'il n'y a pas déjà un combat actif
        if combat_state_service.has_active_combat(session_id):
            return {"error": "Un combat est déjà en cours pour cette session"}
        # Normaliser les participants (gérer les champs name/nom, health/hp)
        for p in participants:
            if 'id' not in p:
                p['id'] = str(uuid.uuid4())
            
            # Normaliser name -> nom
            if 'name' in p and 'nom' not in p:
                p['nom'] = p['name']
            elif 'nom' not in p:
                p['nom'] = p.get('id', 'Inconnu')
            
            # Normaliser health -> hp
            if 'health' in p and 'hp' not in p:
                p['hp'] = p['health']
            elif 'hp' not in p:
                p['hp'] = 1
            
            # Ajouter initiative si manquante
            if 'initiative' not in p:
                p['initiative'] = 10  # Valeur par défaut
            
            # Ajouter camp si manquant
            if 'camp' not in p:
                p['camp'] = 'adversaire'  # Par défaut adversaire sauf le premier qui est souvent le joueur
        
        # Le premier participant est souvent le joueur
        if participants and 'camp' not in participants[0]:
            participants[0]['camp'] = 'joueur'
        
        # Créer l'état initial du combat
        combat_state = combat_service.start_combat(participants)
        combat_state.combat_id = f"{session_id}_{uuid.uuid4().hex[:8]}"
        
        # Calculer l'initiative
        combat_state = combat_service.roll_initiative(combat_state)
        
        # Sauvegarder l'état initial
        combat_state_service.save_combat_state(session_id, combat_state)
        
        summary = combat_service.get_combat_summary(combat_state)
        
        # Ajouter des informations sur le premier participant
        current_participant = None
        if combat_state.current_turn < len(combat_state.initiative_order):
            current_id = combat_state.initiative_order[combat_state.current_turn]
            current_participant = next((p for p in combat_state.participants if p['id'] == current_id), None)
        
        summary["current_participant"] = current_participant
        summary["message"] = f"Combat démarré ! C'est au tour de {current_participant['nom'] if current_participant else 'Inconnu'}"
        
        return summary
        
    except Exception as e:
        log_debug("Erreur dans start_combat_tool", error=str(e))
        return {"error": str(e)}

# Tool definition removed - now handled directly by PydanticAI agent
