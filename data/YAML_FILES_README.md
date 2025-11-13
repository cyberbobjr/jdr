# Game Data YAML Files

This directory contains the YAML configuration files that define the game rules, statistics, skills, equipment, and other game data.

## File Descriptions

- **stats.yaml** - Character statistics (Strength, Constitution, Agility, Intelligence, Wisdom, Charisma) with cost tables and bonuses
- **skills_for_llm.yaml** - Complete skills organized in 6 groups (Combat, General, Stealth, Social, Magic, Knowledge)
- **skill_groups.yaml** - Skill group definitions
- **skills_affinities.yaml** - Culture-skill affinities mapping
- **races_and_cultures.yaml** - Available races and cultures with bonuses
- **equipment.yaml** - Weapons, armor, and items with stats and costs
- **spells.yaml** - Magic spells organized by sphere
- **combat_system.yaml** - Combat mechanics and rules

## Usage

These files are loaded by manager classes in `back/models/domain/*_manager.py`:

- `StatsManager` → `stats.yaml`
- `SkillsManager` → `skills_for_llm.yaml`
- `RacesManager` → `races_and_cultures.yaml`
- `EquipmentManager` → `equipment.yaml`
- `SpellsManager` → `spells.yaml`
- `CombatSystemManager` → `combat_system.yaml`

## Editing

When modifying game data:

1. **Edit source files** in `back/gamedata/`
2. **Copy to data/** directory: `cp back/gamedata/*.yaml data/`
3. **Test changes** by running the application
4. **Commit both** `back/gamedata/*.yaml` and `data/*.yaml` files

## Data Directory Configuration

The data directory path is configurable:

- **Config file**: `back/config.yaml` → `data.directory: "../data"`
- **Environment variable**: `JDR_DATA_DIR` (overrides config)
- **Default** (if config not found): `back/gamedata`

## Backup

Original JSON files (pre-migration) are preserved in `data/json_backup/` for reference.

---

**Note**: Never use hardcoded fallback data. If these YAML files are missing or invalid, the application should fail fast with a clear error message.
