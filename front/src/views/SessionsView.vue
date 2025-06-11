<template>
  <div class="jdr-container jdr-p-4">
    <!-- En-tête de la page -->
    <div class="jdr-text-center jdr-mb-4">
      <h1 class="jdr-title jdr-title-lg">Sessions en Cours</h1>
      <p class="jdr-subtitle">Reprendre une aventure ou observer les parties actives</p>
    </div>

    <!-- Indicateur de chargement -->
    <div v-if="loading" class="jdr-text-center jdr-p-4">
      <div class="jdr-animate-pulse">
        <i class="fas fa-dice-d20 fa-3x jdr-text-accent"></i>
        <p class="jdr-mt-4">Chargement des sessions...</p>
      </div>
    </div>

    <!-- Message d'erreur -->
    <div v-else-if="error" class="jdr-card jdr-card-highlight" style="border-color: var(--jdr-danger);">
      <div class="jdr-card-body jdr-text-center">
        <i class="fas fa-exclamation-triangle fa-2x" style="color: var(--jdr-danger);"></i>
        <h3 class="jdr-title jdr-title-sm jdr-mt-4">Erreur de connexion</h3>
        <p class="jdr-text-muted">{{ error }}</p>
        <button @click="loadSessions" class="jdr-btn jdr-btn-primary jdr-mt-4">
          <i class="fas fa-redo"></i>
          Réessayer
        </button>
      </div>
    </div>

    <!-- Liste des sessions -->
    <div v-else-if="sessions.length > 0" class="jdr-animate-fadeIn">
      <!-- Statistiques -->
      <div class="jdr-flex jdr-justify-between jdr-items-center jdr-mb-4 jdr-gap-4">
        <div class="jdr-badge jdr-badge-info">
          <i class="fas fa-users"></i>
          {{ sessions.length }} session{{ sessions.length > 1 ? 's' : '' }} active{{ sessions.length > 1 ? 's' : '' }}
        </div>
        
        <button @click="loadSessions" class="jdr-btn jdr-btn-outline jdr-btn-sm">
          <i class="fas fa-sync-alt"></i>
          Actualiser
        </button>
      </div>

      <!-- Grille de sessions -->
      <div class="sessions-grid">
        <div 
          v-for="session in sessions" 
          :key="session.session_id"
          class="jdr-card jdr-card-scenario jdr-animate-slideIn session-card"
          :class="{ 'jdr-card-highlight': session.status === 'active' }"
        >
          <!-- En-tête de session -->
          <div class="jdr-card-header">
            <div class="jdr-flex jdr-justify-between jdr-items-center">
              <h3 class="jdr-card-title">
                <i class="fas fa-scroll"></i>
                {{ formatScenarioName(session.scenario_name) }}
              </h3>
              <div class="jdr-badge" :class="getStatusBadgeClass(session.status)">
                <i :class="getStatusIcon(session.status)"></i>
                {{ getStatusLabel(session.status) }}
              </div>
            </div>
          </div>

          <!-- Corps de session -->
          <div class="jdr-card-body">
            <!-- Informations du personnage -->
            <div class="session-info">
              <div class="info-item">
                <i class="fas fa-user-shield jdr-text-accent"></i>
                <span class="info-label">Personnage :</span>
                <span class="info-value">{{ session.character_name }}</span>
              </div>
              
              <div class="info-item">
                <i class="fas fa-clock jdr-text-muted"></i>
                <span class="info-label">Dernière activité :</span>
                <span class="info-value">{{ formatLastActivity(session.last_activity) }}</span>
              </div>
              
              <div class="info-item">
                <i class="fas fa-fingerprint jdr-text-muted"></i>
                <span class="info-label">Session ID :</span>
                <span class="info-value session-id">{{ session.session_id.substring(0, 8) }}...</span>
              </div>
            </div>

            <!-- Aperçu de l'historique (si disponible) -->
            <div v-if="sessionHistories[session.session_id]" class="session-preview jdr-mt-4">
              <h4 class="preview-title">
                <i class="fas fa-history"></i>
                Dernier échange
              </h4>
              <div class="preview-content">
                {{ getLastMessage(sessionHistories[session.session_id]) }}
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="jdr-card-footer">
            <button 
              @click="viewHistory(session)"
              class="jdr-btn jdr-btn-outline jdr-btn-sm"
              title="Voir l'historique complet"
            >
              <i class="fas fa-book-open"></i>
              Historique
            </button>
            
            <button 
              @click="resumeSession(session)"
              class="jdr-btn jdr-btn-primary"
              :disabled="session.status !== 'active'"
            >
              <i class="fas fa-play"></i>
              {{ session.status === 'active' ? 'Reprendre' : 'Indisponible' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Aucune session trouvée -->
    <div v-else class="jdr-card jdr-text-center jdr-animate-fadeIn">
      <div class="jdr-card-body">
        <i class="fas fa-dragon fa-3x jdr-text-muted jdr-mb-4"></i>
        <h3 class="jdr-title jdr-title-sm">Aucune session en cours</h3>
        <p class="jdr-text-muted jdr-mb-4">
          Il n'y a actuellement aucune aventure active. Commencez une nouvelle quête !
        </p>
        <router-link to="/nouveau-scenario" class="jdr-btn jdr-btn-primary jdr-btn-lg">
          <i class="fas fa-plus"></i>
          Commencer une aventure
        </router-link>
      </div>
    </div>

    <!-- Modal d'historique -->
    <div v-if="showHistoryModal" class="jdr-modal-overlay show" @click="closeHistoryModal">
      <div class="jdr-modal" @click.stop>
        <div class="jdr-modal-header">
          <h2 class="jdr-modal-title">
            <i class="fas fa-scroll"></i>
            Historique - {{ selectedSession?.scenario_name }}
          </h2>
          <button @click="closeHistoryModal" class="jdr-modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="jdr-modal-body">
          <div v-if="loadingHistory" class="jdr-text-center jdr-p-4">
            <div class="jdr-animate-pulse">
              <i class="fas fa-spinner fa-spin fa-2x jdr-text-accent"></i>
              <p class="jdr-mt-4">Chargement de l'historique...</p>
            </div>
          </div>
          
          <div v-else-if="historyError" class="jdr-text-center jdr-p-4">
            <i class="fas fa-exclamation-triangle fa-2x" style="color: var(--jdr-danger);"></i>
            <p class="jdr-mt-4">{{ historyError }}</p>
          </div>
          
          <div v-else-if="currentHistory.length > 0" class="history-container">
            <div 
              v-for="(message, index) in currentHistory" 
              :key="index"
              class="jdr-message"
              :class="message.role || 'assistant'"
            >
              <div class="jdr-message-author">
                <i :class="getMessageIcon(message.role)"></i>
                {{ getMessageAuthor(message.role) }}
              </div>
              <div class="jdr-message-content">
                {{ formatMessageContent(message) }}
              </div>
              <div class="jdr-message-time">
                {{ formatMessageTime(message.timestamp) }}
              </div>
            </div>
          </div>
          
          <div v-else class="jdr-text-center jdr-p-4">
            <i class="fas fa-book-open fa-2x jdr-text-muted"></i>
            <p class="jdr-mt-4 jdr-text-muted">Aucun historique disponible</p>
          </div>
        </div>
        
        <div class="jdr-modal-footer">
          <button @click="closeHistoryModal" class="jdr-btn jdr-btn-outline">
            <i class="fas fa-times"></i>
            Fermer
          </button>
          
          <button 
            v-if="selectedSession" 
            @click="resumeFromHistory" 
            class="jdr-btn jdr-btn-primary"
          >
            <i class="fas fa-play"></i>
            Reprendre la session
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import JdrApiService, { type GameSession } from '@/core/api';

const router = useRouter();

// État réactif
const loading = ref(true);
const error = ref<string | null>(null);
const sessions = ref<GameSession[]>([]);
const sessionHistories = ref<Record<string, any[]>>({});

// Modal d'historique
const showHistoryModal = ref(false);
const selectedSession = ref<GameSession | null>(null);
const currentHistory = ref<any[]>([]);
const loadingHistory = ref(false);
const historyError = ref<string | null>(null);

// Chargement des sessions
const loadSessions = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    // Récupération des sessions actives
    const activeSessions = await JdrApiService.getActiveSessions();
    sessions.value = activeSessions;
    
    // Préchargement de l'historique récent pour l'aperçu
    for (const session of activeSessions) {
      try {
        const history = await JdrApiService.getScenarioHistory(session.session_id);
        sessionHistories.value[session.session_id] = history.slice(-3); // Derniers 3 messages
      } catch (err) {
        console.warn(`Erreur lors du chargement de l'historique pour la session ${session.session_id}:`, err);
      }
    }
  } catch (err) {
    console.error('Erreur lors du chargement des sessions:', err);
    error.value = err instanceof Error ? err.message : 'Erreur de connexion au serveur';
  } finally {
    loading.value = false;
  }
};

