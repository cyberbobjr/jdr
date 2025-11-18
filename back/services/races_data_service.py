"""Service wrapper for race and culture data lookups."""
from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Tuple

from back.models.domain.races_manager import RacesManager
from back.models.schema import RaceData, CultureData


class RacesDataService:
    """Expose read-only helpers around `races_and_cultures.yaml`."""

    def __init__(self, manager: Optional[RacesManager] = None) -> None:
        self._manager = manager or RacesManager()

    def get_all_races(self) -> List[RaceData]:
        """Return every race definition."""
        return self._manager.get_all_races()

    def get_race_by_id(self, race_id: str) -> Optional[RaceData]:
        """Return a single race when it exists."""
        return self._manager.get_race_by_id(race_id)

    def get_cultures_for_race(self, race_id: str) -> List[CultureData]:
        """Return the cultures tied to a race."""
        return self._manager.get_cultures_for_race(race_id)

    def get_complete_character_bonuses(self, race_id: str, culture_id: str) -> Dict[str, Any]:
        """Return combined stat, skill, and language bonuses."""
        return self._manager.get_complete_character_bonuses(race_id, culture_id)

    def get_random_race_and_culture(self) -> Tuple[RaceData, CultureData]:
        """Pick a random race and one of its cultures."""
        races = self.get_all_races()
        if not races:
            raise ValueError("No races available to choose from.")
        race = random.choice(races)
        cultures = race.cultures or []
        if not cultures:
            raise ValueError(f"Race '{race.name}' has no cultures defined.")
        return race, random.choice(cultures)
