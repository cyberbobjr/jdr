# JdR "Terres du Milieu" orchestré par LLM

Ce projet est un jeu de rôle (JdR) se déroulant dans les Terres du Milieu, où la narration et les mécaniques de jeu sont orchestrées par un Large Language Model (LLM) agissant comme Maître du Jeu (MJ).

## Architecture Générale

L'architecture s'articule autour d'un backend FastAPI et **PydanticAI**, avec une infrastructure DevOps complète. Les détails de la spécification technique se trouvent dans [instructions/openai-instructions.md](instructions/openai-instructions.md).

### Principes architecturaux
- **Services** (`back/services/`) : chaque service encapsule une responsabilité métier unique (SRP strict)
- **Agents** (`back/agents/`) : assemblent les outils et la mémoire, orchestrent la narration via le LLM avec PydanticAI
- **Routers** (`back/routers/`) : exposent les endpoints REST, délèguent toute la logique métier aux services
- **Mémoire** : découplée de l'agent, persistée via un store JSONL custom PydanticAI
- **Conventions** : SRP strict, aucune logique d'E/S dans les services, aucune règle de jeu dans les routers

### Documentation PydanticAI
- [PydanticAI Documentation](./pydanticai.md)
- [Gestion de la mémoire (mémoire persistante, stores, etc.)](./pydanticai.md)

## Architecture des Services

Le backend utilise une architecture modulaire avec séparation stricte des responsabilités (SRP) :

### Services Spécialisés

- **CharacterDataService** : Service spécialisé pour le chargement et la sauvegarde des données de personnage
- **CharacterBusinessService** : Service spécialisé pour la logique métier (XP, or, dégâts, soins)
- **InventoryService** : Service spécialisé pour la gestion d'inventaire (ajout, retrait, équipement)
- **EquipmentService** : Service spécialisé pour l'achat/vente d'équipement et gestion de l'argent

### Services de Support

- **CharacterPersistenceService** : Service centralisé pour la persistance des personnages (JSON)
- **SessionService** : Gestion des sessions de jeu (historique, personnage, scénario)
- **CombatService** : Gestion des mécaniques de combat
- **ScenarioService** : Gestion du déroulement des scénarios
- **CharacterCreationService** : Service dédié à la création de personnage

### Agents et Outils

- **Agent MJ** : Utilise `pydantic_ai.Agent` avec le modèle `openai:gpt-4o` et une mémoire persistante (JSONL)
- **Outils PydanticAI** : Tous les outils utilisent la signature `RunContext[SessionService]` pour accéder aux services
- **Mémoire** : Historique des conversations stocké en JSONL via `back/storage/pydantic_jsonl_store.py`

## Structure du Projet

