from fastapi import APIRouter, HTTPException
from back.models.domain.preferences import UserPreferences
from back.services.settings_service import SettingsService
from back.utils.logger import log_debug

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/preference", response_model=UserPreferences)
async def get_preferences() -> UserPreferences:
    """
    ### Get User Preferences
    **Description:** Retrieve the global user preferences.
    **Returns:**
    - `UserPreferences`: The current user preferences.
    """
    log_debug("Endpoint call: GET /user/preference")
    service = SettingsService()
    return service.get_preferences()

@router.put("/preference", response_model=UserPreferences)
async def update_preferences(preferences: UserPreferences) -> UserPreferences:
    """
    ### Update User Preferences
    **Description:** Update the global user preferences.
    **Parameters:**
    - `preferences` (UserPreferences): The new preferences to save.
    **Returns:**
    - `UserPreferences`: The updated user preferences.
    """
    log_debug("Endpoint call: PUT /user/preference", preferences=preferences.model_dump())
    service = SettingsService()
    try:
        return service.update_preferences(preferences)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")
