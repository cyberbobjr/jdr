# Spécification Technique – JdR « Terres du Milieu » orchestré par LLM

> **Objectif :** Proposer une architecture claire, modulaire et maintenable permettant à une équipe (ou à un bot de génération de code) de livrer :
>
> * un **back‑end** FastAPI + LangChain qui délègue la mécanique des règles à des *tools* Python ;
>
> > - une **infrastructure DevOps** (Docker / GitHub Actions) prête à l’emploi.
>
> Les règles de jeu (déjà modélisées dans les fichiers Python fournis) et la narration sont orchestrées par un LLM agissant comme Maître du Jeu.

---

## 1. Arborescence recommandée

```text
.
├── back/                        # Back‑end FastAPI + LangChain
│   ├── app.py                  # Point d’entrée FastAPI
│   ├── main.py                 # Target uvicorn – démarre l’app + l’agent
│   ├── config.py               # Variables d’environnement
│   ├── models/                 # Schémas Pydantic & objets métier
│   │   ├── domain/             # Reprise des fichiers .py uploadés (1 concept = 1 fichier)
│   │   └── schema.py           # DTO exposés par l’API
│   ├── services/               # Logique métier unitaire (SRP)
│   │   ├── character_service.py # Gestion des personnages et de leur inventaire
│   │   ├── combat_service.py
│   │   ├── skill_service.py
│   │   └── scenario_service.py
│   ├── tools/                  # Déclarations @tool LangChain
│   │   ├── inventory_tools.py
│   │   ├── combat_tools.py
│   │   ├── skill_tools.py
│   │   └── scenario_tools.py
│   ├── agents/                 # Assemblage AgentExecutor + mémoire
│   │   └── gm_agent.py
│   ├── routers/                # Endpoints REST (FastAPI "router")
│   │   ├── characters.py
│   │   ├── inventory.py
│   │   ├── scenarios.py
│   │   └── combat.py
│   ├── storage/                # Persistance JSON & ressources
│   │   └── file_storage.py     # CRUD thread‑safe (aiofiles + asyncio.Lock)
│   ├── utils/                  # Aides génériques
│   │   ├── dice.py             # Jets de dés
│   │   └── logger.py           # Logger JSON (Grafana/Loki‑friendly)
│   └── tests/                  # pytest – miroir des services
```

> **SRP** : un fichier = une responsabilité. Aucune logique d’E/S dans les services, aucune règle de jeu dans les routers.

---

## 2. Back‑end FastAPI + LangChain

### 2.1. Démarrage de l’application

```python
# back/app.py
from fastapi import FastAPI
from .routers import characters, inventory, combat, scenarios
from .agents.gm_agent import build_gm_agent

app = FastAPI(title="JdR – Terres du Milieu")

# Routers REST
app.include_router(characters.router, prefix="/api/characters")
app.include_router(inventory.router,  prefix="/api/inventory")
app.include_router(combat.router,     prefix="/api/combat")
app.include_router(scenarios.router,  prefix="/api/scenarios")

# Agent LangChain
gm_agent = build_gm_agent()

@app.post("/api/agent/respond")
async def agent_respond(session_id: UUID, message: str):
    """Le front envoie le message du joueur, reçoit la réponse du LLM."""
    return await gm_agent.ainvoke({"session_id": str(session_id), "message": message})
```

### 2.2. Modèles Pydantic (extrait)

```python
class Item(BaseModel):
    id: str
    name: str
    weight: float
    base_value: float

class Character(BaseModel):    id: UUID
    name: str
    race: str
    culture: str
    caracteristiques: Dict[str, int]
    competences: Dict[str, int]
    hp: int = 100  # calculé à partir de Constitution
    inventory: List[Item] = []
```

### 2.3. Services – signatures obligatoires

> **Gestion d’erreurs & journalisation :** chaque service encapsule ses échecs métier dans `GameError`. Un middleware global traduit celles‑ci en réponses HTTP appropriées (`400`, `404`, `409`, `500`, …) avec un corps JSON `{code, message}`. Tous les événements significatifs (niveau **INFO+**) sont journalisés via `utils.logger` au format JSON, enrichis d’un champ `trace_id` pour la corrélation.
>
> **Richesse & monnaie :** la trésorerie du personnage est modélisée par un dictionnaire `MoneyDict = {gold:int, silver:int, copper:int}`. Les services convertissent systématiquement ces montants en *cuivres* (`int`) pour les calculs, puis reconvertissent pour l’affichage. Tout débit insuffisant lève `NotEnoughMoneyError` → HTTP 409.

