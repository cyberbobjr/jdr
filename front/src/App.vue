<script setup lang="ts">
import { RouterView } from 'vue-router'
import JdrHeader from './components/JdrHeader.vue'
</script>

<template>
    <JdrHeader />
    <!-- Contenu principal -->
    <main>
      <div class="app-content-wrapper">
        <RouterView />
      </div>
    </main>
</template>

<style scoped>
.app-content-wrapper {
  max-width: 1600px;
  width: 100%;
  margin: 0 auto;
  padding: 0 1rem;
}

/* Responsive design pour le contenu principal */
@media (max-width: 768px) {
  .app-content-wrapper {
    padding: 0 0.5rem;
  }
}

@media (max-width: 480px) {
  .app-content-wrapper {
    padding: 0 0.25rem;
  }
}
</style>