```
.
├── back/                        # Back‑end FastAPI + PydanticAI
│   ├── __init__.py
│   ├── .coverage
│   ├── app.py                  # Point d'entrée FastAPI
│   ├── config.py               # Configuration centralisée
│   ├── config.yaml             # Fichier de configuration YAML
│   ├── main.py                 # Target uvicorn – démarre l'app + l'agent
│   ├── requirements.txt        # Dépendances Python
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── gm_agent_pydantic.py # Agent LLM Maître du Jeu (PydanticAI - production)
│   │   └── PROMPT.py           # Prompt système modulaire
│   ├── docs/
│   │   └── LOGGING_GUIDE.md    # Guide de logging
│   ├── models/
│   │   ├── __init__.py
│   │   ├── api_dto.py          # DTO pour l'API
│   │   ├── schema.py           # DTO exposés par l'API
│   │   └── domain/
│   │       ├── __init__.py
│   │       ├── base.py         # Classes de base
│   │       ├── character.py    # Modèle de personnage
│   │       ├── combat_state.py # État de combat
│   │       ├── combat_system_manager.py # Gestionnaire du système de combat
│   │       ├── equipment_manager.py # Gestionnaire d'équipement
│   │       ├── races_manager.py # Gestionnaire des races
│   │       ├── skills_manager.py # Gestionnaire des compétences
│   │       ├── spells_manager.py # Gestionnaire des sorts
│   │       └── stats_manager.py # Gestionnaire des statistiques
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── characters.py       # Endpoints pour la gestion des personnages
│   │   ├── creation.py         # Endpoints spécialisés pour la création de personnage
│   │   └── scenarios.py        # Endpoints pour la gestion des scénarios
│   ├── services/
│   │   ├── __init__.py
│   │   ├── character_business_service.py # Service spécialisé pour la logique métier (XP, or, dégâts)
│   │   ├── character_creation_service.py # Service dédié à la création de personnage
│   │   ├── character_data_service.py # Service spécialisé pour le chargement/sauvegarde des données
│   │   ├── character_persistence_service.py # Service centralisé pour la persistance des personnages (JSON)
│   │   ├── character_service.py # Service legacy en cours de refactoring
│   │   ├── combat_service.py    # Gestion des mécaniques de combat
│   │   ├── combat_state_service.py # Persistance de l'état des combats actifs
│   │   ├── equipment_service.py # Service spécialisé pour l'achat/vente d'équipement
│   │   ├── inventory_service.py # Service spécialisé pour la gestion d'inventaire
│   │   ├── item_service.py      # Gestion des objets
│   │   ├── scenario_service.py  # Gestion du déroulement des scénarios
│   │   ├── session_service.py   # Gestion des sessions de jeu (historique, personnage, scénario)
│   │   └── skill_service.py     # Gestion des compétences et de leurs jets
│   ├── storage/
│   │   ├── __init__.py
│   │   └── pydantic_jsonl_store.py # Store JSONL pour l'historique des messages PydanticAI
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_character_service_refactored.py # Test spécifique du service personnage
│   │   ├── test_logging.py     # Tests de logging
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   └── test_gm_agent_dependency_injection.py # Tests d'injection de dépendances pour l'agent
│   │   ├── domain/
│   │   │   └── __init__.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── test_characters_refactored.py # Tests refactorés pour les personnages
│   │   ├── services/
│   │   │   └── __init__.py
│   │   ├── storage/
│   │   │   └── __init__.py
│   │   ├── tools/
│   │   │   └── __init__.py
│   │   └── utils/
│   │       └── __init__.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── character_tools.py  # Outils pour la gestion des personnages
│   │   ├── combat_tools.py     # Outils de combat
│   │   ├── inventory_tools.py  # Outils pour l'inventaire (ajout, retrait, gestion d'objets)
│   │   └── skill_tools.py      # Outils pour les compétences
│   └── utils/
│       ├── __init__.py
│       ├── dice.py             # Fonctions pour les jets de dés
│       ├── exceptions.py       # Exceptions personnalisées
│       ├── logger.py           # Logger JSON (Grafana/Loki‑friendly)
│       ├── logging_tool.py     # Outil de logging pour l'agent
│       └── message_adapter.py  # Adaptateur de messages
├── front/                       # Front‑end Vue.js + TypeScript + TailwindCSS ✅
│   ├── src/                    # Code source de l'interface utilisateur
│   │   ├── components/         # Composants Vue réutilisables
│   │   │   ├── JdrDemo.vue     # Composant de démonstration avec lanceur de dés
│   │   │   ├── ChatMessage.vue # Composant générique d'affichage des messages LLM
│   │   │   ├── CharacterSheet.vue # Fiche de personnage
│   │   │   └── README-ChatMessage.md # Documentation du composant ChatMessage
│   │   ├── views/              # Pages/vues de l'application
│   │   │   ├── HomeView.vue    # Page d'accueil avec présentation des fonctionnalités
│   │   │   ├── Create.vue      # Création de personnage
│   │   │   ├── JeuView.vue     # Interface de jeu
│   │   │   ├── PersonnagesView.vue # Gestion des personnages
│   │   │   ├── ScenariosView.vue # Gestion des scénarios
│   │   │   ├── SessionsView.vue # Gestion des sessions
│   │   │   └── NouveauScenarioView.vue # Création de scénario
│   │   ├── core/               # Services et interfaces TypeScript ✅
│   │   │   ├── interfaces.ts   # Interfaces TypeScript basées sur OpenAPI JSON (strictement typées)
│   │   │   ├── api.ts          # Service API refactorisé avec nouvelles interfaces
│   │   │   └── api.test.ts     # Tests unitaires pour les interfaces et service API
│   │   ├── router/             # Configuration du routage Vue Router
│   │   ├── assets/             # Ressources CSS avec TailwindCSS configuré
│   │   ├── App.vue             # Composant racine avec navigation et thème JDR
│   │   └── main.ts             # Point d'entrée avec configuration FontAwesome
│   ├── tests/                  # Tests unitaires Vitest
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
│   ├── sessions/               # Historique des conversations et états des sessions de jeu
│   └── game/                   # Données de jeu (CSV)
├── docs/                        # Documentation du système de jeu
│   ├── 00 - introduction.md    # Introduction générale au système de jeu
│   ├── 01 - Caractéristiques.md
│   ├── 02 - Guide Complet des Compétences.md
│   ├── 02 - Races et cultures.md
│   ├── 04 - Equipement, armes et armures.md
│   ├── 05 - Styles de combat.md
│   ├── 06 - Magie.md           # Système de magie et sorts
│   ├── 07 - Sorts.md           # Liste détaillée des sorts
│   └── section-6-combat.md     # Règles de combat détaillées
├── instructions/                # Spécifications et instructions pour le développement
│   └── openai-instructions.md  # Document principal des spécifications techniques
└── README.md                    # Ce fichier
```

