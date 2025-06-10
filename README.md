# JdR "Terres du Milieu" orchestré par LLM

Ce projet vise à créer un jeu de rôle (JdR) se déroulant dans les Terres du Milieu, où la narration et les mécaniques de jeu sont orchestrées par un Large Language Model (LLM) agissant comme Maître du Jeu (MJ).

## Architecture Générale

L'architecture s'articule autour d'un backend FastAPI et **PydanticAI** (remplaçant complètement Haystack 3.x et LangChain), et d'une infrastructure DevOps. Les détails de la spécification technique se trouvent dans [instructions/openai-instructions.md](instructions/openai-instructions.md).

### Principes architecturaux
- **Services** (`back/services/`) : chaque service encapsule une responsabilité métier (inventaire, personnage, combat, scénario, session).
- **Agents** (`back/agents/`) : assemblent les outils et la mémoire, orchestrent la narration via le LLM avec PydanticAI.
- **Routers** (`back/routers/`) : exposent les endpoints REST, délèguent toute la logique métier aux services.
- **Mémoire** : découplée de l'agent, persistée via un store JSONL custom PydanticAI.
- **Conventions** : SRP strict, aucune logique d'E/S dans les services, aucune règle de jeu dans les routers.

### Documentation PydanticAI
- [PydanticAI Documentation](./pydanticai.md)
- [Gestion de la mémoire (mémoire persistante, stores, etc.)](./pydanticai.md)

## Migration PydanticAI (2025) - TERMINÉE ✅

- **Stack 100% PydanticAI :** Suppression complète de Haystack 3.x, migration de tous les outils et de l'agent MJ vers PydanticAI.
- **Agent MJ :** Utilise `pydantic_ai.Agent` avec le modèle `openai:gpt-4o` et une mémoire persistante (JSONL) via `SessionService`.
- **Outils :** Tous les 13 outils migrés vers PydanticAI avec signature `RunContext[SessionService]` :
  - **Compétences :** `skill_check_with_character` (refactorisé pour supprimer la redondance avec `character_perform_skill_check`)
  - **Personnage :** `character_apply_xp`, `character_add_gold`, `character_take_damage`
  - **Inventaire :** `inventory_add_item`, `inventory_remove_item`
  - **Combat :** `roll_initiative_tool`, `perform_attack_tool`, `resolve_attack_tool`, `calculate_damage_tool`, `end_combat_tool`
  - **Utilitaires :** `logging_tool`
- **Tests :** Suite complète de tests dans `/back/tests/` validant la migration et la refactorisation.
- **Mémoire :** Historique des conversations stocké en JSONL via `back/storage/pydantic_jsonl_store.py`.
  - **Prompt système non dupliqué :** Le prompt système n'est jamais stocké dans l'historique JSONL. Il est injecté dynamiquement par l'agent à chaque appel.
  - **Compatibilité stricte :** Structure de chaque message respecte le schéma PydanticAI (sérialisation via `to_jsonable_python`).

## Structure du Projet

