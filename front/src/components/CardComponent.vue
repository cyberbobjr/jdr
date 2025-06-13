<template>
  <div class="jdr-card">
    <div class="jdr-card-header">
      <h2 class="jdr-card-title">{{ title }}</h2>
      <h3 :v-if="subtitle">{{ subtitle }}</h3>
    </div>
    <div class="jdr-card-body">
      <slot />
    </div>
    <div class="jdr-card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  subtitle?: string;
}>();
</script>

<style scoped>
.jdr-card {
  background: var(--jdr-bg-secondary);
  border: 2px solid var(--jdr-border-color);
  border-radius: var(--jdr-border-radius-large);
  padding: 1.5rem;
  box-shadow: var(--jdr-shadow-medium);
  position: relative;
  overflow: hidden;
}

.jdr-card:before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--jdr-secondary);
}

.jdr-card-header {
  border-bottom: 1px solid var(--jdr-border-color);
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

.jdr-card-title {
  font-family: var(--jdr-font-fantasy);
  color: var(--jdr-secondary);
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}

.jdr-card-subtitle {
  color: var(--jdr-text-muted);
  font-style: italic;
  margin: 0.5rem 0 0 0;
}

.jdr-card-body {
  flex: 1;
}

.jdr-card-footer {
  border-top: 1px solid var(--jdr-border-color);
  padding-top: 1rem;
  margin-top: 1rem;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}
</style>
