<template>
  <div class="jdr-modal-backdrop" @click.self="onCancel">
    <div class="jdr-modal">
      <div class="jdr-modal-header">
        <h2 class="jdr-modal-title">{{ title }}</h2>
        <h3 v-if="subtitle" class="jdr-modal-subtitle">{{ subtitle }}</h3>
      </div>
      <div class="jdr-modal-body">
        <slot />
      </div>
      <div class="jdr-modal-footer">
        <button
          v-if="showCancel"
          class="jdr-btn jdr-btn-secondary"
          @click="onCancel"
        >
          {{ cancelLabel }}
        </button>
        <button
          v-if="showOk"
          class="jdr-btn jdr-btn-primary"
          @click="onOk"
        >
          {{ okLabel }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from "vue";

const props = defineProps<{
  title: string;
  subtitle?: string;
  showOk?: boolean;
  showCancel?: boolean;
  okLabel?: string;
  cancelLabel?: string;
}>();

const emit = defineEmits<{
  (e: "close", status: boolean): void;
}>();

function onOk() {
  emit("close", true);
}
function onCancel() {
  emit("close", false);
}
</script>

<style scoped>
.jdr-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.jdr-modal {
  background: var(--jdr-bg-secondary, #222);
  border-radius: var(--jdr-border-radius-large, 12px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.25);
  min-width: 320px;
  max-width: 90vw;
  min-height: 120px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.jdr-modal-header {
  padding: 1.2rem 1.5rem 0.5rem 1.5rem;
  border-bottom: 1px solid var(--jdr-border-color, #444);
}
.jdr-modal-title {
  margin: 0;
  font-size: 1.4rem;
  color: var(--jdr-secondary, #e2b714);
  font-family: var(--jdr-font-fantasy, serif);
}
.jdr-modal-subtitle {
  margin: 0.3rem 0 0 0;
  color: var(--jdr-text-muted, #aaa);
  font-size: 1rem;
  font-style: italic;
}
.jdr-modal-body {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
}
.jdr-modal-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  padding: 1rem 1.5rem 1.2rem 1.5rem;
  border-top: 1px solid var(--jdr-border-color, #444);
}
</style>
