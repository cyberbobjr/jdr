<template>
  <div class="jdr-point-input">
    <button 
      type="button"
      class="point-btn point-btn-minus"
      @click="decrement"
      :disabled="isDecrementDisabled"
      :title="decrementTooltip"
    >
      -
    </button>
    
    <input
      type="number"
      :min="min"
      :max="max"
      :value="modelValue"
      @input="updateValue"
      @blur="validateValue"
      class="point-input"
      :disabled="disabled"
    />
    
    <button 
      type="button"
      class="point-btn point-btn-plus"
      @click="increment"
      :disabled="isIncrementDisabled"
      :title="incrementTooltip"
    >
      +
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  modelValue: number;
  min?: number;
  max?: number;
  disabled?: boolean;
  canIncrement?: boolean; // Pour gérer les contraintes externes (ex: points restants)
  canDecrement?: boolean; // Pour gérer les contraintes externes
  incrementTooltip?: string;
  decrementTooltip?: string;
}

const props = withDefaults(defineProps<Props>(), {
  min: 0,
  max: 10,
  disabled: false,
  canIncrement: true,
  canDecrement: true,
  incrementTooltip: 'Augmenter la valeur',
  decrementTooltip: 'Diminuer la valeur'
});

const emit = defineEmits<{
  'update:modelValue': [value: number];
  'increment': [newValue: number];
  'decrement': [newValue: number];
}>();

// Computed pour gérer les états de désactivation
const isIncrementDisabled = computed(() => {
  return props.disabled || 
         props.modelValue >= props.max || 
         !props.canIncrement;
});

const isDecrementDisabled = computed(() => {
  return props.disabled || 
         props.modelValue <= props.min || 
         !props.canDecrement;
});

// Fonctions de modification
function increment() {
  if (!isIncrementDisabled.value) {
    const newValue = Math.min(props.modelValue + 1, props.max);
    emit('update:modelValue', newValue);
    emit('increment', newValue);
  }
}

function decrement() {
  if (!isDecrementDisabled.value) {
    const newValue = Math.max(props.modelValue - 1, props.min);
    emit('update:modelValue', newValue);
    emit('decrement', newValue);
  }
}

// Gestion de la saisie manuelle
function updateValue(event: Event) {
  const target = event.target as HTMLInputElement;
  let value = parseInt(target.value) || props.min;
  
  // Contraindre la valeur dans les limites
  value = Math.max(props.min, Math.min(props.max, value));
  
  emit('update:modelValue', value);
}

// Validation lors de la perte de focus
function validateValue(event: Event) {
  const target = event.target as HTMLInputElement;
  let value = parseInt(target.value) || props.min;
  
  // Contraindre la valeur dans les limites
  value = Math.max(props.min, Math.min(props.max, value));
  
  // Remettre la valeur corrigée dans l'input
  target.value = value.toString();
  
  if (value !== props.modelValue) {
    emit('update:modelValue', value);
  }
}
</script>

<style scoped>
.jdr-point-input {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: var(--jdr-bg-primary);
  border: 2px solid var(--jdr-border);
  border-radius: 6px;
  padding: 0.125rem;
  transition: border-color 0.2s ease;
}

.jdr-point-input:focus-within {
  border-color: var(--jdr-primary);
  box-shadow: 0 0 0 2px var(--jdr-primary-bg);
}

.point-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: var(--jdr-bg-secondary);
  color: var(--jdr-text-primary);
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  user-select: none;
}

.point-btn:not(:disabled):hover {
  background: var(--jdr-primary);
  color: white;
  transform: scale(1.05);
}

.point-btn:not(:disabled):active {
  transform: scale(0.95);
}

.point-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  background: var(--jdr-bg-tertiary);
  color: var(--jdr-text-secondary);
}

.point-btn-plus {
  color: var(--jdr-success);
}

.point-btn-plus:not(:disabled):hover {
  background: var(--jdr-success);
  color: white;
}

.point-btn-minus {
  color: var(--jdr-danger);
}

.point-btn-minus:not(:disabled):hover {
  background: var(--jdr-danger);
  color: white;
}

.point-input {
  width: 50px;
  height: 28px;
  border: none;
  background: transparent;
  text-align: center;
  font-size: 14px;
  font-weight: 600;
  color: var(--jdr-text-primary);
  outline: none;
}

.point-input:disabled {
  color: var(--jdr-text-secondary);
  cursor: not-allowed;
}

/* Masquer les boutons natifs des inputs number */
.point-input::-webkit-outer-spin-button,
.point-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.point-input[type=number] {
  -moz-appearance: textfield;
  appearance: textfield;
}
</style>