// Actions sur les sessions
const resumeSession = (session: GameSession) => {
  // Navigation vers la page de jeu avec l'ID de session
  router.push({
    name: 'jeu',
    params: { sessionId: session.session_id }
  });
};

const viewHistory = async (session: GameSession) => {
  selectedSession.value = session;
  showHistoryModal.value = true;
  loadingHistory.value = true;
  historyError.value = null;
  
  try {
    const history = await JdrApiService.getScenarioHistory(session.session_id);
    currentHistory.value = history;
  } catch (err) {
    console.error('Erreur lors du chargement de l\'historique:', err);
    historyError.value = err instanceof Error ? err.message : 'Erreur de chargement';
  } finally {
    loadingHistory.value = false;
  }
};

const closeHistoryModal = () => {
  showHistoryModal.value = false;
  selectedSession.value = null;
  currentHistory.value = [];
  historyError.value = null;
};

const resumeFromHistory = () => {
  if (selectedSession.value) {
    resumeSession(selectedSession.value);
  }
};

// Utilitaires de formatage
const formatScenarioName = (name: string) => {
  return JdrApiService.formatScenarioName(name);
};

const formatLastActivity = (timestamp: string) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 1) return 'À l\'instant';
  if (diffMins < 60) return `Il y a ${diffMins} min`;
  if (diffHours < 24) return `Il y a ${diffHours}h`;
  if (diffDays < 7) return `Il y a ${diffDays}j`;
  
  return date.toLocaleDateString('fr-FR');
};

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'active': return 'jdr-badge-success';
    case 'paused': return 'jdr-badge-warning';
    case 'completed': return 'jdr-badge-info';
    default: return 'jdr-badge-info';
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'active': return 'fas fa-play';
    case 'paused': return 'fas fa-pause';
    case 'completed': return 'fas fa-check';
    default: return 'fas fa-question';
  }
};

