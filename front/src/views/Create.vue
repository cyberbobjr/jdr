<template>
  <div class="create-character jdr-p-4">
    <h1>Créer un nouveau personnage</h1>
    <div v-if="!characterId">
      <p>Initialisation de la création...</p>
    </div>
    <div v-else class="jdr-p-4">
      <JdrStepComponent
        :steps="stepLabels"
        :current="currentStepIndex"
        @step-click="goToStep"
      />      <component
        :is="currentStepComponent"
        :character-id="characterId"
        :initial-data="characterData"
        :characteristics-data="characteristicsData"
        :skills-data="skillsData"
        @next-step="goToNextStep"
        @update-character="updateCharacterData"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Step1 from './steps/Step1.vue';
import Step2 from './steps/Step2.vue';
import Step3 from './steps/Step3.vue';
import Step4 from './steps/Step4.vue';
import Step5 from './steps/Step5.vue';
import JdrApiService from '@/core/api';
import type { Character, CharacteristicsData } from '@/core/interfaces';
import JdrStepComponent from '@/components/JdrStepComponent.vue';

const route = useRoute();
const router = useRouter();

const characterId = ref<string | null>(null);
const characterData = ref<Character | null>(null);
const characteristicsData = ref<CharacteristicsData | null>(null);
const skillsData = ref<any | null>(null);
const step = ref<string>('step1');

const stepLabels = [
  'Race & Culture',
  'Caractéristiques',
  'Compétences',
  'Équipement',
  'Nom & Finalisation'
];
const steps = ['step1', 'step2', 'step3', 'step4', 'step5'];
const stepComponents: Record<string, any> = {
  step1: Step1,
  step2: Step2,
  step3: Step3,
  step4: Step4,
  step5: Step5
};
const currentStepComponent = computed(() => stepComponents[step.value] || stepComponents['step1']);
const currentStepIndex = computed(() => steps.indexOf(step.value));

onMounted(async () => {
  // Charger les données des caractéristiques
  try {
    characteristicsData.value = await JdrApiService.getCharacteristics();
  } catch (error) {
    console.error('Erreur lors du chargement des caractéristiques:', error);
  }
  // Charger les données des compétences
  try {
    skillsData.value = await JdrApiService.getSkills();
    console.log('Données de compétences chargées:', skillsData.value);
  } catch (error) {
    console.error('Erreur lors du chargement des compétences:', error);
  }

  const { characterId: routeId, step: routeStep } = route.params as { characterId?: string, step?: string };
  if (routeId) {
    characterId.value = routeId;
    step.value = routeStep || 'step1';
    characterData.value = await JdrApiService.getCharacter(routeId);
  }
});

watch(() => route.params, async (params) => {
  if (params.characterId) {
    characterId.value = params.characterId as string;
    // Recharger les données du personnage quand on change de caractère ou d'étape
    try {
      characterData.value = await JdrApiService.getCharacter(params.characterId as string);
      console.log('Données du personnage rechargées:', characterData.value);
    } catch (error) {
      console.error('Erreur lors du rechargement des données du personnage:', error);
    }
  }
  if (params.step) step.value = params.step as string;
});

function goToNextStep(payload?: any) {
  const idx = steps.indexOf(step.value);
  const next = steps[idx + 1] || steps[steps.length - 1];
  router.push({ name: 'create', params: { characterId: characterId.value, step: next } });
}

function goToStep(idx: number) {
  const stepName = steps[idx];
  router.push({ name: 'create', params: { characterId: characterId.value, step: stepName } });
}

function updateCharacterData(newData: Character) {
  characterData.value = newData;
}
</script>

<style scoped>
.create-character {
  margin: 2rem auto;
  background: var(--jdr-bg-secondary);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
</style>