| Service              | Méthode         | Signature (sync)                                                    | Rôle métier                                                    |
| -------------------- | --------------- | ------------------------------------------------------------------- | -------------------------------------------------------------- |
| **CharacterService** | `add_item`      | `(player_id: UUID, item_id: str, qty: int = 1) -> InventorySummary` | Ajoute un objet (contrôle poids, duplicata, coût)              |
|                      | `remove_item`   | `(player_id: UUID, item_id: str, qty: int = 1) -> InventorySummary` | Retire l’objet ou diminue la quantité                          |
|                      | `equip_item`    | `(player_id: UUID, item_id: str) -> None`                           | Marque l’objet comme équipé ↔ mod. stats                       |
|                      | `sell_item`     | `(player_id: UUID, item_id: str, qty: int = 1) -> MoneySummary`     | Créditer le portefeuille après vente                           |
| **CharacterService** | `roll_skill`    | `(player_id: UUID, skill: str, difficulty: int = 50) -> RollResult` | Jet 1d100 + bonus de compétence                                |
|                      | `apply_xp`      | `(player_id: UUID, xp: int) -> int`                                 | Ajoute l’XP et gère la montée de niveau                        |
|                      | `take_damage`   | `(player_id: UUID, amount: int, source: str) -> int`                | Diminue les HP et renvoie le total restant                     |
|                      | `heal`          | `(player_id: UUID, amount: int, source: str) -> int`                | Soigne le personnage (max = hp\_max)                           |
|                      | `set_hp`        | `(player_id: UUID, new_hp: int) -> int`                             | Force un total de HP (réservé MJ / tests)                      |
|                      | `get_balance`   | `(player_id: UUID) -> MoneySummary`                                 | Retourne le solde `{gold, silver, copper}`                     |
|                      | `add_money`     | `(player_id: UUID, amount: MoneyDict, source: str) -> MoneySummary` | Crédite le porte‑monnaie (récompense, vente, butin)            |
|                      | `spend_money`   | `(player_id: UUID, amount: MoneyDict, source: str) -> MoneySummary` | Débite après achat ; lève `NotEnoughMoneyError` si insuffisant |
| **CombatService**    | `start_combat`  | `(player_ids: List[UUID], enemy_group: List[Enemy]) -> CombatState` | Initialise l’initiative                                        |
|                      | `resolve_round` | `(state: CombatState) -> CombatState`                               | Exécute un tour complet (cf. §4)                               |
|                      | `abort_combat`  | `(combat_id: UUID) -> None`                                         | Termine ou sauvegarde l’état                                   |
| **ScenarioService**  | `load_scenario` | `(file_name: str) -> Scenario`                                      | Charge le fichier .md                                          |
|                      | `advance_step`  | `(session_id: UUID, player_input: str) -> ScenarioStep`             | Retourne le nœud suivant + éventuel gain d’XP                  |

#### Exemples d’API (routers FastAPI)

> Chaque endpoint renvoie un corps JSON conforme aux DTO décrits dans `models/schema.py` et interagit avec le service correspondant.

| Service              | Méthode HTTP | Chemin                                    | Payload minimal                                     | Réponse 200 (exemple)                                                         |
| -------------------- | ------------ | ----------------------------------------- | --------------------------------------------------- | ----------------------------------------------------------------------------- |
| **CharacterService** | `POST`       | `/api/inventory/add`                      | `{ "item_id": "epee_arnor", "qty": 1 }`             | `{ "inventory": [...], "wallet": { "gold": 2, "silver": 12, "copper": 40 } }` |
|                      | `POST`       | `/api/inventory/equip`                    | `{ "item_id": "epee_arnor" }`                       | `{ "equipped": true }`                                                        |
| **CharacterService** | `POST`       | `/api/characters/{player_id}/skill-check` | `{ "skill": "esquive", "difficulty": 50 }`          | `{ "total": 67, "outcome": "success" }`                                       |
|                      | `PATCH`      | `/api/characters/{player_id}/hp`          | `{ "delta": -13, "source": "sword" }`               | `{ "hp": 63 }`                                                                |
| **CombatService**    | `POST`       | `/api/combat/start`                       | `{ "players": ["{uuid}"], "enemy_group": [ ... ] }` | `{ "combat_id": "combat-123", "state": "ongoing" }`                           |
|                      | `POST`       | `/api/combat/{combat_id}/round`           | *none*                                              | `CombatState` JSON                                                            |
| **ScenarioService**  | `GET`        | `/api/scenarios/{file_name}`              | *none*                                              | Markdown brut                                                                 |
|                      | `POST`       | `/api/scenarios/{session_id}/advance`     | `{ "player_input": "Je fouille la pièce" }`         | `{ "step": 5, "narration": "…", "xp_gain": 10 }`                              |