const getStatusLabel = (status: string) => {
  switch (status) {
    case 'active': return 'Active';
    case 'paused': return 'En pause';
    case 'completed': return 'Terminée';
    default: return 'Inconnue';
  }
};

const getLastMessage = (history: any[]) => {
  if (!history || history.length === 0) return 'Aucun message';
  
  const lastMessage = history[history.length - 1];
  const content = formatMessageContent(lastMessage);
  
  return content.length > 100 ? content.substring(0, 100) + '...' : content;
};

const getMessageIcon = (role: string) => {
  switch (role) {
    case 'user': return 'fas fa-user';
    case 'assistant': return 'fas fa-hat-wizard';
    case 'system': return 'fas fa-cog';
    default: return 'fas fa-comment';
  }
};

const getMessageAuthor = (role: string) => {
  switch (role) {
    case 'user': return 'Joueur';
    case 'assistant': return 'Maître du Jeu';
    case 'system': return 'Système';
    default: return 'Message';
  }
};

const formatMessageContent = (message: any) => {
  if (typeof message === 'string') return message;
  if (message.content) return message.content;
  if (message.parts && message.parts.length > 0) {
    return message.parts.map((part: any) => part.content || '').join(' ');
  }
  return 'Message vide';
};

const formatMessageTime = (timestamp: string) => {
  if (!timestamp) return '';
  
  const date = new Date(timestamp);
  return date.toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Montage du composant
onMounted(() => {
  loadSessions();
});
</script>

<style scoped>
.sessions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.session-card {
  transition: all 0.3s ease;
  height: fit-content;
}

.session-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--jdr-shadow-large);
}

.session-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.info-label {
  color: var(--jdr-text-muted);
  min-width: 120px;
}

.info-value {
  color: var(--jdr-text-primary);
  font-weight: 500;
}

.session-id {
  font-family: monospace;
  font-size: 0.8rem;
  background: var(--jdr-bg-tertiary);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
}

.session-preview {
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
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preview-content {
  color: var(--jdr-text-secondary);
  font-style: italic;
  line-height: 1.4;
  font-size: 0.9rem;
}

.history-container {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.history-container::-webkit-scrollbar {
  width: 6px;
}

.history-container::-webkit-scrollbar-track {
  background: var(--jdr-bg-tertiary);
  border-radius: 3px;
}

.history-container::-webkit-scrollbar-thumb {
  background: var(--jdr-border-color);
  border-radius: 3px;
}

.history-container::-webkit-scrollbar-thumb:hover {
  background: var(--jdr-secondary);
}

@media (max-width: 768px) {
  .sessions-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .info-label {
    min-width: auto;
    font-weight: 600;
  }
}
</style>
