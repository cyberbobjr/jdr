# Règles Cline pour le projet JdR "Terres du Milieu"

## 🎯 **PROJET : JdR orchestré par LLM**
**Stack :** FastAPI + PydanticAI
**Objectif :** Système de jeu de rôle avec Maître du Jeu LLM

---

## 🏗️ **ARCHITECTURE ET STRUCTURE**

### Organisation des fichiers (Backend uniquement)
```
back/                           # Backend FastAPI + PydanticAI
├── app.py                      # Point d'entrée FastAPI
├── main.py                     # Target uvicorn – démarre l'app + l'agent
├── config.py                   # Variables d'environnement
├── models/                     # Schémas Pydantic & objets métier
│   ├── domain/                 # Domain models (1 concept = 1 fichier)
│   │   ├── character.py        # Character domain model
│   │   ├── combat_state.py     # Combat state model
│   │   ├── stats_manager.py    # Stats management
│   │   ├── skills_manager.py   # Skills management
│   │   ├── equipment_manager.py # Equipment management
│   │   ├── races_manager.py    # Races/cultures management
│   │   └── spells_manager.py   # Spells management
│   └── schema.py               # DTO exposés par l'API
├── services/                   # Logique métier unitaire (SRP)
│   ├── character_service.py    # Gestion des personnages
│   ├── character_creation_service.py # Création de personnages
│   ├── character_persistence_service.py # Persistance
│   ├── character_business_service.py # Logique métier
│   ├── character_data_service.py # Données personnage
│   ├── combat_service.py       # Système de combat
│   ├── combat_state_service.py # État combat
│   ├── equipment_service.py    # Équipement
│   ├── inventory_service.py    # Inventaire
│   ├── item_service.py         # Objets
│   ├── skill_service.py        # Compétences
│   ├── scenario_service.py     # Scénarios
│   └── session_service.py      # Sessions de jeu
├── tools/                      # Outils PydanticAI
│   ├── character_tools.py      # Outils personnages
│   ├── combat_tools.py         # Système de combat
│   ├── inventory_tools.py      # Gestion inventaire
│   ├── skill_tools.py          # Tests de compétences
│   └── schema_tools.py         # Outils schéma
├── agents/                     # Agents LLM PydanticAI
│   └── gm_agent_pydantic.py    # Game Master Agent
├── routers/                    # Endpoints REST FastAPI
│   ├── characters.py           # Routes personnages
│   ├── creation.py             # Routes création
│   └── scenarios.py            # Routes scénarios
├── storage/                    # Persistance
│   ├── __init__.py
│   └── pydantic_jsonl_store.py # Store JSONL
├── utils/                      # Utilitaires
│   ├── dependency_injector.py  # Injection de dépendances
│   ├── dice.py                 # Jets de dés
│   ├── exceptions.py           # Exceptions métier
│   ├── logger.py               # Logger
│   ├── logging_tool.py         # Outils de log
│   ├── message_adapter.py      # Adaptateur de messages
│   └── model_converter.py      # Conversion de modèles
└── tests/                      # Tests pytest
    ├── agents/                 # Tests agents
    ├── domain/                 # Tests domain
    ├── routers/                # Tests API
    ├── services/               # Tests services
    ├── storage/                # Tests persistance
    ├── tools/                  # Tests outils
    └── utils/                  # Tests utilitaires
```

### Principes architecturaux
- **SRP strict** : Un service = une responsabilité
- **Séparation des couches** : Routers → Services → Agents → Tools
- **Typage fort** : Pydantic pour tous les modèles
- **Persistance** : JSONL via `pydantic_jsonl_store.py`

---

## 🔧 **CONVENTIONS DE DÉVELOPPEMENT**

### Agents PydanticAI
```python
# ✅ CORRECT
from pydantic_ai import Agent, RunContext

def create_agent(model: str) -> Agent:
    agent = Agent(
        model=model,
        deps_type=UserContext,
        output_type=StructuredResponse,
        retries=2
    )
    
    @agent.tool
    async def my_tool(ctx: RunContext[UserContext], param: str) -> dict:
        # Logique métier
        return {"result": "data"}
    
    return agent
```

### Services
- **Nommage** : `{domain}_service.py` (ex: `character_service.py`)
- **Instance-based** : Services instanciés avec contexte
- **Pas de logique HTTP** dans les services
- **Validation Pydantic** pour tous les inputs/outputs

### Routers FastAPI
- **Responsabilité unique** : Gestion HTTP uniquement
- **Délégation** : Toute logique métier déléguée aux services
- **Documentation** : Docstrings complètes avec exemples

### Modèles Domain
- **Localisation** : `back/models/domain/` uniquement
- **Nommage** : Un fichier par concept métier
- **Validation** : Pydantic pour tous les modèles
- **Language** : Anglais pour les nouveaux modèles V2

---

## 🚨 **RÈGLES CRITIQUES - NE JAMAIS VIOLER**

