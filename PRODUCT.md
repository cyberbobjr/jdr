# Vision Produit : JDR AI Backend

## Vision

Créer un maître de jeu (MJ) virtuel infatigable, capable d'offrir des aventures personnalisées, cohérentes et mécaniquement rigoureuses à n'importe quel moment. Le système combine la flexibilité narrative des LLM avec la rigueur d'un moteur de règles de JDR classique.

## Cibles

- **Joueurs Solo**: Pour tester des builds ou vivre une aventure rapide.
- **Groupes sans MJ**: Pour jouer en coopératif avec une IA comme arbitre.
- **Développeurs**: Une API robuste pour construire des frontends de JDR.

## Périmètre Fonctionnel Actuel

### 1. Création de Personnage Assistée

- Création complète (Race, Classe, Stats, Équipement).
- Validation stricte des règles.
- Persistance JSON.

### 2. Moteur de Jeu (Backend)

- **Système de Combat**: Tour par tour, initiative, gestion des PV, attaques, dégâts.
- **Gestion d'État**: Sauvegarde et reprise des combats (`CombatStateService`).
- **Inventaire**: Achat, vente, équipement (`EquipmentService`).
- **Préférences**: Gestion des paramètres utilisateur (`SettingsService`).

### 3. Narration & IA

- **Narrative Agent**: Gère l'exploration et le dialogue.
- **Combat Agent**: Prend le relais lors des affrontements, gère la stratégie des ennemis.
- **Orchestration**: Transition fluide entre narration et combat via Pydantic Graph.

## Differentiateurs

- **Hybride**: Pas juste un chatbot, mais un vrai moteur de jeu avec des règles appliquées par le code.
- **Persistant**: Le monde et les personnages "existent" au-delà de la fenêtre de contexte du LLM.
- **Transparent**: Les jets de dés et les calculs sont exposés, pas hallucinés.

## Maturité du Produit

- **Backend**: 🟢 Stable (Core features implémentées).
- **Règles**: 🟡 Partiel (Combat de base fonctionnel, Magie simplifiée).
- **IA**: 🟢 Fonctionnelle (Agents spécialisés en place).

## Roadmap Court Terme

1. **Enrichissement du Bestiaire**: Plus de monstres et de capacités spéciales.
2. **Scénarios Complexes**: Support pour des campagnes multi-sessions.
3. **Frontend**: Développement d'une interface utilisateur graphique (Web/Mobile).

## Métriques de Succès

- **Validité des Règles**: 100% des personnages créés sont légaux.
- **Stabilité**: Pas de crash lors des transitions Narration <-> Combat.
- **Performance**: Temps de réponse des agents < 5s.
