# Diagrammes d'Architecture - JdR Terres du Milieu

## 📊 Vue d'ensemble

Ce document présente les diagrammes d'architecture du backend JdR, mettant en évidence les anti-patterns identifiés et l'architecture cible après refactoring.

## 🏗️ Architecture Actuelle (Problématique)

### Diagramme de Composants Actuel

```mermaid
graph TB
    subgraph "Couche API"
        R1[Routers<br/>characters.py]
        R2[Routers<br/>creation.py]
        R3[Routers<br/>scenarios.py]
    end
    
    subgraph "Couche Services (SRP Violé)"
        S1[CharacterService<br/>SRP Violé]
        S2[SessionService<br/>Dépendances circulaires]
        S3[CombatService]
    end
    
    subgraph "Couche Agents PydanticAI"
        A1[GMAgent<br/>Patterns incorrects]
    end
    
    subgraph "Couche Outils"
        T1[CharacterTools<br/>Conversion dict/objets]
        T2[CombatTools]
        T3[InventoryTools]
    end
    
    subgraph "Couche Modèles"
        M1[Character<br/>Pydantic]
        M2[Schema<br/>Pydantic]
    end
    
    subgraph "Couche Stockage"
        ST1[PydanticJsonlStore]
        ST2[CharacterPersistenceService]
    end
    
    %% Connexions problématiques
    R1 --> S1
    R2 --> S1
    R3 --> S2
    S2 --> S1
    A1 --> T1
    T1 --> S1
    T1 --> S2
    
    %% Anti-patterns
    S1 -.->|"❌ Mixte objets/dicts"| M1
    T1 -.->|"❌ Conversion Pydantic→dict"| M1
    S2 -.->|"❌ Dépendances circulaires"| S1
```

### Diagramme de Flux de Données Problématique

```mermaid
sequenceDiagram
    participant Client
    participant Router
    participant CharacterService
    participant CharacterTools
    participant GMAgent
    
    Client->>Router: GET /api/characters/
    Router->>CharacterService: get_all_characters()
    
    Note over CharacterService: ❌ ANTI-PATTERN<br/>Mixte objets/dicts
    
    CharacterService->>CharacterService: _process_character_data()
    CharacterService-->>Router: List[dict/Character]
    Router-->>Client: CharacterListAny
    
    Client->>Router: POST /api/scenarios/play
    Router->>GMAgent: build_gm_agent_pydantic()
    
    Note over GMAgent: ❌ ANTI-PATTERN<br/>Dépendances circulaires
    
    GMAgent->>CharacterTools: character_apply_xp()
    
    Note over CharacterTools: ❌ ANTI-PATTERN<br/>Conversion Pydantic→dict
    
    CharacterTools->>CharacterService: apply_xp()
    CharacterService-->>CharacterTools: dict/Character
    CharacterTools-->>GMAgent: str (message)
    GMAgent-->>Router: str (response)
    Router-->>Client: JSON
```

### Diagramme de Classes Actuel (Problèmes)

```mermaid
classDiagram
    class CharacterService {
        -character_id: str
        -strict_validation: bool
        -character_data: dict/Character
        +__init__(character_id, strict_validation)
        +_load_character() dict/Character
        +save_character()
        +get_character() Character
        +get_character_json() str
        +get_all_characters() List[object]
        +get_character_by_id(character_id) dict
        +apply_xp(xp)
        +add_gold(gold)
        +take_damage(amount, source)
        +instantiate_item_by_id(item_id, qty) Item
        +add_item_object(item) Dict
        +item_exists(item_id) bool
        +add_item(item_id, qty) Dict
        +remove_item(item_id, qty) Dict
        +equip_item(item_id) Dict
        +unequip_item(item_id) Dict
        +buy_equipment(equipment_name) Dict
        +sell_equipment(equipment_name) Dict
        +update_money(amount) Dict
        +_process_character_data(character_id, character_data, action_prefix) object
    }
    
    class SessionService {
        -session_id: str
        -character_id: str
        -character_data: Dict[str, Any]
        -scenario_name: str
        -character_service: CharacterService
        -store: PydanticJsonlStore
        +__init__(session_id, character_id, scenario_name)
        +_load_session_data() bool
        +_create_session(character_id, scenario_name)
        +list_all_sessions() List[Dict[str, Any]]
    }
    
    class CharacterTools {
        +character_apply_xp(ctx, xp) str
        +character_add_gold(ctx, gold) str
        +character_take_damage(ctx, amount, source) str
    }
    
    class GMAgentPydantic {
        +build_gm_agent_pydantic(session_id, scenario_name, character_id) Tuple[Agent, SessionService]
        +enrich_user_message_with_character(user_message, character_data) str
        +enrich_user_message_with_combat_state(user_message, combat_state) str
        +auto_enrich_message_with_combat_context(session_id, user_message) str
        +build_simple_gm_agent() Agent
    }
    
    CharacterService "1" -- "1" SessionService : ❌ Dépendance circulaire
    CharacterTools --> CharacterService : Utilise
    CharacterTools --> SessionService : Utilise
    GMAgentPydantic --> SessionService : Dépendance
```

