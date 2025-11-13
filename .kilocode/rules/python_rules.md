# Python Coding Rules for Kilocode Agent

**YOU MUST STRICTLY ADHERE TO THESE RULES FOR ALL PYTHON CODE GENERATION AND MODIFICATION.**

These rules are derived from the project's established coding standards. Refer to `.github/copilot-instructions.md` for more details.

---

## 1. Typing and Data Modeling

### 1.1. Universal Type Hinting

- All variables, function parameters, and return values **must** be explicitly typed.
- Use the `typing` module for complex types (`List`, `Dict`, `Optional`, `Tuple`, etc.).

**INCORRECT:**

```python
def get_character(character_id):
    # ...
```

**CORRECT:**

```python
from typing import Optional
from back.models.domain.character_v2 import CharacterV2

def get_character(character_id: str) -> Optional[CharacterV2]:
    # ...
```

### 1.2. Pydantic for Data Structures

- **Always** use Pydantic `BaseModel` for data structures, API DTOs, and domain models. Do not use plain `dict` or `object`.
- Use Pydantic's `Field` for validation rules (`min_length`, `ge`, `le`, etc.).
- Implement custom validation with `@field_validator` and `@model_validator`.

**INCORRECT:**

```python
character_data = {
    "name": "Gandalf",
    "level": 20
}
```

**CORRECT:**

```python
from pydantic import BaseModel, Field

class Character(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    level: int = Field(..., ge=1)
```

### 1.3. Always response_model in FastAPI route

- **Always** use response_model in FastAPI route

**INCORRECT:**

```python
@router.get("/{character_id}")

```

**CORRECT:**

```python
@router.get("/{character_id}", response_model=CharacterDetailResponse)

```

### 1.4. Always type the variable setted by method

- **Always** type the variable setted by method

**INCORRECT:**

```python
        characters = data_service.get_all_characters()
```

**CORRECT:**

```python
        characters : List[CharacterV2] = data_service.get_all_characters()
```

---

## 2. Documentation and Docstrings

- Every function, method, and class **must** have a structured docstring.
- Follow the specified pydoc format.

### Method/Function Docstring Format

```python
def calculate_bonus(stat_value: int) -> int:
    """
    Calculate the modifier bonus for a stat value.
    
    Args:
        stat_value (int): The stat value (3-20).
    
    Returns:
        int: The calculated bonus modifier (-3 to +5).
    
    Raises:
        ValueError: If stat_value is out of the valid range.
    """
    if not (3 <= stat_value <= 20):
        raise ValueError(f"Stat value must be 3-20, got {stat_value}")
    return (stat_value - 10) // 2
```

---

## 3. Architecture and Design Principles

### 3.1. Service Layer (Strict SRP)

- **Business Logic Services** (e.g., `CharacterBusinessService`): Contain pure business logic. **Must not** perform any I/O operations (file access, database calls). They should operate on data passed to them.
- **Data Services** (e.g., `CharacterDataService`): Handle all I/O operations (reading/writing files). **Must not** contain business logic.
- **Routers** (`back/routers/`): Handle HTTP request/response logic only. Delegate all business operations to services. **Must not** contain any game rules or business logic.

### 3.2. Data Access

- All game data (stats, skills, races, etc.) **must** be loaded via the dedicated Manager classes (e.g., `StatsManager`, `SkillsManager`).
- **Never** hardcode game data. **Never** use fallback data within managers.

**INCORRECT:**

```python
# In a service
with open("gamedata/stats.yaml", "r") as f:
    stats = yaml.safe_load(f)
```

**CORRECT:**

```python
from back.models.domain.stats_manager import StatsManager

stats_manager = StatsManager()
all_stats = stats_manager.get_all_stats_data()
```

---

## 4. Asynchronous Programming

- Use `async` and `await` for all I/O-bound operations, including file access (`aiofiles`) and API calls.
- All FastAPI route handlers **must** be `async`.

---

## 5. Error Handling and Logging

### 5.1. Custom Exceptions

- Use the custom exceptions defined in `back.utils.exceptions.py` (e.g., `CharacterNotFoundError`, `InvalidInputError`).
- Raise specific exceptions instead of generic `Exception` or `ValueError` where a custom one exists.

### 5.2. Structured Logging

- Use the centralized JSON logger from `back.utils.logger.py`.
- **Do not** use `print()` for debugging or logging.

**INCORRECT:**

```python
print(f"Error loading character {character_id}")
```

**CORRECT:**

```python
from back.utils.logger import log_error

log_error("Failed to load character", character_id=character_id, error=str(e))
```

---

## 6. Naming and Conventions

- **File Naming**:
  - Services: `{domain}_service.py` (e.g., `combat_service.py`)
  - Models: `{model}.py` (e.g., `character_v2.py`)
  - Managers: `{resource}_manager.py` (e.g., `races_manager.py`)
  - Tools: `{category}_tools.py` (e.g., `equipment_tools.py`)
- **Language**: All code, comments, variables, and documentation **must** be in English.

---

## 7. Testing

- For every new feature or bug fix, corresponding tests **must** be added in the `back/tests/` directory.
- Use `pytest` and `pytest-asyncio` for testing.
- Test structure should mirror the source code structure.

```
back/
├── services/
│   └── character_business_service.py
└── tests/
    └── services/
        └── test_character_business_service.py
```

