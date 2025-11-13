# GitHub Copilot Instructions - JdR "Terres du Milieu"

## Project Overview

This is a Role-Playing Game (RPG) set in Middle-earth, where the narration and game mechanics are orchestrated by a Large Language Model (LLM) acting as Game Master (GM). The project uses FastAPI for the backend with **PydanticAI** as the agent framework.

## Architecture Principles

### Backend Architecture (FastAPI + PydanticAI)

The architecture is organized around:

- **Services** (`back/services/`): Each service encapsulates a unique business responsibility (Strict SRP)
- **Agents** (`back/agents/`): Assemble tools and memory, orchestrate narration via LLM with PydanticAI
- **Routers** (`back/routers/`): Expose REST endpoints, delegate all business logic to services
- **Memory**: Decoupled from the agent, persisted via custom JSONL store for PydanticAI
- **Models** (`back/models/domain/`): Pydantic models for domain objects with strict validation

### Key Conventions

- **Strict SRP**: One responsibility per file/service
- **No I/O logic in services**: Services handle business logic, not file operations directly
- **No game rules in routers**: Routers only handle HTTP logic
- **English naming**: All code, models, and data use English (post-migration from French)

## Recent Major Changes

### 1. Data Format Migration (JSON → YAML)

**Status**: ✅ Complete

All game data has been migrated from JSON to YAML format and is now stored in the `data/` directory:

- `data/stats.yaml` - Character statistics (6 attributes: Strength, Constitution, Agility, Intelligence, Wisdom, Charisma)
- `data/skills_for_llm.yaml` - Skills organized in 6 groups (Combat, General, Stealth, Social, Magic, Knowledge)
- `data/races_and_cultures.yaml` - Available races and cultures
- `data/equipment.yaml` - Weapons, armor, and items
- `data/spells.yaml` - Magic spells
- `data/combat_system.yaml` - Combat mechanics
- `data/skills_affinities.yaml` - Culture-skill affinities
- `data/skill_groups.yaml` - Skill group definitions

**Source**: YAML files are also maintained in `back/gamedata/` for development
**Backup**: Original JSON files preserved in `data/json_backup/`

### 2. French to English Translation

**Status**: ✅ Complete

All game characteristics, skills, and domain models have been translated to English:

**Characteristics (Caractéristiques → Stats)**:
- Force → Strength
- Constitution → Constitution (unchanged)
- Agilité → Agility  
- Rapidité → (removed/merged)
- Intelligence → Intelligence (unchanged)
- Volonté → Wisdom
- Raisonnement → (removed/merged)
- Intuition → (removed/merged)
- Présence → Charisma

**Skills (Compétences → Skills)**:
All skill names and descriptions translated to English in `skills_for_llm.yaml`

**Domain Models**:
- `caracteristiques` → `stats`
- `competences` → `skills`
- `nom` → `name`
- Field names in all Pydantic models now use English

### 3. Simplified Character System (V2)

**Status**: ✅ Character V2 model created, migration in progress

New simplified system in `back/models/domain/character_v2.py`:

**Stats System**:
- 6 main attributes (down from 8)
- 400 total points (down from 550)
- Simplified bonus calculation

**Skills System**:
- 6 skill groups (down from 9)
- 40 development points (down from 84)
- Uniform cost: 1 point = 1 rank

**Validation**:
- Strict Pydantic validation with `field_validator` and `model_validator`
- Type safety with UUID, datetime, and Enum types
- Combat stats automatically calculated

## Technology Stack

### Backend

- **Framework**: FastAPI 0.111+
- **Agent Framework**: PydanticAI (not LangChain)
- **Validation**: Pydantic V2
- **Data Format**: YAML (loaded with PyYAML)
- **Persistence**: 
  - JSONL for conversation history (PydanticAI messages)
  - JSON for character sheets
  - Markdown for scenarios
- **LLM Provider**: OpenAI-compatible API (configurable, defaults to DeepSeek)

### Frontend

- **Framework**: Vue.js 3
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Build Tool**: Vite

