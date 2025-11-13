"""
Skill Affinities Manager for loading race-based skill affinities from YAML.
"""

import yaml
from typing import Dict, List
from pathlib import Path


class SkillAffinitiesManager:
    """
    Manager for loading and accessing skill affinities by race.

    This manager loads the skill affinities from skills_affinities.yaml
    and provides methods to query affinities for specific races.
    """

    def __init__(self, data_dir: str | None = None):
        """
        Initialize the manager.

        Args:
            data_dir: Directory containing the YAML files (defaults to ../gamedata)
        """
        if data_dir is None:
            # Default to the gamedata directory relative to this file
            current_dir = Path(__file__).parent
            data_dir = str(current_dir.parent.parent / "gamedata")

        self.data_dir = Path(data_dir)
        self._affinities_data: Dict[str, Dict[str, List[str]]] | None = None

    @property
    def affinities_data(self) -> Dict[str, Dict[str, List[str]]]:
        """Lazy load the affinities data."""
        if self._affinities_data is None:
            self._load_affinities()
        if self._affinities_data is None:
            raise RuntimeError("Failed to load affinities data")
        return self._affinities_data

    def _load_affinities(self) -> None:
        """Load skill affinities from the YAML file."""
        affinities_file = self.data_dir / "skills_affinities.yaml"

        if not affinities_file.exists():
            raise FileNotFoundError(f"Skill affinities file not found: {affinities_file}")

        with open(affinities_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        self._affinities_data = data

    def get_race_affinities(self, race_name: str) -> List[str]:
        """
        Get the skill affinities for a specific race.

        Args:
            race_name: Name of the race

        Returns:
            List of skill affinity names for the race
        """
        races = self.affinities_data.get('races', {})
        return races.get(race_name, [])

    def get_all_races_with_affinities(self) -> Dict[str, List[str]]:
        """
        Get all races and their skill affinities.

        Returns:
            Dictionary mapping race names to their skill affinity lists
        """
        return self.affinities_data.get('races', {})

    def has_affinity(self, race_name: str, skill_name: str) -> bool:
        """
        Check if a race has affinity for a specific skill.

        Args:
            race_name: Name of the race
            skill_name: Name of the skill

        Returns:
            True if the race has affinity for the skill
        """
        race_affinities = self.get_race_affinities(race_name)
        return skill_name in race_affinities