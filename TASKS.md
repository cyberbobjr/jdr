# Tasklist pour l'implémentation du plan de refactorisation du système de combat

## 1. Structure de fichiers pour le graphe

- [x] Créer le répertoire `back/graph/`
- [x] Créer `back/graph/__init__.py`
- [x] Créer `back/graph/dto/__init__.py`
- [x] Créer `back/graph/nodes/__init__.py`

## 2. DTOs essentiels

- [x] Créer `back/graph/dto/session.py` avec `GameState`, `SessionGraphState`, `PlayerMessagePayload`, `DispatchResult`
- [x] Créer `back/graph/dto/combat.py` avec `CombatSeedPayload`, `CombatTurnContinuePayload`, `CombatTurnEndPayload`, `CombatResultPayload` et sous-DTOs

## 3. Nœuds du graphe

- [x] Créer `back/graph/nodes/dispatcher_node.py` avec `DispatcherNode`
- [x] Créer `back/graph/nodes/narrative_node.py` avec `NarrativeNode`
- [x] Créer `back/graph/nodes/combat_node.py` avec `CombatNode`

## 4. Agents séparés

- [x] Créer `back/agents/narrative_agent.py` avec `NarrativeAgent` et ses outils
- [x] Créer `back/agents/combat_agent.py` avec `CombatAgent` et ses outils

## 5. Modifications au GameSessionService

- [x] Ajouter `save_history(kind: str, messages: list[ModelMessage])` dans `GameSessionService`
- [x] Ajouter `load_history(kind: str) -> list[ModelMessage]` dans `GameSessionService`
- [x] Ajouter `update_game_state(game_state: GameState)` dans `GameSessionService`
- [x] Ajouter `load_game_state() -> GameState` dans `GameSessionService`

## 6. Modification du routeur `/api/gamesession/play`

- [x] Modifier `back/routers/gamesession.py` pour utiliser le graphe au lieu de l'agent direct
- [x] Implémenter le chargement de `game_state.json` et construction de `SessionGraphState`
- [x] Implémenter l'exécution du graphe et gestion du streaming (implémentation basique fonctionnelle)
- [x] Implémenter le streaming temps réel avec run_stream des agents (bypass du graphe pour perf)

## 7. Persistance et stockage

- [x] Assurer la création de `game_state.json` à l'initialisation de session
- [x] Vérifier la séparation des fichiers JSONL (`history_narrative.jsonl` et `history_combat.jsonl`)

## 9. Corrections de types et imports

- [x] Corriger les types génériques des BaseNode pour cohérence (StateT, DepsT, RunEndT)
- [x] Uniformiser les imports absolus dans les nœuds du graphe
- [x] Corriger les imports relatifs dans utils/logger.py
- [x] Vérifier que tous les nœuds importent correctement

## 9. Documentation et architecture

- [x] Mettre à jour `README.md` avec la nouvelle architecture graphe
- [ ] Mettre à jour `ARCHITECTURE.md` avec diagrammes et explications
- [ ] Créer un diagramme Mermaid pour le graphe

## 10. Validation finale

- [x] Corriger les imports et types dans les fichiers du graphe
- [x] Exécuter `back/run_tests.sh` pour valider tous les tests (72/72 tests passent ✅)
- [x] Corriger la route `/play-stream` pour passer par le graphe Pydantic
- [x] Implémenter tous les tests de streaming (nominal + cas aux bornes)
- [ ] Tester manuellement une session complète (narration → combat → narration)
- [ ] Vérifier la persistance des états entre redémarrages</content>
<parameter name="filePath">/home/cyberbobjr/projects/jdr/TASKS.md