> **Codes d’erreur** : `400` données invalides ; `404` ressource manquante ; `409` conflit métier (ex. fonds insuffisants) ; `500` erreur inattendue.

### 2.4. LangChain Tools LangChain Tools (exemple)

LangChain Tools (exemple)

```python
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from uuid import UUID

class AddItemInput(BaseModel):
    player_id: UUID = Field(..., description="Identifiant du joueur")
    item_id: str = Field(..., description="Identifiant de l’objet à acquérir")
    qty: int = Field(1, description="Quantité")

@tool(args_schema=AddItemInput)
async def inventory_add_item(player_id: UUID, item_id: str, qty: int = 1) -> str:
    """Ajoute un objet à l’inventaire puis renvoie le résumé."""
    summary = svc.add_item(player_id=player_id, item_id=item_id, qty=qty)
    return summary.model_dump_json()
```

Appliquer le même schéma pour **toutes** les actions du §2.3.

---

## 3. Persistance JSON

### 3.1 Règle de nommage

Toutes les clés JSON suivent le **snake\_case** (minuscules + « \_ ») pour rester cohérentes avec les attributs Pydantic. Les identifiants uniques (UUID, combat\_id, etc.) utilisent également le snake\_case lorsqu’ils apparaissent comme clé.

### 3.2 Schémas et exemples

| Type de fichier                                                         | Emplacement                        | Clés obligatoires                                                                                                             | Exemple minimal |
| ----------------------------------------------------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | --------------- |
| **Fiche personnage**                                                    | `data/characters/{player_id}.json` | `id`, `name`, `race`, `culture`, `hp`, `hp_max`, `xp`, `caracteristiques`, `competences`, `gold`, `inventory` | \`\`\`json      |
| {                                                                       |                                    |                                                                                                                               |                 |
| "id": "123e4567-e89b-12d3-a456-426614174000",                           |                                    |                                                                                                                               |                 |
| "name": "Galadhwen",                                                    |                                    |                                                                                                                               |                 |
| "race": "Elfe",                                                         |                                    |                                                                                                                               |                 |
| "culture": "Sindar",                                                    |                                    |                                                                                                                               |                 |
| "hp": 76,                                                               |                                    |                                                                                                                               |                 |
| "hp\_max": 100,                                                         |                                    |                                                                                                                               |                 |
| "xp": 235,                                                              |                                    |                                                                                                                               |                 |
| "caracteristiques": {"force": 70, "constitution": 65, "dexterite": 80}, |                                    |                                                                                                                               |                 |
| "competences": {"esquive": 45, "connaissance\_generale": 60},           |                                    |                                                                                                                               |                 |
| "gold": 125,                                                            |                                    |                                                                                                                               |                 |
| "inventory": \[                                                         |                                    |                                                                                                                               |                 |

```
{"id": "epee_arnor", "name": "Épée d'Arnor", "qty": 1, "equipped": true}
```

]
}

````|
| **État de combat** | `data/combat/{combat_id}.json` | `combat_id`, `start_time`, `round`, `participants`, `log` | ```json
{
  "combat_id": "combat-9f6d84",
  "start_time": "2025-05-30T18:04:00Z",
  "round": 2,
  "participants": [
    {"ref": "player:123e4567-e89b-12d3-a456-426614174000", "initiative": 83, "hp": 76},
    {"ref": "npc:spectre-01", "initiative": 72, "hp": 24}
  ],
  "log": [
    {"round": 1, "actor": "player:123e4567-e89b-12d3-a456-426614174000", "description": "Galadhwen attaque le spectre", "hp_change": {"target": "npc:spectre-01", "delta": -13}}
  ]
}
``` |
| **Historique de session** | `data/sessions/{session_id}/history.json` | `session_id`, `created`, `messages` | ```json
{
  "session_id": "sess-f7251a",
  "created": "2025-05-30T18:00:00Z",
  "messages": [
    {"role": "user", "content": "Je pénètre dans la crypte…", "timestamp": "2025-05-30T18:01:02Z"},
    {"role": "gm", "content": "Une odeur glaciale t’enveloppe…", "timestamp": "2025-05-30T18:01:45Z"}
  ]
}
``` |
| **Scénario** | `data/scenarios/{file}.md` | Contenu Markdown (hors spécification JSON) | *Voir fichier `Les_Pierres_du_Passe.md` fourni* |

> **Note :** `file_storage.update()` doit conserver l’ordre des clés tel que défini par les schémas pour simplifier les diff Git.

---

## 4. Algorithme de combat détaillé

### 4.1. Séquence d’un round

1. **Initiative** – `1d100 + Rapidité + mod. équipement`.
2. **Tour du combattant actif**
   1. Choix de l’action.
   2. Jet d’attaque.
   3. Jet de défense (si possible).
   4. **Résolution** – différence des jets : échec, réussite, critique ou fumble.
   5. **Dégâts** – `base + delta // 10` – armure.
   6. **Mise à jour** des HP et de l’état (KO / mort).