### Organisation des fichiers
- ❌ **NE JAMAIS** créer de fichiers à la racine (sauf configuration)
- ❌ **NE JAMAIS** mélanger les responsabilités entre couches
- ✅ **TOUJOURS** respecter la structure modulaire

### PydanticAI - Patterns obligatoires
```python
# ✅ CORRECT - Accès direct aux objets Pydantic
result.output.chunks  # ✅
result.data.model_dump().get("chunks")  # ❌ ANTI-PATTERN

# ✅ CORRECT - Structured output
agent = Agent(model, output_type=MyModel)  # ✅
agent = Agent(model)  # ❌ (sans structured output)
```

### Gestion des données
- **Personnages** : Format JSON racine (pas de clé `state`)
- **Historique** : JSONL via `pydantic_jsonl_store.py`
- **Scénarios** : Markdown dans `data/scenarios/`
- **Configuration** : Format YAML pour tous les fichiers de règles

---

## 🛠️ **OUTILS ET PATTERNS SPÉCIFIQUES**

### Outils PydanticAI existants
- `skill_tools.py` : Tests de compétences
- `combat_tools.py` : Système de combat complet
- `inventory_tools.py` : Gestion d'inventaire
- `character_tools.py` : Gestion des personnages

### Patterns de création d'outils
```python
@agent.tool
async def my_tool(
    ctx: RunContext[UserContext],
    param: str = Field(description="Description claire")
) -> Dict[str, Any]:
    """
    Description de l'outil.
    
    Args:
        param: Description du paramètre
        
    Returns:
        Structure de retour documentée
    """
    # Accès aux dépendances
    character_service = ctx.deps.character_service
    # Logique métier
    return {"result": "data"}
```

### Gestion des sessions
- **Prévention des doublons** : Vérification `character_name + scenario_name`
- **Statut personnage** : Vérifier `status !== "en_cours"` avant jeu
- **Historique** : Gestion via `SessionService`

---

## 🧪 **TESTS ET QUALITÉ**

### Organisation des tests
```
back/tests/
├── agents/     # Tests PydanticAI
├── domain/     # Tests modèles domain
├── routers/    # Tests API
├── services/   # Tests métier
├── storage/    # Tests persistance
├── tools/      # Tests outils
└── utils/      # Tests utilitaires
```

### Règles de test
- **Mocking obligatoire** : Redis, LightRAG, OpenAI, Neo4j
- **Tests asynchrones** : `pytest-asyncio` pour async/await
- **Couverture** : ≥80% pour les services critiques
- **Nettoyage** : Sessions de test automatiquement nettoyées
- **Counverture** : Toujours tester les cas aux limites

---

## 🔄 **WORKFLOWS DE DÉVELOPPEMENT**

### Ajout d'un nouvel endpoint
1. Modèle Pydantic dans `models/domain/{concept}.py`
2. Service dans `services/{domain}_service.py`
3. Route dans `routers/{domain}.py`
4. Tests dans `tests/services/` et `tests/routers/`

### Ajout d'un nouvel agent PydanticAI
1. Modèles de réponse dans `models/domain/{concept}.py`
2. Agent dans `agents/{agent_name}.py`
3. Outils dans `tools/{domain}_tools.py`
4. Registration dans `services/llm_service.py`
5. Tests complets

### Modification des données de jeu
- **Compétences** : `data/skills_for_llm.yaml`
- **Races/cultures** : `data/races_and_cultures.yaml`
- **Équipement** : `data/equipment.yaml`
- **Scripts** : `tools/` pour la génération automatique

---

## ⚠️ **PROBLÈMES COURANTS ET SOLUTIONS**

### Boucles infinies LLM
- **Cause** : Agent qui ne respecte pas la structure des tours
- **Solution** : Instructions structurées dans le prompt système

### Sessions dupliquées
- **Cause** : Même personnage + scénario
- **Solution** : Vérification dans `ScenarioService.start_scenario()`

### Format personnage obsolète
- **Cause** : Clé `state` dans les JSON
- **Solution** : Format racine uniquement

---

## 🚀 **COMMANDES DE DÉVELOPPEMENT**

### Installation et lancement
```bash
# Backend
cd back && python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Tests
```bash
# Backend
cd back && pytest tests/ -v
```

### Qualité de code
```bash
# Backend
ruff check back/
black back/
```

---

## 📚 **DOCUMENTATION ET RESSOURCES**

### Fichiers importants
- `README.md` : Documentation générale
- `pydanticai.md` : Documentation PydanticAI
- `instructions/openai-instructions.md` : Spécifications techniques

### Références
- **FastAPI** : https://fastapi.tiangolo.com/
- **PydanticAI** : https://ai.pydantic.dev/

---

**Version** : 2.0
**Dernière mise à jour** : 2025-11-12
**Mainteneur** : Équipe de développement JdR
