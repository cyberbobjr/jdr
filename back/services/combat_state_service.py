from typing import Optional
from uuid import UUID
import os
import json
from back.models.domain.combat_state import CombatState
from back.config import get_data_dir
from back.utils.logger import log_error

class CombatStateService:
    def _get_file_path(self, session_id: UUID) -> str:
        return os.path.join(get_data_dir(), 'combat', f"{session_id}.json")

    def load_combat_state(self, session_id: UUID) -> Optional[CombatState]:
        file_path = self._get_file_path(session_id)
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return CombatState.model_validate(data)
        except Exception as e:
            log_error(f"Failed to load combat state for session {session_id}", error=str(e))
            return None

    def save_combat_state(self, session_id: UUID, state: CombatState) -> None:
        file_path = self._get_file_path(session_id)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            with open(file_path, 'w') as f:
                f.write(state.model_dump_json(indent=2))
        except Exception as e:
            log_error(f"Failed to save combat state for session {session_id}", error=str(e))

    def delete_combat_state(self, session_id: UUID) -> None:
        file_path = self._get_file_path(session_id)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                log_error(f"Failed to delete combat state for session {session_id}", error=str(e))

    def has_active_combat(self, session_id: UUID) -> bool:
        state = self.load_combat_state(session_id)
        return state is not None and state.is_active
