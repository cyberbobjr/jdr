<script setup lang="ts">
import { RouterView, useRoute } from 'vue-router'
import { computed } from 'vue'
import JdrHeader from './components/JdrHeader.vue'

const route = useRoute()

// Détecte si on est sur la page de jeu
const isGamePage = computed(() => route.name === 'jeu')
</script>

<template>
    <JdrHeader />
    <!-- Contenu principal -->
    <main class="app-main" :class="{ 'game-page': isGamePage }">
      <RouterView />
    </main>
</template>

<style scoped>
/* Main container qui prend toute la hauteur disponible */
.app-main {
  height: calc(100vh - var(--header-height));
  overflow: hidden;
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  flex-direction: column;
}

/* Pour les pages de jeu, utiliser toute la largeur */
.app-main.game-page {
  padding: 0;
  max-width: none;
}

/* Responsive design pour le contenu principal */
@media (max-width: 768px) {
  .app-main {
    padding: 0 0.5rem;
  }
  
  .app-main.game-page {
    padding: 0;
  }
}

@media (max-width: 480px) {
  .app-main {
    padding: 0 0.25rem;
  }
  
  .app-main.game-page {
    padding: 0;
  }
}
</style>


