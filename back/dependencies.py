"""
Dependency Injection Container.
Manages the lifecycle of singleton services to avoid unnecessary instantiation.
"""

from typing import Optional
from back.services.character_data_service import CharacterDataService
from back.services.equipment_service import EquipmentService
from back.utils.logger import log_info

class DependencyContainer:
    """
    ### DependencyContainer
    **Description:** Singleton container for application services.
    Ensures that stateless services are instantiated only once.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DependencyContainer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        log_info("Initializing DependencyContainer...")
        
        # 1. Initialize CharacterDataService (Base persistence layer)
        self.character_data_service = CharacterDataService()
        
        # 2. Initialize EquipmentService (Depends on CharacterDataService)
        self.equipment_service = EquipmentService(self.character_data_service)
        
        self._initialized = True
        log_info("DependencyContainer initialized.")

    @classmethod
    def get_instance(cls) -> 'DependencyContainer':
        """
        Returns the singleton instance of the container.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# Global instance for easy access
global_container = DependencyContainer()
