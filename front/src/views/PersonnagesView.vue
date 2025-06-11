<template>
  <div class="jdr-container jdr-p-4">
    <!-- En-tête de la page -->
    <div class="jdr-text-center jdr-mb-4">
      <h1 class="jdr-title jdr-title-lg">Personnages</h1>
      <p class="jdr-subtitle">Gérez et consultez tous les personnages disponibles</p>
    </div>

    <!-- Indicateur de chargement -->
    <div v-if="loading" class="jdr-text-center jdr-p-4">
      <div class="jdr-animate-pulse">
        <i class="fas fa-user-shield fa-3x jdr-text-accent"></i>
        <p class="jdr-mt-4">Chargement des personnages...</p>
      </div>
    </div>

    <!-- Message d'erreur -->
    <div v-else-if="error" class="jdr-card jdr-card-highlight" style="border-color: var(--jdr-danger);">
      <div class="jdr-card-body jdr-text-center">
        <i class="fas fa-exclamation-triangle fa-2x" style="color: var(--jdr-danger);"></i>
        <h3 class="jdr-title jdr-title-sm jdr-mt-4">Erreur de chargement</h3>
        <p class="jdr-text-muted">{{ error }}</p>
        <button @click="loadCharacters" class="jdr-btn jdr-btn-primary jdr-mt-4">
          <i class="fas fa-redo"></i>
          Réessayer
        </button>
      </div>
    </div>

    <!-- Liste des personnages -->
    <div v-else-if="characters.length > 0" class="jdr-animate-fadeIn">
      <!-- Actions et filtres -->
      <div class="characters-header jdr-flex jdr-justify-between jdr-items-center jdr-mb-4">
        <div class="jdr-badge jdr-badge-info">
          <i class="fas fa-users"></i>
          {{ characters.length }} personnage{{ characters.length > 1 ? 's' : '' }}
        </div>
        
        <div class="header-actions jdr-flex jdr-gap-2">
          <button @click="loadCharacters" class="jdr-btn jdr-btn-outline jdr-btn-sm">
            <i class="fas fa-sync-alt"></i>
            Actualiser
          </button>
          
          <button @click="toggleViewMode" class="jdr-btn jdr-btn-outline jdr-btn-sm">
            <i :class="viewMode === 'grid' ? 'fas fa-list' : 'fas fa-th'"></i>
            {{ viewMode === 'grid' ? 'Liste' : 'Grille' }}
          </button>
        </div>
      </div>

      <!-- Vue en grille -->
      <div v-if="viewMode === 'grid'" class="characters-grid">
        <div 
          v-for="character in characters" 
          :key="character.id"
          class="jdr-card jdr-card-character character-card jdr-animate-slideIn"
          @click="selectCharacter(character)"
        >
          <!-- En-tête du personnage -->
          <div class="jdr-card-header">
            <div class="character-header">
              <div class="character-avatar">
                <i class="fas fa-user-circle fa-3x"></i>
              </div>
              <div class="character-basic-info">
                <h3 class="jdr-card-title">{{ character.name }}</h3>
                <p class="jdr-card-subtitle">{{ character.race }} - {{ character.profession }}</p>
              </div>
            </div>
          </div>

          <!-- Informations du personnage -->
          <div class="jdr-card-body">
            <div class="character-details">
              <div class="detail-row">
                <span class="detail-label">Culture :</span>
                <span class="detail-value">{{ character.culture }}</span>
              </div>
              
              <div class="detail-row">
                <span class="detail-label">Points de Vie :</span>
                <div class="hp-display">
                  <div class="jdr-progress">
                    <div 
                      class="jdr-progress-bar" 
                      :class="getHpBarClass(character.hp)"
                      :style="{ width: `${(character.hp / 100) * 100}%` }"
                    ></div>
                  </div>
                  <span class="hp-value">{{ character.hp }}/100</span>
                </div>
              </div>
            </div>

            <!-- Caractéristiques principales -->
            <div class="main-stats">
              <h4 class="stats-title">
                <i class="fas fa-chart-bar"></i>
                Caractéristiques
              </h4>
              <div class="stats-grid">
                <div 
                  v-for="(value, stat) in getMainStats(character.caracteristiques)" 
                  :key="stat"
                  class="jdr-stat"
                >
                  <span class="jdr-stat-name">{{ formatStatName(stat) }}</span>
                  <span class="jdr-stat-value">{{ value }}</span>
                </div>
              </div>
            </div>

            <!-- Compétences principales -->
            <div class="main-skills">
              <h4 class="stats-title">
                <i class="fas fa-cogs"></i>
                Compétences Clés
              </h4>
              <div class="skills-list">
                <div 
                  v-for="(value, skill) in getTopSkills(character.competences)" 
                  :key="skill"
                  class="skill-item"
                >
                  <span class="skill-name">{{ formatSkillName(skill) }}</span>
                  <span class="skill-value">{{ value }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="jdr-card-footer">
            <button @click.stop="viewCharacterDetails(character)" class="jdr-btn jdr-btn-outline jdr-btn-sm">
              <i class="fas fa-eye"></i>
              Détails
            </button>
            
            <router-link 
              :to="{ name: 'nouveau-scenario', query: { characterId: character.id } }"
              class="jdr-btn jdr-btn-primary jdr-btn-sm"
              @click.stop
            >
              <i class="fas fa-play"></i>
              Jouer
            </router-link>
          </div>
        </div>
      </div>

      <!-- Vue en liste -->
      <div v-else class="characters-table">
        <table class="jdr-table">
          <thead>
            <tr>
              <th>Personnage</th>
              <th>Race</th>
              <th>Culture</th>
              <th>Profession</th>
              <th>PV</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="character in characters" :key="character.id" @click="selectCharacter(character)">
              <td>
                <div class="character-name-cell">
                  <i class="fas fa-user-circle fa-lg jdr-text-accent"></i>
                  <strong>{{ character.name }}</strong>
                </div>
              </td>
              <td>{{ character.race }}</td>
              <td>{{ character.culture }}</td>
              <td>{{ character.profession }}</td>
              <td>
                <div class="hp-cell">
                  <div class="jdr-progress">
                    <div 
                      class="jdr-progress-bar" 
                      :class="getHpBarClass(character.hp)"
                      :style="{ width: `${(character.hp / 100) * 100}%` }"
                    ></div>
                  </div>
                  <span>{{ character.hp }}/100</span>
                </div>
              </td>
              <td>
                <div class="table-actions jdr-flex jdr-gap-2">
                  <button @click.stop="viewCharacterDetails(character)" class="jdr-btn jdr-btn-outline jdr-btn-sm">
                    <i class="fas fa-eye"></i>
                  </button>
                  
                  <router-link 
                    :to="{ name: 'nouveau-scenario', query: { characterId: character.id } }"
                    class="jdr-btn jdr-btn-primary jdr-btn-sm"
                    @click.stop
                  >
                    <i class="fas fa-play"></i>
                  </router-link>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Aucun personnage -->
    <div v-else class="jdr-card jdr-text-center jdr-animate-fadeIn">
      <div class="jdr-card-body">
        <i class="fas fa-user-times fa-3x jdr-text-muted jdr-mb-4"></i>
        <h3 class="jdr-title jdr-title-sm">Aucun personnage disponible</h3>
        <p class="jdr-text-muted jdr-mb-4">
          Il n'y a actuellement aucun personnage créé. Créez un personnage pour commencer !
        </p>
        <button class="jdr-btn jdr-btn-primary jdr-btn-lg" disabled>
          <i class="fas fa-plus"></i>
          Créer un personnage
        </button>
        <p class="jdr-text-muted jdr-mt-4">
          <small>Fonctionnalité à venir</small>
        </p>
      </div>
    </div>

    <!-- Modal de détails du personnage -->
    <div v-if="showDetailsModal && selectedCharacter" class="jdr-modal-overlay show" @click="closeDetailsModal">
      <div class="jdr-modal character-details-modal" @click.stop>
        <div class="jdr-modal-header">
          <h2 class="jdr-modal-title">
            <i class="fas fa-user-shield"></i>
            {{ selectedCharacter.name }}
          </h2>
          <button @click="closeDetailsModal" class="jdr-modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="jdr-modal-body">
          <div class="character-full-details">
            <!-- Informations générales -->
            <div class="details-section">
              <h3 class="section-title">
                <i class="fas fa-info-circle"></i>
                Informations Générales
              </h3>
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">Race :</span>
                  <span class="info-value">{{ selectedCharacter.race }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Culture :</span>
                  <span class="info-value">{{ selectedCharacter.culture }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Profession :</span>
                  <span class="info-value">{{ selectedCharacter.profession }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">Points de Vie :</span>
                  <span class="info-value">{{ selectedCharacter.hp }}/100</span>
                </div>
              </div>
            </div>

            <!-- Caractéristiques complètes -->
            <div class="details-section">
              <h3 class="section-title">
                <i class="fas fa-chart-bar"></i>
                Caractéristiques
              </h3>
              <div class="stats-complete">
                <div 
                  v-for="(value, stat) in selectedCharacter.caracteristiques" 
                  :key="stat"
                  class="jdr-stat"
                >
                  <span class="jdr-stat-name">{{ formatStatName(stat) }}</span>
                  <span class="jdr-stat-value">{{ value }}</span>
                </div>
              </div>
            </div>

            <!-- Compétences complètes -->
            <div class="details-section">
              <h3 class="section-title">
                <i class="fas fa-cogs"></i>
                Compétences
              </h3>
              <div class="skills-complete">
                <div 
                  v-for="(value, skill) in selectedCharacter.competences" 
                  :key="skill"
                  class="skill-item"
                  v-show="value > 0"
                >
                  <span class="skill-name">{{ formatSkillName(skill) }}</span>
                  <span class="skill-value">{{ value }}</span>
                </div>
              </div>
            </div>

            <!-- Équipement -->
            <div class="details-section" v-if="selectedCharacter.equipment && selectedCharacter.equipment.length > 0">
              <h3 class="section-title">
                <i class="fas fa-shield-alt"></i>
                Équipement
              </h3>
              <div class="equipment-list">
                <div 
                  v-for="item in selectedCharacter.equipment" 
                  :key="item"
                  class="equipment-item"
                >
                  <i class="fas fa-sword jdr-text-accent"></i>
                  <span>{{ item }}</span>
                </div>
              </div>
            </div>

            <!-- Sorts -->
            <div class="details-section" v-if="selectedCharacter.spells && selectedCharacter.spells.length > 0">
              <h3 class="section-title">
                <i class="fas fa-magic"></i>
                Sorts
              </h3>
              <div class="spells-list">
                <div 
                  v-for="spell in selectedCharacter.spells" 
                  :key="spell"
                  class="spell-item"
                >
                  <i class="fas fa-sparkles jdr-text-accent"></i>
                  <span>{{ spell }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="jdr-modal-footer">
          <button @click="closeDetailsModal" class="jdr-btn jdr-btn-outline">
            <i class="fas fa-times"></i>
            Fermer
          </button>
          
          <router-link 
            :to="{ name: 'nouveau-scenario', query: { characterId: selectedCharacter.id } }"
            class="jdr-btn jdr-btn-primary"
            @click="closeDetailsModal"
          >
            <i class="fas fa-play"></i>
            Jouer avec ce personnage
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import JdrApiService, { type Character } from '@/core/api';

// État réactif
const loading = ref(true);
const error = ref<string | null>(null);
const characters = ref<Character[]>([]);
const viewMode = ref<'grid' | 'list'>('grid');

// Modal de détails
const showDetailsModal = ref(false);
const selectedCharacter = ref<Character | null>(null);

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
const toggleViewMode = () => {
  viewMode.value = viewMode.value === 'grid' ? 'list' : 'grid';
};

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

// Utilitaires de formatage
const formatStatName = (stat: string) => {
  const statNames: Record<string, string> = {
    'force': 'Force',
    'constitution': 'Constitution',
    'agilite': 'Agilité',
    'dexterite': 'Dextérité',
    'intelligence': 'Intelligence',
    'perception': 'Perception',
    'volonte': 'Volonté',
    'charisme': 'Charisme',
    'chance': 'Chance'
  };
  
  return statNames[stat] || stat.charAt(0).toUpperCase() + stat.slice(1);
};

const formatSkillName = (skill: string) => {
  return skill
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const getHpBarClass = (hp: number) => {
  if (hp > 70) return '';
  if (hp > 30) return 'warning';
  return 'danger';
};

const getMainStats = (stats: Record<string, number>) => {
  // Retourne les 4 caractéristiques principales
  const mainStatKeys = ['force', 'constitution', 'agilite', 'intelligence'];
  const result: Record<string, number> = {};
  
  mainStatKeys.forEach(key => {
    if (stats[key] !== undefined) {
      result[key] = stats[key];
    }
  });
  
  return result;
};

const getTopSkills = (skills: Record<string, number>) => {
  // Retourne les 3 meilleures compétences
  const sortedSkills = Object.entries(skills)
    .filter(([_, value]) => value > 0)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3);
  
  const result: Record<string, number> = {};
  sortedSkills.forEach(([skill, value]) => {
    result[skill] = value;
  });
  
  return result;
};

// Montage du composant
onMounted(() => {
  loadCharacters();
});
</script>

<style scoped>
.characters-header {
  margin-bottom: 1.5rem;
}

.characters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.character-card {
  transition: all 0.3s ease;
  cursor: pointer;
  height: fit-content;
}

.character-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--jdr-shadow-large);
}

.character-header {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.character-avatar {
  color: var(--jdr-accent);
  opacity: 0.8;
}

.character-basic-info {
  flex: 1;
}

.character-details {
  margin-bottom: 1.5rem;
}

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

.hp-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  justify-content: flex-end;
}

.hp-value {
  min-width: 60px;
  text-align: right;
  font-weight: 600;
  color: var(--jdr-text-secondary);
}

.main-stats,
.main-skills {
  margin-bottom: 1.5rem;
}

.stats-title {
  font-family: var(--jdr-font-fantasy);
  color: var(--jdr-accent);
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.skills-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.skill-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
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

/* Styles pour la vue en liste */
.characters-table {
  background: var(--jdr-bg-secondary);
  border-radius: var(--jdr-border-radius);
  overflow: hidden;
  box-shadow: var(--jdr-shadow-medium);
}

.character-name-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.hp-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 120px;
}

.table-actions {
  justify-content: center;
}

/* Modal de détails */
.character-details-modal {
  max-width: 800px;
  max-height: 90vh;
  width: 95%;
}

.character-full-details {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.details-section {
  background: var(--jdr-bg-tertiary);
  border: 1px solid var(--jdr-border-color);
  border-radius: var(--jdr-border-radius);
  padding: 1.5rem;
}

.section-title {
  font-family: var(--jdr-font-fantasy);
  color: var(--jdr-secondary);
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  color: var(--jdr-text-muted);
  font-weight: 500;
  font-size: 0.9rem;
}

.info-value {
  color: var(--jdr-text-primary);
  font-weight: 600;
}

.stats-complete {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.75rem;
}

.skills-complete {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
}

.equipment-list,
.spells-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.5rem;
}

.equipment-item,
.spell-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: var(--jdr-bg-primary);
  border-radius: var(--jdr-border-radius);
  border: 1px solid rgba(139, 69, 19, 0.3);
  font-size: 0.9rem;
  color: var(--jdr-text-secondary);
}

/* Responsive design */
@media (max-width: 768px) {
  .characters-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .character-header {
    flex-direction: column;
    text-align: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-complete {
    grid-template-columns: 1fr 1fr;
  }
  
  .skills-complete {
    grid-template-columns: 1fr;
  }
  
  .equipment-list,
  .spells-list {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .detail-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .hp-display {
    justify-content: flex-start;
    width: 100%;
  }
  
  .characters-table {
    font-size: 0.8rem;
  }
  
  .table-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
