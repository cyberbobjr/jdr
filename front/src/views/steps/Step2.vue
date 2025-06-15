<template>
  <div>
    <h2>Étape 2 : Répartition des caractéristiques</h2>
    <div class="caracs-list">
      <div
        v-for="carac in caracNames"
        :key="carac"
        class="carac-item"
      >
        <JdrPopover>
          <span class="carac-label">{{ carac }}</span>
          <template #content>
            <div v-if="caracDetails[carac]">
              <strong>{{ carac }}</strong><br />
              {{ caracDetails[carac] }}
            </div>
          </template>
        </JdrPopover>
        <input
          type="number"
          min="1"
          max="105"
          v-model.number="caracs[carac]"
          @change="onCaracChange"
        />
      </div>
    </div>
    <div class="caracs-actions">
      <button class="jdr-btn jdr-btn-secondary" @click="proposeDistribution">Proposer une répartition</button>
      <button class="jdr-btn jdr-btn-primary" :disabled="!isValid" @click="goToNextStep">Suivant</button>
    </div>
    <div v-if="!isValid" class="caracs-error">La répartition n'est pas valide selon les règles du jeu.</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import JdrApiService from '@/core/api';
import JdrPopover from '@/components/JdrPopover.vue';
import type { Character } from '@/core/interfaces';

const props = defineProps<{
  characterId?: string;
  initialData?: Character | null;
}>();
const emit = defineEmits(['next-step', 'update-character']);

const caracNames = [
  'Force', 'Constitution', 'Agilité', 'Rapidité',
  'Volonté', 'Raisonnement', 'Intuition', 'Présence'
];
const caracDetails: Record<string, string> = {
  'Force': "Détermine la puissance physique, la capacité à porter, soulever, frapper.",
  'Constitution': "Résistance aux maladies, fatigue, endurance physique.",
  'Agilité': "Souplesse, coordination, capacité à esquiver ou manipuler avec précision.",
  'Rapidité': "Vitesse de déplacement, réflexes, initiative.",
  'Volonté': "Force mentale, résistance à la peur, détermination.",
  'Raisonnement': "Logique, capacité d'analyse, résolution de problèmes.",
  'Intuition': "Perception instinctive, flair, capacité à anticiper.",
  'Présence': "Charisme, capacité à influencer, prestance."
};

const caracs = ref<Record<string, number>>({});
const isValid = ref(true);

onMounted(() => {
  // Pré-remplissage si édition
  if (props.initialData && props.initialData.caracteristiques) {
    caracs.value = { ...props.initialData.caracteristiques };
  } else {
    caracNames.forEach(n => caracs.value[n] = 50);
  }
  validateCaracs();
});

watch(caracs, validateCaracs, { deep: true });

async function proposeDistribution() {
  if (!props.initialData) return;
  const { profession, race } = props.initialData;
  if (!profession || !race) return;
  const result = await JdrApiService.allocateAttributes({ profession, race });
  caracs.value = { ...result.attributes };
}

async function onCaracChange() {
  validateCaracs();
  await saveCaracs();
}

async function saveCaracs() {
  if (!props.characterId) return;
  await JdrApiService.saveCharacter({
    character_id: props.characterId,
    character: {
      ...(props.initialData || {}),
      caracteristiques: { ...caracs.value }
    }
  });
  emit('update-character', {
    ...(props.initialData || {}),
    caracteristiques: { ...caracs.value }
  } as Character);
}

async function validateCaracs() {
  if (!props.characterId) return;
  const res = await JdrApiService.checkAttributes({ attributes: { ...caracs.value } });
  isValid.value = res.valid;
}

function goToNextStep() {
  if (isValid.value) emit('next-step');
}
</script>

<style scoped>
.caracs-list {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  margin-bottom: 2rem;
}
.carac-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 120px;
}
.carac-label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  cursor: pointer;
  color: var(--jdr-secondary);
}
.caracs-actions {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}
.caracs-error {
  color: var(--jdr-danger);
  font-weight: 500;
  margin-top: 1rem;
}
</style>
