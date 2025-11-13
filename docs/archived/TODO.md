# TODO.md - Améliorations du Backend JDR

## Introduction
Ce document détaille les pistes d'améliorations pour le backend du projet JDR (Jeu de Rôle) afin d'améliorer la maintenabilité, la testabilité et le respect des bonnes pratiques (SOLID, DRY, Clean Code). Basé sur l'analyse des fichiers dans `back/`, des résultats de recherche (e.g., utilisation de `model_dump()`, classes Service), et du contexte du projet.

## Analyse de la Structure Actuelle et Problèmes Identifiés

### 1. Violations des Principes SOLID
Le code présente plusieurs violations des principes SOLID, impactant la maintenabilité et l'extensibilité.

#### Single Responsibility Principle (SRP) - Violation
- **Problème** : `CharacterService` gère trop de responsabilités (chargement/sauvegarde, inventaire, équipement, achat/vente, XP, gold, HP), violant SRP. Désormais, l'inventaire est géré par `EquipmentService` (fusion de l'ancien `InventoryService`).
- **Exemple de Code Actuel** (dans `back/services/character_service.py`) :
  ```python
  def add_item(self, item_id: str, qty: int = 1) -> Dict:
      # Logique d'inventaire mélangée à la logique de personnage
      if not hasattr(self.character_data, 'inventory') or self.character_data.inventory is None:
          self.character_data.inventory = []
      # ... logique répétée de conversion et sauvegarde
      self.save_character()
      return {"inventory": [item.model_dump() if hasattr(item, 'model_dump') else item for item in self.character_data.inventory]}
  ```
- **Impact** : Difficulté à tester et maintenir, couplage fort entre fonctionnalités.
- **Amélioration Proposée** : Décomposer `CharacterService` en services spécialisés via composition et injection de dépendances. Exemple refactorisé :
  ```python
  class CharacterService:
      def __init__(self, character_id: str, equipment_service: EquipmentService, persistence_service: CharacterPersistenceService):
          self.inventory_service = inventory_service
          self.persistence_service = persistence_service
          # ...

      def add_item(self, item_id: str, qty: int = 1) -> Dict:
          self.inventory_service.add_item(self.character_id, item_id, qty)
          return self.persistence_service.get_character(self.character_id).inventory
  ```
  **Justification** : Respecte SRP en déléguant à des services spécialisés, améliore la testabilité via DI.

#### Dependency Inversion Principle (DIP) - Violation
- **Problème** : Utilisation d'instances globales (e.g., `config` dans `config.py`) et appels directs à d'autres services (e.g., `ItemService()` dans `CharacterService`), créant un couplage fort.
- **Exemple de Code Actuel** (dans `back/services/character_service.py`) :
  ```python
  def instantiate_item_by_id(self, item_id: str, qty: int = 1) -> 'Item':
      item_service = ItemService()  # Instanciation directe, pas d'injection
      item = item_service.create_item_from_name(item_id, quantity=qty)
      return item
  ```
- **Impact** : Difficulté à tester (impossible de mocker `ItemService`), violation de l'inversion des dépendances.
- **Amélioration Proposée** : Implémenter un conteneur de dépendances (e.g., avec `dependency_injector`). Exemple :
  ```python
  # utils/dependency_injector.py
  from dependency_injector import containers, providers

  class Container(containers.DeclarativeContainer):
      config = providers.Singleton(Config)
      item_service = providers.Singleton(ItemService, config=config)
      character_service = providers.Factory(CharacterService, item_service=item_service)
  ```
  **Justification** : Respecte DIP en injectant les dépendances, facilite les tests avec mocks.

### 2. Duplication de Code (Violation DRY)
- **Problème** : Conversion répétée entre objets Pydantic et dictionnaires. `model_dump()` est utilisé 18 fois, souvent avec des checks `hasattr(obj, 'model_dump')`.
- **Exemple de Code Actuel** (répété dans `back/services/character_service.py`, `back/routers/scenarios.py`, etc.) :
  ```python
  # Dans plusieurs méthodes
  if hasattr(self.character_data, 'model_dump'):
      character_dict = self.character_data.model_dump()
  else:
      character_dict = self.character_data.copy() if isinstance(self.character_data, dict) else self.character_data
  ```
- **Impact** : Code verbeux, propice aux erreurs, difficile à maintenir.
- **Amélioration Proposée** : Créer une utilité centralisée. Exemple :
  ```python
  # utils/model_converter.py
  class ModelConverter:
      @staticmethod
      def to_dict(obj: Any) -> Dict[str, Any]:
          if hasattr(obj, 'model_dump'):
              return obj.model_dump()
          elif hasattr(obj, 'dict'):
              return obj.dict()
          else:
              return vars(obj)
  ```
  **Justification** : Centralise la logique, respecte DRY, simplifie les tests.

### 3. Problèmes de Testabilité
- **Problème** : Couverture de tests insuffisante (peu de tests pour les services critiques), structure des tests incohérente, et erreurs dans les tests existants (e.g., `service.status` au lieu de `service.character_data.status` dans `test_character_service_refactored.py`). Manque de mocks pour les dépendances externes (e.g., Redis, OpenAI, fichiers JSON).
- **Exemple de Code Actuel** (dans `back/tests/test_character_service_refactored.py`) :
  ```python
  def test_properties_work_correctly(self):
      # ...
      assert service.status == CharacterStatus.PROGRESS  # Erreur : devrait être service.character_data.status
  ```
