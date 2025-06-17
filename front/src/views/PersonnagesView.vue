<template>
  <div class="jdr-container jdr-p-4">
    <!-- En-tête de la page -->
    <div class="jdr-text-center jdr-mb-4">
      <h1 class="jdr-title jdr-title-lg">Personnages</h1>
      <p class="jdr-subtitle">Gérez et consultez tous les personnages disponibles</p>
    </div>

    <!-- Indicateur de chargement -->
    <div v-if="loading" class="jdr-text-center jdr-p-4">
      <JdrSpinner class="jdr-mx-auto jdr-mb-2" :size="48" />
      <p class="jdr-mt-4">Chargement des personnages...</p>
    </div>

    <!-- Message d'erreur -->
    <div v-else-if="error" class="jdr-card jdr-card-highlight" style="border-color: var(--jdr-danger);">
      <div class="jdr-card-body jdr-text-center">
        <font-awesome-icon :icon="['fas', 'exclamation-triangle']" size="2x" style="color: var(--jdr-danger);" />
        <h3 class="jdr-title jdr-title-sm jdr-mt-4">Erreur de chargement</h3>
        <p class="jdr-text-muted">{{ error }}</p>
        <button @click="loadCharacters" class="jdr-btn jdr-btn-primary jdr-mt-4">
          <font-awesome-icon :icon="['fas', 'redo']" />
          Réessayer
        </button>
      </div>
    </div>

    <!-- Liste des personnages -->
    <div v-else-if="characters.length > 0" class="jdr-animate-fadeIn">
      <!-- Actions et filtres -->
      <div class="characters-header jdr-flex jdr-justify-between jdr-items-center jdr-mb-4">
        <div class="jdr-badge jdr-badge-info">
          <font-awesome-icon :icon="['fas', 'users']" />
          {{ characters.length }} personnage{{ characters.length > 1 ? 's' : '' }}
        </div>
        <div class="header-actions jdr-flex jdr-gap-2">
          <button @click="loadCharacters" class="jdr-btn jdr-btn-outline jdr-btn-sm">
            <font-awesome-icon :icon="['fas', 'sync-alt']" />
            Actualiser
          </button>
          <button @click="onCreateCharacterClick" class="jdr-btn jdr-btn-primary">
            <font-awesome-icon :icon="['fas', 'plus']" />
            Créer un personnage
          </button>
        </div>
      </div>

      <!-- Affichage unique en CardComponent -->
      <div class="jdr-flex jdr-flex-wrap jdr-gap-4 jdr-justify-center">
        <CardComponent
          v-for="character in characters"
          :key="character.id"
          :title="character.name"
          :subtitle="character.race?.name || 'Race non définie'"
          @click="selectCharacter(character)"
          class="jdr-w-full md:jdr-w-1/3 lg:jdr-w-1/4"
        >
          <template #default>
            <div class="jdr-mb-2">
              <span class="jdr-text-muted">Culture :</span>
              <span>{{ character.culture?.name || 'Culture non définie' }}</span>
            </div>
          </template>
          <template #footer>
            <button @click.stop="viewCharacterDetails(character)" class="jdr-btn jdr-btn-outline jdr-btn-sm">
              <font-awesome-icon :icon="['fas', 'eye']" />
              Détails
            </button>
            <template v-if="character.status === 'en_cours'">
              <button
                class="jdr-btn jdr-btn-warning jdr-btn-sm"
                @click.stop="finalizeCharacter(character)"
              >
                <font-awesome-icon :icon="['fas', 'edit']" />
                Finaliser le personnage
              </button>
            </template>
            <template v-else>
              <router-link 
                :to="{ name: 'nouveau-scenario', query: { characterId: character.id } }"
                class="jdr-btn jdr-btn-primary jdr-btn-sm"
                @click.stop
              >
                <font-awesome-icon :icon="['fas', 'play']" />
                Jouer
              </router-link>
            </template>
          </template>
        </CardComponent>
      </div>
    </div>

    <!-- Aucun personnage -->
    <div v-else class="jdr-card jdr-text-center jdr-animate-fadeIn">
      <div class="jdr-card-body">
        <font-awesome-icon :icon="['fas', 'user-times']" size="3x" class="jdr-text-muted jdr-mb-4" />
        <h3 class="jdr-title jdr-title-sm">Aucun personnage disponible</h3>
        <p class="jdr-text-muted jdr-mb-4">
          Il n'y a actuellement aucun personnage créé. Créez un personnage pour commencer !
        </p>
        <button @click="onCreateCharacterClick" class="jdr-btn jdr-btn-primary jdr-btn-lg">
          <font-awesome-icon :icon="['fas', 'plus']" />
          Créer un personnage
        </button>
      </div>
    </div>

    <!-- Modal de détails du personnage -->
    <JdrModale
      v-if="showDetailsModal && selectedCharacter"
      :title="selectedCharacter.name"
      :subtitle="selectedCharacter.profession + ' - ' + selectedCharacter.race.name"
      :showOk="false"
      :showCancel="true"
      cancelLabel="Fermer"
      @close="closeDetailsModal"
    >
      <template #default>
        <div class="jdr-mb-4">
          <h2 class="jdr-title jdr-title-lg jdr-mb-2 jdr-text-center">{{ selectedCharacter.name }}</h2>
          <div class="jdr-flex jdr-justify-center jdr-gap-4 jdr-mb-2">
            <div>
              <h4 class="jdr-title jdr-title-sm jdr-mb-1">Race</h4>
              <div class="jdr-text-primary jdr-text-center">{{ selectedCharacter.race?.name || 'Race non définie' }}</div>
            </div>
            <div>
              <h4 class="jdr-title jdr-title-sm jdr-mb-1">Culture</h4>
              <div class="jdr-text-primary jdr-text-center">{{ selectedCharacter.culture?.name || 'Culture non définie' }}</div>
            </div>
            <div>
              <h4 class="jdr-title jdr-title-sm jdr-mb-1">Profession</h4>
              <div class="jdr-text-primary jdr-text-center">{{ selectedCharacter.profession }}</div>
            </div>
          </div>
        </div>
        <div class="jdr-mb-4">
          <h3 class="jdr-title jdr-title-sm jdr-mb-2">Points de vie</h3>
          <div class="jdr-flex jdr-items-center jdr-gap-2">
            <div class="jdr-progress jdr-w-full" style="max-width: 300px;">
              <div class="jdr-progress-bar" :class="getHpBarClass(selectedCharacter.hp)" :style="{ width: `${(selectedCharacter.hp / 100) * 100}%` }"></div>
            </div>
            <span class="hp-value">{{ selectedCharacter.hp }}/100</span>
          </div>
        </div>
        <div class="jdr-mb-4">
          <h3 class="jdr-title jdr-title-sm jdr-mb-2">Caractéristiques</h3>
          <div class="jdr-grid jdr-grid-cols-2 md:jdr-grid-cols-4 jdr-gap-2">
            <div v-for="(value, stat) in selectedCharacter.caracteristiques" :key="stat" class="jdr-stat jdr-p-2 jdr-text-center jdr-border jdr-rounded">
              <div class="jdr-stat-name jdr-font-bold jdr-mb-1">{{ stat }}</div>
              <div class="jdr-stat-value jdr-text-lg">{{ value }}</div>
            </div>
          </div>
        </div>
        <div class="jdr-mb-4">
          <h3 class="jdr-title jdr-title-sm jdr-mb-2">Compétences</h3>
          <div class="jdr-grid jdr-grid-cols-2 md:jdr-grid-cols-4 jdr-gap-2">
            <div v-for="(value, skill) in selectedCharacter.competences" :key="skill" class="jdr-stat jdr-p-2 jdr-text-center jdr-border jdr-rounded" v-show="value > 0">
              <div class="jdr-stat-name jdr-font-bold jdr-mb-1">{{ formatSkillName(skill) }}</div>
              <div class="jdr-stat-value jdr-text-lg">{{ value }}</div>
            </div>
          </div>
        </div>
        <div v-if="selectedCharacter.equipment && selectedCharacter.equipment.length > 0" class="jdr-mb-4">
          <h3 class="jdr-title jdr-title-sm jdr-mb-2">Équipement</h3>
          <div class="equipment-list">
            <div v-for="item in selectedCharacter.equipment" :key="item" class="equipment-item">
              <font-awesome-icon :icon="['fas', 'sword']" class="jdr-text-accent jdr-mr-2" />
              <span>{{ item }}</span>
            </div>
          </div>
        </div>
        <div v-if="selectedCharacter.spells && selectedCharacter.spells.length > 0" class="jdr-mb-4">
          <h3 class="jdr-title jdr-title-sm jdr-mb-2">Sorts</h3>
          <div class="jdr-grid jdr-grid-cols-2 md:jdr-grid-cols-4 jdr-gap-2">
            <div v-for="spell in selectedCharacter.spells" :key="spell" class="jdr-stat jdr-p-2 jdr-text-center jdr-border jdr-rounded">
              <font-awesome-icon :icon="['fas', 'sparkles']" class="jdr-text-accent jdr-mb-1" />
              <div class="jdr-stat-name">{{ spell }}</div>
            </div>
          </div>
        </div>
      </template>
    </JdrModale>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import JdrApiService, { type Character } from '@/core/api';