```
.
├── back/                        # Back‑end FastAPI + PydanticAI
│   ├── app.py                  # Point d'entrée FastAPI
│   ├── main.py                 # Target uvicorn – démarre l'app + l'agent
│   ├── config.py               # Variables d'environnement
│   ├── models/                 # Schémas Pydantic & objets métier
│   │   ├── domain/             # Reprise des fichiers .py uploadés (1 concept = 1 fichier)
│   │   └── schema.py           # DTO exposés par l'API
│   ├── services/               # Logique métier unitaire (SRP)
│   │   ├── character_persistence_service.py # Service centralisé pour la persistance des personnages (JSON)
│   │   ├── inventory_service.py # Gestion de l'inventaire des personnages
│   │   ├── character_service.py # Gestion des personnages (création, évolution, etc.)
│   │   ├── combat_service.py    # Gestion des mécaniques de combat
│   │   ├── skill_service.py     # Gestion des compétences et de leurs jets
│   │   ├── scenario_service.py  # Gestion du déroulement des scénarios
│   │   └── session_service.py   # Gestion des sessions de jeu (historique, personnage, scénario)
│   ├── tools/                  # Outils PydanticAI (signature RunContext[SessionService])
│   │   ├── inventory_tools.py  # Outils pour l'inventaire (ajout, retrait, gestion d'objets)
│   │   ├── combat_tools.py     # Outils pour le combat
│   │   ├── skill_tools.py      # Outils pour les compétences (refactorisé)
│   │   └── character_tools.py  # Outils pour la gestion des personnages
│   ├── agents/                 # Assemblage Agent PydanticAI + mémoire
│   │   └── gm_agent_pydantic.py # Agent LLM Maître du Jeu (PydanticAI - production)
│   ├── routers/                # Endpoints REST (FastAPI "router")
│   │   ├── characters.py       # Endpoints pour la gestion des personnages
│   │   ├── inventory.py        # Endpoints pour la gestion de l'inventaire
│   │   ├── scenarios.py        # Endpoints pour la gestion des scénarios
│   │   └── combat.py           # Endpoints pour la gestion du combat
│   ├── storage/                # Persistance JSON & ressources
│   │   ├── file_storage.py     # CRUD thread‑safe (aiofiles + asyncio.Lock) pour la persistance des données
│   │   └── pydantic_jsonl_store.py # Store JSONL pour l'historique des messages PydanticAI
│   ├── utils/                  # Aides génériques
│   │   ├── dice.py             # Fonctions pour les jets de dés
│   │   └── logger.py           # Logger JSON (Grafana/Loki‑friendly)
│   └── tests/                  # Tests unitaires et d'intégration (pytest)
│       ├── agents/             # Tests pour les agents PydanticAI
│       │   └── test_gm_agent_consolidated.py # ⭐ Suite consolidée de 29 tests (100% réussite)
│       ├── domain/             # Tests pour les modèles du domaine
│       │   └── test_caracteristiques.py
│       ├── routers/            # Tests pour les endpoints REST
│       ├── services/           # Tests pour les services
│       │   └── test_session_service.py
│       ├── storage/            # Tests pour la persistance
│       ├── tools/              # Tests consolidés pour les outils PydanticAI
│       │   ├── test_character_tools_consolidated.py    # Tests pour les outils de personnage
│       │   ├── test_combat_tools_consolidated.py       # Tests pour les outils de combat
│       │   ├── test_inventory_tools_consolidated.py    # Tests pour les outils d'inventaire
│       │   ├── test_skill_tools_consolidated.py        # Tests pour les outils de compétences
│       │   └── test_all_tools_integration_consolidated.py # Tests d'intégration généraux
│       ├── utils/              # Tests pour les utilitaires
│       ├── cleanup_test_sessions.py # 🧹 Script de nettoyage automatique des sessions de test
│       ├── test_complete_migration.py # Test de migration générale
│       ├── conftest.py         # Configuration pytest + hooks de nettoyage automatique
│       └── __init__.py
├── data/                        # Données persistantes du jeu
│   ├── characters/             # Fiches des personnages joueurs et non-joueurs
│   ├── combat/                 # États des combats en cours
│   ├── scenarios/              # Fichiers Markdown décrivant les scénarios
│   └── sessions/               # Historique des conversations et états des sessions de jeu
├── instructions/                # Spécifications et instructions pour le développement
│   └── openai-instructions.md  # Document principal des spécifications techniques
├── HaystackMemoryDoc.md         # Documentation détaillée sur la mémoire Haystack
└── README.md                    # Ce fichier
```

## Factorisation et Organisation (2025) - TERMINÉE ✅

### Factorisation du Code Dupliqué
- **CharacterPersistenceService** : Service centralisé pour la persistance des personnages dans les fichiers JSON
  - Extraction de ~80 lignes de code dupliqué dans `CharacterService`
  - API uniforme : `load_character_data()`, `save_character_data()`, `update_character_state()`, etc.
  - Gestion d'erreurs robuste et logging centralisé
  - Respect du principe SRP (Single Responsibility Principle)

