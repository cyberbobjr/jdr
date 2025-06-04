from typing import List, Dict
from back.models.domain.combat_state import CombatState

class CombatService:
    """
    ### CombatService
    **Description :** Service métier pour manipuler l’état du combat (démarrage, attaque, dégâts, fin, etc.).
    """
    def start_combat(self, participants: List[Dict]) -> CombatState:
        """
        ### start_combat
        **Description :** Initialise un nouveau combat avec les participants donnés.
        **Paramètres :**
        - `participants` (List[Dict]) : Liste des participants (id, nom, PV, etc.).
        **Retour :** Instance de CombatState initialisée.
        """
        initiative_order = sorted(participants, key=lambda c: c.get('initiative', 0), reverse=True)
        return CombatState(
            combat_id="TODO-GENERATE-ID",
            participants=participants,
            initiative_order=[c['id'] for c in initiative_order],
            log=[],
            status="en_cours",
            round=1,
            current_turn=0
        )

    def roll_initiative(self, combat_state: CombatState) -> CombatState:
        """
        ### roll_initiative
        **Description :** Calcule et met à jour l’ordre d’initiative des participants.
        **Paramètres :**
        - `combat_state` (CombatState) : État courant du combat.
        **Retour :** CombatState mis à jour.
        """
        initiative_order = sorted(combat_state.participants, key=lambda c: c.get('initiative', 0), reverse=True)
        combat_state.initiative_order = [c['id'] for c in initiative_order]
        combat_state.log.append("Nouvel ordre d'initiative calculé.")
        return combat_state

    def perform_attack(self, combat_state: CombatState, attacker_id: str, target_id: str, attack_value: int) -> CombatState:
        """
        ### perform_attack
        **Description :** Applique une attaque d’un participant sur un autre.
        **Paramètres :**
        - `combat_state` (CombatState) : État courant du combat.
        - `attacker_id` (str) : ID de l’attaquant.
        - `target_id` (str) : ID de la cible.
        - `attack_value` (int) : Valeur d’attaque.
        **Retour :** CombatState mis à jour.
        """
        combat_state.log.append(f"{attacker_id} attaque {target_id} (valeur: {attack_value})")
        # La logique métier réelle serait ici
        return combat_state

    def apply_damage(self, combat_state: CombatState, target_id: str, amount: int) -> CombatState:
        """
        ### apply_damage
        **Description :** Applique des dégâts à un participant.
        **Paramètres :**
        - `combat_state` (CombatState) : État courant du combat.
        - `target_id` (str) : ID de la cible.
        - `amount` (int) : Points de dégâts à appliquer.
        **Retour :** CombatState mis à jour.
        """
        for p in combat_state.participants:
            if p['id'] == target_id:
                p['hp'] = max(0, p.get('hp', 0) - amount)
                combat_state.log.append(f"{target_id} subit {amount} dégâts.")
        return combat_state

    def end_turn(self, combat_state: CombatState) -> CombatState:
        """
        ### end_turn
        **Description :** Passe au tour suivant dans l’ordre d’initiative.
        **Paramètres :**
        - `combat_state` (CombatState) : État courant du combat.
        **Retour :** CombatState mis à jour.
        """
        combat_state.current_turn = (combat_state.current_turn + 1) % len(combat_state.initiative_order)
        if combat_state.current_turn == 0:
            combat_state.round += 1
        combat_state.log.append("Tour terminé.")
        return combat_state

    def check_combat_end(self, combat_state: CombatState) -> bool:
        """
        ### check_combat_end
        **Description :** Vérifie si le combat est terminé (tous les adversaires ou joueurs hors de combat).
        **Paramètres :**
        - `combat_state` (CombatState) : État courant du combat.
        **Retour :** True si le combat est terminé, False sinon.
        """
        # Exemple simple : combat terminé si un camp n’a plus de participants vivants
        players_alive = any(p.get('camp') == 'joueur' and p.get('hp', 1) > 0 for p in combat_state.participants)
        enemies_alive = any(p.get('camp') == 'adversaire' and p.get('hp', 1) > 0 for p in combat_state.participants)
        return not (players_alive and enemies_alive)

    def end_combat(self, combat_state: CombatState, reason: str) -> CombatState:
        """
        ### end_combat
        **Description :** Termine explicitement le combat avec une raison (victoire, fuite, reddition, etc.).
        **Paramètres :**
        - `combat_state` (CombatState) : État courant du combat.
        - `reason` (str) : Raison de la fin du combat.
        **Retour :** CombatState mis à jour (statut = "termine").
        """
        combat_state.status = "termine"
        combat_state.end_reason = reason
        combat_state.log.append(f"Combat terminé ({reason})")
        return combat_state

    def get_combat_summary(self, combat_state: CombatState) -> dict:
        """
        ### get_combat_summary
        **Description :** Retourne un résumé de l’état du combat (pour le prompt ou l’UI).
        **Paramètres :**
        - `combat_state` (CombatState) : État courant du combat.
        **Retour :** Dictionnaire résumant l’état du combat.
        """
        return {
            "combat_id": combat_state.combat_id,
            "round": combat_state.round,
            "participants": combat_state.participants,
            "initiative_order": combat_state.initiative_order,
            "current_turn": combat_state.current_turn,
            "status": combat_state.status,
            "end_reason": combat_state.end_reason
        }