import CardComponent from '@/components/CardComponent.vue';
import JdrSpinner from '@/components/JdrSpinner.vue';
import JdrModale from '@/components/JdrModale.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { useRouter } from 'vue-router';

// État réactif
const loading = ref(true);
const error = ref<string | null>(null);
const characters = ref<Character[]>([]);

// Modal de détails
const showDetailsModal = ref(false);
const selectedCharacter = ref<Character | null>(null);

// Router
const router = useRouter();

// Chargement des personnages
const loadCharacters = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    const charactersData = await JdrApiService.getCharacters();
    characters.value = charactersData;
  } catch (err) {
    console.error('Erreur lors du chargement des personnages:', err);
    error.value = err instanceof Error ? err.message : 'Erreur de connexion au serveur';
  } finally {
    loading.value = false;
  }
};

// Actions
const selectCharacter = (character: Character) => {
  console.log('Personnage sélectionné:', character.name);
  // Ici on pourrait ajouter une logique de sélection
};

const viewCharacterDetails = (character: Character) => {
  selectedCharacter.value = character;
  showDetailsModal.value = true;
};

const closeDetailsModal = () => {
  showDetailsModal.value = false;
  selectedCharacter.value = null;
};

// Création d'un personnage
const onCreateCharacterClick = async () => {
  try {
    loading.value = true;
    error.value = null;

    // Appel à l'API pour créer un personnage (étape 1)
    const newCharacter = await JdrApiService.createNewCharacter();

    // Redirection vers la route de création avec l'ID du personnage et l'étape 1
    if (newCharacter && newCharacter.id) {
      router.push({ name: 'create', params: { characterId: newCharacter.id, step: 'step1' } });
    }
  } catch (err) {
    console.error('Erreur lors de la création du personnage:', err);
    error.value = err instanceof Error ? err.message : 'Erreur de connexion au serveur';
  } finally {
    loading.value = false;
  }
};