### Consolidation des Tests
- **Regroupement par catégorie** : Les 17 fichiers de test éparpillés dans `/back/tests/tools/` ont été consolidés en 5 fichiers organisés :
  - `test_character_tools_consolidated.py` : Tests des outils de personnage (XP, or, dégâts)
  - `test_combat_tools_consolidated.py` : Tests des outils de combat (initiative, attaque, dégâts)
  - `test_inventory_tools_consolidated.py` : Tests des outils d'inventaire (ajout/suppression d'objets)
  - `test_skill_tools_consolidated.py` : Tests des outils de compétences (jets de dés, difficultés)
  - `test_all_tools_integration_consolidated.py` : Tests d'intégration généraux

- **Suppression des fichiers obsolètes** : 7 fichiers vides et plusieurs fichiers redondants supprimés
- **Structure maintenant maintenable** : 38 tests organisés et fonctionnels (100% de succès)

## Organisation des Tests ✅

**Tous les fichiers de test ont été organisés et déplacés vers `/back/tests/` avec la structure suivante :**

### Tests des Agents (`/back/tests/agents/`)
- **`test_agent_refactored.py`** : Tests de l'agent refactorisé
- **`test_pydantic_agent.py`** : Tests de l'agent PydanticAI
- Tests d'intégration de l'agent MJ avec les outils PydanticAI

### Tests des Outils (`/back/tests/tools/`)
- **Tests de compétences** : `test_skill_direct.py`, `test_skill_functionality.py`, `test_skill_refactoring.py`
- **Tests d'inventaire** : `test_inventory_tool.py`, `test_inventory_tools.py`
- **Tests de combat** : `test_combat_tools.py`, `test_calculate_damage.py`
- **Tests de personnages** : `test_character_tools.py`
- **Tests d'intégration** : `test_all_tools.py`, `test_all_tools_integration.py`
- **Tests de refactorisation** : `test_refactoring_simple.py`

### Tests Généraux (`/back/tests/`)
- **`test_complete_migration.py`** : Tests de validation de la migration complète PydanticAI

## Tableau synthétique des routes API