## Diagrams

### Architecture Diagram

This diagram illustrates the overall backend architecture, showing the flow from entry points to agents, services, and dependencies.

```mermaid
graph TD
    A[main.py] --> B[uvicorn]
    B --> C[app.py - FastAPI]
    C --> D[routers/ - characters, scenarios, creation]
    D --> E[services/ - character_service, scenario_service, etc.]
    E --> F[models/domain/ - Character, CombatState, EquipmentManager]
    E --> G[agents/ - gm_agent_pydantic.py]
    G --> H[tools/ - character_tools, combat_tools, etc.]
    G --> I[storage/ - pydantic_jsonl_store.py]
    C --> J[config.py - Config class]
    J --> K[config.yaml]
    J --> L[LLM Config]
    J --> M[Data Dir]
```

### Class Diagrams

#### Character Model

```mermaid
classDiagram
    class Character {
        +UUID id
        +str name
        +RaceData race
        +CultureData culture
        +Dict[str, int] stats
        +Dict[str, int] skills
        +int hp
        +int xp
        +float gold
        +List[Item] inventory
        +List[str] spells
        +Dict[str, int] culture_bonuses
        +str background
        +str physical_description
        +CharacterStatus status
        +str last_update
        +is_character_finalized(character_dict: Dict) bool
    }
    class RaceData {
        +str name
        +Dict bonuses
    }
    class CultureData {
        +str name
        +Dict bonuses
    }
    class Item {
        +str id
        +str name
        +float weight
        +float base_value
    }
    Character --> RaceData
    Character --> CultureData
    Character --> Item
```

#### CombatState Model

```mermaid
classDiagram
    class CombatState {
        +str combat_id
        +int round
        +List[Dict] participants
        +List[str] initiative_order
        +int current_turn
        +List[str] log
        +str status
        +Optional[str] end_reason
    }
```

#### EquipmentManager

```mermaid
classDiagram
    class EquipmentManager {
        -Dict _equipment_data
        +__init__()
        +_load_equipment_data() Dict
        +get_all_equipment() Dict
        +get_equipment_names() List[str]
        +get_weapons() Dict
        +get_armor() Dict
        +get_items() Dict
        +get_equipment_by_name(name: str) Optional[Dict]
    }
```

### Sequence Diagram for API Request Workflow

This diagram shows the sequence for a user playing a scenario turn via the API.

```mermaid
sequenceDiagram
    participant User
    participant Router as scenarios.py
    participant Service as scenario_service.py
    participant Agent as gm_agent_pydantic.py
    participant Tools as tools/*.py
    participant Storage as pydantic_jsonl_store.py

    User->>Router: POST /api/scenarios/play (session_id, message)
    Router->>Service: play_scenario(session_id, message)
    Service->>Agent: build_gm_agent_pydantic(session_id)
    Agent->>Agent: enrich_user_message_with_character/combat
    Agent->>Tools: Execute tools if needed (e.g., skill_check)
    Tools->>Storage: Access/update data if required
    Agent->>Service: Generate response via LLM
    Service->>Router: Return response
    Router->>User: Response with LLM output
```

## Tableau synthétique des routes API

