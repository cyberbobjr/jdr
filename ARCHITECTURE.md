# Architecture Overview - JdR "Terres du Milieu"

## System Architecture

**JdR "Terres du Milieu"** is a Role-Playing Game set in Middle-earth where narration and game mechanics are orchestrated by Large Language Models (LLMs) acting as Game Master. The system uses a **strict service-based architecture** following SOLID principles with clear separation between presentation, business logic, and data layers.

### Technology Stack

**Backend:**

- **Framework**: FastAPI (async REST API)
- **AI Framework**: PydanticAI (agent orchestration with OpenAI-compatible APIs)
- **Validation**: Pydantic V2 (comprehensive type safety)
- **Data Persistence**: YAML (game configuration), JSONL (conversation history), JSON (character sheets)
- **LLM Provider**: OpenAI-compatible API (DeepSeek default)

**Frontend:**

- Removed for now; will be recreated later.

## Architectural Principles

1. **Strict SRP (Single Responsibility Principle)**: One responsibility per file/service
2. **No I/O logic in services**: Services handle business logic, not file operations
3. **No game rules in routers**: Routers only handle HTTP logic
4. **Type Safety Everywhere**: Pydantic models throughout
5. **English-only codebase**: Post-migration standard (from French)

## Layer Architecture

### 1. Presentation Layer (FastAPI Routers)

**Location**: `back/routers/`

Three main routers expose REST endpoints:

- **`characters.py`** (`/api/characters/`) - Character management and retrieval
- **`scenarios.py`** (`/api/scenarios/`) - Scenario flow, gameplay, session management
- **`creation.py`** (`/api/creation/`) - Character creation wizard with LLM-assisted generation

**Responsibilities**: HTTP logic only - request validation, response formatting, delegation to services.

### 2. Business Logic Layer (Services)

**Location**: `back/services/`

Services encapsulate unique business responsibilities:

**Character Management Services:**

- `CharacterDataService` - I/O operations (loading/saving)
- `CharacterService` - Business logic (XP, gold, damage, healing) and inventory management
- `EquipmentService` - Equipment buy/sell and money management

**Game Services:**

- `GameSessionService` - Game session management (history, character, scenario)
- `ScenarioService` - Scenario flow orchestration
- `ItemService` - Item management
- `SkillAllocationService` - Automated skill distribution logic

### 3. Graph & Agent Layer (PydanticAI + Pydantic Graph)

**Location**: `back/graph/` and `back/agents/`

The system uses **Pydantic Graph** to orchestrate the game flow between Narrative and Combat modes.

**Graph Nodes** (`back/graph/nodes/`):

- **`NarrativeNode`**: Handles story progression using `NarrativeAgent`.
- **`CombatNode`**: Handles combat turns using `CombatAgent`.
- **`DispatcherNode`**: Routes the session to the correct node based on state.

**Specialized Agents** (`back/agents/`):

- **`NarrativeAgent`**: PydanticAI agent for storytelling. Can trigger combat via `CombatSeedPayload`.
- **`CombatAgent`**: PydanticAI agent for combat resolution. Returns `CombatTurnContinuePayload` or `CombatTurnEndPayload`.
- **`GenericAgent`** (`gm_agent_pydantic.py`): Simple agent for content generation (names, backgrounds) without session context.

**Agent Tools** (`back/tools/`):

- `character_tools.py` - apply_xp, add_gold, take_damage
- `combat_tools.py` - roll_initiative, perform_attack, resolve_attack, calculate_damage, end_combat
- `equipment_tools.py` - add_item, remove_item (via EquipmentService)
- `skill_tools.py` - skill_check_with_character

### 4. Domain Model Layer

**Location**: `back/models/domain/`

**Core Models:**

- `character.py` - Simplified character model (6 attributes, 3–20 per stat, bonus = (value - 10) // 2)
- `combat_state.py` - Combat state tracking
- `npc.py` - NPC models

**Data Managers** (load YAML configuration):

- `stats_manager.py` - Stats info, value range (3–20), bonus formula
- `unified_skills_manager.py` - Unified interface for skill groups and definitions
- `races_manager.py` - Available races, cultures, stat bonuses
- `equipment_manager.py` - Weapons, armor, items with stats
- `spells_manager.py` - Available spells by sphere
- `combat_system_manager.py` - Combat rules and damage calculations

### 5. Storage Layer

**Location**: `back/storage/`

- `PydanticJsonlStore` - Custom JSONL store for PydanticAI conversation history
- Character sheets: `data/characters/*.json`
- Combat states: `data/combat/*.json` (managed via Graph state)
- Session history: `data/sessions/*.jsonl`
- Game data: `back/gamedata/*.yaml`

## Data Flow

### Character Creation Flow

```text
User (Frontend) → Creation Router → Managers (races/skills/stats/equipment)
                                  ↓
                        CharacterDataService → JSON file
```

### Gameplay Flow

```text
User prompt → Scenarios Router → GameSessionService → GM Agent (PydanticAI)
                                                      ↓
                                              Tools (character, combat, inventory, skills)
                                                      ↓
                                              Services (business logic)
                                                      ↓
                                              Persistence (JSONL, JSON)
                                                      ↓
                                              Response to user
```

## Character System

- **6 Core Attributes**: STR, CON, AGI, INT, WIS, CHA (range 3-20, total 400 points)
- **Skills**: 6 skill groups, 40 development points, uniform cost (1 point = 1 rank)
- **Combat**: Initiative-based, 1 major + 1 minor + 1 reaction per turn
- **Persistence**: JSON character sheets, JSONL combat states

## Configuration Management

**Centralized Config**: `back/config.yaml` + `back/config.py`

- Data directory paths
- LLM configuration (model, endpoint, API key)
- Application settings
- Environment variable overrides supported

## Frontend Architecture

Frontend is currently removed and will be recreated later.

## Key Design Patterns

1. **Dependency Injection**: Services passed as parameters, no global state
2. **Repository Pattern**: Separation of data access (DataService) from business logic (BusinessService)
3. **Agent Pattern**: LLM agent with tools for dynamic decision-making
4. **Manager Pattern**: YAML data managers for game configuration
5. **Message History Pattern**: JSONL-based conversation persistence

---

**Version**: 2.0 (Major Refactoring Complete)  
**Language**: English (post-migration)  
**Framework**: PydanticAI + FastAPI
