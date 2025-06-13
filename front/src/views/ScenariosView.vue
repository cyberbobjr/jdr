<template>
  <div class="jdr-container jdr-p-4">
    <!-- En-tête de la page -->
    <div class="jdr-text-center jdr-mb-4">
      <h1 class="jdr-title jdr-title-lg">Bibliothèque de Scénarios</h1>
      <p class="jdr-subtitle">Découvrez et explorez tous les scénarios disponibles</p>
    </div>

    <!-- Indicateur de chargement -->
    <div v-if="loading" class="jdr-text-center jdr-p-4">
      <div class="jdr-animate-pulse">
        <i class="fas fa-scroll fa-3x jdr-text-accent"></i>
        <p class="jdr-mt-4">Chargement des scénarios...</p>
      </div>
    </div>

    <!-- Message d'erreur -->
    <div v-else-if="error" class="jdr-card jdr-card-highlight" style="border-color: var(--jdr-danger);">
      <div class="jdr-card-body jdr-text-center">
        <i class="fas fa-exclamation-triangle fa-2x" style="color: var(--jdr-danger);"></i>
        <h3 class="jdr-title jdr-title-sm jdr-mt-4">Erreur de chargement</h3>
        <p class="jdr-text-muted">{{ error }}</p>
        <button @click="loadScenarios" class="jdr-btn jdr-btn-primary jdr-mt-4">
          <i class="fas fa-redo"></i>
          Réessayer
        </button>
      </div>
    </div>

    <!-- Liste des scénarios -->
    <div v-else-if="scenarios.length > 0" class="jdr-animate-fadeIn">
      <!-- Filtres et actions -->
      <div class="scenarios-header jdr-flex jdr-justify-between jdr-items-center jdr-mb-4">
        <div class="header-info">
          <div class="jdr-badge jdr-badge-info">
            <i class="fas fa-book"></i>
            {{ scenarios.length }} scénario{{ scenarios.length > 1 ? 's' : '' }}
          </div>
          
          <div class="status-badges jdr-flex jdr-gap-2 jdr-mt-2">
            <div class="jdr-badge jdr-badge-success">
              <i class="fas fa-check"></i>
              {{ availableCount }} disponible{{ availableCount > 1 ? 's' : '' }}
            </div>
            <div class="jdr-badge jdr-badge-warning" v-if="activeCount > 0">
              <i class="fas fa-play"></i>
              {{ activeCount }} en cours
            </div>
            <div class="jdr-badge jdr-badge-info" v-if="completedCount > 0">
              <i class="fas fa-flag-checkered"></i>
              {{ completedCount }} terminé{{ completedCount > 1 ? 's' : '' }}
            </div>
          </div>
        </div>
        
        <div class="header-actions jdr-flex jdr-gap-2">
          <div class="filter-group">
            <label for="statusFilter" class="jdr-form-label">Statut :</label>
            <select 
              id="statusFilter" 
              v-model="statusFilter" 
              class="jdr-form-control jdr-form-select"
            >
              <option value="all">Tous</option>
              <option value="available">Disponibles</option>
              <option value="active">En cours</option>
              <option value="completed">Terminés</option>
            </select>
          </div>
          
          <button @click="loadScenarios" class="jdr-btn jdr-btn-outline jdr-btn-sm">
            <i class="fas fa-sync-alt"></i>
            Actualiser
          </button>
        </div>
      </div>

      <!-- Grille de scénarios -->
      <div class="scenarios-grid">
        <div 
          v-for="scenario in filteredScenarios" 
          :key="scenario.name"
          class="jdr-card jdr-card-scenario scenario-card jdr-animate-slideIn"
          :class="getScenarioCardClass(scenario)"
        >
          <!-- En-tête du scénario -->
          <div class="jdr-card-header">
            <div class="scenario-header">
              <div class="scenario-icon">
                <i class="fas fa-scroll fa-2x"></i>
              </div>
              <div class="scenario-title-area">
                <h3 class="jdr-card-title">{{ formatScenarioName(scenario.name) }}</h3>
                <div class="scenario-meta">
                  <div class="jdr-badge" :class="getStatusBadgeClass(scenario.status)">
                    <i :class="getStatusIcon(scenario.status)"></i>
                    {{ getStatusLabel(scenario.status) }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Corps du scénario -->
          <div class="jdr-card-body">
            <div class="scenario-description">
              <p>{{ getScenarioDescription(scenario.name) }}</p>
            </div>
            
            <!-- Informations de session active -->
            <div v-if="scenario.session_id" class="active-session-info">
              <h4 class="session-title">
                <i class="fas fa-gamepad"></i>
                Session Active
              </h4>
              <div class="session-details">
                <div class="session-item">
                  <span class="session-label">Personnage :</span>
                  <span class="session-value">{{ scenario.character_name || 'Inconnu' }}</span>
                </div>
                <div class="session-item">
                  <span class="session-label">Session :</span>
                  <span class="session-value session-id">{{ scenario.session_id.substring(0, 8) }}...</span>
                </div>
              </div>
            </div>

            <!-- Aperçu du contenu -->
            <div v-if="scenarioContents[scenario.name]" class="scenario-preview">
              <h4 class="preview-title">
                <i class="fas fa-eye"></i>
                Aperçu
              </h4>
              <div class="preview-content">
                {{ getPreviewText(scenarioContents[scenario.name]) }}
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="jdr-card-footer">
            <button 
              @click="previewScenario(scenario)"
              class="jdr-btn jdr-btn-outline jdr-btn-sm"
              :disabled="loadingPreviews.has(scenario.name)"
            >
              <i v-if="loadingPreviews.has(scenario.name)" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-book-open"></i>
              {{ scenarioContents[scenario.name] ? 'Voir plus' : 'Lire' }}
            </button>
            
            <router-link 
              v-if="scenario.session_id"
              :to="{ name: 'jeu', params: { sessionId: scenario.session_id } }"
              class="jdr-btn jdr-btn-warning"
            >
              <i class="fas fa-play"></i>
              Reprendre
            </router-link>
            
            <router-link 
              v-else-if="scenario.status === 'available'"
              :to="{ name: 'nouveau-scenario', query: { scenarioName: scenario.name } }"
              class="jdr-btn jdr-btn-primary"
            >
              <i class="fas fa-rocket"></i>
              Commencer
            </router-link>
            
            <button 
              v-else 
              class="jdr-btn jdr-btn-outline" 
              disabled
            >
              <i class="fas fa-lock"></i>
              Indisponible
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Aucun scénario -->
    <div v-else class="jdr-card jdr-text-center jdr-animate-fadeIn">
      <div class="jdr-card-body">
        <i class="fas fa-book-dead fa-3x jdr-text-muted jdr-mb-4"></i>
        <h3 class="jdr-title jdr-title-sm">Aucun scénario disponible</h3>
        <p class="jdr-text-muted jdr-mb-4">
          Il n'y a actuellement aucun scénario dans la bibliothèque.
        </p>
        <button class="jdr-btn jdr-btn-primary jdr-btn-lg" disabled>
          <i class="fas fa-plus"></i>
          Ajouter un scénario
        </button>
        <p class="jdr-text-muted jdr-mt-4">
          <small>Fonctionnalité à venir</small>
        </p>
      </div>
    </div>

    <!-- Modal de prévisualisation -->
    <div v-if="showPreviewModal" class="jdr-modal-overlay show" @click="closePreviewModal">
      <div class="jdr-modal scenario-preview-modal" @click.stop>
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
          
          <div v-else class="full-preview-content">
            <div v-html="formattedPreviewContent"></div>
          </div>
        </div>
        
        <div class="jdr-modal-footer">
          <button @click="closePreviewModal" class="jdr-btn jdr-btn-outline">
            <i class="fas fa-times"></i>
            Fermer
          </button>
          
          <router-link 
            v-if="previewScenarioData && canStartScenario(previewScenarioData)"
            :to="{ name: 'nouveau-scenario', query: { scenarioName: previewScenarioData.name } }"
            class="jdr-btn jdr-btn-primary"
            @click="closePreviewModal"
          >
            <i class="fas fa-rocket"></i>
            Commencer ce scénario
          </router-link>
          
          <router-link 
            v-else-if="previewScenarioData && previewScenarioData.session_id"
            :to="{ name: 'jeu', params: { sessionId: previewScenarioData.session_id } }"
            class="jdr-btn jdr-btn-warning"
            @click="closePreviewModal"
          >
            <i class="fas fa-play"></i>
            Reprendre la session
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import JdrApiService, { type ScenarioStatus } from '@/core/api';

// État réactif
const loading = ref(true);
const error = ref<string | null>(null);
const scenarios = ref<ScenarioStatus[]>([]);
const statusFilter = ref<string>('all');

// Contenu des scénarios
const scenarioContents = ref<Record<string, string>>({});
const loadingPreviews = ref(new Set<string>());

// Modal de prévisualisation
const showPreviewModal = ref(false);
const loadingPreviewContent = ref(false);
const previewError = ref<string | null>(null);
const previewScenarioData = ref<ScenarioStatus | null>(null);
const previewScenarioTitle = ref('');
const previewContent = ref('');

// Descriptions de scénarios (fallback)
const scenarioDescriptions: Record<string, string> = {
  'Les_Pierres_du_Passe.md': 'Une mystérieuse quête dans les terres anciennes où des pierres runiques révèlent les secrets du passé. Explorez des ruines oubliées et découvrez des pouvoirs ancestraux.',
  'La_Menace_du_Nord.md': 'Des créatures sombres émergent des terres glacées du Nord, menaçant les royaumes paisibles. Unissez-vous pour repousser cette menace ancestrale.',
  'Les_Secrets_de_la_Foret_Noire.md': 'Au cœur de la Forêt Noire se cachent des mystères que peu d\'aventuriers osent affronter. Découvrez les secrets cachés dans ses profondeurs.',
  'default': 'Une aventure épique vous attend dans les Terres du Milieu. Préparez-vous à vivre des moments légendaires dans un monde riche en mystères et en dangers.'
};

// Computed properties
const filteredScenarios = computed(() => {
  if (statusFilter.value === 'all') {
    return scenarios.value;
  }
  return scenarios.value.filter(scenario => scenario.status === statusFilter.value);
});

const availableCount = computed(() => {
  return scenarios.value.filter(s => s.status === 'available' || !s.session_id).length;
});

const activeCount = computed(() => {
  return scenarios.value.filter(s => s.status === 'active' && s.session_id).length;
});

const completedCount = computed(() => {
  return scenarios.value.filter(s => s.status === 'completed').length;
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
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(.+)$/gim, '<p>$1</p>');
});

