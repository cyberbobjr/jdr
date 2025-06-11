# Frontend - JDR Manager

## Description
Interface utilisateur moderne pour le gestionnaire de jeux de rôle, construite avec Vue.js 3, TypeScript, TailwindCSS et FontAwesome.

## Technologies utilisées

### Framework et langage
- **Vue.js 3** : Framework JavaScript progressif avec Composition API
- **TypeScript** : Langage typé pour JavaScript
- **Vue Router** : Routage pour applications Vue.js SPA

### Styles et interface
- **TailwindCSS** : Framework CSS utilitaire pour un design moderne
- **FontAwesome** : Bibliothèque d'icônes complète
  - Icônes solid (`fas`)
  - Icônes regular (`far`) 
  - Icônes brands (`fab`)

### Outils de développement
- **Vite** : Outil de build rapide
- **PostCSS** : Processeur CSS avec Autoprefixer
- **Vitest** : Framework de test unitaire
- **Vue Test Utils** : Utilitaires pour tester les composants Vue

## Installation et démarrage

### Prérequis
- Node.js 16+ 
- npm ou yarn

### Installation des dépendances
```bash
cd front
npm install
```

### Démarrage du serveur de développement
```bash
npm run dev
```

L'application sera accessible sur `http://localhost:5173`

### Build de production
```bash
npm run build
```

### Tests
```bash
npm run test          # Tests en mode watch
npm run test -- --run # Tests en mode run unique
```

## Fonctionnalités implémentées

### Interface utilisateur
- ✅ Design moderne avec thème sombre
- ✅ Navigation responsive avec Vue Router
- ✅ Composants avec animations et transitions
- ✅ Utilisation extensive de TailwindCSS pour le styling

### Composants de démonstration
- ✅ **Lanceur de dés** : Simulation de lancement de D20 avec animation
- ✅ **Fiche de personnage** : Affichage des statistiques avec barres de progression
- ✅ **Interface JDR** : Boutons d'action pour les différentes fonctionnalités

### Icônes FontAwesome
- ✅ Icônes thématiques pour le JDR (dés, épées, magie, etc.)
- ✅ Animations et effets visuels
- ✅ Intégration complète dans tous les composants

### Tests
- ✅ **19 tests unitaires** couvrant les composants principaux
- ✅ Configuration Vitest avec jsdom
- ✅ Mocks pour FontAwesome et Vue Router
- ✅ Tests de montage, affichage et interactions

## Scripts disponibles

- `npm run dev` : Démarre le serveur de développement
- `npm run build` : Crée le build de production
- `npm run preview` : Prévisualise le build de production
- `npm run test` : Lance les tests unitaires
- `npm run test -- --run` : Lance les tests en mode run unique

## État du projet

✅ **TERMINÉ** - Configuration complète de Vue.js 3 + TypeScript + TailwindCSS + FontAwesome  
✅ **TERMINÉ** - Interface moderne avec thème JDR  
✅ **TERMINÉ** - Composants de démonstration fonctionnels  
✅ **TERMINÉ** - Suite de tests unitaires (19 tests)  
✅ **TERMINÉ** - Configuration de développement optimale  

Prêt pour l'intégration avec le backend FastAPI + PydanticAI.
