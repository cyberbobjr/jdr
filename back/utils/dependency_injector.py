"""
Conteneur de dépendances pour le backend JDR.
Implémente l'injection de dépendances pour respecter DIP et faciliter les tests.
"""

from typing import Dict, Any
from back.config import Config
from back.services.character_persistence_service import CharacterPersistenceService
from back.services.character_data_service import CharacterDataService
from back.services.item_service import ItemService
from back.services.equipment_service import EquipmentService
from back.services.character_service import CharacterService


class DependencyContainer:
    """
    Conteneur de dépendances simple pour gérer les instances de services.
    Évite les globals et facilite les tests avec des mocks.
    """

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._config = Config()
        self._register_services()

    def _register_services(self) -> None:
        """Enregistre tous les services avec leurs dépendances."""
        # Services de base
        self._services['config'] = self._config
        self._services['character_persistence_service'] = CharacterPersistenceService()
        self._services['character_data_service'] = CharacterDataService()
        self._services['item_service'] = ItemService()
        self._services['equipment_service'] = EquipmentService(self._services['character_data_service'])

        # Services avec dépendances
        self._services['character_service'] = CharacterService

    def get(self, service_name: str) -> Any:
        """
        Récupère une instance de service.

        Args:
            service_name: Nom du service.

        Returns:
            Instance du service.

        Raises:
            ValueError: Si le service n'existe pas.
        """
        if service_name not in self._services:
            raise ValueError(f"Service '{service_name}' non enregistré.")
        return self._services[service_name]

    def register(self, service_name: str, service_instance: Any) -> None:
        """
        Enregistre un service personnalisé (utile pour les tests avec mocks).

        Args:
            service_name: Nom du service.
            service_instance: Instance du service.
        """
        self._services[service_name] = service_instance


# Instance globale du conteneur (peut être remplacée en tests)
container = DependencyContainer()


def get_service(service_name: str) -> Any:
    """
    Fonction utilitaire pour récupérer un service.

    Args:
        service_name: Nom du service.

    Returns:
        Instance du service.
    """
    return container.get(service_name)


def register_service(service_name: str, service_instance: Any) -> None:
    """
    Fonction utilitaire pour enregistrer un service (pour les tests).

    Args:
        service_name: Nom du service.
        service_instance: Instance du service.
    """
    container.register(service_name, service_instance)