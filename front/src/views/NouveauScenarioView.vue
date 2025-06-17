<template>
  <div class="jdr-container jdr-p-4">
    <!-- En-tête de la page -->
    <div class="jdr-text-center jdr-mb-4">
      <h1 class="jdr-title jdr-title-lg">Nouvelle Aventure</h1>
      <p class="jdr-subtitle">Choisissez votre personnage et le scénario pour commencer une nouvelle quête</p>
    </div>

    <!-- Indicateur de chargement initial -->
    <div v-if="initialLoading" class="jdr-text-center jdr-p-4">
      <div class="jdr-animate-pulse">
        <i class="fas fa-dice-d20 fa-3x jdr-text-accent"></i>
        <p class="jdr-mt-4">Chargement des données...</p>
      </div>
    </div>

    <!-- Message d'erreur global -->
    <div v-else-if="globalError" class="jdr-card jdr-card-highlight" style="border-color: var(--jdr-danger);">
      <div class="jdr-card-body jdr-text-center">
        <i class="fas fa-exclamation-triangle fa-2x" style="color: var(--jdr-danger);"></i>
        <h3 class="jdr-title jdr-title-sm jdr-mt-4">Erreur de connexion</h3>
        <p class="jdr-text-muted">{{ globalError }}</p>
        <button @click="loadInitialData" class="jdr-btn jdr-btn-primary jdr-mt-4">
          <i class="fas fa-redo"></i>
          Réessayer
        </button>
      </div>
    </div>

    <!-- Formulaire de création -->
    <div v-else class="creation-form jdr-animate-fadeIn">
      <div class="form-grid">
        
        <!-- Section Sélection du personnage -->
        <div class="jdr-card jdr-card-character">
          <div class="jdr-card-header">
            <h2 class="jdr-card-title">
              <i class="fas fa-user-shield"></i>
              Choisir un Personnage
            </h2>
            <p class="jdr-card-subtitle">Sélectionnez le héros qui vivra cette aventure</p>
          </div>
          
          <div class="jdr-card-body">
            <div v-if="loadingCharacters" class="loading-state">
              <i class="fas fa-spinner fa-spin jdr-text-accent"></i>
              <span>Chargement des personnages...</span>
            </div>
            
            <div v-else-if="characters.length === 0" class="empty-state">
              <i class="fas fa-user-times fa-2x jdr-text-muted"></i>
              <p class="jdr-mt-4 jdr-text-muted">Aucun personnage disponible</p>
            </div>
            
            <div v-else class="characters-list">
              <div 
                v-for="character in characters" 
                :key="character.id"
                class="character-card"
                :class="{ active: selectedCharacterId === character.id }"
                @click="selectCharacter(character.id)"
              >
                <div class="character-avatar">
                  <i class="fas fa-user-circle fa-3x"></i>
                </div>
                
                <div class="character-info">
                  <h3 class="character-name">{{ character.name }}</h3>
                  <div class="character-details">
                    <span class="detail-item">
                      <i class="fas fa-dragon"></i>
                      {{ character.race.name }}
                    </span>
                    <span class="detail-item">
                      <i class="fas fa-globe"></i>
                      {{ character.culture.name }}
                    </span>
                    <span class="detail-item">
                      <i class="fas fa-briefcase"></i>
                      {{ character.profession }}
                    </span>
                  </div>
                  
                  <div class="character-stats">
                    <div class="stat-bar">
                      <span class="stat-label">Points de Vie</span>
                      <div class="jdr-progress">
                        <div 
                          class="jdr-progress-bar" 
                          :style="{ width: `${(character.hp / 100) * 100}%` }"
                        ></div>
                      </div>
                      <span class="stat-value">{{ character.hp }}/100</span>
                    </div>
                  </div>
                </div>
                
                <div class="character-selection">
                  <i v-if="selectedCharacterId === character.id" class="fas fa-check-circle jdr-text-accent"></i>
                  <i v-else class="far fa-circle jdr-text-muted"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Section Sélection du scénario -->
        <div class="jdr-card jdr-card-scenario">
          <div class="jdr-card-header">
            <h2 class="jdr-card-title">
              <i class="fas fa-scroll"></i>
              Choisir un Scénario
            </h2>
            <p class="jdr-card-subtitle">Sélectionnez l'aventure que vous souhaitez vivre</p>
          </div>
          
          <div class="jdr-card-body">
            <div v-if="loadingScenarios" class="loading-state">
              <i class="fas fa-spinner fa-spin jdr-text-accent"></i>
              <span>Chargement des scénarios...</span>
            </div>
            
            <div v-else-if="availableScenarios.length === 0" class="empty-state">
              <i class="fas fa-scroll fa-2x jdr-text-muted"></i>
              <p class="jdr-mt-4 jdr-text-muted">Aucun scénario disponible</p>
            </div>
            
            <div v-else class="scenarios-list">
              <div 
                v-for="scenario in availableScenarios" 
                :key="scenario.name"
                class="scenario-card"
                :class="{ active: selectedScenarioName === scenario.name }"
                @click="selectScenario(scenario.name)"
              >
                <div class="scenario-header">
                  <h3 class="scenario-title">{{ formatScenarioName(scenario.name) }}</h3>
                  <div class="scenario-status">
                    <div class="jdr-badge" :class="getScenarioStatusClass(scenario.status)">
                      <i :class="getScenarioStatusIcon(scenario.status)"></i>
                      {{ getScenarioStatusLabel(scenario.status) }}
                    </div>
                  </div>
                </div>
                
                <div class="scenario-description">
                  <p class="scenario-text">{{ getScenarioDescription(scenario.name) }}</p>
                </div>
                
                <div class="scenario-footer">
                  <button 
                    @click.stop="previewScenario(scenario.name)"
                    class="jdr-btn jdr-btn-outline jdr-btn-sm"
                    :disabled="loadingPreview === scenario.name"
                  >
                    <i v-if="loadingPreview === scenario.name" class="fas fa-spinner fa-spin"></i>
                    <i v-else class="fas fa-eye"></i>
                    Aperçu
                  </button>
                  
                  <div class="scenario-selection">
                    <i v-if="selectedScenarioName === scenario.name" class="fas fa-check-circle jdr-text-accent"></i>
                    <i v-else class="far fa-circle jdr-text-muted"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Résumé et actions -->
      <div class="jdr-card jdr-mt-4 creation-summary">
        <div class="jdr-card-header">
          <h2 class="jdr-card-title">
            <i class="fas fa-clipboard-check"></i>
            Résumé de l'Aventure
          </h2>
        </div>
        
        <div class="jdr-card-body">
          <div class="summary-content">
            <div class="summary-section">
              <h4 class="summary-title">
                <i class="fas fa-user-shield"></i>
                Personnage sélectionné
              </h4>
              <div v-if="selectedCharacter" class="summary-item">
                <span class="item-name">{{ selectedCharacter.name }}</span>
                <span class="item-details">{{ selectedCharacter.race.name }} - {{ selectedCharacter.profession }}</span>
              </div>
              <div v-else class="summary-item empty">
                <span class="jdr-text-muted">Aucun personnage sélectionné</span>
              </div>
            </div>
            
            <div class="summary-section">
              <h4 class="summary-title">
                <i class="fas fa-scroll"></i>
                Scénario sélectionné
              </h4>
              <div v-if="selectedScenarioName" class="summary-item">
                <span class="item-name">{{ formatScenarioName(selectedScenarioName) }}</span>
                <span class="item-details">Aventure disponible</span>
              </div>
              <div v-else class="summary-item empty">
                <span class="jdr-text-muted">Aucun scénario sélectionné</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="jdr-card-footer">
          <router-link to="/sessions" class="jdr-btn jdr-btn-outline">
            <i class="fas fa-arrow-left"></i>
            Retour aux sessions
          </router-link>
          
          <button 
            @click="startAdventure"
            class="jdr-btn jdr-btn-primary jdr-btn-lg"
            :disabled="!canStartAdventure || startingAdventure"
          >
            <i v-if="startingAdventure" class="fas fa-spinner fa-spin"></i>
            <i v-else class="fas fa-play"></i>
            {{ startingAdventure ? 'Démarrage...' : 'Commencer l\'Aventure' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal d'aperçu de scénario -->
    <div v-if="showPreviewModal" class="jdr-modal-overlay show" @click="closePreviewModal">
      <div class="jdr-modal" @click.stop>
        <div class="jdr-modal-header">
          <h2 class="jdr-modal-title">
            <i class="fas fa-scroll"></i>
            {{ previewScenarioTitle }}
          </h2>
          <button @click="closePreviewModal" class="jdr-modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="jdr-modal-body">
          <div v-if="loadingPreviewContent" class="jdr-text-center jdr-p-4">
            <div class="jdr-animate-pulse">
              <i class="fas fa-spinner fa-spin fa-2x jdr-text-accent"></i>
              <p class="jdr-mt-4">Chargement du contenu...</p>
            </div>
          </div>
          
          <div v-else-if="previewError" class="jdr-text-center jdr-p-4">
            <i class="fas fa-exclamation-triangle fa-2x" style="color: var(--jdr-danger);"></i>
            <p class="jdr-mt-4">{{ previewError }}</p>
          </div>
          
          <div v-else class="preview-content">
            <div v-html="formattedPreviewContent"></div>
          </div>
        </div>
        
        <div class="jdr-modal-footer">
          <button @click="closePreviewModal" class="jdr-btn jdr-btn-outline">
            <i class="fas fa-times"></i>
            Fermer
          </button>
          
          <button 
            @click="selectScenarioFromPreview" 
            class="jdr-btn jdr-btn-primary"
            v-if="previewScenarioName && previewScenarioName !== selectedScenarioName"
          >
            <i class="fas fa-check"></i>
            Choisir ce scénario
          </button>
        </div>
      </div>
    </div>

    <!-- Message de démarrage -->
    <div v-if="startingAdventure" class="jdr-modal-overlay show">
      <div class="jdr-modal">
        <div class="jdr-modal-body jdr-text-center">
          <div class="jdr-animate-pulse">
            <i class="fas fa-dragon fa-4x jdr-text-accent jdr-mb-4"></i>
            <h3 class="jdr-title jdr-title-sm">L'aventure commence...</h3>
            <p class="jdr-text-muted">Préparation de votre session de jeu</p>
            
            <div class="jdr-progress jdr-mt-4">
              <div class="jdr-progress-bar jdr-animate-glow" style="width: 75%;"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import JdrApiService, { type Character, type ScenarioStatus } from '@/core/api';

const router = useRouter();

// État réactif
const initialLoading = ref(true);
const globalError = ref<string | null>(null);

// Personnages
const loadingCharacters = ref(false);
const characters = ref<Character[]>([]);
const selectedCharacterId = ref<string | null>(null);

// Scénarios
const loadingScenarios = ref(false);
const scenarios = ref<ScenarioStatus[]>([]);
const selectedScenarioName = ref<string | null>(null);

// Aperçu de scénario
const showPreviewModal = ref(false);
const loadingPreview = ref<string | null>(null);
const loadingPreviewContent = ref(false);
const previewError = ref<string | null>(null);
const previewScenarioName = ref<string | null>(null);
const previewScenarioTitle = ref('');
const previewContent = ref('');

// Démarrage d'aventure
const startingAdventure = ref(false);

// Descriptions de scénarios (fallback si pas d'API)
const scenarioDescriptions: Record<string, string> = {
  'Les_Pierres_du_Passe.md': 'Une mystérieuse quête dans les terres anciennes où des pierres runiques révèlent les secrets du passé.',
  'default': 'Une aventure épique vous attend dans les Terres du Milieu. Préparez-vous à vivre des moments légendaires.'
};

// Computed properties
const selectedCharacter = computed(() => {
  return characters.value.find(char => char.id === selectedCharacterId.value) || null;
});

const availableScenarios = computed(() => {
  // Filtrer les scénarios disponibles (non en cours)
  return scenarios.value.filter(scenario => scenario.status === 'available' || !scenario.session_id);
});

const canStartAdventure = computed(() => {
  return selectedCharacterId.value && selectedScenarioName.value && !startingAdventure.value;
});

const formattedPreviewContent = computed(() => {
  if (!previewContent.value) return '';
  
  // Conversion basique du Markdown en HTML
  return previewContent.value
    .replace(/^# (.*$)/gim, '<h1 class="jdr-title jdr-title-md">$1</h1>')
    .replace(/^## (.*$)/gim, '<h2 class="jdr-title jdr-title-sm">$1</h2>')
    .replace(/^### (.*$)/gim, '<h3 class="jdr-title">$1</h3>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(.+)$/gim, '<p>$1</p>');
});

// Chargement des données initiales
const loadInitialData = async () => {
  try {
    initialLoading.value = true;
    globalError.value = null;
    
    await Promise.all([
      loadCharacters(),
      loadScenarios()
    ]);
  } catch (err) {
    console.error('Erreur lors du chargement initial:', err);
    globalError.value = err instanceof Error ? err.message : 'Erreur de connexion au serveur';
  } finally {
    initialLoading.value = false;
  }
};

const loadCharacters = async () => {
  try {
    loadingCharacters.value = true;
    const charactersData = await JdrApiService.getCharacters();
    characters.value = charactersData;
  } catch (err) {
    console.error('Erreur lors du chargement des personnages:', err);
    throw err;
  } finally {
    loadingCharacters.value = false;
  }
};

const loadScenarios = async () => {
  try {
    loadingScenarios.value = true;
    const scenariosData = await JdrApiService.getScenarios();
    scenarios.value = scenariosData;
  } catch (err) {
    console.error('Erreur lors du chargement des scénarios:', err);
    throw err;
  } finally {
    loadingScenarios.value = false;
  }
};

// Actions de sélection
const selectCharacter = (characterId: string) => {
  selectedCharacterId.value = characterId;
};

const selectScenario = (scenarioName: string) => {
  selectedScenarioName.value = scenarioName;
};

// Aperçu de scénario
const previewScenario = async (scenarioName: string) => {
  try {
    loadingPreview.value = scenarioName;
    previewScenarioName.value = scenarioName;
    previewScenarioTitle.value = formatScenarioName(scenarioName);
    showPreviewModal.value = true;
    loadingPreviewContent.value = true;
    previewError.value = null;
    
    const content = await JdrApiService.getScenarioDetails(scenarioName);
    previewContent.value = content;
  } catch (err) {
    console.error('Erreur lors du chargement de l\'aperçu:', err);
    previewError.value = err instanceof Error ? err.message : 'Erreur de chargement';
  } finally {
    loadingPreview.value = null;
    loadingPreviewContent.value = false;
  }
};

const closePreviewModal = () => {
  showPreviewModal.value = false;
  previewScenarioName.value = null;
  previewContent.value = '';
  previewError.value = null;
};

const selectScenarioFromPreview = () => {
  if (previewScenarioName.value) {
    selectScenario(previewScenarioName.value);
    closePreviewModal();
  }
};

// Démarrage de l'aventure
const startAdventure = async () => {
  if (!canStartAdventure.value) return;
  
  try {
    startingAdventure.value = true;
    
    const response = await JdrApiService.startScenario({
      scenario_name: selectedScenarioName.value!,
      character_id: selectedCharacterId.value!
    });
    
    // Navigation vers la page de jeu avec la nouvelle session
    router.push({
      name: 'jeu',
      params: { sessionId: response.session_id }
    });
    
  } catch (err) {
    console.error('Erreur lors du démarrage de l\'aventure:', err);
    
    // Afficher l'erreur à l'utilisateur
    const errorMessage = err instanceof Error ? err.message : 'Erreur lors du démarrage de l\'aventure';
    alert(errorMessage); // À remplacer par un toast/notification plus élégant
    
    startingAdventure.value = false;
  }
};

// Utilitaires de formatage
const formatScenarioName = (name: string) => {
  return JdrApiService.formatScenarioName(name);
};

const getScenarioDescription = (name: string) => {
  return scenarioDescriptions[name] || scenarioDescriptions.default;
};

const getScenarioStatusClass = (status: string) => {
  switch (status) {
    case 'available': return 'jdr-badge-success';
    case 'active': return 'jdr-badge-warning';
    case 'completed': return 'jdr-badge-info';
    default: return 'jdr-badge-info';
  }
};

const getScenarioStatusIcon = (status: string) => {
  switch (status) {
    case 'available': return 'fas fa-check';
    case 'active': return 'fas fa-play';
    case 'completed': return 'fas fa-flag-checkered';
    default: return 'fas fa-question';
  }
};

const getScenarioStatusLabel = (status: string) => {
  switch (status) {
    case 'available': return 'Disponible';
    case 'active': return 'En cours';
    case 'completed': return 'Terminé';
    default: return 'Inconnu';
  }
};

// Montage du composant
onMounted(() => {
  loadInitialData();
});
</script>

<style scoped>
.creation-form {
  width: 100%;
  margin: 0 auto;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.loading-state,
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: var(--jdr-text-muted);
}

.empty-state {
  flex-direction: column;
}

/* Styles pour les personnages */
.characters-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.character-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--jdr-bg-tertiary);
  border: 2px solid transparent;
  border-radius: var(--jdr-border-radius);
  cursor: pointer;
  transition: all 0.3s ease;
}

.character-card:hover {
  background: var(--jdr-bg-secondary);
  border-color: var(--jdr-accent);
}

.character-card.active {
  border-color: var(--jdr-secondary);
  background: var(--jdr-bg-secondary);
  box-shadow: var(--jdr-glow-gold);
}

.character-avatar {
  color: var(--jdr-accent);
  opacity: 0.8;
}

.character-info {
  flex: 1;
}

.character-name {
  font-family: var(--jdr-font-fantasy);
  color: var(--jdr-text-primary);
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.character-details {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.85rem;
  color: var(--jdr-text-muted);
}

.character-stats {
  margin-top: 0.5rem;
}

.stat-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
}

.stat-label {
  min-width: 80px;
  color: var(--jdr-text-muted);
}

.stat-value {
  min-width: 50px;
  color: var(--jdr-text-secondary);
  font-weight: 500;
}

.character-selection {
  font-size: 1.5rem;
}

/* Styles pour les scénarios */
.scenarios-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.scenario-card {
  padding: 1rem;
  background: var(--jdr-bg-tertiary);
  border: 2px solid transparent;
  border-radius: var(--jdr-border-radius);
  cursor: pointer;
  transition: all 0.3s ease;
}

.scenario-card:hover {
  background: var(--jdr-bg-secondary);
  border-color: var(--jdr-success);
}

.scenario-card.active {
  border-color: var(--jdr-secondary);
  background: var(--jdr-bg-secondary);
  box-shadow: var(--jdr-glow-gold);
}

.scenario-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.scenario-title {
  font-family: var(--jdr-font-fantasy);
  color: var(--jdr-text-primary);
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  flex: 1;
}

.scenario-description {
  margin-bottom: 1rem;
}

.scenario-text {
  color: var(--jdr-text-secondary);
  font-style: italic;
  line-height: 1.5;
  margin: 0;
  font-size: 0.9rem;
}

.scenario-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.scenario-selection {
  font-size: 1.5rem;
}

/* Styles pour le résumé */
.creation-summary {
  background: var(--jdr-bg-secondary);
}

.summary-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.summary-section {
  padding: 1rem;
  background: var(--jdr-bg-tertiary);
  border-radius: var(--jdr-border-radius);
  border: 1px solid var(--jdr-border-color);
}

.summary-title {
  font-family: var(--jdr-font-fantasy);
  color: var(--jdr-accent);
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.summary-item.empty {
  font-style: italic;
  text-align: center;
  padding: 1rem;
}

.item-name {
  font-weight: 600;
  color: var(--jdr-text-primary);
  font-size: 1.1rem;
}

.item-details {
  color: var(--jdr-text-muted);
  font-size: 0.9rem;
}

/* Styles pour l'aperçu modal */
.preview-content {
  max-height: 400px;
  overflow-y: auto;
  line-height: 1.6;
  color: var(--jdr-text-primary);
}

.preview-content h1,
.preview-content h2,
.preview-content h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.preview-content h1:first-child,
.preview-content h2:first-child,
.preview-content h3:first-child {
  margin-top: 0;
}

.preview-content p {
  margin-bottom: 1rem;
}

.preview-content strong {
  color: var(--jdr-secondary);
}

.preview-content em {
  color: var(--jdr-accent);
}

/* Responsive design */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .summary-content {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .character-card {
    flex-direction: column;
    text-align: center;
  }
  
  .character-details {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .scenario-header {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .scenario-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}

@media (max-width: 480px) {
  .character-details {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .stat-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 0.25rem;
  }
}
</style>