// Chargement des scénarios
const loadScenarios = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    const scenariosData = await JdrApiService.getScenarios();
    scenarios.value = scenariosData;
    
    // Préchargement des aperçus pour les scénarios disponibles
    const availableScenarios = scenariosData.filter(s => s.status === 'available' || !s.session_id);
    for (const scenario of availableScenarios.slice(0, 3)) { // Limite aux 3 premiers
      loadScenarioPreview(scenario.name);
    }
  } catch (err) {
    console.error('Erreur lors du chargement des scénarios:', err);
    error.value = err instanceof Error ? err.message : 'Erreur de connexion au serveur';
  } finally {
    loading.value = false;
  }
};

// Prévisualisation des scénarios
const loadScenarioPreview = async (scenarioName: string) => {
  if (scenarioContents.value[scenarioName] || loadingPreviews.value.has(scenarioName)) {
    return;
  }
  
  try {
    loadingPreviews.value.add(scenarioName);
    
    const content = await JdrApiService.getScenarioDetails(scenarioName);
    scenarioContents.value[scenarioName] = content;
  } catch (err) {
    console.warn(`Erreur lors du chargement de l'aperçu pour ${scenarioName}:`, err);
  } finally {
    loadingPreviews.value.delete(scenarioName);
  }
};

const previewScenario = async (scenario: ScenarioStatus) => {
  try {
    previewScenarioData.value = scenario;
    previewScenarioTitle.value = formatScenarioName(scenario.name);
    showPreviewModal.value = true;
    loadingPreviewContent.value = true;
    previewError.value = null;
    
    if (scenarioContents.value[scenario.name]) {
      previewContent.value = scenarioContents.value[scenario.name];
      loadingPreviewContent.value = false;
    } else {
      const content = await JdrApiService.getScenarioDetails(scenario.name);
      previewContent.value = content;
      scenarioContents.value[scenario.name] = content;
    }
  } catch (err) {
    console.error('Erreur lors du chargement de la prévisualisation:', err);
    previewError.value = err instanceof Error ? err.message : 'Erreur de chargement';
  } finally {
    loadingPreviewContent.value = false;
  }
};

