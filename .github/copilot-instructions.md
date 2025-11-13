# Copilot Instructions for JdR "Terres du Milieu" Project

## Project Overview

This is a LLM-orchestrated Role Playing Game (JdR) set in Middle Earth, using **PydanticAI** as the game master. The architecture follows strict **Single Responsibility Principle (SRP)** with clear separation between services, tools, agents, and routers.

**Stack**: FastAPI + PydanticAI (backend) | Vue.js 3 + TypeScript + TailwindCSS (frontend)

## Critical Architecture Patterns

### Backend Service Hierarchy (MUST FOLLOW)

```
Routers (HTTP only) → Services (Business logic) → Tools (Agent capabilities) → Agent (LLM orchestration)
```

**Rules**:
- **Routers** (`back/routers/`): HTTP layer only, NO business logic. Delegate everything to services.
- **Services** (`back/services/`): Pure business logic, NO I/O operations. Return data, don't format responses.
- **Tools** (`back/tools/`): PydanticAI tool functions with signature `RunContext[SessionService]`. Access services via context.
- **Agents** (`back/agents/`): PydanticAI Agent configuration with system prompts and tool registration.

**Example Tool Pattern**:
```python
from pydantic_ai import RunContext
from back.services.session_service import SessionService

@agent.tool
async def my_tool(ctx: RunContext[SessionService], param: str) -> str:
    """Tool docstring becomes LLM description."""
    # Access services via ctx.deps (SessionService instance)
    result = ctx.deps.inventory_service.some_method(param)
    return result
```

### Memory & Session Management

- **Session History**: JSONL format via `PydanticJsonlStore` (custom PydanticAI store)
- **Location**: `data/sessions/{session_id}.jsonl`
- **Character Data**: JSON files in `data/characters/`, flat structure (NO `state` wrapper)
- **Combat State**: JSON files in `data/combat/` for active combats
- **Message Structure**: PydanticAI's `ModelMessage` types (UserPrompt, SystemPrompt, ToolCall, ToolReturn)

**Key**: System prompts are NEVER stored in history (only in agent config). Only user, assistant, and tool messages persist.

### Configuration & Environment

- **Central Config**: `back/config.yaml` defines LLM model, API endpoints, data paths
- **Environment Override**: `DEEPSEEK_API_KEY`, `JDR_DATA_DIR` override config values
- **Access Pattern**: Use `from back.config import get_llm_config, get_data_dir`

## Development Workflows

### Backend Development

**Setup**:
```bash
cd back
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Run Server**:
```bash
cd back
uvicorn main:app --reload  # Port 8000
```

**Run Tests**:
```bash
# From project root
./run_tests.sh
# OR
pytest --asyncio-mode=auto --rootdir=back/tests -v
```

**Add Dependencies**: Always update `back/requirements.txt` when adding Python packages.

### Frontend Development

**Setup**:
```bash
cd front
npm install
```

**Dev Server**:
```bash
cd front
npm run dev  # Usually port 5173
```

**Tests**:
```bash
cd front
npm test        # Run tests
npm run test:ui # UI for tests
```

**Type Check**:
```bash
npm run type-check  # Vue-tsc
```

## Project-Specific Conventions

### Naming & Code Style

- **Python**: camelCase (functions), PascalCase (classes), snake_case (variables)
- **TypeScript**: camelCase (functions/variables), PascalCase (components/interfaces)
- **Constants**: ALL_CAPS
- **Private members**: Prefix with underscore `_`

### Documentation Standards

Every Python method MUST have:
```python
def method_name(param1: type) -> return_type:
    """
    ### method_name
    **Description:** Brief description of what it does.
    **Parameters:**
    - `param1` (type): Description
    **Returns:** Description of return value.
    """
