import json
import os
from typing import Dict, List
from ...config import get_data_dir

class StatsManager:
    """Stats manager using the new JSON system"""

    def __init__(self):
        """Initialize the stats manager with default values.

        **Description:** Creates a new stats manager instance, loads stats
        data from JSON file and initializes all stats with default values.
        **Parameters:** None
        **Returns:** None
        """
        self.values = {}
        self.racial_bonuses = {}
        self._load_stats_data()
        # Initialize default values
        for name in self.names:
            self.values[name] = 50
            self.racial_bonuses[name] = 0

    def _load_stats_data(self):
        """Load data from the JSON file.

        **Description:** Loads stats data from the stats.json file
        including stats info, bonus table, cost table and starting points.
        **Parameters:** None
        **Returns:** None
        """
        data_path = os.path.join(get_data_dir(), "stats.json")
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.stats_info = data["stats"]
        self.names = list(self.stats_info.keys())
        self.bonus_table = data["bonus_table"]
        self.cost_table = data["cost_table"]
        self.starting_points = data["starting_points"]

    def get_description(self, stat: str) -> str:
        """Return the description of a stat.

        **Description:** Retrieves the description text for a given stat from the stats info.
        **Parameters:**
        - `stat` (str): Name of the stat to get description for.
        **Returns:** A string containing the stat description or empty string if not found.
        """
        stat_info = self.stats_info.get(stat, {})
        return stat_info.get("description", "")

    def get_bonus(self, stat: str) -> int:
        """Calculate the final bonus of a stat (value + racial bonus).

        **Description:** Computes the total bonus for a stat by combining
        the base bonus from the stat value and the racial bonus.
        **Parameters:**
        - `stat` (str): Name of the stat to calculate bonus for.
        **Returns:** An integer representing the total bonus for the stat.
        """
        base_value = self.values.get(stat, 50)
        base_bonus = self._get_base_bonus(base_value)
        racial_bonus = self.racial_bonuses.get(stat, 0)
        return base_bonus + racial_bonus

    def _get_base_bonus(self, value: int) -> int:
        """Calculate the base bonus from a stat value.

        **Description:** Converts a stat value (0-100) to its corresponding
        bonus (-10 to +10) using the game's conversion formula.
        **Parameters:**
        - `value` (int): The stat value (0-100).
        **Returns:** An integer representing the base bonus derived from the value.
        """
        return value // 5 - 10

    def calculate_cost(self, value: int) -> int:
        """Calculate the cost in points to increase a stat to a specific value.

        **Description:** Computes the total point cost required to increase a
        stat from its base value (50) to the target value, using the
        game's cost progression system.
        **Parameters:**
        - `stat` (str): Name of the stat to calculate cost for.
        - `value` (int): Target value for the stat.
        **Returns:** An integer representing the total point cost.
        """
        if value <= 50:
            return 0  # No cost for reducing below base value

        total_cost = 0
        for val in range(51, value + 1):
            total_cost += self._get_cost_for_value(val)
        return total_cost

    def _get_cost_for_value(self, value: int) -> int:
        """Calculate the cost for a single point increase at a specific value.

        **Description:** Returns the point cost to increase a stat by
        one point at the given value level. Higher values cost more points.
        **Parameters:**
        - `value` (int): The stat value to calculate cost for.
        **Returns:** An integer representing the cost for one point increase.
        """
        if value <= 70:
            return 1
        elif value <= 80:
            return 2
        elif value <= 90:
            return 3
        else:
            return 4

    def set_racial_bonus(self, stat: str, bonus: int) -> None:
        """Set the racial bonus for a specific stat.

        **Description:** Assigns a racial bonus value to the specified stat.
        This bonus is added to the base bonus when calculating final bonuses.
        **Parameters:**
        - `stat` (str): Name of the stat to set racial bonus for.
        - `bonus` (int): The racial bonus value to assign.
        **Returns:** None.
        """
        self.racial_bonuses[stat] = bonus

    def set_value(self, stat: str, value: int) -> None:
        """Set the value of a specific stat.

        **Description:** Assigns a new value to the specified stat.
        The value should typically be between 0 and 100.
        **Parameters:**
        - `stat` (str): Name of the stat to set value for.
        - `value` (int): The new value to assign to the stat.
        **Returns:** None.
        """
        self.values[stat] = value

    def get_all_stats_names(self) -> List[str]:
        """Get all available stat names.

        **Description:** Returns a list of all stat names available
        in the loaded stats data.
        **Parameters:** None.
        **Returns:** List[str] - A list containing all stat names.
        """
        return list(self.names)

    def get_all_stats_data(self) -> Dict:
        """Get all stats data from the JSON file.

        **Description:** Returns the complete stats JSON file structure
        containing stats information, bonus tables, cost tables, and starting points.
        **Parameters:** None.
        **Returns:** Dict - A dictionary containing the complete stats data
        structure with stats, bonus_table, cost_table, and starting_points.
        """
        return {
            "stats": self.stats_info,
            "bonus_table": self.bonus_table,
            "cost_table": self.cost_table,
            "starting_points": self.starting_points
        }

    def get_all_stats_with_values(self, stats: Dict[str, int] = None) -> Dict:
        """Get all stats with their current values and bonuses.

        **Description:** Returns comprehensive stats information including
        the complete JSON structure plus current values and bonuses for each stat.
        **Parameters:**
        - `stats` (Dict[str, int], optional): Dictionary mapping stat
          names to their current values. Defaults to empty dictionary if None.
        **Returns:** Dict - A dictionary containing the complete stats data
        structure (stats, bonus_table, cost_table, starting_points) plus current
        values and bonuses for each stat.
        """
        stats = stats or {}

        result = self.get_all_stats_data()

        for name, stat_info in result["stats"].items():
            current_value = stats.get(name, 50) # Default to 50 if not provided
            self.set_value(name, current_value) # Set the value in the manager
            current_bonus = self.get_bonus(name)

            stat_info['current_value'] = current_value
            stat_info['current_bonus'] = current_bonus

        return result
