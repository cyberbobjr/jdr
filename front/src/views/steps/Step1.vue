<template>
  <div>
    <h3 class="culture-title">Choisissez une race</h3>
    <div class="culture-cards" v-if="races.length">
      <CardComponent
        v-for="race in races"
        :key="race.name"
        :title="race.name"
        :subtitle="race.special_abilities.join(', ')"
        :class="{ selected: selectedRaceName === race.name, clickable: true }"
        @click="selectRace(race.name)"
      >
        <div>
          <strong>Bonus caractéristiques :</strong>
          <ul>
            <li v-for="(bonus, stat) in race.characteristic_bonuses" :key="stat">
              {{ stat }} : +{{ bonus }}
            </li>
          </ul>
          <div><strong>Points de destin :</strong> {{ race.destiny_points }}</div>
          <div><strong>Langues de base :</strong> {{ race.base_languages.join(', ') }}</div>
        </div>
      </CardComponent>
    </div>
    <div v-if="selectedRace && selectedRace.cultures">
      <h3 class="culture-title">Choisissez une culture</h3>
      <div class="culture-cards">
        <CardComponent
          v-for="culture in selectedRace.cultures"
          :key="culture.name"
          :title="culture.name"
          :subtitle="culture.description"
          :class="{ selected: selectedCultureName === culture.name, clickable: true }"
          @click="selectCulture(culture.name)"
        >
          <div v-if="culture.skill_bonuses">
            <strong>Bonus de compétences :</strong> 
            <span v-for="(bonus, skill) in culture.skill_bonuses" :key="skill">
              {{ skill }}: +{{ bonus }}
            </span>
          </div>
          <div v-if="culture.characteristic_bonuses">
            <strong>Bonus de caractéristiques :</strong>
            <span v-for="(bonus, char) in culture.characteristic_bonuses" :key="char">
              {{ char }}: +{{ bonus }}
            </span>
          </div>
          <div v-if="culture.free_skill_points">
            <strong>Points de compétence gratuits :</strong> {{ culture.free_skill_points }}
          </div>
        </CardComponent>
      </div>
    </div>
    <div class="jdr-flex jdr-justify-end">
    <button
      class="jdr-btn jdr-btn-primary"
      :disabled="!canGoNext"
      :class="{ disabled: !canGoNext }"
      @click="goToNextStep"
    >
      Suivant
    </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import JdrApiService from '@/core/api';
import type { RaceData, CultureData, Character } from '@/core/interfaces';
import CardComponent from '@/components/CardComponent.vue';

const props = defineProps<{
  characterId?: string;
  initialData?: Character | null;
}>();
const emit = defineEmits<{
  (e: 'next-step', payload: { race: RaceData; culture: CultureData }): void;
  (e: 'update-character', payload: Character): void;
}>();

const races = ref<RaceData[]>([]);
const selectedRaceName = ref<string>('');
const selectedCultureName = ref<string>('');
const isInitialLoading = ref<boolean>(true); // Flag pour ignorer les changements lors du chargement initial

const selectedRace = computed(() =>
  races.value.find(r => r.name === selectedRaceName.value)
);

onMounted(async () => {
  isInitialLoading.value = true;
  races.value = await JdrApiService.getRaces();
  
  // Pré-remplissage si édition - après le chargement des races
  if (props.initialData && races.value.length > 0) {
    selectedRaceName.value = props.initialData.race?.name || '';
    selectedCultureName.value = props.initialData.culture?.name || '';
  }
  
  // Marquer que le chargement initial est terminé
  setTimeout(() => {
    isInitialLoading.value = false;
  }, 100); // Petit délai pour s'assurer que tous les watchers ont fini
});

// Ajout d'un watcher pour réagir à l'arrivée tardive de initialData (cas du SSR ou du fetch asynchrone)
watch(
  () => props.initialData,
  (newVal) => {
    if (newVal && races.value.length > 0 && isInitialLoading.value) {
      selectedRaceName.value = newVal.race?.name || '';
      selectedCultureName.value = newVal.culture?.name || '';
    }
  },
  { immediate: true }
);

// Watcher pour pré-remplir les données quand les races sont chargées (cas où races arrivent après initialData)
watch(
  () => races.value,
  (newRaces) => {
    if (newRaces.length > 0 && props.initialData && isInitialLoading.value) {
      selectedRaceName.value = props.initialData.race?.name || '';
      selectedCultureName.value = props.initialData.culture?.name || '';
    }
  },
  { immediate: false } // Pas immediate car on gère déjà dans onMounted
);

watch([selectedRaceName, selectedCultureName], async ([raceName, cultureName]) => {
  // Ne pas sauvegarder pendant le chargement initial
  if (isInitialLoading.value) {
    return;
  }
  
  if (props.characterId && raceName && cultureName) {
    const selectedRace = races.value.find(r => r.name === raceName);
    const selectedCulture = selectedRace?.cultures?.find(c => c.name === cultureName);
    
    if (selectedRace && selectedCulture) {
      // Créer une copie de la race sans la propriété cultures pour éviter la duplication
      const { cultures, ...raceWithoutCultures } = selectedRace;
      
      // Enregistrement automatique côté back dès qu'une race ou culture est sélectionnée
      await JdrApiService.saveCharacter({
        character_id: props.characterId,
        character: {
          ...props.initialData,
          race: raceWithoutCultures,
          culture: selectedCulture
        }
      });
      emit('update-character', {
        ...(props.initialData || {}),
        race: raceWithoutCultures as RaceData,
        culture: selectedCulture
      } as Character);
    }
  }
});

function selectRace(raceName: string) {
  selectedRaceName.value = raceName;
  selectedCultureName.value = '';
}

function selectCulture(cultureName: string) {
  selectedCultureName.value = cultureName;
}

const canGoNext = computed(() => {
  return (
    selectedRaceName.value &&
    selectedCultureName.value
  );
});

function goToNextStep() {
  if (
    selectedRace.value &&
    selectedCultureName.value &&
    canGoNext.value
  ) {
    const selectedCulture = selectedRace.value.cultures?.find(
      c => c.name === selectedCultureName.value
    );
    
    if (selectedCulture) {
      // Créer une copie de la race sans la propriété cultures pour éviter la duplication
      const { cultures, ...raceWithoutCultures } = selectedRace.value;
      
      emit('next-step', {
        race: raceWithoutCultures as RaceData,
        culture: selectedCulture
      });
    }
  }
}
</script>

<style scoped>
.culture-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-bottom: 2rem;
}
.culture-title {
  margin-bottom: 1rem;
}
.selected {
  border: 3px solid var(--jdr-secondary);
  box-shadow: 0 0 0 2px var(--jdr-secondary-light);
}
.clickable {
  cursor: pointer;
}
 .culture-cards > * {
  flex: 1 1 260px;
  min-width: 260px;
  max-width: 320px;
  box-sizing: border-box;
}
button.jdr-btn.disabled,
button.jdr-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
