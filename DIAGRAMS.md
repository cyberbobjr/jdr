# Diagrammes Mermaid pour l'Analyse du Backend JDR

Ce document contient des diagrammes Mermaid pour visualiser la structure du backend du projet JDR, basés sur le code actuel, les tests, les modèles Pydantic, les utilitaires, et les améliorations proposées (respect de SOLID, DRY, injection de dépendances).

## Table des Matières
1. [Diagramme de Classes - Modèles et Schémas](#diagramme-de-classes---modèles-et-schémas)
2. [Diagramme de Séquence - Processus de Conversion](#diagramme-de-séquence---processus-de-conversion)
3. [Diagramme de Flux - Injection de Dépendances](#diagramme-de-flux---injection-de-dépendances)
4. [Diagramme d'Architecture - Structure Globale du Backend](#diagramme-darchitecture---structure-globale-du-backend)
5. [Diagramme de Séquence - Tests Unitaires](#diagramme-de-séquence---tests-unitaires)
6. [Diagramme Avant/Après - Refactorisation CharacterService](#diagramme-avantaprès---refactorisation-characterservice)
7. [Diagramme de Flux - Workflow d'Amélioration](#diagramme-de-flux---workflow-damélioration)

## Diagramme de Classes - Modèles et Schémas

Ce diagramme illustre les classes principales des modèles Pydantic, des services, et des utilitaires, en mettant en évidence les relations et les responsabilités.

```mermaid
classDiagram
    class Character {
        +id: str
        +name: str
        +race: Race
        +culture: Culture
        +caracteristiques: Dict[str, int]
        +competences: Dict[str, int]
        +inventory: List[Item]
        +equipment: List[str]
        +gold: float
        +xp: int
        +hp: int
        +status: CharacterStatus
        +is_complete: bool
    }

    class Item {
        +id: str
        +name: str
        +quantity: int
        +weight_kg: float
        +is_equipped: bool
    }

    class CharacterStatus {
        <<enumeration>>
        IN_PROGRESS
        DONE
    }

    class ModelConverter {
        +to_dict(obj: Any) Dict[str, Any]
        +to_json(obj: Any) str
    }

    class DependencyContainer {
        -_services: Dict[str, Any]
        -_config: Config
        +get(service_name: str) Any
        +register(service_name: str, service_instance: Any)
    }

    class CharacterService {
        -character_id: str
        -character_data: Character | Dict
        +__init__(character_id: str, strict_validation: bool)
        +save_character()
        +get_character() Character
        +add_item(item_id: str, qty: int) Dict
        +apply_xp(xp: int)
        +add_gold(gold: float)
    }

    class InventoryService {
        -data_service: CharacterDataService
        +add_item(character: Character, item_id: str, quantity: int) Character
        +add_item_object(character: Character, item: Item) Character
        +remove_item(character: Character, item_id: str, quantity: int) Character
    }

    class EquipmentService {
        -data_service: CharacterDataService
        -equipment_manager: EquipmentManager
        +buy_equipment(character: Character, equipment_name: str) Character
        +sell_equipment(character: Character, equipment_name: str) Character
        +update_money(character: Character, amount: float) Character
    }

    class CharacterDataService {
        +load_character(character_id: str) Character
        +save_character(character: Character)
    }

    class ItemService {
        +create_item_from_name(name: str, quantity: int) Item
    }

    class EquipmentManager {
        +get_equipment_by_name(name: str) Dict
    }

    Character --> Item : inventory
    Character --> CharacterStatus : status
    CharacterService --> Character : character_data
    CharacterService --> InventoryService : delegates to
    CharacterService --> EquipmentService : delegates to
    CharacterService --> ModelConverter : uses for conversion
    InventoryService --> CharacterDataService : persistence
    InventoryService --> ItemService : item creation
    EquipmentService --> CharacterDataService : persistence
    EquipmentService --> EquipmentManager : equipment details
    DependencyContainer --> CharacterService : manages
    DependencyContainer --> InventoryService : manages
    DependencyContainer --> EquipmentService : manages
```

## Diagramme de Séquence - Processus de Conversion

Ce diagramme montre le processus de conversion d'un objet Pydantic en dictionnaire via ModelConverter, illustrant le respect de DRY.

```mermaid
sequenceDiagram
    participant Client as Client Code
    participant ModelConverter as ModelConverter
    participant PydanticModel as Pydantic Model (e.g., Item)

    Client->>ModelConverter: to_dict(obj)
    alt obj has model_dump
        ModelConverter->>PydanticModel: obj.model_dump()
        PydanticModel-->>ModelConverter: dict
    else obj has dict
        ModelConverter->>PydanticModel: obj.dict()
        PydanticModel-->>ModelConverter: dict
    else obj is dict
        ModelConverter-->>ModelConverter: return obj as is
    else standard object
        ModelConverter->>PydanticModel: vars(obj)
        PydanticModel-->>ModelConverter: dict
    end
    ModelConverter-->>Client: dict

    Note over ModelConverter: Centralise la logique<br/>Évite la duplication de code<br/>Facilite les tests
```

## Diagramme de Flux - Injection de Dépendances

Ce diagramme illustre le flux d'injection de dépendances via DependencyContainer, remplaçant les globals et appels directs.

```mermaid
flowchart TD
    A[Client Code] --> B{Service Needed?}
    B -->|Yes| C[get_service(service_name)]
    C --> D[DependencyContainer.get()]
    D --> E{Service Registered?}
    E -->|Yes| F[Return Service Instance]
    E -->|No| G[Raise ValueError]
    F --> A
    B -->|No| H[Direct Usage]

    I[Container Initialization] --> J[Register Services]
    J --> K[Config]
    J --> L[CharacterPersistenceService]
    J --> M[CharacterDataService]
    J --> N[ItemService]
    J --> O[EquipmentService]
    J --> P[InventoryService with data_service]
    J --> Q[CharacterService]

    Note over D,F: Respecte DIP<br/>Facilite les mocks en tests<br/>Évite les couplages forts
```

## Diagramme d'Architecture - Structure Globale du Backend

Ce diagramme présente l'architecture globale du backend, en mettant en évidence les couches et les dépendances.

```mermaid
graph TB
    subgraph "API Layer"
        A[FastAPI App]
        B[Characters Router]
        C[Scenarios Router]
        D[Creation Router]
    end

    subgraph "Service Layer"
        E[CharacterService]
        F[InventoryService]
        G[EquipmentService]
        H[ScenarioService]
        I[CombatService]
        J[SessionService]
    end

    subgraph "Data Layer"
        K[CharacterDataService]
        L[CharacterPersistenceService]
        M[ItemService]
        N[EquipmentManager]
    end

    subgraph "Utilities"
        O[ModelConverter]
        P[DependencyContainer]
        Q[Logger]
        R[Config]
    end

    subgraph "Models"
        S[Character]
        T[Item]
        U[CharacterStatus]
        V[Equipment]
    end

    subgraph "Agents & Tools"
        W[GMAgentPydantic]
        X[CharacterTools]
        Y[CombatTools]
        Z[InventoryTools]
    end

    subgraph "Storage"
        AA[PydanticJsonlStore]
        BB[JSON Files]
    end

    A --> B
    A --> C
    A --> D
    B --> E
    C --> H
    D --> E
    E --> F
    E --> G
    E --> O
    F --> K
    G --> K
    H --> I
    I --> J
    K --> L
    L --> AA
    AA --> BB
    E --> P
    F --> P
    G --> P
    P --> R
    E --> S
    F --> T
    S --> U
    W --> X
    W --> Y
    W --> Z
    X --> E
    Y --> I
    Z --> F

    Note over A,AA: Architecture modulaire<br/>Séparation des couches<br/>Injection de dépendances
```

## Diagramme de Séquence - Tests Unitaires

Ce diagramme illustre le processus de test unitaire pour ModelConverter, montrant l'utilisation de mocks et l'isolation des tests.

```mermaid
sequenceDiagram
    participant Test as TestModelConverter
    participant Mock as Mock Object
    participant ModelConverter as ModelConverter
    participant Assert as Assertions

    Test->>Mock: Create mock object with model_dump()
    Mock-->>Test: mock_object
    Test->>ModelConverter: to_dict(mock_object)
    ModelConverter->>Mock: mock_object.model_dump()
    Mock-->>ModelConverter: {"id": "test", "name": "Test"}
    ModelConverter-->>Test: dict
    Test->>Assert: assert isinstance(result, dict)
    Test->>Assert: assert result["id"] == "test"
    Assert-->>Test: Pass

    Note over Test,Assert: Tests isolés<br/>Mocks pour dépendances<br/>Validation des conversions
```

## Diagramme Avant/Après - Refactorisation CharacterService

Ce diagramme compare la structure avant et après refactorisation de CharacterService, illustrant le respect de SRP et l'utilisation de DI.

```mermaid
flowchart LR
    subgraph "Avant Refactorisation"
        A1[CharacterService] --> B1[Inventaire Logic]
        A1 --> C1[Équipement Logic]
        A1 --> D1[Conversion Dict/Obj]
        A1 --> E1[Persistence]
        B1 --> D1
        C1 --> D1
        D1 --> E1
    end

    subgraph "Après Refactorisation"
        A2[CharacterService] --> B2[InventoryService]
        A2 --> C2[EquipmentService]
        A2 --> D2[ModelConverter]
        A2 --> E2[DependencyContainer]
        B2 --> F2[CharacterDataService]
        C2 --> F2
        D2 --> G2[Conversion Centralisée]
        E2 --> H2[Service Injection]
    end

    Note over A1,E2: Avant: Couplage fort, duplication<br/>Après: SRP respecté, DI, DRY
```

## Diagramme de Flux - Workflow d'Amélioration

Ce diagramme montre le workflow global des améliorations implémentées, de l'analyse à la validation.

```mermaid
flowchart TD
    A[Analyse du Code Existant] --> B[Identification des Problèmes<br/>- Violations SOLID<br/>- Duplication DRY<br/>- Manque de DI]
    B --> C[Proposition d'Améliorations<br/>- ModelConverter<br/>- DependencyContainer<br/>- Refactorisation Services]
    C --> D[Implémentation<br/>- Création des utilitaires<br/>- Refactorisation des services<br/>- Mise à jour des tests]
    D --> E[Tests et Validation<br/>- Tests unitaires<br/>- Intégration<br/>- Vérification des diagrammes]
    E --> F[Documentation<br/>- TODO.md<br/>- DIAGRAMS.md<br/>- Guide de migration]

    G[Problèmes Identifiés] -.-> A
    H[Améliorations Proposées] -.-> C
    I[Tests Échoués] -.-> D
    J[Feedback Utilisateur] -.-> B

    Note over A,F: Workflow itératif<br/>Améliorations progressives<br/>Validation continue
```

## Conclusion

Ces diagrammes Mermaid fournissent une visualisation complète de la structure du backend JDR, des problèmes identifiés, et des améliorations implémentées. Ils facilitent la compréhension des relations entre composants, des processus de conversion, et des workflows de test, tout en illustrant le respect des principes SOLID et DRY.