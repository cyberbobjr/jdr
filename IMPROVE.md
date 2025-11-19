# Plan d'Amélioration du Projet

Ce document présente les améliorations recommandées pour le projet JdR "Terres du Milieu", basées sur une analyse architecturale.

## 1. Architecture & Conception

### [Criticité : 4] Refactoriser `GameSessionService` (Odeur de code "Middle Man")

**Justification :** `GameSessionService` agit actuellement comme un "Intermédiaire" (Middle Man) pour de nombreuses opérations, se contentant de déléguer les appels à `CharacterService` ou `EquipmentService` (ex: `apply_xp`, `add_gold`, `buy_equipment`). Cela viole la Loi de Demeter et alourdit le service avec des méthodes passe-plats.
**Recommandation :**

- **Approche Préférée :** Traiter `GameSessionService` comme un **Conteneur de Services** (ou Contexte) qui expose publiquement les services spécialisés (ex: `session.character_service.apply_xp(...)`).
- **Compromis :** Cela viole techniquement la Loi de Demeter (accéder au "voisin du voisin"), mais cela réduit considérablement le code boilerplate et l'effort de maintenance par rapport au pattern "Middle Man".
- **Stratégie de Test :** Cela rend les tests plus robustes car vous pouvez mocker les services spécialisés (`CharacterService`, `EquipmentService`) individuellement lors du test de la logique d'orchestration de `GameSessionService`, ou tester les services spécialisés de manière isolée sans avoir besoin de `GameSessionService`.

### [Criticité : 3] Standardiser les Modèles de Réponse API

**Justification :** Les endpoints `/play` et `/history` renvoient du JSON brut (`return store.load_raw_json_history()`) pour "éviter les erreurs de sérialisation". Cela contourne la validation et la documentation de Pydantic, rendant le contrat d'API faible et plus difficile à consommer pour les clients.
**Recommandation :**

- Corriger les modèles Pydantic pour représenter correctement la sortie du graphe et le format de l'historique.
- S'assurer que tous les endpoints renvoient des modèles Pydantic stricts.

## 2. Fiabilité & Gestion des Erreurs

### [Criticité : 4] Améliorer la Gestion des Exceptions

**Justification :**

- Les méthodes de `GameSessionService` lèvent des `ValueError` génériques pour des services non initialisés.
- Les routeurs utilisent des blocs `try...except Exception` larges, ce qui peut masquer des bugs inattendus et rendre le débogage difficile.
**Recommandation :**
- Créer des classes d'exception personnalisées (ex: `ServiceNotInitializedError`, `SessionNotFoundError`, `CharacterInvalidStateError`).
- Attraper des exceptions spécifiques dans les routeurs et les mapper aux codes de statut HTTP appropriés (404, 400, 409).
- Éviter d'attraper `Exception` sauf pour un gestionnaire final 500.

### [Criticité : 3] Logging Structuré

**Justification :** La fonction `log_debug` actuelle est une implémentation personnalisée. Les systèmes en production bénéficient d'un logging structuré (JSON) qui s'intègre aux outils de monitoring.
**Recommandation :**

- Adopter une bibliothèque de logging standard comme `structlog` ou le module `logging` de Python avec un formateur JSON.
- S'assurer que les IDs de requête sont propagés dans les logs pour tracer les requêtes à travers les services.

## 3. Performance

### [Criticité : 3] Implémenter un Cache pour les Données de Session

**Justification :** `GameSessionService` recharge les données du personnage et du scénario depuis le disque à chaque requête (`_load_session_data`). À mesure que la base d'utilisateurs ou la taille des données augmente, cela deviendra un goulot d'étranglement.
**Recommandation :**

- Implémenter un cache simple en mémoire (ex: `functools.lru_cache` ou une couche de cache dédiée) pour les sessions et personnages chargés.
- Invalider le cache lors des écritures.

### [Criticité : 2] Optimiser le Chargement de l'Historique

**Justification :** Charger l'historique complet de la conversation (`load_history`) à chaque tour pourrait devenir lent pour les longues sessions.
**Recommandation :**

- Implémenter une pagination pour la récupération de l'historique.
- Pour le contexte du LLM, ne charger que les N derniers messages ou utiliser une stratégie de résumé (bien que cela puisse faire partie de la logique de l'agent).

## 4. Sécurité

### [Criticité : 5] Implémenter Authentification/Autorisation

**Justification :** L'API n'a actuellement aucune authentification. N'importe qui avec un accès réseau peut manipuler les sessions et les personnages. Même s'il s'agit d'une application locale pour l'instant, c'est un risque de sécurité majeur si elle est exposée.
**Recommandation :**

- Implémenter au moins un mécanisme basique de Clé API ou une authentification JWT.
- S'assurer que les utilisateurs ne peuvent accéder qu'à leurs propres sessions/personnages.

## 5. Qualité du Code & Standards

### [Criticité : 2] Supprimer le Code Mort

**Justification :** `GameSessionService` contient des commentaires sur des méthodes supprimées (`load_history`, `save_history`) mais elles sont toujours présentes.
**Recommandation :**

- Supprimer les méthodes inutilisées et le code commenté pour garder la base de code propre.

### [Criticité : 2] Standardiser les Docstrings

**Justification :** Les docstrings sont présentes mais varient en style.
**Recommandation :**

- Appliquer un format de docstring cohérent (ex: Google Style) via des règles de linting (ex: `pydocstyle`).

## Résumé des Points Critiques

1. **Sécurité (Auth)** - Criticité 5
2. **Refactoriser GameSessionService** - Criticité 4
3. **Améliorer la Gestion des Exceptions** - Criticité 4