- **Impact** : Tests fragiles, difficile à déboguer, faible confiance dans les changements.
- **Amélioration Proposée** : Augmenter la couverture avec des tests unitaires mocks. Exemple :
  ```python
  # tests/services/test_character_service.py
  import pytest
  from unittest.mock import Mock
  from back.services.character_service import CharacterService

  def test_add_item_uses_inventory_service():
      mock_inventory = Mock(spec=EquipmentService)
      service = CharacterService("test-id", inventory_service=mock_inventory)
      
      service.add_item("sword", 1)
      
      mock_inventory.add_item.assert_called_once_with("test-id", "sword", 1)
  ```
  **Justification** : Améliore l'isolation des tests, respecte les bonnes pratiques de testing, facilite la refactorisation.

### 4. Autres Problèmes de Clean Code
- **Méthodes Trop Longues et Complexes** : E.g., `buy_equipment` dans `CharacterService` fait plus de 50 lignes, mélangeant logique métier et conversion.
- **Imports à l'Intérieur des Fonctions** : E.g., dans `back/agents/gm_agent_pydantic.py`, des imports comme `from pydantic_ai.models.openai import OpenAIModel` sont à l'intérieur de fonctions, violant les conventions.
- **Gestion d'Erreurs Incohérente** : Mélange d'exceptions personnalisées et génériques sans logging uniforme.
- **Amélioration Proposée** : Décomposer les méthodes, déplacer les imports en haut, standardiser la gestion d'erreurs avec une classe `ApiError` personnalisée.

## Étapes d'Implémentation
1. Créer `utils/model_converter.py` et refactoriser les conversions.
2. Refactoriser `CharacterService` pour utiliser DI et déléguer à des services spécialisés.
3. Implémenter un conteneur de dépendances et l'intégrer dans `app.py`.
4. Écrire des tests pour les nouveaux services et corriger les existants.
5. Mettre à jour la documentation et créer un guide de migration.

## Améliorations Implémentées

### 1. Utilité pour Conversion Dict/Objet (DRY)
- **Fichier créé** : `back/utils/model_converter.py`
- **Objectif** : Centraliser la logique de conversion entre objets Pydantic et dictionnaires, remplaçant les 18 occurrences de `model_dump()` dupliquées.
- **Exemple d'utilisation** :
  ```python
  # Avant
  if hasattr(obj, 'model_dump'):
      return obj.model_dump()
  else:
      return obj.dict() if hasattr(obj, 'dict') else vars(obj)

  # Après
  return ModelConverter.to_dict(obj)
  ```
- **Impact** : Réduit la duplication, améliore la maintenabilité, facilite les tests.

### 2. Injection de Dépendances (DIP)
- **Fichier créé** : `back/utils/dependency_injector.py`
- **Objectif** : Remplacer les instances globales et les appels directs par un conteneur de dépendances.
- **Exemple d'utilisation** :
  ```python
  # Avant
  item_service = ItemService()

  # Après
  item_service = get_service('item_service')
  ```
- **Impact** : Respecte DIP, facilite les tests avec mocks, évite les couplages forts.

### 3. Refactorisation de CharacterService (SRP)
- **Modifications** : Décomposition des responsabilités, utilisation de `ModelConverter`, délégation à `EquipmentService` (incluant l'inventaire) et `CharacterBusinessService`.
- **Exemple** :
  ```python
  # Avant : Logique d'inventaire dans CharacterService
  def add_item(self, item_id: str, qty: int = 1) -> Dict:
      # Logique dupliquée...

  # Après : Délégation
  def add_item(self, item_id: str, qty: int = 1) -> Dict:
      inventory_service = get_service('inventory_service')
      inventory_service.add_item(self.character_id, item_id, qty)
      return self._get_inventory()
  ```
- **Impact** : Respecte SRP, réduit la complexité, améliore la testabilité.

### 4. Tests Améliorés
- **Fichier créé** : `back/tests/utils/test_model_converter.py`
- **Modifications** : Correction des tests existants (e.g., `service.status` → `service.character_data.status`).
- **Exemple** :
  ```python
  def test_to_dict_with_pydantic_model(self):
      item = Item(id="sword", name="Épée", quantity=1)
      result = ModelConverter.to_dict(item)
      assert result["id"] == "sword"
  ```
- **Impact** : Augmente la couverture, améliore la fiabilité.

## Guide de Migration

### Étapes pour Appliquer les Changements
1. **Installer les dépendances** : Ajouter `dependency-injector` si nécessaire (pip install dependency-injector).
2. **Mettre à jour les imports** : Remplacer les imports directs par `get_service()`.
3. **Refactoriser les services** : Utiliser `ModelConverter` pour les conversions.
4. **Mettre à jour les tests** : Adapter les mocks pour utiliser le conteneur de dépendances.
5. **Tester l'intégration** : Vérifier que les endpoints FastAPI fonctionnent.

### Tests à Exécuter
- `pytest back/tests/utils/test_model_converter.py` : Tests pour ModelConverter.
- `pytest back/tests/test_character_service_refactored.py` : Tests mis à jour pour CharacterService.
- `pytest back/tests/services/` : Tests pour les services refactorisés.

### Rollback en Cas de Problème
- Conserver une branche Git avant les changements.
- Les modifications sont backward-compatible, mais tester localement.

## Conclusion
Ces améliorations alignent le code avec les principes du Clean Code, SOLID, et DRY, rendant le backend plus maintenable et testable. Le contexte du projet JDR (FastAPI + PydanticAI) est respecté, en priorisant la séparation des couches et le typage fort.