## Directory Structure

```
back/
├── agents/                      # PydanticAI agents
│   ├── gm_agent_pydantic.py    # Game Master agent
│   └── PROMPT.py               # Modular system prompt
├── models/
│   ├── domain/                 # Domain models (Pydantic)
│   │   ├── character.py        # Legacy character model
│   │   ├── character_v2.py     # New simplified character model
│   │   ├── npc_v2.py          # NPC model
│   │   ├── combat_state_v2.py # Combat state model
│   │   ├── stats_manager.py   # Stats data manager
│   │   ├── skills_manager.py  # Skills data manager
│   │   ├── races_manager.py   # Races data manager
│   │   ├── equipment_manager.py # Equipment data manager
│   │   ├── spells_manager.py  # Spells data manager
│   │   └── combat_system_manager.py # Combat system manager
│   ├── api_dto.py             # API DTOs
│   └── schema.py              # API schemas
├── routers/                   # FastAPI routers
│   ├── characters.py         # Character management endpoints
│   ├── creation.py          # Character creation endpoints
│   └── scenarios.py         # Scenario/gameplay endpoints
├── services/                # Business logic services
│   ├── character_service.py           # Legacy character service
│   ├── character_data_service.py      # Character I/O operations
│   ├── character_business_service.py  # Character business logic
│   ├── character_creation_service.py  # Character creation
│   ├── character_persistence_service.py # Character persistence
│   ├── combat_service.py             # Combat mechanics
│   ├── combat_state_service.py       # Combat state persistence
│   ├── equipment_service.py          # Equipment buy/sell
│   ├── inventory_service.py          # Inventory management
│   ├── item_service.py               # Item management
│   ├── scenario_service.py           # Scenario flow
│   ├── session_service.py            # Session management
│   └── skill_service.py              # Skill checks
├── storage/
│   └── pydantic_jsonl_store.py # JSONL store for PydanticAI history
├── tools/                     # PydanticAI tools
│   ├── character_tools.py    # Character manipulation tools
│   ├── combat_tools.py       # Combat tools
│   ├── inventory_tools.py    # Inventory tools
│   └── skill_tools.py        # Skill check tools
├── utils/
│   ├── dice.py              # Dice rolling functions
│   ├── exceptions.py        # Custom exceptions
│   ├── logger.py            # JSON logger (Grafana/Loki compatible)
│   └── message_adapter.py   # Message format adapter
├── gamedata/                 # Game data (YAML files)
│   ├── stats.yaml
│   ├── skills_for_llm.yaml
│   ├── races_and_cultures.yaml
│   ├── equipment.yaml
│   ├── spells.yaml
│   └── combat_system.yaml
├── config.py                # Configuration management
├── config.yaml              # Configuration file
├── app.py                   # FastAPI app
└── main.py                  # Entry point (uvicorn)

data/                        # Runtime data
├── characters/             # Character JSON files
├── combat/                # Combat state files
├── scenarios/             # Scenario markdown files
├── sessions/              # Session history (JSONL)
└── json_backup/           # Backup of original JSON game data

front/
├── src/
│   ├── components/        # Vue components
│   │   ├── ChatMessage.vue      # Generic LLM message display
│   │   ├── CharacterSheet.vue   # Character sheet
│   │   └── JdrDemo.vue         # Demo component
│   ├── views/            # Application views
│   ├── core/
│   │   ├── interfaces.ts # TypeScript interfaces (OpenAPI-based)
│   │   └── api.ts       # API service
│   └── router/          # Vue Router config
```

## Data Loading and Managers

All game data is loaded through manager classes that read YAML files:

### StatsManager (`back/models/domain/stats_manager.py`)
- Loads `data/stats.yaml`
- Provides: stat info, bonus table, cost table, starting points (400)
- Methods: `get_description()`, `get_bonus()`, `calculate_cost()`

### SkillsManager (`back/models/domain/skills_manager.py`)
- Loads `data/skills_for_llm.yaml`
- Provides: 6 skill groups with skills
- Methods: `get_all_skills()`, `get_skill_by_name()`, `get_skills_by_group()`

