# Plan de Refactoring : Services Personnage

Ce document décrit le plan de refactoring visant à simplifier et consolider les services de gestion des personnages dans le backend.

## 1. Objectif

Réduire la complexité et la redondance en passant de 4 services à 2 services clairement définis, respectant le principe de responsabilité unique (SRP) mais regroupés par domaine fonctionnel (Données vs Métier).

## 2. État Actuel vs État Cible

### État Actuel (4 Services)
1.  **`back/services/character_persistence_service.py`** : Gestion bas niveau des fichiers JSON (I/O).
2.  **`back/services/character_data_service.py`** : Wrapper autour de la persistance, parfois instancié.
3.  **`back/services/character_business_service.py`** : Logique métier pure (XP, Or, Dégâts).
4.  **`back/services/character_service.py`** : Mélange de logique métier et de gestion d'état pour une session.

### État Cible (2 Services)

#### 1. `back/services/character_data_service.py` (Couche Données)
**Responsabilité :** Gestion complète du cycle de vie des données (CRUD).
**Fonctionnalités :**
*   Chargement (`load_character`)
*   Sauvegarde (`save_character`)
*   Listing (`get_all_characters`)
*   Suppression (`delete_character`)
*   Validation des IDs et chemins de fichiers.
*   **Note :** Ce service absorbera tout le code de `CharacterPersistenceService`.

#### 2. `back/services/character_service.py` (Couche Métier)
**Responsabilité :** Gestion d'un personnage actif au sein d'une session de jeu.
**Fonctionnalités :**
*   Modification des stats (HP, XP, Or).
*   Gestion de l'inventaire (via `EquipmentService` si nécessaire).
*   Tests de compétences et jets de dés.
*   Passage de niveau.
*   **Note :** Ce service absorbera tout le code de `CharacterBusinessService`. Il utilisera `CharacterDataService` pour persister les changements.

## 3. Plan d'Action Détaillé

### Étape 1 : Consolidation de la Couche Données (`CharacterDataService`)

1.  Modifier `back/services/character_data_service.py`.
2.  Y intégrer toutes les méthodes statiques de `back/services/character_persistence_service.py` (`_get_character_file_path`, `load_character_data`, `save_character_data`, `delete_character_data`).
3.  Adapter les signatures pour qu'elles soient cohérentes (choisir entre méthodes statiques ou d'instance, de préférence d'instance pour l'injection de dépendances, mais statiques pour la simplicité de migration immédiate si l'existant est fortement couplé). *Recommandation : Méthodes d'instance pour le futur, mais garder la compatibilité.*
4.  S'assurer que `CharacterDataService` couvre : `load`, `save`, `list`, `delete`.

### Étape 2 : Consolidation de la Couche Métier (`CharacterService`)

1.  Modifier `back/services/character_service.py`.
2.  Y intégrer les méthodes de `back/services/character_business_service.py` (`apply_xp`, `add_gold`, `take_damage`, `heal`).
3.  S'assurer que `CharacterService` utilise `CharacterDataService` pour sauvegarder l'état après modification.
4.  Nettoyer les imports inutiles.

### Étape 3 : Mise à jour des Références

Il faudra rechercher et remplacer les imports et utilisations dans tout le projet :

*   **Remplacer** `CharacterPersistenceService` **par** `CharacterDataService`.
*   **Remplacer** `CharacterBusinessService` **par** `CharacterService`.

**Fichiers susceptibles d'être impactés :**
*   `back/routers/characters.py`
*   `back/routers/gamesession.py`
*   `back/routers/creation.py`
*   `back/tools/character_tools.py`
*   `back/tools/skill_tools.py`
*   `back/agents/gm_agent_pydantic.py`
*   `back/tests/*`

### Étape 4 : Nettoyage

1.  Supprimer `back/services/character_persistence_service.py`.
2.  Supprimer `back/services/character_business_service.py`.
3.  Vérifier que tous les tests passent (`./run_tests.sh`).

## 4. Exemple de Structure Cible

### `CharacterDataService`
```python
class CharacterDataService:
    def load_character(self, character_id: str) -> Character: ...
    def save_character(self, character: Character) -> None: ...
    def get_all_characters(self) -> List[Character]: ...
    def delete_character(self, character_id: str) -> None: ...
```

### `CharacterService`
```python
class CharacterService:
    def __init__(self, character_id: str): ...
    def apply_xp(self, amount: int) -> None: ...
    def add_gold(self, amount: float) -> None: ...
    def take_damage(self, amount: int) -> None: ...
    # ... autres méthodes métier
```
