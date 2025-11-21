# Processus de Création de Personnage (AI Copilot)

Ce document décrit le flux de création de personnage assisté par l'IA.

## Architecture

Le processus est piloté par un agent IA ("Character Creation Copilot") qui guide l'utilisateur étape par étape. La validation finale est assurée par le backend via des règles strictes.

### Endpoints de Validation

1. **Validation à la volée (Chat)**: L'IA valide les choix de l'utilisateur au fur et à mesure via ses connaissances internes et les outils disponibles.
2. **Validation Finale (Backend)**:
    - `POST /creation/validate-character`: Reçoit un objet `Character` complet et vérifie sa cohérence (stats, points dépensés, équipement valide).
    - `POST /creation/validate-character/by-id`: Charge un personnage existant par son ID et le re-valide. Utile pour vérifier un personnage avant de lancer une partie.

## Flux de Création

1. **Initialisation**: L'utilisateur exprime un concept (ex: "Je veux jouer un guerrier nain bourru").
2. **Remplissage**: L'IA propose des valeurs pour les champs requis (Race, Classe, Stats, etc.).
3. **Raffinement**: L'utilisateur ajuste les propositions.
4. **Finalisation**: L'IA soumet le personnage pour validation.
5. **Persistance**: Si valide, le personnage est sauvegardé (JSON).

## Règles de Validation

- **Stats**: La somme des points de caractéristiques doit respecter le budget (Standard Array ou Point Buy).
- **Équipement**: L'équipement de départ doit correspondre à la classe et au background.
- **Sorts**: Si la classe est magique, les sorts connus doivent être valides pour le niveau 1.

## Intégration LLM

L'agent de création utilise des outils pour :

- Lister les races/classes disponibles.
- Obtenir les détails d'une compétence.
- Vérifier la validité d'un choix spécifique.

## État et Persistance

Le processus de création peut être interrompu. L'état intermédiaire est géré par le contexte de la conversation jusqu'à la sauvegarde finale.

## Gestion des Erreurs

Si la validation backend échoue, l'API renvoie une liste détaillée des erreurs (ex: "Trop de points de force", "Sort inconnu"). L'IA doit interpréter ces erreurs et guider l'utilisateur pour les corriger.
