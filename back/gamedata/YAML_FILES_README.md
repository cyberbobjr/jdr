# Game Data YAML Files

This directory contains the YAML configuration files that define the game rules, statistics, skills, equipment, and other game data.

## File Descriptions

- **stats.yaml** - Character statistics (Strength, Constitution, Agility, Intelligence, Wisdom, Charisma) with cost tables and bonuses
- **skills.yaml** - Unified skills data with groups, racial affinities, and stat bonuses
- **races_and_cultures.yaml** - Available races and cultures with bonuses
- **equipment.yaml** - Weapons, armor, and items with stats and costs
- **spells.yaml** - Magic spells organized by sphere
- **combat_system.yaml** - Combat mechanics and rules

## Usage

These files are loaded by manager classes in `back/models/domain/*_manager.py`:

- `StatsManager` → `stats.yaml`
- `UnifiedSkillsManager` → `skills.yaml`
- `RacesManager` → `races_and_cultures.yaml`
- `EquipmentManager` → `equipment.yaml`
- `SpellsManager` → `spells.yaml`
- `CombatSystemManager` → `combat_system.yaml`
---

**Note**: Never use hardcoded fallback data. If these YAML files are missing or invalid, the application should fail fast with a clear error message.