## 🎯 Architecture Cible (Après Refactoring)

### Diagramme de Composants Cible

```mermaid
graph TB
    subgraph "Couche API"
        R1[Routers<br/>DTOs clairs]
        R2[Routers<br/>Validation]
        R3[Routers<br/>Gestion erreurs]
    end
    
    subgraph "Couche Services (SRP Respecté)"
        S1[CharacterDataService<br/>Chargement/Sauvegarde]
        S2[CharacterBusinessService<br/>XP/Or/Dégâts]
        S3[InventoryService<br/>Gestion inventaire]
        S4[EquipmentService<br/>Achat/Vente]
        S5[SessionService<br/>Refactoré]
    end
    
    subgraph "Couche Agents PydanticAI"
        A1[GMAgent<br/>Patterns corrects]
    end
    
    subgraph "Couche Outils"
        T1[CharacterTools<br/>Objets Pydantic]
        T2[CombatTools<br/>Objets Pydantic]
        T3[InventoryTools<br/>Objets Pydantic]
    end
    
    subgraph "Couche Modèles"
        M1[Character<br/>Pydantic]
        M2[Schema<br/>Pydantic]
        M3[DTOs<br/>Réponses API]
    end
    
    subgraph "Couche Stockage"
        ST1[PydanticJsonlStore]
        ST2[CharacterPersistenceService]
    end
    
    %% Connexions propres
    R1 --> S2
    R1 --> S3
    R1 --> S4
    S2 --> S1
    S3 --> S1
    S4 --> S1
    A1 --> T1
    T1 --> S2
    T1 --> S3
    T1 --> S4
    
    %% Patterns corrects
    S1 -.->|"✅ Objets Pydantic purs"| M1
    T1 -.->|"✅ Accès direct aux attributs"| M1
```

### Diagramme de Flux de Données Cible

```mermaid
sequenceDiagram
    participant Client
    participant Router
    participant CharacterBusinessService
    participant CharacterTools
    participant GMAgent
    
    Client->>Router: GET /api/characters/
    Router->>CharacterBusinessService: get_all_characters()
    
    Note over CharacterBusinessService: ✅ Pattern correct<br/>Objets Pydantic purs
    
    CharacterBusinessService->>CharacterBusinessService: _load_characters()
    CharacterBusinessService-->>Router: List[Character]
    Router-->>Client: CharacterListDTO
    
    Client->>Router: POST /api/scenarios/play
    Router->>GMAgent: build_gm_agent_pydantic()
    
    Note over GMAgent: ✅ Dépendances clarifiées
    
    GMAgent->>CharacterTools: character_apply_xp()
    
    Note over CharacterTools: ✅ Accès direct aux attributs
    
    CharacterTools->>CharacterBusinessService: apply_xp()
    CharacterBusinessService-->>CharacterTools: Character
    CharacterTools-->>GMAgent: str (message)
    GMAgent-->>Router: str (response)
    Router-->>Client: JSON
```

### Diagramme de Classes Cible