```

### File Organization Rules

**Backend**:
- New services → `back/services/` with `{domain}_service.py` naming
- New tools → `back/tools/` with `{category}_tools.py` naming
- Tests mirror source structure: `back/tests/services/test_{service}.py`
- Domain models → `back/models/domain/` for business entities
- API DTOs → `back/models/api_dto.py` and `back/models/schema.py`

**Frontend**:
- Components → `front/src/components/` (reusable Vue components)
- Views → `front/src/views/` (page-level components)
- Core services → `front/src/core/` (TypeScript interfaces, API client)
- **NO new CSS files**: Use global `assets/style.css` or TailwindCSS utility classes

### Styling (Frontend)

- **Global styles**: `front/src/assets/style.css` (check first before creating)
- **Layout/positioning**: Use TailwindCSS classes only
- **Responsive**: Classes defined in `front/src/assets/responsive.css`

### Character Data Structure (IMPORTANT)

Characters are stored WITHOUT a `state` wrapper. Flat structure:
```json
{
  "id": "uuid",
  "name": "Character Name",
  "race": "Humain",
  "culture": "Gondor",
  "caracteristiques": { "Force": 10, ... },
  "competences": { "Athletisme": 5 },
  "hp": 42,
  "inventory": [],
  "status": "en_cours"
}
```

**Never** wrap in `{"state": {...}}` structure.

## Integration Points & Dependencies

### PydanticAI Agent Dependencies

Tools receive `SessionService` as dependency via `RunContext[SessionService]`:
- `session_service.character_data` → Current character (typed `Character` object)
- `session_service.data_service` → Load/save character data
- `session_service.business_service` → XP, gold, damage logic
- `session_service.inventory_service` → Add/remove items
- `session_service.equipment_service` → Buy/sell equipment
- `session_service.combat_service` → Combat mechanics

### External Services Communication

- **LLM API**: Configured via `config.yaml` (default: DeepSeek Chat at `api.deepseek.com`)
- **Model**: Abstracted via PydanticAI's `OpenAIModel` with custom provider
- **Storage**: All paths relative to `JDR_DATA_DIR` environment variable

### Frontend-Backend API

- **Base URL**: `http://localhost:8000/api`
- **Key Endpoints**:
  - `POST /api/scenarios/start` → Start new game session
  - `POST /api/scenarios/play?session_id={uuid}` → Send player action
  - `GET /api/scenarios/history/{session_id}` → Get conversation history
  - `GET /api/characters/` → List all characters
  - `POST /api/creation/*` → Character creation endpoints

- **TypeScript Interfaces**: Generated from OpenAPI, located in `front/src/core/interfaces.ts`

## Common Pitfalls to Avoid

1. **Don't** add business logic to routers (use services)
2. **Don't** perform I/O in services (return data, let routers handle responses)
3. **Don't** create tool functions without `RunContext[SessionService]` signature
4. **Don't** store system prompts in JSONL history (agent-only)
5. **Don't** wrap character data in `state` object (flat structure only)
6. **Don't** create new CSS files without checking global styles first
7. **Don't** forget to update `requirements.txt` (Python) or `package.json` (Node)
8. **Don't** write tests that modify production data (use test fixtures)

## Key Files Reference

- **Architecture docs**: [`README.md`](../README.md) (diagrams, API table, service descriptions)
- **PydanticAI guide**: [`pydanticai.md`](../pydanticai.md) (agent patterns, message history, tools)
- **System prompt builder**: [`back/agents/PROMPT.py`](../back/agents/PROMPT.py) (scenario + rules integration)
- **Agent factory**: [`back/agents/gm_agent_pydantic.py`](../back/agents/gm_agent_pydantic.py) (agent creation pattern)
- **Session orchestration**: [`back/services/session_service.py`](../back/services/session_service.py) (dependency hub)
- **Message storage**: [`back/storage/pydantic_jsonl_store.py`](../back/storage/pydantic_jsonl_store.py) (custom PydanticAI store)
- **Game rules**: [`data/rules/`](../data/rules/) (combat, skills, magic rules in French)
- **Scenarios**: [`data/scenarios/`](../data/scenarios/) (Markdown adventure files)

## Testing Strategy

- **Backend**: pytest with `--asyncio-mode=auto` for async tests
- **Frontend**: vitest for Vue components and TypeScript utilities
- **Test locations**: Mirror source structure (`back/tests/`, `front/tests/`)
- **Fixtures**: Use temporary test data, don't modify `data/` directory
- **Coverage**: Run `pytest --cov=back` for backend coverage reports

## Quick Start Commands

```bash
# Backend
cd back && uvicorn main:app --reload

# Frontend  
cd front && npm run dev

# Tests
./run_tests.sh                    # Backend
cd front && npm test              # Frontend

# Type checking
cd front && npm run type-check    # TypeScript
```

---

*Last updated: 2025-01-13*
*For detailed architecture, see [README.md](../README.md) | For PydanticAI patterns, see [pydanticai.md](../pydanticai.md)*
