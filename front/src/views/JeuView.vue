<template>
  <!-- Indicateur de chargement initial -->
  <div v-if="loadingSession" class="loading-screen">
    <div class="jdr-animate-pulse">
      <font-awesome-icon icon="dice-d20" size="3x" class="jdr-text-accent" />
      <p class="jdr-mt-4">Chargement de la session...</p>
    </div>
  </div>

  <!-- Message d'erreur -->
  <div v-else-if="sessionError" class="error-screen">
    <CardComponent title="Erreur de session" class="jdr-card-highlight" style="border-color: var(--jdr-danger);">
      <div class="jdr-text-center">
        <font-awesome-icon icon="exclamation-triangle" size="2x" style="color: var(--jdr-danger);" />
        <p class="jdr-text-muted jdr-mt-4">{{ sessionError }}</p>
        <button @click="loadSession" class="jdr-btn jdr-btn-primary jdr-mt-4">
          <font-awesome-icon icon="redo" />
          Réessayer
        </button>
      </div>
    </CardComponent>
  </div>

  <!-- Interface de jeu principale -->
  <div v-else-if="session" class="game-container"><!-- Header fixe -->
      <header class="game-header">
        <div class="session-info">
          <h1 class="session-title">{{ formatScenarioName(session.scenario_name) }}</h1>
          <div class="session-meta">
            <div class="character-badge">
              <font-awesome-icon icon="user" />
              {{ session.character_name }}
            </div>
            <div class="session-badge">
              <font-awesome-icon icon="gamepad" />
              {{ session.session_id.substring(0, 8) }}...
            </div>
          </div>
        </div>
        
        <div class="header-actions">
          <button 
            @click="exportHistory"
            class="export-btn"
            :disabled="history.length === 0"
            title="Exporter l'historique"
          >
            <font-awesome-icon icon="download" />
          </button>
          
          <button 
            @click="showDebugMode = !showDebugMode"
            :class="['debug-btn', { active: showDebugMode }]"
            title="Mode debug"
          >
            <font-awesome-icon icon="bug" />
          </button>
          
          <router-link to="/sessions" class="back-btn">
            <font-awesome-icon icon="arrow-left" />
            Retour
          </router-link>
        </div>
      </header><!-- Contenu principal -->
      <main class="game-main">        <!-- Zone de chat (3/4) -->
        <section class="chat-section">
          <div class="chat-history" ref="chatHistory">
            <div v-if="loadingHistory" class="loading-messages">
              <font-awesome-icon icon="spinner" spin class="jdr-text-accent" />
              <p>Chargement de l'historique...</p>
            </div>
            
            <div v-else-if="history.length === 0" class="empty-chat">
              <font-awesome-icon icon="scroll" size="2x" class="jdr-text-muted" />
              <p>L'aventure va commencer...</p>
            </div>
            
            <ChatMessage 
              v-else 
              :messages="history" 
              :show-debug-info="showDebugMode" 
              @delete-message="handleDeleteMessage"
            />
          </div>

          <!-- Zone de saisie dans la section chat -->
          <div class="input-container">
            <div class="input-group">
              <textarea
                v-model="currentMessage"
                @keydown.enter.exact.prevent="sendMessage"
                @keydown.enter.shift.exact="addNewLine"
                placeholder="Tapez votre action ou votre dialogue... (Entrée pour envoyer, Maj+Entrée pour une nouvelle ligne)"
                class="message-input"
                :disabled="sendingMessage"
                rows="2"
              ></textarea>
              
              <button 
                @click="sendMessage"
                class="send-button"
                :disabled="!canSendMessage"
              >
                <font-awesome-icon v-if="sendingMessage" icon="spinner" spin />
                <font-awesome-icon v-else icon="paper-plane" />
              </button>
            </div>
            
            <div class="input-help">
              <small>Décrivez vos actions, dialogues ou intentions. Le Maître du Jeu vous guidera dans l'aventure.</small>
            </div>
          </div>
        </section>

        <!-- Panneau latéral (1/4) -->
        <aside class="info-panel">
          <div class="panel-scroll">
            <!-- Informations de session -->
            <div class="info-card">
              <h3>Session Active</h3>
              <div class="session-details">
                <div class="detail-item">
                  <span class="detail-label">
                    <font-awesome-icon icon="scroll" />
                    Scénario
                  </span>
                  <span class="detail-value">{{ formatScenarioName(session.scenario_name) }}</span>
                </div>
                
                <div class="detail-item">
                  <span class="detail-label">
                    <font-awesome-icon icon="user-shield" />
                    Personnage
                  </span>
                  <span class="detail-value">{{ session.character_name }}</span>
                </div>
                
                <div class="detail-item">
                  <span class="detail-label">
                    <font-awesome-icon icon="clock" />
                    Dernière activité
                  </span>
                  <span class="detail-value">{{ formatTimestamp(session.last_activity) }}</span>
                </div>
              </div>
            </div>

            <!-- Aide rapide -->
            <div class="info-card">
              <h3>Comment jouer</h3>
              <ul class="help-list">
                <li>
                  <font-awesome-icon icon="comment" class="help-icon" />
                  Décrivez vos actions en langage naturel
                </li>
                <li>
                  <font-awesome-icon icon="dice" class="help-icon" />
                  Le MJ gère automatiquement les jets de dés
                </li>
                <li>
                  <font-awesome-icon icon="map" class="help-icon" />
                  Explorez et interagissez avec l'environnement
                </li>
                <li>
                  <font-awesome-icon icon="users" class="help-icon" />
                  Dialoguez avec les PNJ rencontrés
                </li>
              </ul>
            </div>          </div>
        </aside>
      </main>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import JdrApiService, { type GameSession } from '@/core/api';
