# JdR "Terres du Milieu" orchestré par LLM

Ce projet vise à créer un jeu de rôle (JdR) se déroulant dans les Terres du Milieu, où la narration et les mécaniques de jeu sont orchestrées par un Large Language Model (LLM) agissant comme Maître du Jeu (MJ).

## Architecture Générale

L'architecture s'articule autour d'un backend FastAPI et **Haystack 3.x** (remplaçant totalement LangChain), et d'une infrastructure DevOps. Les détails de la spécification technique se trouvent dans [instructions/openai-instructions.md](instructions/openai-instructions.md).

- **Documentation Haystack** :
  - [Haystack Documentation](https://docs.haystack.deepset.ai/docs/introduction)
  - [Haystack Tools](https://docs.haystack.deepset.ai/docs/tool)
  - [Haystack Agents](https://docs.haystack.deepset.ai/docs/agents)
  - [Gestion de la mémoire (mémoire persistante, stores, etc.)](./HaystackMemoryDoc.md)

## Migration Haystack 3.x (2025)

- **Stack 100% Haystack :** Suppression complète de LangChain, migration de tous les outils et de l’agent MJ vers Haystack 3.x.
- **Agent MJ :** Utilise `haystack.components.agents.Agent` avec un générateur compatible outils (`OpenAIChatGenerator`) et une mémoire persistante custom (JSONL).
- **Outils :** Tous les outils sont des instances de `haystack.tools.Tool` (combat, inventaire, compétences). Plus aucun décorateur LangChain.
- **Mémoire :** Historique des conversations stocké en JSONL via un store custom, compatible Haystack (voir [HaystackMemoryDoc.md](./HaystackMemoryDoc.md)).
  - **Prompt système non dupliqué :** Le prompt système (`system_prompt`) n’est jamais stocké dans l’historique JSONL. Il est injecté dynamiquement par l’agent à chaque appel, ce qui évite toute duplication ou pollution du contexte envoyé au LLM. Seuls les messages utilisateur, assistant et outils sont persistés.

## Structure du Projet

```
.
├── back/                        # Back‑end FastAPI + Haystack
│   ├── app.py                  # Point d’entrée FastAPI
│   ├── main.py                 # Target uvicorn – démarre l’app + l’agent
│   ├── config.py               # Variables d’environnement
│   ├── models/                 # Schémas Pydantic & objets métier
│   │   ├── domain/             # Reprise des fichiers .py uploadés (1 concept = 1 fichier)
│   │   └── schema.py           # DTO exposés par l’API
│   ├── services/               # Logique métier unitaire (SRP)
│   │   ├── inventory_service.py # Gestion de l'inventaire des personnages
│   │   ├── character_service.py # Gestion des personnages (création, évolution, etc.)
│   │   ├── combat_service.py    # Gestion des mécaniques de combat
│   │   ├── skill_service.py     # Gestion des compétences et de leurs jets
│   │   └── scenario_service.py  # Gestion du déroulement des scénarios
│   ├── tools/                  # Outils Haystack (ex-tools LangChain migrés)
│   │   ├── inventory_tools.py  # Outils pour l'inventaire (ajout, retrait, gestion d'objets)
│   │   ├── combat_tools.py     # Outils pour le combat
│   │   ├── skill_tools.py      # Outils pour les compétences
│   │   └── scenario_tools.py   # (Supprimé : tools scénario désormais inutiles, toute la logique passe par l'API REST)
│   ├── agents/                 # Assemblage Agent Haystack + mémoire
│   │   └── gm_agent.py         # Agent LLM Maître du Jeu (mémoire persistante JSONL via store custom)
│   ├── routers/                # Endpoints REST (FastAPI "router")
│   │   ├── characters.py       # Endpoints pour la gestion des personnages
│   │   ├── inventory.py        # Endpoints pour la gestion de l'inventaire
│   │   ├── scenarios.py        # Endpoints pour la gestion des scénarios
│   │   └── combat.py           # Endpoints pour la gestion du combat
│   ├── storage/                # Persistance JSON & ressources
│   │   └── file_storage.py     # CRUD thread‑safe (aiofiles + asyncio.Lock) pour la persistance des données
│   ├── utils/                  # Aides génériques
│   │   ├── dice.py             # Fonctions pour les jets de dés
│   │   └── logger.py           # Logger JSON (Grafana/Loki‑friendly)
│   └── tests/                  # Tests unitaires et d'intégration (pytest – miroir des services)
│       └── domain/             # Tests pour les modèles du domaine
│           └── test_caracteristiques.py # Tests pour la classe Caracteristiques
├── data/                        # Données persistantes du jeu
│   ├── characters/             # Fiches des personnages joueurs et non-joueurs
│   ├── combat/                 # États des combats en cours
│   ├── scenarios/              # Fichiers Markdown décrivant les scénarios
│   └── sessions/               # Historique des conversations et états des sessions de jeu
├── instructions/                # Spécifications et instructions pour le développement
│   └── openai-instructions.md  # Document principal des spécifications techniques
├── HaystackMemoryDoc.md         # Documentation détaillée sur la mémoire Haystack
└── README.md                    # Ce fichier
```

## Objectifs des Fichiers (Backend)

### `back/app.py`
**Objectif:** Point d'entrée principal de l'application FastAPI. Initialise l'application, inclut les routers et configure l'agent LangChain.

### `back/main.py`
**Objectif:** Fichier cible pour `uvicorn`. Responsable du démarrage de l'application FastAPI et de l'agent LangChain.

### `back/config.py`
**Objectif:** Gérer les variables d'environnement et les configurations de l'application.

### `back/models/domain/`
**Objectif:** Contenir les modèles de données métier (objets Python purs) représentant les concepts clés du jeu (Personnage, Objet, Compétence, etc.). Chaque concept devrait avoir son propre fichier.

### `back/models/schema.py`
**Objectif:** Définir les schémas Pydantic utilisés pour la validation des données des requêtes et des réponses de l'API (Data Transfer Objects - DTO).

### `back/services/inventory_service.py`
**Objectif:** Encapsuler la logique métier liée à la gestion de l'inventaire des personnages (ajout, suppression, équipement, vente d'objets).

### `back/services/character_service.py`
**Objectif:** Gérer la logique métier des personnages, incluant les jets de compétence, l'application de l'expérience (XP), la gestion des points de vie (PV), et la gestion de la monnaie.

### `back/services/combat_service.py`
**Objectif:** Implémenter la logique métier pour la gestion des combats, incluant le démarrage, la résolution des rounds et l'arrêt des combats.

### `back/services/skill_service.py`
**Objectif:** Centraliser la logique liée à l'utilisation et à la résolution des tests de compétences des personnages.

### `back/services/scenario_service.py`
**Objectif:** Gérer le chargement et la progression dans les scénarios du jeu, en interprétant les actions des joueurs pour faire avancer l'histoire.

### `back/tools/inventory_tools.py`
**Objectif:** Définir les outils LangChain permettant à l'agent LLM d'interagir avec le `InventoryService` (par exemple, ajouter un objet à l'inventaire).

### `back/tools/combat_tools.py`
**Objectif:** Définir les outils LangChain permettant à l'agent LLM d'interagir avec le `CombatService` et de participer à la gestion du combat.

### `back/tools/skill_tools.py`
**Objectif :** Fournit des outils LangChain pour effectuer des tests de compétences et de caractéristiques.

- **`skill_check(skill_level: int, difficulty: int) -> bool`** :
  - **Description :** Effectue un test de compétence en comparant un jet de dé au niveau de compétence ajusté par la difficulté.
  - **Paramètres :**
    - `skill_level` (int) : Niveau de compétence du personnage.
    - `difficulty` (int) : Difficulté du test.
  - **Retourne :** `True` si le test est réussi, sinon `False`.

### Intégration avec le LLM
Le LLM peut appeler ces outils pour simuler des actions des personnages, comme escalader un mur, crocheter une serrure ou convaincre un PNJ. Les résultats des tests influencent directement la narration et les événements du scénario.

### `back/agents/gm_agent.py`
**Objectif:** Construire et configurer l'`AgentExecutor` de LangChain qui agira comme Maître du Jeu. Cet agent utilisera les outils définis pour interagir avec les services du backend et générer des réponses narratives.

### `back/routers/characters.py`
**Objectif:** Définir les endpoints de l'API REST (routes FastAPI) pour la gestion des personnages (par exemple, création, récupération d'informations).

### `back/routers/inventory.py`
**Objectif:** Définir les endpoints de l'API REST pour la gestion de l'inventaire des personnages.

### `back/routers/scenarios.py`
**Objectif:** Définir les endpoints de l'API REST pour interagir avec les scénarios (par exemple, démarrer un scénario, soumettre une action de joueur).

### `back/routers/combat.py`
**Objectif:** Définir les endpoints de l'API REST pour la gestion des combats.

### `back/storage/file_storage.py`
**Objectif:** Fournir des fonctions CRUD (Create, Read, Update, Delete) asynchrones et thread-safe pour lire et écrire les données du jeu (personnages, scénarios, sessions, combats) dans des fichiers JSON. Utilise `aiofiles` et `asyncio.Lock`.

### `back/utils/dice.py`
**Objectif:** Fournir des fonctions utilitaires pour effectuer des jets de dés (par exemple, 1d100, nd6).

### `back/utils/logger.py`
**Objectif:** Configurer et fournir une instance de logger pour enregistrer les événements de l'application dans un format structuré (JSON), facilitant l'intégration avec des systèmes de logging centralisés comme Grafana/Loki.

### `back/tests/domain/test_caracteristiques.py`
**Objectif:** Contenir les tests unitaires pour la classe `Caracteristiques` située dans `back/models/domain/caracteristiques.py`. Ces tests visent à vérifier le bon fonctionnement des méthodes de calcul de coût, de validation de distribution et de récupération des bonus et descriptions des caractéristiques.

## Modifications du Modèle `Character`

Le modèle `Character` a été enrichi avec les propriétés suivantes :

- `equipment` (List[str]) : Liste des équipements du personnage.
- `spells` (List[str]) : Liste des sorts connus par le personnage.
- `equipment_summary` (Optional[Dict[str, float]]) : Résumé des équipements, incluant le coût total, le poids total, etc.
- `culture_bonuses` (Optional[Dict[str, int]]) : Bonus culturels du personnage.

Ces propriétés permettent de mieux représenter les données des personnages dans le jeu et sont extraites des fichiers JSON correspondants.

## Mise à jour récente

### Migration de la gestion de la mémoire
- La mémoire conversationnelle persistante repose sur `ConversationBufferMemory` (LangChain) et `FileChatMessageHistory` (langchain_community), pour garantir la persistance multi-session sur disque (JSONL).
- Cette solution assure la compatibilité avec les versions récentes de LangChain et la robustesse de la persistance.

### Tests
- Tous les tests unitaires ont été mis à jour et validés pour garantir la compatibilité avec les changements récents.

---

*Ce README sera mis à jour au fur et à mesure de l'avancement du projet.*

## Routes pour les scénarios

#### `/api/scenarios/{scenario_file}`
**Description :** Récupère le contenu d'un scénario à partir de son nom de fichier Markdown (ex : `Les_Pierres_du_Passe.md`).

**Méthode :** GET

**Paramètre d'URL :**
- `scenario_file` (str) : Nom du fichier du scénario (doit exister dans `data/scenarios/`).

**Réponse :**
- Succès : Contenu brut du fichier Markdown.
- Erreur 404 : Si le fichier n'existe pas.

Exemple :
```
GET /api/scenarios/Les_Pierres_du_Passe.md
```
Retourne le contenu du fichier `data/scenarios/Les_Pierres_du_Passe.md`.

## Nouveaux Endpoints

### Combat
- **POST /attack** : Effectue un jet d'attaque en lançant des dés selon une notation donnée (ex: "1d20").

### Compétences
- **POST /skill-check** : Effectue un test de compétence en comparant un jet de dé au niveau de compétence et à la difficulté.

## Gestion des Combats

### CombatManager
- **Description** : Classe pour gérer les combats, située dans `back/models/domain/combat_manager.py`.
- **Méthodes** :
  - `roll_initiative(characters)` : Calcule l'ordre d'initiative pour les personnages.
  - `next_turn()` : Passe au tour suivant dans l'ordre d'initiative.
  - `reset_combat()` : Réinitialise le combat.
  - `calculate_initiative(character_stats)` : Calcule l'initiative d'un personnage en fonction de ses statistiques.
  - `resolve_attack(attack_roll, defense_roll)` : Résout une attaque en comparant les jets d'attaque et de défense.
  - `calculate_damage(base_damage, modifiers)` : Calcule les dégâts infligés en tenant compte des modificateurs.

### `back/models/domain/combat_manager.py`
**Objectif :** Gère les mécaniques de combat, y compris l'ordre d'initiative, la gestion des tours et les actions des personnages.

- **`roll_initiative(characters: dict) -> list`** :
  - **Description :** Calcule l'ordre d'initiative des personnages en fonction de leurs statistiques.
  - **Paramètres :**
    - `characters` (dict) : Dictionnaire contenant les personnages et leurs statistiques d'initiative.
  - **Retourne :** Une liste triée des personnages avec leurs initiatives.

- **`next_turn() -> object`** :
  - **Description :** Passe au tour suivant dans l'ordre d'initiative.
  - **Retourne :** Le personnage dont c'est le tour.

### `back/tools/combat_tools.py`
**Objectif :** Fournit des outils LangChain pour les actions de combat.

- **`roll_initiative_tool(input: InitiativeInput) -> list`** :
  - **Description :** Calcule l'ordre d'initiative des personnages via un outil LangChain.
  - **Paramètres :**
    - `input` (InitiativeInput) : Modèle contenant les personnages.
  - **Retourne :** Une liste triée des personnages avec leurs initiatives.

- **`perform_attack_tool(input: AttackInput) -> int`** :
  - **Description :** Effectue un jet d'attaque via un outil LangChain.
  - **Paramètres :**
    - `input` (AttackInput) : Modèle contenant la notation des dés.
  - **Retourne :** Le résultat du jet d'attaque.

- **`resolve_attack_tool(input: ResolveAttackInput) -> bool`** :
  - **Description :** Résout une attaque en comparant les jets d'attaque et de défense via un outil LangChain.
  - **Paramètres :**
    - `input` (ResolveAttackInput) : Modèle contenant les jets d'attaque et de défense.
  - **Retourne :** `True` si l'attaque réussit, sinon `False`.

- **`calculate_damage_tool(input: DamageInput) -> int`** :
  - **Description :** Calcule les dégâts infligés en tenant compte des modificateurs via un outil LangChain.
  - **Paramètres :**
    - `input` (DamageInput) : Modèle contenant les dégâts de base et les modificateurs.
  - **Retourne :** Les dégâts finaux infligés.

### Inventaire (`back/tools/inventory_tools.py`)
- **inventory_add_item**  
  Ajoute un objet à l’inventaire d’un joueur.  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du joueur
  - `item_id` (string) : Identifiant de l’objet à acquérir
  - `qty` (int, optionnel, défaut : 1) : Quantité à ajouter
  **Retour :** Résumé de l’inventaire mis à jour (dict)

- **inventory_remove_item**  
  Retire un objet de l’inventaire d’un joueur.  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du joueur
  - `item_id` (string) : Identifiant de l’objet à retirer
  - `qty` (int, optionnel, défaut : 1) : Quantité à retirer
  **Retour :** Résumé de l’inventaire mis à jour (dict)

### Personnage (`back/tools/character_tools.py`)
- **character_apply_xp**  
  Ajoute de l’XP à un personnage.  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du personnage
  - `xp` (int) : Points d’expérience à ajouter
  **Retour :** Fiche personnage mise à jour (dict)

- **character_add_gold**  
  Ajoute de l’or au portefeuille du personnage.  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du personnage
  - `gold` (int) : Montant d’or à ajouter
  **Retour :** Fiche personnage mise à jour (dict)

- **character_take_damage**  
  Applique des dégâts à un personnage (réduit ses PV).  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du personnage
  - `amount` (int) : Points de dégâts à appliquer
  - `source` (string, optionnel, défaut : "combat") : Source des dégâts
  **Retour :** Fiche personnage mise à jour (dict)

### Compétences (`back/tools/skill_tools.py`)
- **skill_check**  
  Effectue un test de compétence (1d100 <= skill_level - difficulty).  
  **Paramètres :**
  - `skill_level` (int) : Niveau de compétence du personnage
  - `difficulty` (int) : Difficulté du test
  **Retour :** Booléen (succès/échec)

### Combat (`back/tools/combat_tools.py`)
- **roll_initiative**  
  Calcule l’ordre d’initiative des personnages.  
  **Paramètres :**
  - `characters` (list[dict]) : Liste des personnages
  **Retour :** Liste triée selon l’initiative

- **perform_attack**  
  Effectue un jet d’attaque.  
  **Paramètres :**
  - `dice` (string) : Notation des dés à lancer (ex : "1d20")
  **Retour :** Résultat du jet d’attaque (int)

- **resolve_attack**  
  Résout une attaque (attaque > défense).  
  **Paramètres :**
  - `attack_roll` (int) : Jet d’attaque
  - `defense_roll` (int) : Jet de défense
  **Retour :** Booléen (succès/échec)

- **calculate_damage**  
  Calcule les dégâts infligés en tenant compte des modificateurs.  
  **Paramètres :**
  - `base_damage` (int) : Dégâts de base de l’attaque
  - `bonus` (int, optionnel, défaut : 0) : Bonus/malus de dégâts
  **Retour :** Dégâts finaux infligés (int)

### Scénario
- Aucun tool Haystack : la gestion des scénarios se fait via l’API REST, le LLM a toujours le contexte système.

## Agent MJ Haystack et gestion de la mémoire

- Le fichier `back/agents/gm_agent.py` définit l'agent Maître du Jeu (MJ) basé sur Haystack 3.x.
- La mémoire persistante est gérée via un store custom `JsonlChatMessageStore` (voir [HaystackMemoryDoc.md](./HaystackMemoryDoc.md)), qui stocke l'historique des messages dans un fichier JSONL par session.
- L'agent charge l'historique au démarrage et le sauvegarde explicitement après chaque interaction.
- Pour la personnalisation avancée (fenêtrage, résumé, etc.), voir la documentation Haystack sur la mémoire.

## Migration LangChain → Haystack

- **LangChain** a été supprimé du projet (voir `requirements.txt`).
- Tous les outils et l'agent MJ sont désormais compatibles Haystack 3.x.
- Les tests et la documentation ont été adaptés à la nouvelle stack.

## Tests

- Les tests unitaires et d'intégration sont dans `back/tests/`.
- Exemple : `back/tests/agents/test_gm_agent_memory.py` vérifie la persistance mémoire de l'agent MJ.

## Système de Prévention des Sessions Dupliquées (2025)

### Fonctionnalité
Le système empêche automatiquement la création de sessions dupliquées en détectant les combinaisons existantes de `character_name` + `scenario_name`. Cette protection évite les conflits de données et assure l'intégrité des sessions de jeu.

### Implémentation technique

#### Vérification automatique (`ScenarioService.check_existing_session()`)
- **Localisation** : `back/services/scenario_service.py`
- **Fonctionnement** : Parcourt tous les dossiers de session UUID existants
- **Vérification** : Compare les fichiers `scenario.txt` et `character.txt` avec les paramètres de la nouvelle session
- **Gestion d'erreurs** : Gestion robuste avec logging des erreurs d'accès fichier

#### Endpoint `/api/scenarios/start` amélioré
- **Vérification préalable** : Contrôle automatique avant création de session
- **Code d'erreur HTTP 409** : Retourné en cas de session dupliquée détectée
- **Message explicite** : Indique clairement quelle combinaison personnage/scénario existe déjà

### Codes de réponse

| Code HTTP | Signification | Description |
|-----------|---------------|-------------|
| **200** | Succès | Session créée avec succès |
| **404** | Scénario introuvable | Le fichier de scénario n'existe pas |
| **409** | Session dupliquée | Une session existe déjà pour cette combinaison personnage/scénario |

### Exemples d'utilisation

#### Première session (succès)
```bash
curl -X POST http://localhost:8000/api/scenarios/start \
  -H "content-type: application/json" \
  -d '{"scenario_name": "Les_Pierres_du_Passe.md", "character_name": "Aragorn"}'
```

**Réponse (200) :**
```json
{
  "session_id": "b1e2c3d4-5678-1234-9abc-abcdef123456",
  "scenario_name": "Les_Pierres_du_Passe.md",
  "character_id": "Aragorn",
  "message": "Scénario 'Les_Pierres_du_Passe.md' démarré avec succès pour le personnage Aragorn."
}
```

#### Tentative de session dupliquée (erreur)
```bash
# Même appel que précédemment
curl -X POST http://localhost:8000/api/scenarios/start \
  -H "content-type: application/json" \
  -d '{"scenario_name": "Les_Pierres_du_Passe.md", "character_name": "Aragorn"}'
```

**Réponse (409) :**
```json
{
  "detail": "Une session existe déjà pour le personnage 'Aragorn' dans le scénario 'Les_Pierres_du_Passe.md'"
}
```

## Tableau synthétique des routes API

| Méthode | Endpoint                              | Arguments d'entrée                                                                 | Retour principal / Description                                      |
|---------|---------------------------------------|-------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| GET     | /api/scenarios/                      | Aucun                                                                              | Liste des scénarios (`ScenarioList`)                                |
| GET     | /api/scenarios/{scenario_file}       | scenario_file (str, path)                                                          | Contenu du fichier Markdown du scénario                             |
| POST    | /api/scenarios/start                 | scenario_name (str), character_id (str) (body JSON)                                | session_id, scenario_name, character_id, message, llm_response      |
| POST    | /api/scenarios/play                  | session_id (UUID, query), message (str, body JSON)                                 | responses (list de messages générés par l'agent)                    |
| GET     | /api/scenarios/history/{session_id}  | session_id (UUID, path)                                                            | history (list de tous les messages de la session)                   |
| GET     | /api/characters/                     | Aucun                                                                              | Liste des personnages (`CharacterList`)                             |
| POST    | /api/combat/attack                   | attacker_id (str), target_id (str), attack_value (int), combat_state (dict, body)  | combat_state (état du combat mis à jour)                            |

> Les routes sont toutes documentées en détail dans le code source et la documentation technique.

---

*Ce README sera mis à jour au fur et à mesure de l'avancement du projet.*

## Routes pour les scénarios

#### `/api/scenarios/{scenario_file}`
**Description :** Récupère le contenu d'un scénario à partir de son nom de fichier Markdown (ex : `Les_Pierres_du_Passe.md`).

**Méthode :** GET

**Paramètre d'URL :**
- `scenario_file` (str) : Nom du fichier du scénario (doit exister dans `data/scenarios/`).

**Réponse :**
- Succès : Contenu brut du fichier Markdown.
- Erreur 404 : Si le fichier n'existe pas.

Exemple :
```
GET /api/scenarios/Les_Pierres_du_Passe.md
```
Retourne le contenu du fichier `data/scenarios/Les_Pierres_du_Passe.md`.

## Nouveaux Endpoints

### Combat
- **POST /attack** : Effectue un jet d'attaque en lançant des dés selon une notation donnée (ex: "1d20").

### Compétences
- **POST /skill-check** : Effectue un test de compétence en comparant un jet de dé au niveau de compétence et à la difficulté.

## Gestion des Combats

### CombatManager
- **Description** : Classe pour gérer les combats, située dans `back/models/domain/combat_manager.py`.
- **Méthodes** :
  - `roll_initiative(characters)` : Calcule l'ordre d'initiative pour les personnages.
  - `next_turn()` : Passe au tour suivant dans l'ordre d'initiative.
  - `reset_combat()` : Réinitialise le combat.
  - `calculate_initiative(character_stats)` : Calcule l'initiative d'un personnage en fonction de ses statistiques.
  - `resolve_attack(attack_roll, defense_roll)` : Résout une attaque en comparant les jets d'attaque et de défense.
  - `calculate_damage(base_damage, modifiers)` : Calcule les dégâts infligés en tenant compte des modificateurs.

### `back/models/domain/combat_manager.py`
**Objectif :** Gère les mécaniques de combat, y compris l'ordre d'initiative, la gestion des tours et les actions des personnages.

- **`roll_initiative(characters: dict) -> list`** :
  - **Description :** Calcule l'ordre d'initiative des personnages en fonction de leurs statistiques.
  - **Paramètres :**
    - `characters` (dict) : Dictionnaire contenant les personnages et leurs statistiques d'initiative.
  - **Retourne :** Une liste triée des personnages avec leurs initiatives.

- **`next_turn() -> object`** :
  - **Description :** Passe au tour suivant dans l'ordre d'initiative.
  - **Retourne :** Le personnage dont c'est le tour.

### `back/tools/combat_tools.py`
**Objectif :** Fournit des outils LangChain pour les actions de combat.

- **`roll_initiative_tool(input: InitiativeInput) -> list`** :
  - **Description :** Calcule l'ordre d'initiative des personnages via un outil LangChain.
  - **Paramètres :**
    - `input` (InitiativeInput) : Modèle contenant les personnages.
  - **Retourne :** Une liste triée des personnages avec leurs initiatives.

- **`perform_attack_tool(input: AttackInput) -> int`** :
  - **Description :** Effectue un jet d'attaque via un outil LangChain.
  - **Paramètres :**
    - `input` (AttackInput) : Modèle contenant la notation des dés.
  - **Retourne :** Le résultat du jet d'attaque.

- **`resolve_attack_tool(input: ResolveAttackInput) -> bool`** :
  - **Description :** Résout une attaque en comparant les jets d'attaque et de défense via un outil LangChain.
  - **Paramètres :**
    - `input` (ResolveAttackInput) : Modèle contenant les jets d'attaque et de défense.
  - **Retourne :** `True` si l'attaque réussit, sinon `False`.

- **`calculate_damage_tool(input: DamageInput) -> int`** :
  - **Description :** Calcule les dégâts infligés en tenant compte des modificateurs via un outil LangChain.
  - **Paramètres :**
    - `input` (DamageInput) : Modèle contenant les dégâts de base et les modificateurs.
  - **Retourne :** Les dégâts finaux infligés.

### Inventaire (`back/tools/inventory_tools.py`)
- **inventory_add_item**  
  Ajoute un objet à l’inventaire d’un joueur.  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du joueur
  - `item_id` (string) : Identifiant de l’objet à acquérir
  - `qty` (int, optionnel, défaut : 1) : Quantité à ajouter
  **Retour :** Résumé de l’inventaire mis à jour (dict)

- **inventory_remove_item**  
  Retire un objet de l’inventaire d’un joueur.  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du joueur
  - `item_id` (string) : Identifiant de l’objet à retirer
  - `qty` (int, optionnel, défaut : 1) : Quantité à retirer
  **Retour :** Résumé de l’inventaire mis à jour (dict)

### Personnage (`back/tools/character_tools.py`)
- **character_apply_xp**  
  Ajoute de l’XP à un personnage.  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du personnage
  - `xp` (int) : Points d’expérience à ajouter
  **Retour :** Fiche personnage mise à jour (dict)

- **character_add_gold**  
  Ajoute de l’or au portefeuille du personnage.  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du personnage
  - `gold` (int) : Montant d’or à ajouter
  **Retour :** Fiche personnage mise à jour (dict)

- **character_take_damage**  
  Applique des dégâts à un personnage (réduit ses PV).  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du personnage
  - `amount` (int) : Points de dégâts à appliquer
  - `source` (string, optionnel, défaut : "combat") : Source des dégâts
  **Retour :** Fiche personnage mise à jour (dict)

### Compétences (`back/tools/skill_tools.py`)
- **skill_check**  
  Effectue un test de compétence (1d100 <= skill_level - difficulty).  
  **Paramètres :**
  - `skill_level` (int) : Niveau de compétence du personnage
  - `difficulty` (int) : Difficulté du test
  **Retour :** Booléen (succès/échec)

### Combat (`back/tools/combat_tools.py`)
- **roll_initiative**  
  Calcule l’ordre d’initiative des personnages.  
  **Paramètres :**
  - `characters` (list[dict]) : Liste des personnages
  **Retour :** Liste triée selon l’initiative

- **perform_attack**  
  Effectue un jet d’attaque.  
  **Paramètres :**
  - `dice` (string) : Notation des dés à lancer (ex : "1d20")
  **Retour :** Résultat du jet d’attaque (int)

- **resolve_attack**  
  Résout une attaque (attaque > défense).  
  **Paramètres :**
  - `attack_roll` (int) : Jet d’attaque
  - `defense_roll` (int) : Jet de défense
  **Retour :** Booléen (succès/échec)

- **calculate_damage**  
  Calcule les dégâts infligés en tenant compte des modificateurs.  
  **Paramètres :**
  - `base_damage` (int) : Dégâts de base de l’attaque
  - `bonus` (int, optionnel, défaut : 0) : Bonus/malus de dégâts
  **Retour :** Dégâts finaux infligés (int)

### Scénario
- Aucun tool Haystack : la gestion des scénarios se fait via l’API REST, le LLM a toujours le contexte système.

## Agent MJ Haystack et gestion de la mémoire

- Le fichier `back/agents/gm_agent.py` définit l'agent Maître du Jeu (MJ) basé sur Haystack 3.x.
- La mémoire persistante est gérée via un store custom `JsonlChatMessageStore` (voir [HaystackMemoryDoc.md](./HaystackMemoryDoc.md)), qui stocke l'historique des messages dans un fichier JSONL par session.
- L'agent charge l'historique au démarrage et le sauvegarde explicitement après chaque interaction.
- Pour la personnalisation avancée (fenêtrage, résumé, etc.), voir la documentation Haystack sur la mémoire.

## Migration LangChain → Haystack

- **LangChain** a été supprimé du projet (voir `requirements.txt`).
- Tous les outils et l'agent MJ sont désormais compatibles Haystack 3.x.
- Les tests et la documentation ont été adaptés à la nouvelle stack.

## Tests

- Les tests unitaires et d'intégration sont dans `back/tests/`.
- Exemple : `back/tests/agents/test_gm_agent_memory.py` vérifie la persistance mémoire de l'agent MJ.

## Système de Prévention des Sessions Dupliquées (2025)

### Fonctionnalité
Le système empêche automatiquement la création de sessions dupliquées en détectant les combinaisons existantes de `character_name` + `scenario_name`. Cette protection évite les conflits de données et assure l'intégrité des sessions de jeu.

### Implémentation technique

#### Vérification automatique (`ScenarioService.check_existing_session()`)
- **Localisation** : `back/services/scenario_service.py`
- **Fonctionnement** : Parcourt tous les dossiers de session UUID existants
- **Vérification** : Compare les fichiers `scenario.txt` et `character.txt` avec les paramètres de la nouvelle session
- **Gestion d'erreurs** : Gestion robuste avec logging des erreurs d'accès fichier

#### Endpoint `/api/scenarios/start` amélioré
- **Vérification préalable** : Contrôle automatique avant création de session
- **Code d'erreur HTTP 409** : Retourné en cas de session dupliquée détectée
- **Message explicite** : Indique clairement quelle combinaison personnage/scénario existe déjà

### Codes de réponse

| Code HTTP | Signification | Description |
|-----------|---------------|-------------|
| **200** | Succès | Session créée avec succès |
| **404** | Scénario introuvable | Le fichier de scénario n'existe pas |
| **409** | Session dupliquée | Une session existe déjà pour cette combinaison personnage/scénario |

### Exemples d'utilisation

#### Première session (succès)
```bash
curl -X POST http://localhost:8000/api/scenarios/start \
  -H "content-type: application/json" \
  -d '{"scenario_name": "Les_Pierres_du_Passe.md", "character_name": "Aragorn"}'
```

**Réponse (200) :**
```json
{
  "session_id": "b1e2c3d4-5678-1234-9abc-abcdef123456",
  "scenario_name": "Les_Pierres_du_Passe.md",
  "character_id": "Aragorn",
  "message": "Scénario 'Les_Pierres_du_Passe.md' démarré avec succès pour le personnage Aragorn."
}
```

#### Tentative de session dupliquée (erreur)
```bash
# Même appel que précédemment
curl -X POST http://localhost:8000/api/scenarios/start \
  -H "content-type: application/json" \
  -d '{"scenario_name": "Les_Pierres_du_Passe.md", "character_name": "Aragorn"}'
```

**Réponse (409) :**
```json
{
  "detail": "Une session existe déjà pour le personnage 'Aragorn' dans le scénario 'Les_Pierres_du_Passe.md'"
}
```

## Tableau synthétique des routes API

| Méthode | Endpoint                              | Arguments d'entrée                                                                 | Retour principal / Description                                      |
|---------|---------------------------------------|-------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| GET     | /api/scenarios/                      | Aucun                                                                              | Liste des scénarios (`ScenarioList`)                                |
| GET     | /api/scenarios/{scenario_file}       | scenario_file (str, path)                                                          | Contenu du fichier Markdown du scénario                             |
| POST    | /api/scenarios/start                 | scenario_name (str), character_id (str) (body JSON)                                | session_id, scenario_name, character_id, message, llm_response      |
| POST    | /api/scenarios/play                  | session_id (UUID, query), message (str, body JSON)                                 | responses (list de messages générés par l'agent)                    |
| GET     | /api/scenarios/history/{session_id}  | session_id (UUID, path)                                                            | history (list de tous les messages de la session)                   |
| GET     | /api/characters/                     | Aucun                                                                              | Liste des personnages (`CharacterList`)                             |
| POST    | /api/combat/attack                   | attacker_id (str), target_id (str), attack_value (int), combat_state (dict, body)  | combat_state (état du combat mis à jour)                            |

> Les routes sont toutes documentées en détail dans le code source et la documentation technique.

---

*Ce README sera mis à jour au fur et à mesure de l'avancement du projet.*

## Routes pour les scénarios

#### `/api/scenarios/{scenario_file}`
**Description :** Récupère le contenu d'un scénario à partir de son nom de fichier Markdown (ex : `Les_Pierres_du_Passe.md`).

**Méthode :** GET

**Paramètre d'URL :**
- `scenario_file` (str) : Nom du fichier du scénario (doit exister dans `data/scenarios/`).

**Réponse :**
- Succès : Contenu brut du fichier Markdown.
- Erreur 404 : Si le fichier n'existe pas.

Exemple :
```
GET /api/scenarios/Les_Pierres_du_Passe.md
```
Retourne le contenu du fichier `data/scenarios/Les_Pierres_du_Passe.md`.

## Nouveaux Endpoints

### Combat
- **POST /attack** : Effectue un jet d'attaque en lançant des dés selon une notation donnée (ex: "1d20").

### Compétences
- **POST /skill-check** : Effectue un test de compétence en comparant un jet de dé au niveau de compétence et à la difficulté.

## Gestion des Combats

### CombatManager
- **Description** : Classe pour gérer les combats, située dans `back/models/domain/combat_manager.py`.
- **Méthodes** :
  - `roll_initiative(characters)` : Calcule l'ordre d'initiative pour les personnages.
  - `next_turn()` : Passe au tour suivant dans l'ordre d'initiative.
  - `reset_combat()` : Réinitialise le combat.
  - `calculate_initiative(character_stats)` : Calcule l'initiative d'un personnage en fonction de ses statistiques.
  - `resolve_attack(attack_roll, defense_roll)` : Résout une attaque en comparant les jets d'attaque et de défense.
  - `calculate_damage(base_damage, modifiers)` : Calcule les dégâts infligés en tenant compte des modificateurs.

### `back/models/domain/combat_manager.py`
**Objectif :** Gère les mécaniques de combat, y compris l'ordre d'initiative, la gestion des tours et les actions des personnages.

- **`roll_initiative(characters: dict) -> list`** :
  - **Description :** Calcule l'ordre d'initiative des personnages en fonction de leurs statistiques.
  - **Paramètres :**
    - `characters` (dict) : Dictionnaire contenant les personnages et leurs statistiques d'initiative.
  - **Retourne :** Une liste triée des personnages avec leurs initiatives.

- **`next_turn() -> object`** :
  - **Description :** Passe au tour suivant dans l'ordre d'initiative.
  - **Retourne :** Le personnage dont c'est le tour.

### `back/tools/combat_tools.py`
**Objectif :** Fournit des outils LangChain pour les actions de combat.

- **`roll_initiative_tool(input: InitiativeInput) -> list`** :
  - **Description :** Calcule l'ordre d'initiative des personnages via un outil LangChain.
  - **Paramètres :**
    - `input` (InitiativeInput) : Modèle contenant les personnages.
  - **Retourne :** Une liste triée des personnages avec leurs initiatives.

- **`perform_attack_tool(input: AttackInput) -> int`** :
  - **Description :** Effectue un jet d'attaque via un outil LangChain.
  - **Paramètres :**
    - `input` (AttackInput) : Modèle contenant la notation des dés.
  - **Retourne :** Le résultat du jet d'attaque.

- **`resolve_attack_tool(input: ResolveAttackInput) -> bool`** :
  - **Description :** Résout une attaque en comparant les jets d'attaque et de défense via un outil LangChain.
  - **Paramètres :**
    - `input` (ResolveAttackInput) : Modèle contenant les jets d'attaque et de défense.
  - **Retourne :** `True` si l'attaque réussit, sinon `False`.

- **`calculate_damage_tool(input: DamageInput) -> int`** :
  - **Description :** Calcule les dégâts infligés en tenant compte des modificateurs via un outil LangChain.
  - **Paramètres :**
    - `input` (DamageInput) : Modèle contenant les dégâts de base et les modificateurs.
  - **Retourne :** Les dégâts finaux infligés.

### Inventaire (`back/tools/inventory_tools.py`)
- **inventory_add_item**  
  Ajoute un objet à l’inventaire d’un joueur.  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du joueur
  - `item_id` (string) : Identifiant de l’objet à acquérir
  - `qty` (int, optionnel, défaut : 1) : Quantité à ajouter
  **Retour :** Résumé de l’inventaire mis à jour (dict)

- **inventory_remove_item**  
  Retire un objet de l’inventaire d’un joueur.  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du joueur
  - `item_id` (string) : Identifiant de l’objet à retirer
  - `qty` (int, optionnel, défaut : 1) : Quantité à retirer
  **Retour :** Résumé de l’inventaire mis à jour (dict)

### Personnage (`back/tools/character_tools.py`)
- **character_apply_xp**  
  Ajoute de l’XP à un personnage.  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du personnage
  - `xp` (int) : Points d’expérience à ajouter
  **Retour :** Fiche personnage mise à jour (dict)

- **character_add_gold**  
  Ajoute de l’or au portefeuille du personnage.  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du personnage
  - `gold` (int) : Montant d’or à ajouter
  **Retour :** Fiche personnage mise à jour (dict)

- **character_take_damage**  
  Applique des dégâts à un personnage (réduit ses PV).  
  **Paramètres :**
  - `player_id` (UUID, string) : Identifiant du personnage
  - `amount` (int) : Points de dégâts à appliquer
  - `source` (string, optionnel, défaut : "combat") : Source des dégâts
  **Retour :** Fiche personnage mise à jour (dict)

### Compétences (`back/tools/skill_tools.py`)
- **skill_check**  
  Effectue un test de compétence (1d100 <= skill_level - difficulty).  
  **Paramètres :**
  - `skill_level` (int) : Niveau de compétence du personnage
  - `difficulty` (int) : Difficulté du test
  **Retour :** Booléen (succès/échec)

### Combat (`back/tools/combat_tools.py`)
- **roll_initiative**  
  Calcule l’ordre d’initiative des personnages.  
  **Paramètres :**
  - `characters` (list[dict]) : Liste des personnages
  **Retour :** Liste triée selon l’initiative

- **perform_attack**  
  Effectue un jet d’attaque.  
  **Paramètres :**
  - `dice` (string) : Notation des dés à lancer (ex : "1d20")
  **Retour :** Résultat du jet d’attaque (int)

- **resolve_attack**  
  Résout une attaque (attaque > défense).  
  **Paramètres :**
  - `attack_roll` (int) : Jet d’attaque
  - `defense_roll` (int) : Jet de défense
  **Retour :** Booléen (succès/échec)

- **calculate_damage**  
  Calcule les dégâts infligés en tenant compte des modificateurs.  
  **Paramètres :**
  - `base_damage` (int) : Dégâts de base de l’attaque
  - `bonus` (int, optionnel, défaut : 0) : Bonus/malus de dégâts
  **Retour :** Dégâts finaux infligés (int)

### Scénario
- Aucun tool Haystack : la gestion des scénarios se fait via l’API REST, le LLM a toujours le contexte système.

## Agent MJ Haystack et gestion de la mémoire

- Le fichier `back/agents/gm_agent.py` définit l'agent Maître du Jeu (MJ) basé sur Haystack 3.x.
- La mémoire persistante est gérée via un store custom `JsonlChatMessageStore` (voir [HaystackMemoryDoc.md](./HaystackMemoryDoc.md)), qui stocke l'historique des messages dans un fichier JSONL par session.
- L'agent charge l'historique au démarrage et le sauvegarde explicitement après chaque interaction.
- Pour la personnalisation avancée (fenêtrage, résumé, etc.), voir la documentation Haystack sur la mémoire.

## Changements récents (2025) - Amélioration de l'agent MJ

### Nouvelles fonctionnalités implémentées

#### 1. Nouvelle route `/api/scenarios/play`
- **Route simplifiée** : Remplace `/api/agent/respond` avec une interface plus simple
- **Récupération automatique** : Les informations de session (`character_id`, `scenario_name`) sont automatiquement récupérées
- **Moins de paramètres** : Seulement `session_id` et `message` requis

#### 2. Prompt système enrichi
- **Règles du jeu intégrées** : Les règles sont automatiquement chargées depuis `docs/rules.md` et ajoutées au prompt système
- **Contexte enrichi** : L'agent dispose d'un contexte complet des règles pour des décisions cohérentes

#### 3. Injection automatique de la fiche personnage
- **Cache prompting optimisé** : La fiche personnage complète est automatiquement ajoutée au début de chaque message utilisateur
- **Performance améliorée** : Optimisation pour le cache prompting d'OpenAI

#### 4. Outils de jeu réels
L'agent dispose maintenant de **10 outils fonctionnels** remplaçant les outils placeholder :

**Gestion des personnages (3 outils) :**
- `character_apply_xp_tool` : Ajouter de l'expérience
- `character_add_gold_tool` : Ajouter de l'or
- `character_take_damage_tool` : Appliquer des dégâts

**Système de compétences (1 outil) :**
- `skill_check_tool` : Effectuer des tests de compétences

**Combat (4 outils) :**
- `roll_initiative` : Calculer l'ordre d'initiative
- `perform_attack` : Effectuer des jets d'attaque
- `resolve_attack` : Résoudre les attaques
- `calculate_damage` : Calculer les dégâts

**Inventaire (2 outils) :**
- `inventory_add_item_tool` : Ajouter des objets
- `inventory_remove_item_tool` : Retirer des objets

#### 5. Améliorations techniques
- **Bug fixes** : Correction du TypeError dans `log_debug`
- **Gestion de session améliorée** : Stockage automatique du nom de scénario dans les sessions
- **Architecture simplifiée** : Réduction de la complexité d'utilisation

#### 6. Migration complète vers les outils Haystack
- **Tous les outils** sont maintenant des instances de `haystack.tools.Tool`
- **Suppression des outils placeholder** comme `ExampleTool`
- **Intégration complète** avec les services backend
- **Documentation enrichie** : Toutes les fonctions d'outils disposent de docstrings détaillées en français
- **Gestion d'erreurs robuste** : Gestion des exceptions et logging pour chaque outil

#### 7. Tests étendus et validation
- **Tests de l'agent MJ** : `back/tests/agents/test_gm_agent.py` et `test_gm_agent_memory.py`
- **Tests des nouvelles routes** : Validation de `/api/scenarios/play` dans `test_scenarios.py`
- **Tests de persistance** : Vérification du stockage des informations de session
- **Tests d'intégration** : Validation complète du flux session -> agent -> réponse
- **Tests des outils** : Chaque outil Haystack dispose de ses tests unitaires

### Impact pour les développeurs
- **API simplifiée** : Moins de paramètres à gérer côté client
- **Fonctionnalités automatisées** : Récupération automatique des informations de session
- **Outils fonctionnels** : L'agent peut maintenant réellement affecter l'état du jeu
- **Performance améliorée** : Optimisations pour le cache prompting OpenAI
- **Maintenance réduite** : Moins de synchronisation manuelle entre client et serveur
- **Robustesse accrue** : Gestion d'erreurs améliorée et logs structurés

## Exploitation des logs structurés (JSON)

Le backend génère des logs structurés au format JSON sur toutes les couches critiques (services, tools, routers, agent LLM) via la fonction `log_debug` (voir `back/utils/logger.py`).

### Activation des logs
- **DEBUG** : Pour activer les logs sur stderr, définir la variable d’environnement `DEBUG=true`.
- **LOG_FILE** : Pour écrire les logs dans un fichier, définir la variable d’environnement `LOG_FILE=/chemin/vers/log.jsonl`.
- Les deux modes peuvent être combinés.

### Format des logs
Chaque log est une ligne JSON, compatible Grafana/Loki, par exemple :

```json
{"timestamp": "2025-06-03T12:34:56.789Z", "level": "DEBUG", "message": "Ajout d'un objet à l'inventaire", "character_id": "abc123", "item": "épée courte", "service": "InventoryService"}
```

Champs courants :
- `timestamp` : Date ISO UTC du log
- `level` : Niveau du log (toujours DEBUG ici)
- `message` : Message principal
- Autres : Contexte métier (ex : `character_id`, `item`, `service`, etc.)

### Exploitation avec Grafana/Loki
- Les logs peuvent être collectés par un agent Loki ou tout collecteur JSONL.
- Exemple de requête Grafana pour filtrer les logs d’un service :
  ```logql
  {service="InventoryService"} |= "Ajout d'un objet"
  ```
- Les logs étant au format JSON, ils sont facilement requêtables et indexables.

### Bonnes pratiques
- Chaque action critique (modification d’état, appel d’outil, accès agent LLM) génère un log détaillé.
- Pour ajouter un contexte métier, passer des kwargs à `log_debug` (ex : `character_id`, `item`, etc.).
- En cas d’erreur d’écriture dans le fichier de log, un message d’erreur est affiché sur stderr.

### Exemple d’activation (bash)
```bash
export DEBUG=true
export LOG_FILE="/tmp/jdr_backend.log"
uvicorn back.main:app
```

Voir la documentation de `back/utils/logger.py` pour plus de détails sur l’API de logging.

## API REST – Gestion des sessions

### Récupération des informations de session
La nouvelle route `/api/scenarios/play` utilise automatiquement la fonction `get_session_info()` du `ScenarioService` pour récupérer les informations nécessaires à partir du `session_id` uniquement.

**Fonctionnement interne :**
- Le système stocke automatiquement `character_id` et `scenario_name` lors du démarrage d'une session
- Ces informations sont stockées dans des fichiers texte (`character.txt` et `scenario.txt`) dans le répertoire de session
- La route `/api/scenarios/play` récupère automatiquement ces informations, éliminant le besoin de les passer en paramètres

**Avantages :**
- **Simplicité côté client** : Plus besoin de maintenir ces informations côté frontend
- **Cohérence** : Garantit que les bonnes informations sont utilisées pour chaque session
- **Réduction d'erreurs** : Élimine les risques de désynchronisation entre client et serveur

---

## Statut du Projet

### ✅ Fonctionnalités Implémentées
- **Stack Haystack 3.x complète** : Migration totale de LangChain vers Haystack
- **Agent MJ fonctionnel** : Maître du Jeu LLM avec mémoire persistante
- **10 outils de jeu réels** : Combat, inventaire, compétences, personnages
- **API REST simplifiée** : Route `/api/scenarios/play` avec récupération automatique de session
- **Injection automatique** : Fiche personnage et règles du jeu dans chaque interaction
- **Mémoire persistante** : Historique JSONL par session avec store Haystack custom
- **Tests complets** : Couverture des agents, services, outils et routes
- **Logs structurés** : Monitoring JSON compatible Grafana/Loki

### 🚧 En Cours de Développement
- **Interface utilisateur** : Frontend web pour une expérience utilisateur complète
- **Système de campagnes** : Gestion de campagnes multi-sessions
- **Outils avancés** : Extension des mécaniques de jeu (magie, commerce, etc.)

### 🔮 Roadmap Future
- **Multijoueur** : Support de parties à plusieurs joueurs
- **IA avancée** : Génération procédurale de contenus (PNJ, lieux, quêtes)
- **Intégrations** : Support d'autres systèmes de JdR et univers fantasy

### Contributions
Le projet suit les standards de développement modernes avec une architecture modulaire, des tests exhaustifs et une documentation complète. Les contributions sont encouragées selon les principes SOLID et les bonnes pratiques Python.

---

*Dernière mise à jour : juin 2025 – Migration complète vers Haystack 3.x avec nouvelle API simplifiée, outils de jeu réels et système de cache prompting optimisé.*

## Migration Haystack → PydanticAI (2025)

> **✅ MIGRATION TERMINÉE** : Transition complète de Haystack vers PydanticAI réussie avec succès !

### Statut de la migration

- ✅ **Agent GM Principal** : Migré vers PydanticAI avec 10 outils complets
- ✅ **Outils de combat** : Migrés (roll_initiative, perform_attack, resolve_attack, calculate_damage, end_combat)
- ✅ **Outils d'inventaire** : Migrés (inventory_add, inventory_remove)
- ✅ **Outils de personnage** : Migrés (apply_xp, add_gold, apply_damage, perform_skill_check)
- ✅ **Store PydanticAI** : Nouveau système de stockage JSONL compatible
- ✅ **Routeurs FastAPI** : Endpoints PydanticAI disponibles sur `/api/scenarios-pydantic/`
- ✅ **Tests et validation** : 26/26 tests passent, validation complète

### Avantages de PydanticAI

1. **🎯 Simplicité** : Configuration plus directe, moins de boilerplate
2. **🔒 Typage strict** : Validation automatique avec Pydantic, meilleure intégration IDE  
3. **⚡ Async natif** : Conçu pour l'asynchrone dès le départ
4. **🛠️ Outils déclaratifs** : Définition via décorateurs, plus lisible
5. **📦 Dépendances intégrées** : Système de dépendances via `RunContext`

### Fichiers de migration

- **`back/agents/gm_agent_pydantic.py`** : Nouvel agent GM utilisant PydanticAI (✅ COMPLET)
- **`back/storage/pydantic_jsonl_store.py`** : Store adapté pour PydanticAI (✅ COMPLET)
- **`back/routers/scenarios_pydantic.py`** : Routeur FastAPI PydanticAI (✅ COMPLET)
- **`back/agents/gm_agent_example.py`** : Exemple d'utilisation du nouvel agent
- **`back/agents/migration_comparison.py`** : Comparaison détaillée Haystack vs PydanticAI

### Utilisation

Les deux systèmes coexistent :
- **Haystack** : `/api/scenarios/` (système original)
- **PydanticAI** : `/api/scenarios-pydantic/` (système migré)

### Documentation PydanticAI

- [PydanticAI Documentation](./pydanticai.md) : Documentation complète et concepts
- [Guide de migration](./back/agents/migration_comparison.py) : Comparaison des approches
- [Rapport de migration](./MIGRATION_STATUS_REPORT.md) : Rapport détaillé de la migration
