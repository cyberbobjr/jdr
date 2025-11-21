"""
Domain model for user preferences.
"""

from pydantic import BaseModel, Field

class UserPreferences(BaseModel):
    """
    ### UserPreferences
    **Description:** Stores user-specific preferences for the game session.
    **Attributes:**
    - `language` (str): The preferred language for interaction (default: "English").
    """
    language: str = Field(default="English", description="Preferred language for the game master interaction.")
