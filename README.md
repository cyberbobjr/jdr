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
- **Prompt système modulaire :** Le prompt système est externalisé dans `back/agents/PROMPT.py` pour faciliter la maintenance et les modifications. Le module contient le template et les fonctions utilitaires pour l'injection du contenu des scénarios et des règles.

## Architecture d'Inventaire Refactorisée (2025) - TERMINÉE ✅

- **Migration vers CharacterService :** Toutes les méthodes d'inventaire (`add_item`, `remove_item`, `equip_item`, `unequip_item`) migrées de `InventoryService` vers `CharacterService`.
- **Architecture orientée instance :** `CharacterService` transformé d'un service statique en service d'instance avec un `character_id` spécifique au constructeur.
- **Intégration SessionService :** `CharacterService` instancié comme propriété de `SessionService` pour une cohésion maximale.
- **Outils unifiés :** Tous les outils utilisent `ctx.deps.character_service` pour accéder aux fonctionnalités de personnage et d'inventaire.
- **Modèle enrichi :** Champs `xp` et `gold` ajoutés au modèle `Character` avec gestion des valeurs par défaut.
- **Tests complets :** 18/18 tests passés validant la nouvelle architecture (services + outils).
- **Suppression du code obsolète :** Fichier `inventory_service.py` supprimé, références mises à jour partout.

## Interfaces Frontend TypeScript (2025) - TERMINÉE ✅

