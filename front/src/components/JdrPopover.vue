<template>
  <span class="popover-wrapper" @mouseenter="show = true" @mouseleave="show = false">
    <slot />
    <div v-if="show" class="popover-content">
      <slot name="content" />
    </div>
  </span>
</template>

<script setup lang="ts">
import { ref } from 'vue';
const show = ref(false);
</script>

<style scoped>
.popover-wrapper {
  position: relative;
  display: inline-block;
}
.popover-content {
  position: absolute;
  top: 120%;
  left: 50%;
  transform: translateX(-50%);
  background: var(--jdr-bg-secondary);
  color: var(--jdr-text-main);
  border: 1.5px solid var(--jdr-border-color);
  border-radius: 8px;
  padding: 0.7rem 1.1rem;
  min-width: 180px;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  font-size: 0.98rem;
  pointer-events: none;
}
</style>