const closePreviewModal = () => {
  showPreviewModal.value = false;
  previewScenarioData.value = null;
  previewContent.value = '';
  previewError.value = null;
};

// Utilitaires
const formatScenarioName = (name: string) => {
  return JdrApiService.formatScenarioName(name);
};

const getScenarioDescription = (name: string) => {
  return scenarioDescriptions[name] || scenarioDescriptions.default;
};

const getPreviewText = (content: string) => {
  if (!content) return '';
  
  // Extraire le premier paragraphe du contenu
  const firstParagraph = content
    .replace(/^#.*$/gm, '') // Supprimer les titres
    .replace(/\*\*/g, '') // Supprimer le gras
    .replace(/\*/g, '') // Supprimer l'italique
    .split('\n\n')[0] // Prendre le premier paragraphe
    .trim();
  
  return firstParagraph.length > 150 
    ? firstParagraph.substring(0, 150) + '...' 
    : firstParagraph;
};

const getScenarioCardClass = (scenario: ScenarioStatus) => {
  const classes = [];
  
  if (scenario.status === 'active') {
    classes.push('scenario-active');
  } else if (scenario.status === 'completed') {
    classes.push('scenario-completed');
  }
  
  return classes.join(' ');
};

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'available': return 'jdr-badge-success';
    case 'active': return 'jdr-badge-warning';
    case 'completed': return 'jdr-badge-info';
    default: return 'jdr-badge-info';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'available': return 'fas fa-check';
    case 'active': return 'fas fa-play';
    case 'completed': return 'fas fa-flag-checkered';
    default: return 'fas fa-question';
  }
};

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'available': return 'Disponible';
    case 'active': return 'En cours';
    case 'completed': return 'Terminé';
    default: return 'Inconnu';
  }
};

