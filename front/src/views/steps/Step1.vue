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
    <div v-if="selectedRace">
      <h3 class="culture-title">Choisissez une culture</h3>
      <div class="culture-cards">
        <CardComponent
          v-for="culture in selectedRace.cultures"
          :key="culture.name"
          :title="culture.name"
          :subtitle="culture.bonus"
          :class="{ selected: selectedCultureName === culture.name, clickable: true }"
          @click="selectCulture(culture.name)"
        >
          <div>
            <strong>Traits :</strong> {{ culture.traits }}
          </div>
        </CardComponent>
      </div>
    </div>
    <!-- Ajout de la sélection de la profession -->
    <div v-if="selectedRace && selectedCultureName && professions.length">
      <h3 class="culture-title">Choisissez une profession</h3>
      <div class="culture-cards">
        <CardComponent
          v-for="profession in professions"
          :key="profession.name"
          :title="profession.name"
          :subtitle="profession.description"
          :class="{ selected: selectedProfession === profession.name, clickable: true }"
          @click="selectProfession(profession.name)"
        >
          <div>
            <strong>Groupes de compétences favoris :</strong>
            <ul>
              <li v-for="(val, group) in profession.favored_skill_groups" :key="group">
                {{ group }} : {{ val }}
              </li>
            </ul>
            <div><strong>Caractéristiques principales :</strong> {{ profession.main_characteristics.join(', ') }}</div>
            <div><strong>Capacités :</strong> {{ profession.abilities.join(', ') }}</div>
            <div v-if="profession.spheres.length"><strong>Sphères :</strong> {{ profession.spheres.join(', ') }}</div>
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
import type { RaceJson, Character, ProfessionJson } from '@/core/interfaces';
import CardComponent from '@/components/CardComponent.vue';

const props = defineProps<{
  characterId?: string;
  initialData?: Character | null;
}>();
const emit = defineEmits<{
  (e: 'next-step', payload: { race: RaceJson; culture: { name: string; bonus: string; traits: string }; profession: string }): void;
  (e: 'update-character', payload: Character): void;
}>();

const races = ref<RaceJson[]>([]);
const professions = ref<ProfessionJson[]>([]);
const selectedRaceName = ref<string>('');
const selectedCultureName = ref<string>('');
const selectedProfession = ref<string>('');

const selectedRace = computed(() =>
  races.value.find(r => r.name === selectedRaceName.value)
);

onMounted(async () => {
  races.value = await JdrApiService.getRaces();
  professions.value = await JdrApiService.getProfessions();
  // Pré-remplissage si édition
  if (props.initialData) {
    selectedRaceName.value = props.initialData.race;
    selectedCultureName.value = props.initialData.culture;
    selectedProfession.value = props.initialData.profession;
  }
});

// Ajout d'un watcher pour réagir à l'arrivée tardive de initialData (cas du SSR ou du fetch asynchrone)
watch(
  () => props.initialData,
  (newVal) => {
    if (newVal) {
      selectedRaceName.value = newVal.race;
      selectedCultureName.value = newVal.culture;
      selectedProfession.value = newVal.profession;
    }
  },
  { immediate: true }
);

watch([selectedRaceName, selectedCultureName, selectedProfession], async ([race, culture, profession]) => {
  if (props.characterId && race && culture && profession) {
    // Enregistrement automatique côté back dès qu'une race, culture ou profession est sélectionnée
    await JdrApiService.saveCharacter({
      character_id: props.characterId,
      character: {
        ...props.initialData,
        race,
        culture,
        profession
      }
    });
    emit('update-character', {
      ...(props.initialData || {}),
      race,
      culture,
      profession
    } as Character);
  }
});

function selectRace(raceName: string) {
  selectedRaceName.value = raceName;
  selectedCultureName.value = '';
  selectedProfession.value = '';
}

function selectCulture(cultureName: string) {
  selectedCultureName.value = cultureName;
  selectedProfession.value = '';
}

function selectProfession(profession: string) {
  selectedProfession.value = profession;
}

const canGoNext = computed(() => {
  return (
    selectedRaceName.value &&
    selectedCultureName.value &&
    selectedProfession.value
  );
});

function goToNextStep() {
  if (
    selectedRace.value &&
    selectedCultureName.value &&
    selectedProfession.value &&
    canGoNext.value
  ) {
    emit('next-step', {
      race: selectedRace.value,
      culture:
        selectedRace.value.cultures.find(
          c => c.name === selectedCultureName.value
        ) || { name: '', bonus: '', traits: '' },
      profession: selectedProfession.value
    });
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