- **Interfaces strictement typées :** Génération automatique des interfaces TypeScript basées sur le fichier OpenAPI JSON du backend.
- **Service API refactorisé :** Suppression de la duplication de code, utilisation des interfaces centralisées dans `front/src/core/interfaces.ts`.
- **Validation robuste :** Validation des UUIDs, gestion d'erreurs typée avec `ApiErrorResponse`, méthodes utilitaires pour la robustesse.
- **Tests complets :** Suite de tests unitaires (10/10) validant les interfaces, la validation, et la conversion de types.
- **Documentation :** Interfaces documentées en français selon les standards du projet, noms de méthodes en anglais.

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
│   │   ├── character_service.py # Gestion des personnages (création, évolution, etc.)
│   │   ├── combat_service.py    # ✅ Gestion complète des mécaniques de combat (initiative, attaques, dégâts, fin automatique)
│   │   ├── combat_state_service.py # ✅ Persistance de l'état des combats actifs (sauvegarde/chargement JSON, nettoyage automatique)
│   │   ├── skill_service.py     # Gestion des compétences et de leurs jets
│   │   ├── scenario_service.py  # Gestion du déroulement des scénarios
│   │   └── session_service.py   # Gestion des sessions de jeu (historique, personnage, scénario)
│   ├── tools/                  # Outils PydanticAI (signature RunContext[SessionService])
│   │   ├── inventory_tools.py  # Outils pour l'inventaire (ajout, retrait, gestion d'objets)
│   │   ├── combat_tools.py     # ✅ 6 outils de combat complets (start, end_turn, check_end, apply_damage, get_status, end_combat)
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
├── front/                       # Front‑end Vue.js + TypeScript + TailwindCSS ✅
│   ├── src/                    # Code source de l'interface utilisateur
│   ├── src/                    # Code source de l'interface utilisateur
│   │   ├── components/         # Composants Vue réutilisables
│   │   │   ├── JdrDemo.vue     # Composant de démonstration avec lanceur de dés
│   │   │   ├── ChatMessage.vue # ✅ Composant générique d'affichage des messages LLM
│   │   │   └── README-ChatMessage.md # Documentation du composant ChatMessage
│   │   ├── views/              # Pages/vues de l'application
│   │   │   ├── HomeView.vue    # Page d'accueil avec présentation des fonctionnalités
│   │   │   └── AboutView.vue   # Page à propos
│   │   ├── core/               # Services et interfaces TypeScript ✅
│   │   │   ├── interfaces.ts   # ✅ Interfaces TypeScript basées sur OpenAPI JSON (strictement typées)
│   │   │   ├── api.ts          # ✅ Service API refactorisé avec nouvelles interfaces (validation UUID, gestion d'erreurs)
│   │   │   └── api.test.ts     # ✅ Tests unitaires pour les interfaces et service API (10/10 tests)
│   │   ├── router/             # Configuration du routage Vue Router
│   │   ├── assets/             # Ressources CSS avec TailwindCSS configuré
│   │   ├── App.vue             # Composant racine avec navigation et thème JDR
│   │   └── main.ts             # Point d'entrée avec configuration FontAwesome
│   ├── tests/                  # Tests unitaires Vitest (19 tests, 100% réussite)
│   │   ├── setup.ts            # Configuration des tests avec mocks
│   │   ├── App.test.ts         # Tests du composant principal
│   │   ├── components/         # Tests des composants
│   │   └── views/              # Tests des vues
│   ├── package.json            # Dépendances npm et scripts
│   ├── vite.config.ts          # Configuration Vite
│   ├── vitest.config.ts        # Configuration des tests
│   ├── tailwind.config.js      # Configuration TailwindCSS
│   └── README.md               # Documentation frontend détaillée
├── data/                        # Données persistantes du jeu
│   ├── characters/             # Fiches des personnages joueurs et non-joueurs
│   ├── combat/                 # États des combats en cours
│   ├── scenarios/              # Fichiers Markdown décrivant les scénarios
│   └── sessions/               # Historique des conversations et états des sessions de jeu
├── docs/                        # Documentation du système de jeu
│   ├── 00 - introduction.md    # Introduction générale au système de jeu
│   ├── 01 - Caractéristiques, Races, Professions et Cultures.md
│   ├── 02 - Guide Complet des Compétences.md
│   ├── 03 - Talents.md         # Système des talents spéciaux
│   ├── 04 - Equipement, armes et armures.md
│   ├── 05 - Styles de combat.md
│   ├── 06 - Magie.md           # Système de magie et sorts
│   ├── 07 - Sorts.md           # Liste détaillée des sorts
│   └── section-6-combat.md     # Règles de combat détaillées
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
| GET     | /api/scenarios/sessions                   | Aucun                                                                   | Sessions actives (`ActiveSessionsResponse`)                         |
| GET     | /api/scenarios/{scenario_file}            | scenario_file (str, path)                                               | Contenu du fichier Markdown du scénario                             |
| POST    | /api/scenarios/start                      | scenario_name (str), character_id (str) (body JSON)                     | session_id, scenario_name, character_id, message, llm_response      |
| POST    | /api/scenarios/play                       | session_id (UUID, query), message (str, body JSON)                      | responses (list de messages générés par l'agent)                    |
| GET     | /api/scenarios/history/{session_id}       | session_id (UUID, path)                                                 | history (list de tous les messages de la session)                   |
| GET     | /api/characters/                          | Aucun                                                                   | Liste complète des personnages avec leurs fiches détaillées         |
| POST    | /api/combat/attack                        | attacker_id (str), target_id (str), attack_value (int), combat_state (dict, body) | combat_state (état du combat mis à jour)                            |

> Toutes les routes sont documentées dans le code source et la [documentation technique](instructions/openai-instructions.md).

## Documentation détaillée des API Scenarios

### 1. `GET /api/scenarios/` - Liste des Scénarios

**Description :** Récupère la liste de tous les scénarios disponibles et en cours.

**Paramètres :** Aucun

**Format de réponse :**
```json
{
    "scenarios": [
        {
            "name": "Les_Pierres_du_Passe.md",
            "status": "available",
            "session_id": null,
            "scenario_name": null,
            "character_name": null
        },
        {
            "name": "Les_Pierres_du_Passe.md - Galadhwen",
            "status": "in_progress", 
            "session_id": "12345678-1234-5678-9012-123456789abc",
            "scenario_name": "Les_Pierres_du_Passe.md",
            "character_name": "Galadhwen"
        }
    ]
}
```

### 2. `GET /api/scenarios/sessions` - Sessions Actives

**Description :** Récupère la liste de toutes les sessions de jeu en cours.

**Paramètres :** Aucun

**Format de réponse :**
```json
{
    "sessions": [
        {
            "session_id": "12345678-1234-5678-9012-123456789abc",
            "scenario_name": "Les_Pierres_du_Passe.md",
            "character_id": "87654321-4321-8765-2109-987654321def",
            "character_name": "Galadhwen"
        }
    ]
}
```

### 3. `GET /api/scenarios/{scenario_file}` - Contenu de Scénario

**Description :** Récupère le contenu complet d'un scénario au format Markdown.

**Paramètres :**
- `scenario_file` (path) : Nom du fichier de scénario (ex: `Les_Pierres_du_Passe.md`)

**Format de réponse :** Chaîne de caractères contenant le Markdown

**Codes d'erreur :** `404` - Scénario introuvable

### 4. `POST /api/scenarios/start` - Démarrer un Scénario

**Description :** Démarre un nouveau scénario avec un personnage spécifique.

**Paramètres (body JSON) :**
```json
{
    "scenario_name": "Les_Pierres_du_Passe.md",
    "character_id": "87654321-4321-8765-2109-987654321def"
}
```

**Format de réponse :**
```json
{
    "session_id": "12345678-1234-5678-9012-123456789abc",
    "scenario_name": "Les_Pierres_du_Passe.md",
    "character_id": "87654321-4321-8765-2109-987654321def",
    "message": "Scénario 'Les_Pierres_du_Passe.md' démarré avec succès...",
    "llm_response": "**Esgalbar, place centrale du village**..."
}
```

**Codes d'erreur :**
- `409` : Session déjà existante pour ce scénario et ce personnage
- `404` : Scénario ou personnage introuvable

### 5. `POST /api/scenarios/play` - Jouer un Tour

**Description :** Envoie un message au Maître du Jeu pour continuer le scénario.

**Paramètres :**
- `session_id` (query) : UUID de la session
- Body JSON : `{"message": "j'examine la fontaine"}`

**Format de réponse :**
```json
{
    "response": [
        {
            "parts": [
                {
                    "content": "j'examine la fontaine",
                    "timestamp": "2025-06-09T17:50:53.234253Z",
                    "part_kind": "user-prompt"
                }
            ],
            "kind": "request"
        },
        {
            "parts": [
                {
                    "content": "**Examen des inscriptions sur la fontaine**...",
                    "part_kind": "text"
                }
            ],
            "kind": "response",
            "usage": {
                "requests": 1,
                "request_tokens": 6447,
                "response_tokens": 480,
                "total_tokens": 6927
            },
            "model_name": "deepseek-chat",
            "timestamp": "2025-06-09T17:51:00Z"
        }
    ]
}
```

**Types de `part_kind` :**
- `"system-prompt"` : Instructions système envoyées au LLM
- `"user-prompt"` : Message du joueur 
- `"text"` : Réponse textuelle du LLM
- `"tool-call"` : Appel d'un outil par le LLM
- `"tool-return"` : Résultat de l'appel d'outil

**Codes d'erreur :**
- `404` : Session introuvable
- `500` : Erreur lors de la génération de la réponse

### 6. `GET /api/scenarios/history/{session_id}` - Historique de Session

**Description :** Récupère l'historique complet des messages d'une session.

**Paramètres :**
- `session_id` (path) : UUID de la session

**Format de réponse :** Identique à `/scenarios/play` mais contient tous les messages depuis le début de la session.

**Codes d'erreur :**
- `404` : Session introuvable
- `500` : Erreur lors de la récupération de l'historique

## Documentation détaillée des API Characters

### 1. `GET /api/characters/` - Liste des Personnages

**Description :** Récupère la liste de tous les personnages disponibles dans le système avec leurs informations complètes.

**Paramètres :** Aucun

**Format de réponse :**
```json
{
    "characters": [
        {
            "id": "d7763165-4c03-4c8d-9bc6-6a2568b79eb3",
            "name": "Aragorn",
            "race": "Humain",
            "culture": "Gondor",
            "profession": "Rôdeur",
            "caracteristiques": {
                "Force": 85,
                "Constitution": 80,
                "Agilité": 70,
                "Rapidité": 75,
                "Volonté": 80,
                "Raisonnement": 65,
                "Intuition": 75,
                "Présence": 70
            },
            "competences": {
                "Perception": 60,
                "Combat": 75,
                "Survie": 55,
                "Nature": 65,
                "Influence": 40,
                "Athlétique": 50
            },
            "hp": 85,            "inventory": [
                {
                    "id": "sword_001",
                    "name": "Coutelas",
                    "item_type": "Arme",
                    "price_pc": 200,
                    "weight_kg": 0.5,
                    "description": "Lame courte large",
                    "category": "Couteau",
                    "damage": "1d4",
                    "protection": null,
                    "armor_type": null,
                    "quantity": 1,
                    "is_equipped": true,
                    "crafting_time": "2 jours",
                    "special_properties": null
                },
                {
                    "id": "boots_001",
                    "name": "Bottes de cuir",
                    "item_type": "Materiel",
                    "price_pc": 50,
                    "weight_kg": 1.0,
                    "description": "Chaussures en cuir",
                    "category": "Vetement",
                    "damage": null,
                    "protection": null,
                    "armor_type": null,
                    "quantity": 1,
                    "is_equipped": true,
                    "crafting_time": "-",
                    "special_properties": null
                }
            ],
            "spells": [],
            "equipment_summary": {
                "total_weight": 8.5,
                "total_value": 500.0,
                "remaining_gold": 200.0
            },
            "culture_bonuses": {
                "Combat": 5,
                "Influence": 3,
                "Nature": 2
            }
        }
    ]
}
```

**Codes d'erreur :**
- `500` : Erreur interne du serveur lors de la récupération des personnages

**Notes :**
- Retourne tous les personnages créés avec leurs fiches complètes
- Inclut les caractéristiques, compétences, inventaire détaillé et bonus culturels  
- L'inventaire contient des objets `Item` complets avec propriétés détaillées :
  - **Type d'objet** : Materiel, Arme, Armure, etc.
  - **Propriétés économiques** : Prix en pièces de cuivre, poids en kg
  - **Propriétés de jeu** : Dégâts pour armes, protection pour armures
  - **Statut d'équipement** : `is_equipped` pour savoir si l'objet est actuellement utilisé
- L'`equipment_summary` fournit un résumé des totaux (poids, valeur, or restant)
- **Conversion automatique** : Les anciens formats `equipment: List[str]` sont automatiquement convertis vers `inventory: List[Item]`

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

## 💬 Interface de Chat LLM Généralisée (2025) ✅

### Composant ChatMessage
Un composant Vue.js générique pour afficher les messages de conversation basé sur l'interface `ConversationMessage` :

#### Fonctionnalités
- **Messages typés** : Support complet de l'interface TypeScript `ConversationMessage[]`
- **Affichage hiérarchique** : Chaque message contient des parties (`MessagePart[]`) avec types distincts
- **Types de messages** : Différenciation visuelle pour `request`, `response`, `system`, `error`
- **Types de parties** : Support des `system-prompt`, `user-prompt`, `text`, `tool-call`, `tool-return`
- **Formatage intelligent** : Contenu code pour les outils, markdown basique pour le texte
- **Informations de debug** : Affichage optionnel des détails d'usage des tokens
- **Timestamps** : Formatage automatique en français pour messages et parties

#### Structure supportée
- **Interface stricte** : `ConversationMessage` avec `MessagePart[]` typés
- **Usage des tokens** : `MessageUsage` avec détails de consommation LLM
- **Métadonnées** : `model_name`, `vendor_details`, `vendor_id` optionnels
- **Références dynamiques** : Support des `dynamic_ref` dans les parties

#### Props du composant
```typescript
interface Props {
  messages: ConversationMessage[]  // Tableau de messages à afficher
  showDebugInfo?: boolean         // Affichage des détails techniques
}
```

#### Intégration
- Composant réutilisable pour tous les historiques de conversation
- Compatible avec les réponses d'API `PlayScenarioResponse` et `GetScenarioHistoryResponse`
- Styling CSS moderne avec différenciation visuelle par type
- Gestion des références temporelles et métadonnées LLM

## Tests

- Les tests unitaires et d'intégration sont dans `back/tests/`.
- Tous les tests ont été migrés et validés pour PydanticAI.
- Organisation par responsabilité : `agents/`, `tools/`, `services/`, `domain/`, etc.
- Exemple : `back/tests/tools/test_all_tools_integration.py` vérifie le bon fonctionnement de tous les outils PydanticAI.
- **Frontend** : Tests Vitest pour les composants Vue.js, dont ChatMessage

## ⚔️ Système de Combat Complet (2025) ✅

### Architecture Combat
Le système de combat a été entièrement implémenté et résout le problème des boucles infinies de l'agent LLM. Il respecte l'architecture **CombatManagement.md** avec une séparation stricte entre logique métier (Python) et narration (LLM).

#### Services de Combat
- **`CombatService`** : Logique métier complète (initiative, attaques, dégâts, fin automatique)
- **`CombatStateService`** : Persistance JSON des états de combat (sauvegarde/chargement/nettoyage)

#### Outils de Combat PydanticAI (6 outils)
```python
# Démarrage et gestion des tours
start_combat_tool(participants: list[dict]) -> dict
end_turn_tool(combat_id: str) -> dict
check_combat_end_tool(combat_id: str) -> dict

# Application des effets
apply_damage_tool(combat_id: str, target_id: str, amount: int) -> dict
get_combat_status_tool(combat_id: str) -> dict
end_combat_tool(combat_id: str, reason: str) -> dict
```

#### Fonctionnalités Clés
- **Persistance automatique** : État sauvegardé à chaque action
- **Détection automatique de fin** : Combat terminé quand un camp n'a plus de participants vivants  
- **Injection de contexte** : État du combat injecté automatiquement dans le prompt LLM
- **Instructions structurées** : Le prompt système guide l'agent avec la structure obligatoire des tours
- **Normalisation des participants** : Support des formats `name`/`nom` et `health`/`hp`

#### Structure Obligatoire d'un Tour (Prompt)
```
1. Décrire la situation (get_combat_status_tool)
2. Résoudre l'action du participant actuel  
3. Appliquer les dégâts (apply_damage_tool)
4. Vérifier la fin (check_combat_end_tool)
5. Si continue : terminer le tour (end_turn_tool)
6. Demander l'action du joueur
7. ATTENDRE la réponse avant de continuer
```

#### Tests Complets
- **19 tests unitaires** : `CombatStateService` (10) + `combat_tools` (9)
- **Test d'intégration** : Validation du flux complet de combat
- **100% de réussite** : Tous les tests passent avec nettoyage automatique

### Résolution du Problème de Boucle Infinie ✅
Avant : L'agent LLM tournait en boucle sans s'arrêter lors des combats
Après : L'agent utilise les outils appropriés, s'arrête automatiquement en fin de tour, et attend l'action du joueur

**Test validé** : L'agent démarre un combat, gère les tours correctement, applique les dégâts, détecte la fin automatiquement et nettoie l'état.

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

## Frontend Vue.js (2025) - TERMINÉ ✅

### Architecture et technologies
- **Vue.js 3.5.13** avec Composition API et TypeScript
- **TailwindCSS 4.1.8** avec configuration PostCSS optimisée
- **FontAwesome 6.7.2** pour les icônes thématiques JDR
- **Vue Router** pour la navigation SPA
- **Vite 6.3.5** pour le développement et build rapide
- **Vitest 3.2.3** avec jsdom pour les tests unitaires

### Fonctionnalités implémentées
- ✅ **Interface moderne** avec thème sombre et design JDR
- ✅ **Composants interactifs** : lanceur de dés D20, fiches de personnage
- ✅ **Navigation responsive** avec header/footer
- ✅ **Animations CSS** et transitions fluides
- ✅ **Tests complets** : 19 tests unitaires (100% réussite)

### Structure frontend
```
front/
├── src/
│   ├── components/JdrDemo.vue      # Composant de démonstration avec lanceur de dés
│   ├── views/HomeView.vue          # Page d'accueil avec présentation
│   ├── router/index.ts             # Configuration des routes
│   ├── assets/main.css             # Styles TailwindCSS
│   ├── App.vue                     # Composant racine
│   └── main.ts                     # Point d'entrée avec FontAwesome
├── tests/ (19 tests)               # Tests unitaires complets
├── package.json                    # Configuration npm
├── vite.config.ts                  # Configuration Vite
├── vitest.config.ts               # Configuration des tests
├── tailwind.config.js             # Configuration TailwindCSS
└── postcss.config.js              # Configuration PostCSS (corrigée)
```

### Intégration backend
Le frontend est prêt pour l'intégration avec l'API FastAPI + PydanticAI :
- Structure modulaire pour l'ajout de nouvelles fonctionnalités
- Configuration TypeScript stricte pour une intégration API robuste
- Tests unitaires pour assurer la stabilité lors des développements futurs

---
