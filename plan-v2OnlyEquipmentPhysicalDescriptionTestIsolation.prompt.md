# Plan: V2-Only Equipment + Physical Description + Test Isolation

Move fully to V2 (no legacy), standardize equipment item keys, expose `physical_description` across API, and isolate tests by purging runtime character data.

## Scope and Constraints
- No frontend changes.
- No legacy aliases or compatibility layers.
- Start from scratch for saved characters (purge `data/characters/`).

## Steps

1) CharacterV2 cleanup (back/models/domain/character_v2.py)
- Remove `Stats.validate_total_points` model validator (per-stat cap 3–20 only).
- Remove `inventory: List[Item]` field and any related compat properties.
- Add `physical_description: Optional[str]` (document, length cap, include example) and include it in `json_schema_extra`.

2) Creation API updates (back/routers/creation.py)
- Add `physical_description` to `CreateCharacterV2Request` and `UpdateCharacterV2Request`.
- Persist `physical_description` into `character_dict` alongside `description` (keep `background` → `description` mapping).
- Validate via `CharacterV2` before save/update to ensure field is accepted and stored.

3) DTOs and character endpoints (back/models/api_dto.py, back/routers/characters.py)
- Add `physical_description: Optional[str]` to `CharacterDetailResponse`.
- Ensure character list/detail endpoints include `physical_description` consistently when reading from `CharacterV2`.

4) Equipment schema standardization (back/models/domain/equipment_manager.py)
- Define `EquipmentItem` with canonical keys:
  - Required: `id: str`, `name: str`, `category: Literal['weapon','armor','accessory','consumable']`, `cost: float|int`, `weight: float`, `quantity: int=1`, `equipped: bool=False`.
  - Optional weapon fields: `damage: str`, `attack_bonus: int`, `range: str|int`.
  - Optional armor fields: `defense: int`, `armor_type: str`.
- Implement normalization utilities:
  - `normalize_item(raw: dict) -> dict` → returns canonical dict using only the keys above (no legacy aliases).
  - `get_equipment_by_id(id_or_name: str) -> Optional[dict]` → case-insensitive lookup by `id` then `name` within standardized catalog.
  - Ensure `get_all_equipment()` returns standardized dicts under `weapons`, `armor`, `accessories`, `consumables`.
- Add clear docstrings and examples to public classes/methods showing canonical item structure.

5) Inventory → equipment refactor (back/services/equipment_service.py, back/services/character_service.py, back/tools/equipment_tools.py)
- Remove any `.inventory` access; operate exclusively on `character.equipment.{weapons, armor, accessories, consumables}`.
- Implement helpers operating on canonical items:
  - `add_item(category, item_id, qty)` → seed from `EquipmentManager.get_equipment_by_id()` and increase `quantity` or append if missing.
  - `remove_item(category, item_id, qty)` → decrease `quantity` and delete when 0.
  - `toggle_equip(category, item_id, equipped)` → set `equipped` field (bool).
  - `list_items()` → return flattened view across categories using canonical keys.
- Ensure totals (weight/value) use `weight`, `cost` and sum `quantity`.

6) Test isolation + new assertions (back/tests/routers/test_creation.py, back/tests/conftest.py)
- Add a pytest fixture in `conftest.py` that clears `data/characters/` before and after tests; ensure directory exists.
- Extend creation test to send `physical_description` and assert persistence via GET `/api/creation/character/{id}`.
- Extend update test to modify `physical_description` and assert the updated value is returned.

7) Data reset + docs (data/characters/, README.md)
- Purge all files under `data/characters/` (fresh start; no backward compatibility).
- Update README:
  - Emphasize per-stat cap (3–20) and removal of total-points validator mention.
  - Reflect removal of `inventory` from Character in favor of `equipment` with canonical keys: `cost`, `weight`, `quantity`, `equipped`.
  - Add `physical_description` to Character fields and example payloads.

## Acceptance Criteria
- `CharacterV2` has no `inventory` field; includes `physical_description` and validates without total-points check.
- Creation and update endpoints accept and persist `physical_description`.
- `CharacterDetailResponse` exposes `physical_description`; endpoints return it.
- Equipment manager returns canonical items with `cost`, `weight`, `quantity`, `equipped` across all categories.
- Inventory operations exclusively use `equipment` and maintain `quantity`/`equipped` correctly.
- Tests pass with added assertions for `physical_description`; test fixtures clean `data/characters/`.
- README accurately reflects the implemented model and flows.