const canStartScenario = (scenario: ScenarioStatus) => {
  return scenario.status === 'available' && !scenario.session_id;
};

// Montage du composant
onMounted(() => {
  loadScenarios();
});
</script>

<style scoped>
.scenarios-header {
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-info {
  flex: 1;
  min-width: 200px;
}

.status-badges {
  flex-wrap: wrap;
}

.header-actions {
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 120px;
}

.filter-group label {
  font-size: 0.8rem;
  margin-bottom: 0;
}

.filter-group select {
  padding: 0.5rem;
}

.scenarios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.scenario-card {
  transition: all 0.3s ease;
  height: fit-content;
}

.scenario-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--jdr-shadow-large);
}

.scenario-card.scenario-active {
  border-color: var(--jdr-warning);
  box-shadow: var(--jdr-shadow-medium), 0 0 15px rgba(255, 140, 0, 0.3);
}

.scenario-card.scenario-completed {
  opacity: 0.8;
  border-color: var(--jdr-info);
}

.scenario-header {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.scenario-icon {
  color: var(--jdr-accent);
  opacity: 0.8;
  flex-shrink: 0;
}

.scenario-title-area {
  flex: 1;
}

.scenario-meta {
  margin-top: 0.5rem;
}

.scenario-description {
  margin-bottom: 1.5rem;
}

.scenario-description p {
  color: var(--jdr-text-secondary);
  line-height: 1.6;
  margin: 0;
  font-style: italic;
}

.active-session-info {
  background: var(--jdr-bg-primary);
  border: 1px solid var(--jdr-warning);
  border-radius: var(--jdr-border-radius);
  padding: 1rem;
  margin-bottom: 1rem;
}

.session-title {
  font-family: var(--jdr-font-fantasy);
  color: var(--jdr-warning);
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.75rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.session-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.session-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-label {
  color: var(--jdr-text-muted);
  font-weight: 500;
}

.session-value {
  color: var(--jdr-text-primary);
  font-weight: 600;
}

.session-id {
  font-family: monospace;
  font-size: 0.9rem;
  background: var(--jdr-bg-tertiary);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}

.scenario-preview {
  background: var(--jdr-bg-primary);
  border: 1px solid var(--jdr-border-color);
  border-radius: var(--jdr-border-radius);
  padding: 1rem;
}

.preview-title {
  font-family: var(--jdr-font-fantasy);
  color: var(--jdr-accent);
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.75rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preview-content {
  color: var(--jdr-text-secondary);
  line-height: 1.5;
  font-size: 0.9rem;
}

/* Modal de prévisualisation */
.scenario-preview-modal {
  max-width: none;
  width: 95%;
  max-height: 90vh;
}

.full-preview-content {
  max-height: 500px;
  overflow-y: auto;
  line-height: 1.6;
  color: var(--jdr-text-primary);
}

.full-preview-content h1,
.full-preview-content h2,
.full-preview-content h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.full-preview-content h1:first-child,
.full-preview-content h2:first-child,
.full-preview-content h3:first-child {
  margin-top: 0;
}

.full-preview-content p {
  margin-bottom: 1rem;
}

.full-preview-content strong {
  color: var(--jdr-secondary);
}

.full-preview-content em {
  color: var(--jdr-accent);
}

.full-preview-content code {
  background: var(--jdr-bg-tertiary);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
  color: var(--jdr-secondary);
}

/* Scrollbar personnalisée */
.full-preview-content::-webkit-scrollbar {
  width: 8px;
}

.full-preview-content::-webkit-scrollbar-track {
  background: var(--jdr-bg-tertiary);
  border-radius: 4px;
}

.full-preview-content::-webkit-scrollbar-thumb {
  background: var(--jdr-border-color);
  border-radius: 4px;
}

.full-preview-content::-webkit-scrollbar-thumb:hover {
  background: var(--jdr-secondary);
}

/* Responsive design */
@media (max-width: 768px) {
  .scenarios-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .scenarios-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .scenario-header {
    flex-direction: column;
    text-align: center;
    gap: 0.75rem;
  }
  
  .session-item {
    flex-direction: column;
    gap: 0.25rem;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .status-badges {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .filter-group {
    min-width: auto;
    width: 100%;
  }
  
  .header-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
}
</style>
