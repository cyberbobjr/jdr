# AI Copilot Character Creation (Suggest + Edit)

A guided wizard where the AI proposes curated options at each step (with concise rationales) and the player edits inline. Every change is validated server-side using V2 Pydantic models and persisted to a draft. This flow uses `back/routers/creation.py` and read-only managers (`RacesManager`, `SkillsManager`, `EquipmentManager`, `StatsManager`) to stay consistent with the project’s architecture.

- Data model: `CharacterV2` with `Stats` (each 3–20, total ≤ 400) and `Skills` (ranks 0–10, total ≤ 40).
- Validation: Use `POST /creation/validate-character` (full payload) or `/creation/validate-character/by-id` (stored draft) before finalization.
- Persistence: `CharacterPersistenceService` to `data/characters/{id}.json`; `status` transitions from `draft` to `active`.

| Validation Endpoint | Body | Primary use case |
| --- | --- | --- |
| `POST /creation/validate-character` | Full character payload (stats, skills, combat, equipment, spells) | Frontend already has the latest JSON (pre-save preview, inline editing) |
| `POST /creation/validate-character/by-id` | `{ "character_id": "uuid" }` | Server-side validation of a persisted draft (after `/creation/save` or `/creation/update`) |

## Architecture Alignment

- Routers: `back/routers/creation.py` for read/write operations.
- Services: `CharacterPersistenceService` for I/O; V2 rules enforced by Pydantic models (`CharacterV2`, `Stats`, `Skills`, `Equipment`, `CombatStats`, `Spells`).
- Managers (read-only data): `RacesManager`, `SkillsManager`, `EquipmentManager`, `StatsManager` (labels/bonus tables only).
- Spells: Available manager-side (`SpellsManager`), expose via a future route if needed.

## Endpoints Used (Creation Router)

- `GET /creation/races`: Race + culture catalog (bonuses, languages, free points, traits).
- `GET /creation/skills`: Skills structure for V2 (groups + items) from `SkillsManager`.
- `GET /creation/equipment`: Equipment catalog from `EquipmentManager`.
- `GET /creation/stats`: Stat labels/bonus/cost tables for UX copy (V2 ignores legacy costs).
- `POST /creation/create`: Create draft `CharacterV2` (returns `character_id`).
- `POST /creation/update`: Update existing character by `character_id`.
- `GET /creation/character/{character_id}`: Load character.
- `DELETE /creation/character/{character_id}`: Delete character.
- `POST /creation/validate-character`: Validate full character object against V2 rules.

## Step‑By‑Step Flow

### 1) Concept & Identity

- Capture: Player concept (role, combat vs social, magic, tone).
- Suggest: 5 names, 3 short backgrounds, 3 physical descriptions with 1–2 line rationales.
- Edit: Player tweaks any suggestion inline.
- Persist: Initialize via `POST /creation/create` using minimal fields (name, race/culture placeholders, default `Stats`/`Skills`); store `character_id`, keep `status="draft"`.
- Validate: Structural (lengths) only; full validation deferred to final checks.

### 2) Race & Culture

- Fetch: `GET /creation/races`.
- Explain: Show `get_complete_character_bonuses(race_id, culture_id)` (characteristic bonuses, skill bonuses, languages, free skill points, special traits, culture description).
- Suggest: Top 3 race+culture fits for the concept with short “why this choice”.
- Select/Edit: Player chooses or overrides; persist via `POST /creation/update`.

### 3) Attributes (Stats)

- Rules: V2 `Stats` — each 3–20; total ≤ 400.
- Fetch: `GET /creation/stats` (labels/descriptions only; ignore legacy 0–100 cost tables for V2).
- Suggest: Three allocations (offensive/defensive/balanced) with derived modifiers for clarity.
- Edit: Inline stat adjustments with running total and remaining points.
- Validate: Build full character payload and call `POST /creation/validate-character`; show precise field errors and actionable hints.

### 4) Skills Distribution

- Rules: V2 `Skills` — each rank 0–10; total development points ≤ 40.
- Fetch: `GET /creation/skills`; display groups, descriptions; enable keyword search.
- Suggest: Three layouts (combat/social/hybrid) aligned to concept and racial/cultural bonuses.
- Edit: Inline per-skill ranks; provide “auto‑rebalance” to fit the 40‑point cap.
- Validate: Reuse `POST /creation/validate-character` with the updated character payload.

### 5) Starter Gear (and Spells if exposed)

- Fetch: `GET /creation/equipment` (and later `GET /creation/spells` if exposing `SpellsManager`).
- Suggest: 2–3 starter kits tailored to concept (e.g., melee scout, archer, healer) with gold cost and light encumbrance notes.
- Edit: Replace kit items; track `equipment.gold` in character.
- Persist: `POST /creation/update`.
- Validate: Ensure non-negative `equipment.gold` and consistent equipment shape.

### 6) Summary, Final Checks, Activation

- Summary: Identity, race/culture and traits, stats with modifiers, skills with totals, gear (and spells if any).
- Explainability: For each accepted AI suggestion, keep a short rationale; allow “reroll similar” with deterministic seeds.
- Validate: Final `POST /creation/validate-character` must pass; map errors to fields.
- Activate: `POST /creation/update` to set `status="active"`.
- Resume/Delete: Use `GET /creation/character/{id}` to resume and `DELETE /creation/character/{id}` to remove.

## Validation Rules (Authoritative)

- Stats: six attributes; each in [3, 20]; sum ≤ 400; modifiers as `(stat - 10) // 2`.
- Skills: six groups; ranks in [0, 10]; total development points ≤ 40 (1 point per rank).
- Combat/magic: `CombatStats` and `Spells` must be structurally valid; ensure current ≤ max for HP/MP.

## LLM Integration

- Suggest: Names, backgrounds, descriptions; race/culture shortlists; 3× stat allocations; 3× skill layouts; 2–3 starter kits.
- Controls: Deterministic seeds; “reroll similar” preserving constraints and selected context; toggles to bias toward stealth/healer/tank, etc.
- Fallback: If LLM endpoints are unavailable, run the same wizard with static templates and manager data; continue using server-side validation.

## State & Persistence

- Autosave: After each accepted suggestion or edit, write to draft via `POST /creation/update`.
- Status: `draft` throughout the wizard; set to `active` on finalization.
- Storage: JSON files under `data/characters/` via `CharacterPersistenceService`.

## Error Handling & UX

- Inline errors: Map `validate-character` messages to fields; provide targeted fixes (e.g., “Reduce total skill points by 3”).
- Accessibility: Keyboard-first inputs, concise labels from managers, tooltips for stat/skill definitions.
- Transparency: Show totals and remaining points; display derived modifiers; clearly flag soft vs hard constraints.

## Non‑LLM Fallback

- Provide manual paths for each step with the same validation and autosave.
- Predefine a small set of archetype templates (balanced, striker, guardian, face, mage) to bootstrap without the LLM.

## Open Decisions

- Spells exposure: Add `GET /creation/spells` (via `SpellsManager`) or defer to an in-game acquisition flow?
- Suggestion counts: Default 3 per step (skills/stats/layouts) and 5 for names—adjustable?
- Race/culture effects: Apply bonuses as passive metadata during creation, or pre-bake into proposed allocations?
