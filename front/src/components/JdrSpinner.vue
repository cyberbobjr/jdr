<template>
  <div class="jdr-spinner-wrapper" :style="{ height: size + 'px', width: size + 'px' }">
    <span class="jdr-spinner" :style="{ borderWidth: border + 'px', width: size + 'px', height: size + 'px' }"></span>
    <span v-if="label" class="jdr-spinner-label">{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'

const props = defineProps({
  size: { type: Number, default: 48 },
  border: { type: Number, default: 5 },
  label: { type: String, default: '' }
})
</script>

<style scoped>
.jdr-spinner-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.jdr-spinner {
  display: inline-block;
  border: 5px solid var(--jdr-bg-tertiary);
  border-top: 5px solid var(--jdr-secondary);
  border-radius: 50%;
  width: 48px;
  height: 48px;
  animation: jdr-spin 1s linear infinite;
  margin-bottom: 0.5rem;
}
.jdr-spinner-label {
  color: var(--jdr-text-secondary);
  font-size: 1rem;
  margin-top: 0.25rem;
}
@keyframes jdr-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