### RacesManager (`back/models/domain/races_manager.py`)
- Loads `data/races_and_cultures.yaml`
- Provides: available races, cultures, bonuses
- Methods: `get_all_races()`, `get_race_by_name()`, `get_cultures_for_race()`

### EquipmentManager (`back/models/domain/equipment_manager.py`)
- Loads `data/equipment.yaml`
- Provides: weapons, armor, items
- Methods: `get_all_equipment()`, `get_equipment_by_name()`, `get_weapons()`, `get_armor()`

### SpellsManager (`back/models/domain/spells_manager.py`)
- Loads `data/spells.yaml`
- Provides: available spells, organized by sphere
- Methods: `get_all_spells()`, `get_spell_by_name()`, `get_spells_by_sphere()`

### CombatSystemManager (`back/models/domain/combat_system_manager.py`)
- Loads `data/combat_system.yaml`
- Provides: combat rules, actions, damage calculations
- Methods: Combat-related rule lookups

## PydanticAI Integration

### Agent Structure

The GM Agent uses PydanticAI with:

```python
from pydantic_ai import Agent, RunContext

# Agent creation
agent = Agent(
    model='openai:gpt-4o',  # Or DeepSeek via OpenAI-compatible API
    deps_type=SessionService,
    system_prompt=build_system_prompt(scenario_name)
)

# Tools use RunContext
@agent.tool
async def skill_check_with_character(
    ctx: RunContext[SessionService],
    skill_name: str,
    difficulty: int = 50
) -> str:
    """Perform a skill check for the character"""
    session_service = ctx.deps
    # Tool implementation
```

### Memory/History

- **Format**: JSONL (one message per line)
- **Location**: `data/sessions/{session_id}.jsonl`
- **Store**: Custom `PydanticJsonlStore` class
- **Content**: Only user, assistant, and tool messages (system prompt not duplicated)
- **Serialization**: Uses `to_jsonable_python()` from PydanticAI
- **Deserialization**: Uses `ModelMessagesTypeAdapter.validate_python()`

### Key Tools

1. **skill_tools.py**: `skill_check_with_character` - Perform skill checks
2. **combat_tools.py**: Initiative, attacks, damage calculation, combat end
3. **inventory_tools.py**: Add/remove items from inventory
4. **character_tools.py**: Apply XP, add gold, take damage

## API Endpoints

### Character Routes (`/api/characters/`)

- `GET /` - List all characters
- `GET /{character_id}` - Get character details

### Creation Routes (`/api/creation/`)

- `GET /races` - Available races
- `GET /skills` - Skill structure
- `GET /equipments` - Available equipment
- `GET /spells` - Available spells
- `GET /stats` - Complete stats data
- `POST /allocate-attributes` - Auto-allocate attributes for race
- `POST /check-attributes` - Validate attribute distribution
- `POST /check-skills` - Validate skill distribution
- `POST /new` - Create new character
- `POST /save` - Save character
- `GET /status/{character_id}` - Get creation status
- `POST /generate-name` - Generate 5 name suggestions (LLM)
- `POST /generate-background` - Generate 5 background stories (LLM)
- `POST /generate-physical-description` - Generate 5 physical descriptions (LLM)
- `POST /add-equipment` - Add equipment (deducts money)
- `POST /remove-equipment` - Remove equipment (refunds money)
- `POST /update-money` - Update character money
- `DELETE /delete/{character_id}` - Delete character

### Scenario Routes (`/api/scenarios/`)

- `GET /` - List available scenarios
- `GET /sessions` - List active sessions
- `GET /{scenario_file}` - Get scenario content (Markdown)
- `POST /start` - Start a new scenario session
- `POST /play` - Send message to GM and get response
- `GET /history/{session_id}` - Get session message history
- `DELETE /history/{session_id}/{message_index}` - Delete specific message

## Coding Standards

### Python