| Méthode | Endpoint                                   | Arguments d'entrée                                                        | Retour principal / Description                                      |
|---------|--------------------------------------------|--------------------------------------------------------------------------|---------------------------------------------------------------------|
| GET     | /api/scenarios/                           | Aucun                                                                   | Liste des scénarios (`ScenarioList`)                                |
| GET     | /api/scenarios/sessions                   | Aucun                                                                   | Sessions actives (`ActiveSessionsResponse`)                         |
| GET     | /api/scenarios/{scenario_file}            | scenario_file (str, path)                                               | Contenu du fichier Markdown du scénario                             |
| POST    | /api/scenarios/start                      | scenario_name (str), character_id (str) (body JSON)                     | session_id, scenario_name, character_id, message, llm_response      |
| POST    | /api/scenarios/play                       | session_id (UUID, query), message (str, body JSON)                      | responses (list de messages générés par l'agent)                    |
| GET     | /api/scenarios/history/{session_id}       | session_id (UUID, path)                                                 | history (list de tous les messages de la session)                   |
| DELETE  | /api/scenarios/history/{session_id}/{message_index} | session_id (UUID, path), message_index (int, path) | Confirmation de suppression avec infos du message supprimé          |
| GET     | /api/characters/                          | Aucun                                                                   | Liste complète des personnages avec leurs fiches détaillées         |
| GET     | /api/characters/{character_id}            | character_id (UUID, path)                                              | Détail du personnage (`Character`)                                  |
| GET     | /creation/races                           | Aucun                                                                   | Liste des races disponibles                                         |
| GET     | /creation/skills                          | Aucun                                                                   | Structure complète des compétences                                  |
| GET     | /creation/equipments                      | Aucun                                                                   | Liste des équipements disponibles                                   |
| GET     | /creation/equipments-detailed             | Aucun                                                                   | Équipements avec détails complets                                   |
| GET     | /creation/spells                          | Aucun                                                                   | Liste des sorts disponibles                                         |
| POST    | /creation/allocate-attributes             | race_id (str, body JSON)                                                | Attributs alloués automatiquement                                   |
| POST    | /creation/check-attributes                | attributes (dict, body JSON)                                            | Validation de la distribution des points d'attributs                |
| POST    | /creation/new                             | Aucun                                                                   | Création d'un nouveau personnage avec ID                            |
| POST    | /creation/save                            | character_id (str), character (dict, body JSON) | Statut de sauvegarde du personnage |
| GET     | /creation/status/{character_id}           | character_id (str, path)                        | Statut de création du personnage |
| POST    | /creation/check-skills                    | skills (dict, body JSON)                        | Validation de la distribution des points de compétences |
| POST    | /creation/generate-name                   | character (dict, body JSON)                     | 5 noms générés par LLM |
| POST    | /creation/generate-background             | character (dict, body JSON)                     | 5 backgrounds générés par LLM |
| POST    | /creation/generate-physical-description   | character (dict, body JSON)                     | 5 descriptions physiques générées par LLM |
| GET     | /creation/stats                           | Aucun                                           | Données complètes des statistiques |
| DELETE  | /creation/delete/{character_id}           | character_id (str, path)                        | Suppression d'un personnage |
| POST    | /creation/update-skills                   | character_id (str), skills (dict, body JSON)    | Mise à jour des compétences |
| POST    | /creation/add-equipment                   | character_id (str), equipment_name (str, body JSON) | Ajout d'équipement avec déduction d'argent |
| POST    | /creation/remove-equipment                | character_id (str), equipment_name (str, body JSON) | Retrait d'équipement avec remboursement |
| POST    | /creation/update-money                    | character_id (str), amount (int, body JSON)     | Mise à jour de l'argent du personnage |

> Toutes les routes sont documentées dans le code source et la [documentation technique](instructions/openai-instructions.md).

## Documentation détaillée des API Scénarios

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

### 7. `DELETE /api/scenarios/history/{session_id}/{message_index}` - Supprimer un Message

**Description :** Supprime un message spécifique de l'historique d'une session.

**Paramètres :**
- `session_id` (path) : UUID de la session
- `message_index` (path) : Index du message à supprimer (base 0)

**Format de réponse :**
```json
{
    "message": "Message à l'index 2 supprimé avec succès...",
    "deleted_message_info": {
        "kind": "response",
        "timestamp": "2025-06-21T12:05:05.000000Z",
        "parts_count": 3,
        "model_name": "deepseek-chat"
    },
    "remaining_messages_count": 5
}
```

## Documentation détaillée des API Personnages

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
                "Nature": 65
            },
            "hp": 85,
            "gold": 200,
            "inventory": [
                {
                    "id": "sword_001",
                    "name": "Épée longue",
                    "weight": 1.5,
                    "base_value": 150.0
                }
            ],
            "spells": [],
            "culture_bonuses": {
                "Combat": 5,
                "Influence": 3
            }
        }
    ]
}
```

**Codes d'erreur :**
- `500` : Erreur interne du serveur lors de la récupération des personnages

### 2. `GET /api/characters/{character_id}` - Détail d'un Personnage

**Description :** Récupère le détail d'un personnage à partir de son identifiant unique (UUID).

**Paramètres :**
- `character_id` (UUID) : Identifiant unique du personnage

**Format de réponse :**
```json
{
  "id": "d7763165-4c03-4c8d-9bc6-6a2568b79eb3",
  "name": "Aragorn",
  "race": "Humain",
  "culture": "Gondor",
  "caracteristiques": { ... },
  "competences": { ... },
  "hp": 85,
  "xp": 0,
  "gold": 0,
  "inventory": [ ... ],
  "spells": [],
  "culture_bonuses": { ... }
}
```

**Codes d'erreur :**
- `404` : Personnage introuvable

## Service de création de personnage (2025)

- **character_creation_service.py** : Service dédié à la création de personnage, gérant l'allocation automatique des caractéristiques selon la race, la validation des points, et la fourniture des listes (races, compétences, cultures, équipements, sorts).
- **creation.py** : Routeur FastAPI spécialisé pour la création de personnage, exposant les routes pour chaque étape, l'enregistrement et le suivi du statut de création.

Ce module permet de découper la création de personnage en étapes validées côté backend, pour un front progressif et interactif.

## Gestion de l'historique et mémoire (PydanticAI)

- L'historique des messages (sessions de jeu) est stocké en JSONL via `back/storage/pydantic_jsonl_store.py`.
- La sérialisation utilise `to_jsonable_python` (PydanticAI) ; la désérialisation utilise `ModelMessagesTypeAdapter.validate_python`.
- Seuls les messages utilisateur, assistant et outils sont persistés : le prompt système n'est jamais dupliqué.
- La structure de chaque message respecte strictement le schéma PydanticAI (voir [pydanticai.md](./pydanticai.md)).

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

## Tests

- Les tests unitaires et d'intégration sont dans `back/tests/`.
- Tous les tests ont été migrés et validés pour PydanticAI.
- Organisation par responsabilité : `agents/`, `tools/`, `services/`, `domain/`, etc.
- **Frontend** : Tests Vitest pour les composants Vue.js, dont ChatMessage

## Système de Prévention des Sessions Dupliquées (2025)

### Fonctionnalité
Le système empêche automatiquement la création de sessions dupliquées en détectant les combinaisons existantes de `character_name` + `scenario_name`. Cette protection évite les conflits de données et assure l'intégrité des sessions de jeu.

### Codes de réponse

| Code HTTP | Signification | Description |
|-----------|---------------|-------------|
| **200** | Succès | Session créée avec succès |
| **404** | Scénario introuvable | Le fichier de scénario n'existe pas |
| **409** | Session dupliquée | Une session existe déjà pour cette combinaison personnage/scénario |

## Migration 2025 : Suppression de la clé `state` dans les fiches de personnage

- **Structure simplifiée** : Les fiches de personnage JSON n'utilisent plus de clé intermédiaire `state`. Tous les champs du personnage (nom, race, caractéristiques, inventaire, etc.) sont désormais à la racine du fichier JSON.
- **Compatibilité** : Toute la logique de lecture/écriture, les services et les tests ont été adaptés pour fonctionner sans la clé `state`.
- **Conséquences** :
  - Les anciennes méthodes manipulant la section `state` (ex : `load_character_state`, `update_character_state`, etc.) ont été supprimées.
  - Les tests unitaires et d'intégration ont été corrigés pour écrire/lire les personnages directement à la racine.
  - Toute fiche de personnage doit désormais respecter ce format :

```json
{
  "id": "d1a4064a-c956-4d46-b6ea-5e688cf2f78b",
  "name": "Test Hero",
  "race": "Humain",
  "culture": "Rurale",
  "caracteristiques": {"Force": 10, ...},
  "competences": {"Athletisme": 5},
  "hp": 42,
  "xp": 0,
  "gold": 0,
  "inventory": [],
  "spells": [],
  "culture_bonuses": {},
  "created_at": "2025-06-14T19:08:31.148010",
  "last_update": "2025-06-14T19:08:31.148010",
  "current_step": "creation",
  "status": "en_cours"
}
```

- **Avantages** :
  - Lecture/écriture plus simple et plus rapide
  - Moins d'ambiguïté sur la structure des données
  - Maintenance facilitée pour les évolutions futures

> ⚠️ Toute référence à la clé `state` dans le code ou les tests doit être supprimée pour garantir la compatibilité.

## Ajout des skills de culture (2025)

- Un nouveau groupe de compétences "Culture" a été ajouté dans `data/skills_for_llm.json`.
- Chaque trait de culture issu de `data/races_and_cultures.json` est désormais représenté comme un skill de culture, avec une propriété `culture` précisant la ou les cultures associées.
- Ces skills de culture ne peuvent être acquis naturellement que par les personnages issus de la culture correspondante.
- La structure d'un skill de culture est identique à celle des autres skills : `name`, `description`, `stats`, `examples`, et `culture`.

- **Affinités culturelles pour les compétences** :
  - Les affinités entre cultures et compétences sont centralisées dans `data/skills_affinities.json`.
  - Un script (`tools/generate_skills_with_affinities.py`) injecte automatiquement la propriété `cultures` dans chaque compétence de `skills_for_llm.json`.
  - Pour ajouter une nouvelle culture ou compétence, il suffit de mettre à jour le mapping dans `skills_affinities.json` puis de relancer le script.
  - Ce système garantit la cohérence et la facilité de maintenance du fichier des compétences.

## Tests

- Les tests unitaires et d'intégration sont organisés dans `back/tests/` avec la structure suivante :
  - `agents/` : Tests des agents PydanticAI
  - `domain/` : Tests des modèles du domaine
  - `routers/` : Tests des endpoints REST
  - `services/` : Tests des services métier
  - `storage/` : Tests de la persistance
  - `tools/` : Tests des outils PydanticAI
  - `utils/` : Tests des utilitaires

- **Frontend** : Tests Vitest pour les composants Vue.js avec 100% de réussite

## Développement

### Installation
```bash
cd back
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Lancement
```bash
# Backend
cd back
uvicorn main:app --reload

# Frontend
cd front
npm install
npm run dev
```