// Finalisation du personnage
const finalizeCharacter = (character: Character) => {
  router.push({ name: 'create', params: { characterId: character.id, step: 'step1' } });
};

// Utilitaires de formatage
const formatSkillName = (skill: string | number) => {
  const skillStr = String(skill);
  return skillStr
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const getHpBarClass = (hp: number) => {
  if (hp > 70) return '';
  if (hp > 30) return 'warning';
  return 'danger';
};

// Montage du composant
onMounted(() => {
  loadCharacters();
});
</script>

<style scoped>
@import "../assets/responsive.css";

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}
.detail-label {
  color: var(--jdr-text-muted);
  font-weight: 500;
}
.detail-value {
  color: var(--jdr-text-primary);
  font-weight: 600;
}
.hp-value {
  min-width: 60px;
  text-align: right;
  font-weight: 600;
  color: var(--jdr-text-secondary);
}
.jdr-stat {
  background: var(--jdr-bg-primary);
  border-radius: var(--jdr-border-radius);
}
.jdr-stat-name {
  color: var(--jdr-text-secondary);
  font-size: 0.9rem;
}
.jdr-stat-value {
  color: var(--jdr-secondary);
  font-weight: bold;
  font-family: monospace;
}
.skill-item {
  background: var(--jdr-bg-primary);
  border-radius: var(--jdr-border-radius);
  border: 1px solid rgba(139, 69, 19, 0.3);
}
.skill-name {
  color: var(--jdr-text-secondary);
  font-size: 0.9rem;
}
.skill-value {
  color: var(--jdr-secondary);
  font-weight: bold;
  font-family: monospace;
}
</style>
