
<template>
  <div class="jdr-stepper">
    <div
      v-for="(label, idx) in steps"
      :key="label"
      class="step-bubble-wrapper"
    >
      <div
        class="step-bubble"
        :class="{ active: idx === current, clickable: true, completed: idx < current }"
        @click="emit('step-click', idx)"
      >
        {{ idx + 1 }}
      </div>
      <div class="step-label">{{ label }}</div>
      <div v-if="idx < steps.length - 1" class="step-connector"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  steps: string[];
  current: number;
}>();
const emit = defineEmits<{
  (e: 'step-click', idx: number): void;
}>();
</script>

<style scoped>
.jdr-stepper {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
}
.step-bubble-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1 1 0;
}
.step-bubble {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: var(--jdr-bg-secondary);
  border: 2.5px solid var(--jdr-border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--jdr-text-muted);
  margin-bottom: 0.5rem;
  transition: border 0.2s, background 0.2s, color 0.2s;
  cursor: pointer;
}
.step-bubble.active {
  border-color: var(--jdr-secondary);
  background: var(--jdr-secondary-light);
  color: var(--jdr-secondary);
}
.step-bubble.completed {
  border-color: var(--jdr-success);
  background: var(--jdr-success-light);
  color: var(--jdr-success);
}
.step-label {
  font-size: 0.95rem;
  color: var(--jdr-text-muted);
  text-align: center;
  margin-top: 0.2rem;
  max-width: 7rem;
}
.step-connector {
  position: absolute;
  top: 1.25rem;
  left: 100%;
  width: 2rem;
  height: 2.5px;
  background: var(--jdr-border-color);
  z-index: 0;
}
</style>
