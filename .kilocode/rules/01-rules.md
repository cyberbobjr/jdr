# JdR "Terres du Milieu" - Coding Agent System Prompt

## 1. Project Overview

This is a Role-Playing Game (RPG) in Middle-earth, orchestrated by an LLM Game Master (GM).
The backend is FastAPI with PydanticAI. Your primary role is to assist in developing and maintaining this backend.

## 2. Core Architecture

- **Services (`back/services/`)**: Single Responsibility Principle (SRP). Each service handles one business function.
- **Agents (`back/agents/`)**: PydanticAI agents that orchestrate narration and game mechanics.
- **Routers (`back/routers/`)**: FastAPI endpoints. Delegate all logic to services.
- **Models (`back/models/domain/`)**: Pydantic models for all data structures.
- **Managers (`back/models/domain/*_manager.py`)**: Load game data from YAML files.

## 3. Key Conventions

- **Strict SRP**: One responsibility per file/service.
- **No I/O in Services**: Services contain business logic only. I/O is handled by dedicated data services (e.g., `CharacterDataService`).
- **No Game Logic in Routers**: Routers handle HTTP requests and responses only.
- **English Naming**: All code, models, and data must be in English.
- **Type Hints**: Use type hints everywhere. This is mandatory.
- **PydanticAI**: Use PydanticAI, not LangChain.

## 4. Technology Stack

- **Framework**: FastAPI
- **Agent Framework**: PydanticAI
- **Validation**: Pydantic V2
- **Game Data**: YAML files in `back/gamedata/`
- **Persistence**: JSONL for session history, JSON for character sheets.
- **LLM Provider**: OpenAI-compatible API.

## 5. Directory Structure

```text
back/
├── agents/                # PydanticAI agents (gm_agent_pydantic.py)
├── gamedata/              # YAML game data (stats.yaml, skills.yaml, etc.)
├── models/
│   └── domain/            # Pydantic domain models & data managers
├── routers/               # FastAPI routers
├── services/              # Business logic services
├── storage/               # pydantic_jsonl_store.py for session history
├── tools/                 # PydanticAI tools for the agent
├── utils/                 # Utilities (dice, exceptions, logger)
├── config.py              # Configuration loading
├── config.yaml            # Configuration file
└── app.py                 # FastAPI app entry point
data/                      # Runtime data (characters, sessions, etc.)
```

## 6. Data Loading via Managers

All game data is loaded from `back/gamedata/*.yaml` via a manager class. **Never hardcode game data.**

- **StatsManager**: `stats.yaml` -> `get_bonus()`, `get_description()`
- **UnifiedSkillsManager**: `skills.yaml` -> `get_all_skills()`, `get_skill_group()`
- **RacesManager**: `races_and_cultures.yaml` -> `get_all_races()`, `get_cultures_for_race()`
- **EquipmentManager**: `equipment.yaml` -> `get_all_equipment()`, `get_weapons()`
- **SpellsManager**: `spells.yaml` -> `get_all_spells()`, `get_spells_by_sphere()`
- **CombatSystemManager**: `combat_system.yaml` -> Combat rules and actions.

**Example Usage:**

```python
from back.models.domain.stats_manager import StatsManager
stats_manager = StatsManager()
bonus = stats_manager.get_bonus(15) # Returns 2
```

## 7. PydanticAI Agent & Tools

The GM agent uses PydanticAI. Tools are methods decorated with `@agent.tool` and use `RunContext` for dependency injection.

**Tool Structure:**

```python
from pydantic_ai import Agent, RunContext
from back.services.session_service import SessionService

@agent.tool
async def skill_check_with_character(
    ctx: RunContext[SessionService],
    skill_name: str,
    difficulty: int = 50
) -> str:
    """Perform a skill check for the character in the current session."""
    session_service = ctx.deps
    # ... implementation using session_service ...
    return result_string
```

**Key Tools:**

- `skill_tools.py`: `skill_check_with_character`
- `combat_tools.py`: Initiative, attacks, damage.
- `equipment_tools.py`: Add/remove items from inventory.
- `character_tools.py`: Apply XP, gold, damage.

## 8. Coding Standards

- **Type Hints**: **MANDATORY**. All functions and methods must have type hints.
- **Pydantic Models**: Use for all data structures. Use V2 features like `field_validator`.
- **Async**: Use `async/await` for all I/O operations.
- **Docstrings**: Document all public methods (description, args, returns).
- **Error Handling**: Use custom exceptions from `utils/exceptions.py`.
- **File Naming**:
  - Services: `{domain}_service.py`
  - Managers: `{resource}_manager.py`
  - Tools: `{category}_tools.py`

## 9. Important Notes

1. **English Only**: All code, comments, and data.
2. **Load Data from YAML**: Use the manager classes. No hardcoded values.
3. **Use PydanticAI**: The project has migrated away from LangChain.
4. **Respect SRP**: Keep services focused on a single responsibility.
5. **Type Everything**: Use Pydantic models and type hints extensively.
6. **Session Isolation**: Each game session is separate with its own history file.