3. **Fin de round** – log dans `CombatLog`; fin si un camp est vaincu.

### 4.2. Extrait de code

```python
# Simplifié : un tour de table
for combatant in turn_order:
    if combatant.hp <= 0:
        continue  # Inconscient ou mort
    action = self._choose_action_ai(combatant, state)  # ou input joueur
    round_log = self._execute_action(combatant, action, state)
    state.log.append(round_log)
```

### 4.3. Exemple narratif (tour unique)

> **Initiative** : Galadhwen (83) > Spectre (72)
> **Attaque** : 67 + 45 = 112 — **Défense** : 53 + 30 = 83 → *réussite* (Δ = 29)
> Dégâts : d8(6) + 2 = 8 → +5 (épée anti‑morts‑vivants) = **13 PV** retirés ; HP Spectre : 24/37.

### 4.4. Gestion des points de vie

La mise à jour des points de vie d’un personnage est centralisée dans **`CharacterService`** afin d’éviter toute duplication de logique. Les méthodes suivantes sont obligatoires :

| Méthode       | Signature (sync)                                     | Description                                                                                           |
| ------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `take_damage` | `(player_id: UUID, amount: int, source: str) -> int` | Diminue les HP (jamais < 0), retourne les HP restants ; journalise la source du dégât.                |
| `heal`        | `(player_id: UUID, amount: int, source: str) -> int` | Augmente les HP (max = hp\_max), retourne les HP restants ; vérifie que le personnage n’est pas mort. |
| `set_hp`      | `(player_id: UUID, new_hp: int) -> int`              | Force un total de HP (réservé au MJ ou aux tests).                                                    |
| `modify_hp`   | `(player_id: UUID, delta: int, source: str) -> int`  | Méthode interne appelée par `take_damage` et `heal`.                                                  |

> **Règles de cohérence** :
> • `hp <= 0` place automatiquement le personnage à l’état *inconscient* ;
> • `hp <= -max_hp * 0.5` déclenche l’état *mort* ;
> • chaque modification de HP est journalisée via `utils.logger` (`event="hp_change"`).

Le **`CombatService`** invoque systématiquement `take_damage` ou `heal` pour refléter les impacts de round ; aucune opération directe sur l’attribut `hp` hors de ces méthodes.

---

## 5. Exemple – gestion d’inventaire

1. Joueur : « J’achète l’épée ancienne chez Thadric pour 15 PO. »
2. `gm_agent` appelle `inventory_tools.add_item(item_id="epee_arnor", qty=1)`. La requête inclut implicitement `price={gold:15, silver:0, copper:0}`.
3. **CharacterService** :

   * Convertit le prix en *cuivres* (1 PO = 100 PI = 10 000 PC).
   * Vérifie que le porte‑monnaie du joueur dispose d’au moins 1 500 PC.
   * Si OK : débite le portefeuille (`wallet.subtract()`), contrôle le poids, ajoute l’objet, met à jour le fichier et renvoie `InventorySummary`.
   * Si fonds insuffisants : lève `NotEnoughMoneyError` (→ HTTP 409).
4. LLM : « Thadric tend l’épée, poids équilibré. Tes bourses sont plus légères de 15 pièces d’or. »

> **Remarque** : les valeurs monétaires sont toujours stockées sous forme d’un dictionnaire `{gold, silver, copper}`. Utiliser des fonctions d’aide `money_to_copper()` et `copper_to_money()` pour les conversions.

---

## 6. Exemple – test de compétence

| Étape | Outil                    | Entrée                                           | Sortie                                    |
| ----- | ------------------------ | ------------------------------------------------ | ----------------------------------------- |
| 1     | `skill_tools.roll_skill` | `{skill:"Connaissance Générale", difficulty:60}` | `RollResult(total=78, outcome:"success")` |
| 2     | LLM                      | Reçoit le `RollResult` et dépeint la scène       | Description narrative (succès ou échec)   |

### 6.1. Exemple de code Python (pour tests)