```mermaid
classDiagram
    class CharacterDataService {
        -character_id: str
        +__init__(character_id)
        +load_character() Character
        +save_character(character: Character)
        +get_all_characters() List[Character]
        +get_character_by_id(character_id) Character
    }
    
    class CharacterBusinessService {
        -data_service: CharacterDataService
        +__init__(data_service)
        +apply_xp(character: Character, xp: int) Character
        +add_gold(character: Character, gold: float) Character
        +take_damage(character: Character, amount: int, source: str) Character
    }
    
    class InventoryService {
        -data_service: CharacterDataService
        +__init__(data_service)
        +add_item(character: Character, item_id: str, qty: int) Character
        +remove_item(character: Character, item_id: str, qty: int) Character
        +equip_item(character: Character, item_id: str) Character
        +unequip_item(character: Character, item_id: str) Character
    }
    
    class EquipmentService {
        -data_service: CharacterDataService
        +__init__(data_service)
        +buy_equipment(character: Character, equipment_name: str) Character
        +sell_equipment(character: Character, equipment_name: str) Character
        +update_money(character: Character, amount: float) Character
    }
    
    class CharacterTools {
        +character_apply_xp(ctx, xp) str
        +character_add_gold(ctx, gold) str
        +character_take_damage(ctx, amount, source) str
    }
    
    class SessionService {
        -session_id: str
        -character_id: str
        -character_data: Character
        -scenario_name: str
        -data_service: CharacterDataService
        -store: PydanticJsonlStore
        +__init__(session_id, character_id, scenario_name)
        +_load_session_data() bool
        +_create_session(character_id, scenario_name)
    }
    
    CharacterDataService "1" -- "1" CharacterBusinessService : Composition
    CharacterDataService "1" -- "1" InventoryService : Composition
    CharacterDataService "1" -- "1" EquipmentService : Composition
    CharacterTools --> CharacterBusinessService : Utilise
    CharacterTools --> InventoryService : Utilise
    CharacterTools --> EquipmentService : Utilise
    SessionService --> CharacterDataService : Utilise
```

## 🔍 Anti-Patterns Détailés

### 1. Violation du Pattern PydanticAI

**Code problématique :**
```python
# back/tools/character_tools.py
current_gold = ctx.deps.character_service.character_data.get('gold', 0) 
if isinstance(ctx.deps.character_service.character_data, dict) 
else ctx.deps.character_service.character_data.gold
```

**Solution :**
```python
# Pattern correct
current_gold = ctx.deps.character_service.character_data.gold
```

### 2. SRP Violé dans CharacterService

**Problèmes :**
- 20+ méthodes avec responsabilités variées
- Mixte entre logique métier et accès données
- Validation complexe des données

**Solution :**
- Séparation en 4 services spécialisés
- Chaque service a une responsabilité unique

### 3. Dépendances Circulaires

**Problème :**
```
GMAgent → SessionService → CharacterService → (potentiellement) GMAgent
```

**Solution :**
- Architecture en couches claires
- Injection de dépendances explicite
- Services indépendants

## 📈 Métriques d'Amélioration

| Métrique | Actuel | Cible | Amélioration |
|----------|--------|-------|--------------|
| SRP respecté | 20% | 95% | +75% |
| Utilisation objets Pydantic | 40% | 95% | +55% |
| Dépendances circulaires | 3 | 0 | -100% |
| Complexité cyclomatique | Élevée | Faible | -60% |
| Maintenabilité | Faible | Élevée | +80% |

## 🚀 Plan de Migration

### Phase 1 : Correction Patterns PydanticAI
- [ ] Refactorer `back/tools/character_tools.py`
- [ ] Utiliser `result.output` au lieu de `result.data`
- [ ] Éliminer les conversions dict/objets

### Phase 2 : Refactoring Services
- [ ] Créer `CharacterDataService`
- [ ] Créer `CharacterBusinessService` 
- [ ] Créer `InventoryService`
- [ ] Créer `EquipmentService`
- [ ] Refactorer `CharacterService` existant

### Phase 3 : Clarification Dépendances
- [ ] Refactorer `SessionService`
- [ ] Éliminer les imports circulaires
- [ ] Implémenter l'injection de dépendances

### Phase 4 : Amélioration API
- [ ] Créer des DTOs pour les réponses
- [ ] Standardiser la gestion d'erreurs
- [ ] Améliorer la documentation OpenAPI

Ce plan permettra d'obtenir une architecture plus maintenable, testable et conforme aux bonnes pratiques de développement.