| Méthode | Endpoint                                   | Arguments d'entrée                                                        | Retour principal / Description                                      |
|---------|--------------------------------------------|--------------------------------------------------------------------------|---------------------------------------------------------------------|
| GET     | /api/scenarios/                           | Aucun                                                                   | Liste des scénarios (`ScenarioList`)                                |
| GET     | /api/scenarios/{scenario_file}            | scenario_file (str, path)                                               | Contenu du fichier Markdown du scénario                             |
| POST    | /api/scenarios/start                      | scenario_name (str), character_id (str) (body JSON)                     | session_id, scenario_name, character_id, message, llm_response      |
| POST    | /api/scenarios/play                       | session_id (UUID, query), message (str, body JSON)                      | responses (list de messages générés par l'agent)                    |
| GET     | /api/scenarios/history/{session_id}       | session_id (UUID, path)                                                 | history (list de tous les messages de la session)                   |
| GET     | /api/characters/                          | Aucun                                                                   | Liste des personnages (`CharacterList`)                             |
| POST    | /api/combat/attack                        | attacker_id (str), target_id (str), attack_value (int), combat_state (dict, body) | combat_state (état du combat mis à jour)                            |

> Toutes les routes sont documentées dans le code source et la [documentation technique](instructions/openai-instructions.md).

## Gestion de l'historique et mémoire (PydanticAI)

- L'historique des messages (sessions de jeu) est stocké en JSONL via `back/storage/pydantic_jsonl_store.py`.
- La sérialisation utilise `to_jsonable_python` (PydanticAI) ; la désérialisation utilise `ModelMessagesTypeAdapter.validate_python`.
- Seuls les messages utilisateur, assistant et outils sont persistés : le prompt système n'est jamais dupliqué.
- La structure de chaque message respecte strictement le schéma PydanticAI (voir [pydanticai.md](./pydanticai.md)).
- Les tests unitaires valident la compatibilité stricte avec PydanticAI (voir `back/tests/storage/test_pydantic_jsonl_store.py`).

## Outils PydanticAI

### Compétences (`back/tools/skill_tools.py`)
- **`skill_check_with_character`** : Effectue un test de compétence pour le personnage de la session courante en récupérant ses données via CharacterService.

### Combat (`back/tools/combat_tools.py`)
- **`roll_initiative_tool`** : Calcule l'ordre d'initiative des personnages
- **`perform_attack_tool`** : Effectue un jet d'attaque
- **`resolve_attack_tool`** : Résout une attaque (attaque > défense)
- **`calculate_damage_tool`** : Calcule les dégâts infligés en tenant compte des modificateurs
- **`end_combat_tool`** : Termine un combat

### Inventaire (`back/tools/inventory_tools.py`)
- **`inventory_add_item`** : Ajoute un objet à l'inventaire du personnage
- **`inventory_remove_item`** : Retire un objet de l'inventaire du personnage

### Personnage (`back/tools/character_tools.py`)
- **`character_apply_xp`** : Applique les points d'expérience au personnage
- **`character_add_gold`** : Ajoute de l'or au portefeuille du personnage
- **`character_take_damage`** : Applique des dégâts au personnage (réduit ses PV)

### Utilitaires
- **`logging_tool`** : Outil de logging pour l'agent

## Tests

- Les tests unitaires et d'intégration sont dans `back/tests/`.
- Tous les tests ont été migrés et validés pour PydanticAI.
- Organisation par responsabilité : `agents/`, `tools/`, `services/`, `domain/`, etc.
- Exemple : `back/tests/tools/test_all_tools_integration.py` vérifie le bon fonctionnement de tous les outils PydanticAI.

## Système de Prévention des Sessions Dupliquées (2025)

### Fonctionnalité
Le système empêche automatiquement la création de sessions dupliquées en détectant les combinaisons existantes de `character_name` + `scenario_name`. Cette protection évite les conflits de données et assure l'intégrité des sessions de jeu.

### Codes de réponse

| Code HTTP | Signification | Description |
|-----------|---------------|-------------|
| **200** | Succès | Session créée avec succès |
| **404** | Scénario introuvable | Le fichier de scénario n'existe pas |
| **409** | Session dupliquée | Une session existe déjà pour cette combinaison personnage/scénario |

## 🧪 Tests et Qualité

### Suite de Tests Consolidée

Le projet dispose d'une **suite de tests complète et automatisée** avec un système de nettoyage intégré :

#### 🎯 Tests de l'Agent GM (29 tests - 100% réussite)
```bash
# Exécution standard
python -m pytest back/tests/agents/test_gm_agent_consolidated.py

# Avec nettoyage automatique (PowerShell)
.\run_tests_clean.ps1 -Verbose
```

#### 📊 Couverture Complète
- ✅ **Initialisation de l'agent** (5 tests)
- ✅ **Edge cases d'initialisation** (4 tests)  
- ✅ **Prompt système et règles** (5 tests)
- ✅ **Enrichissement de messages** (3 tests)
- ✅ **Tests des outils** (5 tests)
- ✅ **Edge cases des outils** (4 tests)
- ✅ **Tests avancés** (3 tests)

#### 🧹 Nettoyage Automatique
Le système empêche la pollution de `/data/sessions` avec :
- **Détection automatique** des fichiers de test
- **Nettoyage sélectif** (préserve les sessions réelles)
- **Hooks pytest** pour nettoyage automatique
- **Script PowerShell** avec options avancées

#### 📈 Métriques de Qualité
- **Taux de réussite :** 100% (29/29 tests)
- **Temps d'exécution :** ~5.5 minutes
- **Nettoyage :** 0 fichier de pollution après tests
- **Documentation :** Tests auto-documentés avec docstrings

Pour plus de détails, voir [RAPPORT_TESTS_FINALISES.md](RAPPORT_TESTS_FINALISES.md).

---

*Ce README reflète l'état actuel du projet après la migration complète vers PydanticAI et l'organisation des tests.*