> **Important :** dans le flux de jeu réel, c’est le LLM (via LangChain) qui appelle automatiquement `skill_tools.roll_skill` pour déterminer la réussite ou l’échec d’une action. Le fragment ci‑dessous illustre simplement la façon de tester l’outil côté développeur ou d’écrire des tests unitaires.

````python
from uuid import UUID
from back.tools.skill_tools import roll_skill

# Identifiant fictif de joueur
a_sync_player_id = UUID("123e4567-e89b-12d3-a456-426614174000")

# Exemple de test automatisé
async def test_roll():
    data = {
        "player_id": a_sync_player_id,
        "skill": "Connaissance Générale",
        "difficulty": 60,
    }
    result_json = await roll_skill.ainvoke(data)
    from back.models.schema import RollResult
    result = RollResult.model_validate_json(result_json)
    assert result.outcome in {"success", "failure"}
```python
from uuid import UUID
from back.tools.skill_tools import roll_skill

# Identifiant fictif de joueur
player_id = UUID("123e4567-e89b-12d3-a456-426614174000")

# Appel asynchrone à l’outil LangChain
data = {
    "player_id": player_id,
    "skill": "Connaissance Générale",
    "difficulty": 60,
}
result_json = await roll_skill.ainvoke(data)  # renvoie un JSON serialisé

# Désérialiser vers l’objet Pydantic
from back.models.schema import RollResult
result = RollResult.model_validate_json(result_json)

if result.outcome == "success":
    print(f"Réussite avec {result.total} !")
else:
    print("Échec du test …")
````

\-------|------|--------|--------|
\| 1 | `skill_tools.roll_skill` | `{skill:"Connaissance Générale", difficulty:60}` | `RollResult(total=78, outcome:"success")` |
\| 2 | LLM | Produit la description narrative | – |

---

## 7. Attribution d’XP

`character_service.apply_xp` stocke l’XP, déclenche les montées de niveau et persiste la fiche personnage.

---

## 8. Endpoint : Récupération de l'historique d'une session de jeu

### GET /api/scenarios/history/{session_id}

Permet de récupérer l'historique complet des messages (utilisateur, assistant, outils, etc.) pour une session de jeu donnée. Utile pour restaurer l'état de la conversation côté front après un rafraîchissement ou une reconnexion.

**Paramètres :**
- `session_id` (UUID, path) : Identifiant unique de la session de jeu.

**Réponse :**
```json
{
  "history": [
    { "role": "user", "text": "Bonjour" },
    { "role": "assistant", "text": "Bienvenue !" },
    { "role": "tool", "text": "Résultat d'outil" }
    // ...
  ]
}
```

**Codes de retour :**
- 200 : Succès, historique retourné.
- 404 : Session non trouvée.
- 500 : Erreur interne.

**Notes :**
- L'ordre des messages est chronologique.
- Chaque message est un dictionnaire issu de la méthode `model_dump()` de Haystack.
- Cette route ne modifie pas l'état de la session.

---

## 9. Pipeline CI & Qualité

* **pytest** + couverture ≥ 90 %.
* **ruff** (lint) + **black** (format).
* **pre‑commit** pour automatiser.
* **build Docker** + push image sur GHCR (branche `main`).

### 9.1 Exemple de workflow GitHub Actions : `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  lint-test-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r back/requirements.txt
          pip install -r back/requirements-dev.txt

      - name: Lint & format check
        run: |
          ruff back
          black --check back

      - name: Run tests + coverage
        run: |
          pytest --cov=back --cov-report=xml

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.xml

      - name: Build Docker image
        run: |
          docker build -t ghcr.io/${{ github.repository }}:${{ github.sha }} back

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Push image
        run: |
          docker push ghcr.io/${{ github.repository }}:${{ github.sha }}
```

> **Astuce :** ajoutez, si besoin, un job de déploiement conditionnel (`on: workflow_run`) pour publier automatiquement sur votre serveur ou Kubernetes.

## 10. Dépendances principales (back)

Dépendances principales (back)

```text
# Framework web et ASGI
fastapi>=0.111
uvicorn[standard]>=0.30

# LLM & LangChain
openai>=1.30
langchain-core>=0.2.0
langchain-community>=0.2.0

# Validation de données & I/O
pydantic>=2.7
aiofiles>=23.2
python-dotenv>=1.0

# Tests et qualité de code
pytest>=8.2
pytest-asyncio>=0.23
coverage>=7.5
ruff>=0.4
black>=24.4

# Observabilité & journalisation
structlog>=24.1
orjson>=3.10

# Optionnel : métriques & tracing
prometheus-client>=0.20
```