### Tests
```bash
# Backend
cd back
pytest tests/ -v

# Frontend
cd front
npm test
```

## Architecture Technique

### Backend (FastAPI + PydanticAI)
- **FastAPI** : Framework web moderne pour les API REST
- **PydanticAI** : Framework d'agents LLM avec outils structurés
- **Pydantic** : Validation des données et modèles
- **Uvicorn** : Serveur ASGI pour le déploiement

### Système de Logging
Le projet utilise un système de logging centralisé et configurable pour tracer les erreurs, informations de débogage et événements métier.

#### Configuration
- **Fichier** : `back/config.yaml` (section `logging`)
- **Format** : JSON structuré compatible Grafana/Loki
- **Niveaux** : DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Rotation** : Fichiers avec taille maximale et archivage automatique

#### Utilisation
```python
from back.config import get_logger

# Obtenir un logger pour le module
logger = get_logger(__name__)

# Utilisation standard
logger.info("Opération réussie", action="create_character", character_id="123")
logger.error("Erreur de validation", error=str(e), character_id="123")
logger.debug("Détails de débogage", variable=value)
```

#### Fonctions spécialisées
```python
from back.utils.logger import log_debug, log_info, log_error, log_warning

# Logging avec contexte métier
log_debug("Chargement du personnage", character_id="123", action="load")
log_info("Personnage créé avec succès", character_name="Aragorn")
log_error("Échec de sauvegarde", error=str(e))
```

#### Modules avec logging complet
- ✅ Services : `character_service.py`, `character_data_service.py`, etc.
- ✅ Outils : Tous les fichiers `tools/*.py`
- ✅ Routers : `scenarios.py`, `characters.py`
- ✅ Stockage : `pydantic_jsonl_store.py`

### Frontend (Vue.js + TypeScript)
- **Vue.js 3** : Framework JavaScript progressif
- **TypeScript** : Typage statique pour la robustesse
- **TailwindCSS** : Framework CSS utilitaire
- **Vite** : Outil de build rapide

### Stockage
- **JSONL** : Historique des conversations PydanticAI
- **JSON** : Fiches de personnage et données de jeu
- **Markdown** : Scénarios et documentation

## Contribution

Le projet suit une architecture modulaire avec séparation stricte des responsabilités :
- Les **routers** ne contiennent que la logique HTTP
- Les **services** encapsulent la logique métier
- Les **agents** orchestrent les interactions LLM
- Les **outils** fournissent des fonctionnalités spécifiques aux agents
- Les **modèles** définissent la structure des données

Toute modification doit respecter ces principes architecturaux et être accompagnée de tests appropriés.