1. **Type Hints**: Use type hints everywhere
2. **Pydantic Models**: Prefer Pydantic models for data structures
3. **Async**: Use async/await for I/O operations
4. **Docstrings**: Use structured docstrings with Description, Parameters, Returns
5. **Error Handling**: Use custom exceptions from `utils/exceptions.py`
6. **Logging**: Use JSON logger from `utils/logger.py`

### Service Layer

- Services should be stateless where possible
- Use dependency injection (pass services as parameters)
- Separate I/O operations (CharacterDataService) from business logic (CharacterBusinessService)
- Never mix HTTP logic with business logic

### Data Models

- Use Pydantic V2 with `field_validator` and `model_validator`
- Include helpful error messages in validators
- Provide example data in `Config.json_schema_extra`
- Use Enums for status/state fields

### File Naming

- Services: `{domain}_service.py` (e.g., `character_service.py`)
- Models: `{model}.py` (e.g., `character.py`)
- Managers: `{resource}_manager.py` (e.g., `stats_manager.py`)
- Tools: `{category}_tools.py` (e.g., `skill_tools.py`)

## Testing

- Test directory: `back/tests/`
- Framework: pytest with pytest-asyncio
- Structure mirrors source code
- Test organization: `agents/`, `services/`, `domain/`, `tools/`, `routers/`

## Configuration

Configuration is centralized in:
- `back/config.yaml` - Main configuration file
- `back/config.py` - Configuration loading and access
- Environment variables can override config values

Key config sections:
- `data.directory` - Path to data directory (default: "../data")
- `llm` - LLM configuration (model, endpoint, API key)
- `logging` - Logging configuration
- `app` - Application settings

## Migration Status

### Completed
- ✅ JSON to YAML migration for game data
- ✅ French to English translation
- ✅ CharacterV2 model created
- ✅ PydanticAI agent implementation
- ✅ YAML data managers
- ✅ Service layer refactoring

### In Progress
- 🔄 Complete migration to CharacterV2
- 🔄 Remove fallback data methods from managers
- 🔄 NPC generation system

### Planned
- ⏳ Combat state management service
- ⏳ Complete test coverage
- ⏳ API versioning (/api/v1, /api/v2)

## Important Notes

1. **Always use English**: All new code, comments, and data should be in English
2. **Load data from YAML**: Never use JSON fallback; all game data is in `data/*.yaml` (loaded via managers)
3. **Use PydanticAI, not LangChain**: The project migrated from LangChain to PydanticAI
4. **Respect SRP**: Each service should have a single, well-defined responsibility
5. **Type everything**: Use Pydantic models and type hints extensively
6. **No hardcoded data**: Load all game data through managers
7. **Session isolation**: Each game session has its own JSONL history file

## Common Patterns

### Loading Game Data

```python
from back.models.domain.stats_manager import StatsManager

stats_manager = StatsManager()
all_stats = stats_manager.stats_info
starting_points = stats_manager.starting_points  # 400
```

### Creating a PydanticAI Tool

```python
from pydantic_ai import Agent, RunContext
from back.services.session_service import SessionService

agent = Agent('openai:gpt-4o', deps_type=SessionService)

@agent.tool
async def my_tool(ctx: RunContext[SessionService], param: str) -> str:
    """Tool description for LLM"""
    session = ctx.deps
    # Implementation using session service
    return result
```

### Using Services

```python
from back.services.character_data_service import CharacterDataService
from back.services.character_business_service import CharacterBusinessService

# I/O operations
data_service = CharacterDataService()
character = data_service.load_character(character_id)

# Business logic
business_service = CharacterBusinessService()
updated_hp = business_service.apply_damage(character, damage_amount)

# Save changes
data_service.save_character(character)
```

## Getting Started

### Backend

```bash
cd back
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd front
npm install
npm run dev
```

### Testing

```bash
cd back
pytest tests/ -v
```

## Resources

- [PydanticAI Documentation](./pydanticai.md)
- [README.md](../README.md) - Main project documentation
- [REFACTO.md](../REFACTO.md) - Refactoring plan
- [TODO.md](../TODO.md) - Improvement roadmap
