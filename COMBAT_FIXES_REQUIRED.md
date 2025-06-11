# CORRECTIONS URGENTES REQUISES - Gestion des Combats

## 🔴 PROBLÈMES CRITIQUES IDENTIFIÉS

### 1. Outils manquants pour la gestion des tours

**À ajouter dans `/back/tools/combat_tools.py` :**

```python
def end_turn_tool(ctx: RunContext[SessionService], combat_id: str) -> dict:
    """
    Termine explicitement le tour courant et passe au suivant.
    """
    # Charger l'état du combat
    # Appeler combat_service.end_turn()
    # Sauvegarder l'état
    # Retourner l'état mis à jour avec le joueur suivant
    pass

def check_combat_end_tool(ctx: RunContext[SessionService], combat_id: str) -> dict:
    """
    Vérifie automatiquement si le combat est terminé.
    """
    # Charger l'état du combat
    # Appeler combat_service.check_combat_end()
    # Si terminé, appeler combat_service.end_combat()
    # Retourner le statut
    pass

def apply_damage_tool(ctx: RunContext[SessionService], combat_id: str, target_id: str, amount: int) -> dict:
    """
    Applique des dégâts à un participant et vérifie l'état du combat.
    """
    # Charger l'état du combat
    # Appeler combat_service.apply_damage()
    # Vérifier automatiquement si le combat est terminé
    # Retourner l'état mis à jour
    pass

def get_combat_status_tool(ctx: RunContext[SessionService], combat_id: str) -> dict:
    """
    Retourne l'état complet du combat pour injection dans le prompt.
    """
    # Charger l'état du combat
    # Retourner un résumé structuré (round, qui joue, HP, etc.)
    pass
```

### 2. Modification du prompt système

**À ajouter dans `/back/agents/PROMPT.py` :**

```python
COMBAT_INSTRUCTIONS = """
### GESTION DES COMBATS

IMPORTANT : Durant un combat, tu DOIS :

1. **Toujours utiliser les outils** pour toute action de combat
2. **Demander les actions du joueur** à la fin de chaque tour
3. **Vérifier l'état du combat** après chaque action avec check_combat_end_tool
4. **Terminer explicitement** chaque tour avec end_turn_tool
5. **Ne JAMAIS conclure un combat** sans utiliser end_combat_tool

STRUCTURE OBLIGATOIRE d'un tour de combat :
1. Décrire la situation actuelle (basée sur l'état du combat)
2. Résoudre l'action du participant actuel
3. Vérifier si le combat continue avec check_combat_end_tool
4. Si le combat continue : terminer le tour avec end_turn_tool
5. Demander au joueur son action pour le tour suivant
6. ATTENDRE la réponse du joueur avant de continuer

Pour terminer un combat : utilise end_combat_tool avec la raison appropriée.
"""

# Ajouter COMBAT_INSTRUCTIONS au SYSTEM_PROMPT_TEMPLATE
```

### 3. Injection de l'état du combat

**À modifier dans `/back/agents/gm_agent_pydantic.py` :**

```python
def enrich_user_message_with_combat_state(user_message: str, combat_state: Optional[Dict]) -> str:
    """
    Enrichit le message avec l'état du combat actuel.
    """
    if not combat_state or combat_state.get('status') != 'en_cours':
        return user_message
    
    combat_context = f"""[État du Combat:
Round: {combat_state.get('round', 1)}
Tour de: {combat_state.get('current_participant', 'Inconnu')}
Participants vivants: {combat_state.get('alive_participants', [])}
Statut: {combat_state.get('status', 'en_cours')}
]

"""
    return combat_context + user_message
```

### 4. Persistance de l'état du combat

**À implémenter dans un nouveau service :**

```python
# /back/services/combat_state_service.py
class CombatStateService:
    """Service pour persister et charger l'état des combats."""
    
    def save_combat_state(self, session_id: str, combat_state: CombatState) -> None:
        """Sauvegarde l'état du combat dans un fichier JSON."""
        pass
    
    def load_combat_state(self, session_id: str) -> Optional[CombatState]:
        """Charge l'état du combat depuis un fichier JSON."""
        pass
    
    def delete_combat_state(self, session_id: str) -> None:
        """Supprime l'état du combat (combat terminé)."""
        pass
```

### 5. Modifications des outils existants

**Tous les outils de combat doivent :**
- Charger/sauvegarder automatiquement l'état du combat
- Inclure des vérifications de fin de combat
- Retourner des informations structurées sur l'état

### 6. Instructions spécifiques pour l'agent

**Le prompt doit contenir :**
- L'état complet du combat à chaque tour
- Des instructions claires sur quand s'arrêter
- L'obligation d'utiliser les outils pour toute action

## 🚨 ORDRE DE PRIORITÉ

1. **URGENT** : Ajouter end_turn_tool et check_combat_end_tool
2. **URGENT** : Modifier le prompt pour inclure les instructions de combat
3. **CRITIQUE** : Implémenter l'injection de l'état du combat
4. **IMPORTANT** : Ajouter la persistance de l'état
5. **IMPORTANT** : Tester avec un combat simple

## 📝 TEST DE VALIDATION

Après corrections, tester avec :
```
"Un orc attaque le personnage. Lance l'initiative et gère le premier tour de combat."
```

L'agent doit :
1. Lancer l'initiative
2. Résoudre l'action du premier participant
3. Demander l'action du joueur
4. ATTENDRE la réponse avant de continuer

## 🔗 COHÉRENCE AVEC LES RÈGLES

Ces corrections alignent l'implémentation avec :
- Section 6 : Structure du Combat (tours, initiative, actions)
- CombatManagement.md : Architecture recommandée
- Flux de données : LLM → Tools → CombatService → Persistance