import type { ConversationMessage, PlayScenarioRequest } from '@/core/interfaces';
import CardComponent from '@/components/CardComponent.vue';
import ChatMessage from '@/components/ChatMessage.vue';

// Route et router
const route = useRoute();
const router = useRouter();

// Données réactives
const session = ref<GameSession | null>(null);
const history = ref<ConversationMessage[]>([]);
const currentMessage = ref('');
const showDebugMode = ref(false);

// États de chargement
const loadingSession = ref(true);
const loadingHistory = ref(false);
const sendingMessage = ref(false);

// États d'erreur
const sessionError = ref<string | null>(null);

// Références DOM
const chatHistory = ref<HTMLElement | null>(null);

// Propriétés calculées
const canSendMessage = computed(() => {
  return currentMessage.value.trim().length > 0 && !sendingMessage.value;
});

// Méthodes utilitaires
const formatScenarioName = (scenarioName: string): string => {
  return scenarioName.replace(/\.md$/, '').replace(/_/g, ' ');
};

const formatTimestamp = (timestamp: string): string => {
  if (!timestamp) return 'Inconnue';
  const date = new Date(timestamp);
  return date.toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Méthodes principales
const loadSession = async () => {
  try {
    loadingSession.value = true;
    sessionError.value = null;
    
    const sessionId = route.params.sessionId as string;
    if (!sessionId) {
      sessionError.value = 'ID de session manquant';
      return;
    }

    const sessionData = await JdrApiService.getSession(sessionId);
    if (!sessionData) {
      sessionError.value = 'Session introuvable';
      return;
    }

    session.value = sessionData;
    await loadHistory();
    
  } catch (error) {
    console.error('Erreur lors du chargement de la session:', error);
    sessionError.value = 'Erreur de connexion au serveur';
  } finally {
    loadingSession.value = false;
  }
};

const loadHistory = async () => {
  if (!session.value) return;

  try {
    loadingHistory.value = true;
    const historyData = await JdrApiService.getScenarioHistory(session.value.session_id);
    history.value = historyData || [];
    
    // Défiler vers le bas après chargement
    await nextTick();
    scrollToBottom();
    
  } catch (error) {
    console.error('Erreur lors du chargement de l\'historique:', error);
    // Ne pas afficher d'erreur critique, l'historique peut être vide
  } finally {
    loadingHistory.value = false;
  }
};

const sendMessage = async () => {
  if (!canSendMessage.value || !session.value) return;

  try {
    sendingMessage.value = true;
    
    const request: PlayScenarioRequest = {
      message: currentMessage.value.trim()
    };

    // Ajouter temporairement le message utilisateur à l'historique
    const userMessage: ConversationMessage = {
      parts: [{
        part_kind: 'user-prompt',
        content: request.message,
        timestamp: new Date().toISOString()
      }],
      kind: 'request',
      timestamp: new Date().toISOString()
    };
    
    history.value.push(userMessage);
    
    // Défiler et vider le champ
    await nextTick();
    scrollToBottom();
    currentMessage.value = '';

    // Envoyer au backend
    const response = await JdrApiService.playScenario(session.value.session_id, request);
    
    // Remplacer l'historique par la réponse complète du serveur
    history.value = response.response || [];
    
    await nextTick();
    scrollToBottom();
    
  } catch (error) {
    console.error('Erreur lors de l\'envoi du message:', error);
    // Retirer le message temporaire en cas d'erreur
    history.value.pop();
    
    // Ajouter un message d'erreur
    const errorMessage: ConversationMessage = {
      parts: [{
        part_kind: 'text',
        content: `Erreur lors de l'envoi du message: ${error instanceof Error ? error.message : 'Erreur inconnue'}`,
        timestamp: new Date().toISOString()
      }],
      kind: 'error',
      timestamp: new Date().toISOString()
    };
    
    history.value.push(errorMessage);
  } finally {
    sendingMessage.value = false;
  }
};

const addNewLine = () => {
  currentMessage.value += '\n';
};

const scrollToBottom = () => {
  if (chatHistory.value) {
    chatHistory.value.scrollTop = chatHistory.value.scrollHeight;
  }
};

const handleDeleteMessage = async (messageIndex: number) => {
  if (!session.value) return;

  try {
    console.log(`Suppression du message à l'index ${messageIndex} de la session ${session.value.session_id}`);
    
    // Appeler l'API de suppression
    await JdrApiService.deleteHistoryMessage(session.value.session_id, messageIndex);
    
    console.log('Message supprimé avec succès, rechargement de l\'historique...');
    
    // Recharger l'historique pour rafraîchir l'affichage
    await loadHistory();
    
  } catch (error) {
    console.error('Erreur lors de la suppression du message:', error);
    
    // Afficher une notification d'erreur à l'utilisateur
    const errorMessage = error instanceof Error ? error.message : 'Erreur inconnue lors de la suppression';
    alert(`Impossible de supprimer le message: ${errorMessage}`);
  }
};

const exportHistory = () => {
  if (history.value.length === 0) return;

  const exportData = {
    session: session.value,
    history: history.value,
    exportDate: new Date().toISOString()
  };

  const blob = new Blob([JSON.stringify(exportData, null, 2)], {
    type: 'application/json'
  });

  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `session-${session.value?.session_id.substring(0, 8)}-${new Date().toISOString().split('T')[0]}.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// Cycle de vie
onMounted(() => {
  loadSession();
});
</script>

<style scoped>
/* Écrans de chargement et d'erreur */
.loading-screen,
.error-screen {
  height: calc(100vh - var(--header-height, 88px));
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: var(--jdr-bg-secondary);
}

/* Container principal du jeu */
.game-container {
  height: calc(100vh - var(--header-height, 88px));
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--jdr-bg-secondary);
}

/* Header fixe */
.game-header {
  background: var(--jdr-bg-primary);
  border-bottom: 1px solid var(--jdr-border-color);
  z-index: 10;
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 100%;
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--jdr-text-primary);
  margin: 0 0 0.5rem 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-meta {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.character-badge,
.session-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: var(--jdr-accent-alpha);
  color: var(--jdr-accent);
  border-radius: var(--jdr-border-radius);
  font-size: 0.875rem;
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.debug-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  background: transparent;
  border: 1px solid var(--jdr-border-color);
  border-radius: var(--jdr-border-radius);
  color: var(--jdr-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.debug-btn:hover {
  background: var(--jdr-bg-secondary);
  color: var(--jdr-text-primary);
}

.debug-btn.active {
  background: var(--jdr-accent);
  color: white;
  border-color: var(--jdr-accent);
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--jdr-bg-secondary);
  color: var(--jdr-text-primary);
  text-decoration: none;
  border-radius: var(--jdr-border-radius);
  border: 1px solid var(--jdr-border-color);
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: var(--jdr-accent);
  color: white;
  border-color: var(--jdr-accent);
}

.export-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  background: transparent;
  border: 1px solid var(--jdr-border-color);
  border-radius: var(--jdr-border-radius);
  color: var(--jdr-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.export-btn:hover:not(:disabled) {
  background: var(--jdr-bg-secondary);
  color: var(--jdr-text-primary);
}

.export-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Contenu principal */
.game-main {
  flex: 1;
  display: flex;
  min-height: 0;
  overflow: hidden;
}

/* Section chat (3/4) */
.chat-section {
  flex: 3;
  background: var(--jdr-bg-primary);
  border-right: 1px solid var(--jdr-border-color);
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 1rem;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;  background: var(--jdr-bg-secondary);
  border-radius: var(--jdr-border-radius);
  min-height: 0;
  scroll-behavior: smooth;
  margin-bottom: 1rem;
}

.loading-messages,
.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 1rem;
  color: var(--jdr-text-muted);
}

/* Panneau latéral (1/4) */
.info-panel {
  flex: 1;
  background: var(--jdr-bg-primary);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.panel-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.info-card {
  background: var(--jdr-bg-secondary);
  border: 1px solid var(--jdr-border-color);
  border-radius: var(--jdr-border-radius);
  padding: 1rem;
}

.info-card h3 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--jdr-text-primary);
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--jdr-border-color);
}

.session-details {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--jdr-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detail-value {
  color: var(--jdr-text-primary);
  font-weight: 500;
  font-size: 0.875rem;
  word-break: break-word;
}

.help-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.help-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: var(--jdr-text-secondary);
  line-height: 1.4;
}

.help-icon {
  color: var(--jdr-accent);
  width: 16px;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

/* Zone de saisie dans la section chat */
.input-container {
  flex-shrink: 0;
  padding: 1rem;
  background: var(--jdr-bg-secondary);
  border-radius: var(--jdr-border-radius);
  border: 1px solid var(--jdr-border-color);
}

.input-group {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid var(--jdr-border-color);
  border-radius: var(--jdr-border-radius);
  background: var(--jdr-bg-primary);
  color: var(--jdr-text-primary);
  font-family: inherit;
  font-size: 0.9rem;
  line-height: 1.4;
  resize: none;
  min-height: 60px;
  max-height: 120px;
  transition: border-color 0.2s ease;
}

.message-input:focus {
  outline: none;
  border-color: var(--jdr-accent);
  box-shadow: 0 0 0 2px var(--jdr-accent-alpha);
}

.message-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  background: var(--jdr-accent);
  color: white;
  border: none;
  border-radius: var(--jdr-border-radius);
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background: var(--jdr-accent-dark, var(--jdr-accent));
  transform: translateY(-1px);
}

.send-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.input-help {
  margin-top: 0.5rem;
  text-align: center;
}

.input-help small {
  color: var(--jdr-text-muted);
  font-size: 0.75rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .chat-section {
    flex: 2;
  }
  
  .info-panel {
    flex: 1;
  }
}

@media (max-width: 768px) {
  .game-main {
    flex-direction: column;
  }
  
  .chat-section {
    flex: 1;
    border-right: none;
    border-bottom: 1px solid var(--jdr-border-color);
    min-height: 60vh;
  }
  
  .info-panel {
    flex: none;
    max-height: 200px;
    border-top: 1px solid var(--jdr-border-color);
    border-right: none;
  }
    .game-header {
    padding: 0.75rem 1rem;
    flex-direction: column;
    gap: 0.75rem;
    align-items: stretch;
  }
  
  .session-title {
    font-size: 1.25rem;
    white-space: normal;
  }
  
  .header-actions {
    justify-content: space-between;
  }
  
  .input-container {
    padding: 0.75rem 1rem;
  }
}

@media (max-height: 600px) {
  .chat-history {
    max-height: calc(100vh - 220px);
  }
  
  .info-panel {
    max-height: 120px;
  }
  
  .message-input {
    min-height: 40px;
    max-height: 80px;
  }
  
  .send-button {
    width: 2.5rem;
    height: 2.5rem;
  }
}

/* Animations */
.jdr-animate-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}
</style>
