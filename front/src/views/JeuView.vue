<template>
  <div class="jeu-container">
    <!-- En-tête de session -->
    <div class="session-header jdr-card">
      <div class="jdr-card-body">
        <div class="session-info jdr-flex jdr-justify-between jdr-items-center">
          <div class="session-details">
            <h1 class="jdr-title jdr-title-md">
              <i class="fas fa-scroll"></i>
              {{ sessionData?.scenario_name ? formatScenarioName(sessionData.scenario_name) : 'Session de Jeu' }}
            </h1>
            <div class="session-meta">
              <span class="meta-item">
                <i class="fas fa-user-shield jdr-text-accent"></i>
                {{ sessionData?.character_name || 'Personnage' }}
              </span>
              <span class="meta-item">
                <i class="fas fa-fingerprint jdr-text-muted"></i>
                Session: {{ sessionId.substring(0, 8) }}...
              </span>
            </div>
          </div>
          
          <div class="session-actions jdr-flex jdr-gap-2">
            <button @click="showSessionMenu = !showSessionMenu" class="jdr-btn jdr-btn-outline jdr-btn-sm">
              <i class="fas fa-cog"></i>
              Options
            </button>
            
            <router-link to="/sessions" class="jdr-btn jdr-btn-outline jdr-btn-sm">
              <i class="fas fa-arrow-left"></i>
              Retour
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Interface de jeu principale -->
    <div class="game-interface">
      <!-- Zone d'historique -->
      <div class="history-panel jdr-card">
        <div class="jdr-card-header">
          <h2 class="jdr-card-title">
            <i class="fas fa-book-open"></i>
            Historique de l'Aventure
          </h2>
          <button @click="refreshHistory" class="jdr-btn jdr-btn-outline jdr-btn-sm" :disabled="loadingHistory">
            <i class="fas fa-sync-alt" :class="{ 'fa-spin': loadingHistory }"></i>
          </button>
        </div>
        
        <div class="jdr-card-body history-content" ref="historyContainer">
          <!-- Messages de chargement -->
          <div v-if="loadingHistory && history.length === 0" class="loading-state">
            <i class="fas fa-spinner fa-spin jdr-text-accent"></i>
            <span>Chargement de l'historique...</span>
          </div>
          
          <!-- Messages d'erreur -->
          <div v-else-if="historyError" class="error-state">
            <i class="fas fa-exclamation-triangle jdr-text-danger"></i>
            <span>{{ historyError }}</span>
            <button @click="loadHistory" class="jdr-btn jdr-btn-primary jdr-btn-sm jdr-mt-4">
              Réessayer
            </button>
          </div>
          
          <!-- Liste des messages -->
          <div v-else-if="history.length > 0" class="messages-list">
            <div 
              v-for="(message, index) in history" 
              :key="index"
              class="jdr-message"
              :class="getMessageClass(message)"
            >
              <div class="jdr-message-author">
                <i :class="getMessageIcon(message)"></i>
                {{ getMessageAuthor(message) }}
              </div>
              <div class="jdr-message-content" v-html="formatMessageContent(message)">
              </div>
              <div class="jdr-message-time">
                {{ formatMessageTime(message.timestamp) }}
              </div>
            </div>
          </div>
          
          <!-- Historique vide -->
          <div v-else class="empty-state">
            <i class="fas fa-dragon fa-2x jdr-text-muted"></i>
            <p class="jdr-mt-4 jdr-text-muted">L'aventure commence maintenant...</p>
          </div>
        </div>
      </div>

      <!-- Zone de saisie -->
      <div class="input-panel jdr-card">
        <div class="jdr-card-header">
          <h3 class="jdr-card-title">
            <i class="fas fa-comment"></i>
            Votre Action
          </h3>
        </div>
        
        <div class="jdr-card-body">
          <form @submit.prevent="sendMessage" class="message-form">
            <div class="jdr-form-group">
              <textarea
                v-model="currentMessage"
                class="jdr-form-control jdr-form-textarea"
                placeholder="Décrivez votre action, posez une question au MJ, ou engagez le dialogue..."
                rows="4"
                :disabled="sendingMessage"
                @keydown.ctrl.enter="sendMessage"
              ></textarea>
            </div>
            
            <div class="form-actions jdr-flex jdr-justify-between jdr-items-center">
              <div class="input-help">
                <small class="jdr-text-muted">
                  <i class="fas fa-lightbulb"></i>
                  Astuce : Ctrl+Entrée pour envoyer rapidement
                </small>
              </div>
              
              <div class="action-buttons jdr-flex jdr-gap-2">
                <button 
                  type="button"
                  @click="rollDice"
                  class="jdr-btn jdr-btn-outline jdr-btn-sm"
                  title="Lancer un dé"
                >
                  <i class="fas fa-dice-d20"></i>
                  Dé
                </button>
                
                <button 
                  type="submit"
                  class="jdr-btn jdr-btn-primary"
                  :disabled="!currentMessage.trim() || sendingMessage"
                >
                  <i v-if="sendingMessage" class="fas fa-spinner fa-spin"></i>
                  <i v-else class="fas fa-paper-plane"></i>
                  {{ sendingMessage ? 'Envoi...' : 'Envoyer' }}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Menu d'options (dropdown) -->
    <div v-if="showSessionMenu" class="session-menu jdr-menu" v-click-outside="closeSessionMenu">
      <div class="jdr-menu-item" @click="saveSession">
        <i class="fas fa-save"></i>
        Sauvegarder la session
      </div>
      <div class="jdr-menu-divider"></div>
      <div class="jdr-menu-item" @click="exportHistory">
        <i class="fas fa-download"></i>
        Exporter l'historique
      </div>
      <div class="jdr-menu-item" @click="showSettings = true">
        <i class="fas fa-cog"></i>
        Paramètres
      </div>
      <div class="jdr-menu-divider"></div>
      <div class="jdr-menu-item" @click="pauseSession" style="color: var(--jdr-warning);">
        <i class="fas fa-pause"></i>
        Mettre en pause
      </div>
    </div>

    <!-- Modal de lancement de dé -->
    <div v-if="showDiceModal" class="jdr-modal-overlay show" @click="closeDiceModal">
      <div class="jdr-modal" @click.stop>
        <div class="jdr-modal-header">
          <h2 class="jdr-modal-title">
            <i class="fas fa-dice-d20"></i>
            Lancer un Dé
          </h2>
          <button @click="closeDiceModal" class="jdr-modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="jdr-modal-body">
          <div class="dice-interface">
            <div class="dice-selection">
              <h4>Type de dé :</h4>
              <div class="dice-types">
                <button 
                  v-for="die in diceTypes" 
                  :key="die.sides"
                  @click="selectedDie = die"
                  class="dice-button"
                  :class="{ active: selectedDie.sides === die.sides }"
                >
                  <i :class="die.icon"></i>
                  D{{ die.sides }}
                </button>
              </div>
            </div>
            
            <div class="dice-result" v-if="diceResult">
              <h4>Résultat :</h4>
              <div class="result-display">
                <span class="result-value">{{ diceResult.value }}</span>
                <span class="result-description">/ {{ diceResult.max }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="jdr-modal-footer">
          <button @click="closeDiceModal" class="jdr-btn jdr-btn-outline">
            <i class="fas fa-times"></i>
            Fermer
          </button>
          
          <button @click="performDiceRoll" class="jdr-btn jdr-btn-primary">
            <i class="fas fa-dice"></i>
            Lancer !
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import JdrApiService, { type GameSession } from '@/core/api';

const router = useRouter();
const route = useRoute();

// Props de la route
const sessionId = ref(route.params.sessionId as string);

// État de la session
const sessionData = ref<GameSession | null>(null);
const loadingSession = ref(true);
const sessionError = ref<string | null>(null);

// Historique des messages
const history = ref<any[]>([]);
const loadingHistory = ref(false);
const historyError = ref<string | null>(null);
const historyContainer = ref<HTMLElement>();

// Interface de messagerie
const currentMessage = ref('');
const sendingMessage = ref(false);

// Menu et modales
const showSessionMenu = ref(false);
const showSettings = ref(false);
const showDiceModal = ref(false);

// Système de dés
const diceTypes = [
  { sides: 4, icon: 'fas fa-dice-four' },
  { sides: 6, icon: 'fas fa-dice-six' },
  { sides: 8, icon: 'fas fa-dice' },
  { sides: 10, icon: 'fas fa-dice' },
  { sides: 12, icon: 'fas fa-dice' },
  { sides: 20, icon: 'fas fa-dice-d20' },
  { sides: 100, icon: 'fas fa-dice' }
];

const selectedDie = ref(diceTypes[5]); // D20 par défaut
const diceResult = ref<{ value: number; max: number } | null>(null);

// Auto-refresh de l'historique
let historyRefreshInterval: number | null = null;

// Chargement initial
onMounted(async () => {
  await loadSession();
  await loadHistory();
  startHistoryRefresh();
});

onUnmounted(() => {
  stopHistoryRefresh();
});

// Watchers
watch(() => route.params.sessionId, async (newSessionId) => {
  if (newSessionId && newSessionId !== sessionId.value) {
    sessionId.value = newSessionId as string;
    await loadSession();
    await loadHistory();
  }
});

// Chargement de la session
const loadSession = async () => {
  try {
    loadingSession.value = true;
    sessionError.value = null;
    
    const session = await JdrApiService.getSession(sessionId.value);
    
    if (!session) {
      throw new Error('Session introuvable');
    }
    
    sessionData.value = session;
  } catch (err) {
    console.error('Erreur lors du chargement de la session:', err);
    sessionError.value = err instanceof Error ? err.message : 'Erreur de chargement';
    
    // Redirection si session introuvable
    if (err instanceof Error && err.message.includes('introuvable')) {
      router.push('/sessions');
    }
  } finally {
    loadingSession.value = false;
  }
};

// Chargement de l'historique
const loadHistory = async () => {
  try {
    loadingHistory.value = true;
    historyError.value = null;
    
    const historyData = await JdrApiService.getScenarioHistory(sessionId.value);
    history.value = historyData;
    
    // Scroll vers le bas après chargement
    await nextTick();
    scrollToBottom();
  } catch (err) {
    console.error('Erreur lors du chargement de l\'historique:', err);
    historyError.value = err instanceof Error ? err.message : 'Erreur de chargement';
  } finally {
    loadingHistory.value = false;
  }
};

// Envoi de message
const sendMessage = async () => {
  if (!currentMessage.value.trim() || sendingMessage.value) return;
  
  try {
    sendingMessage.value = true;
    
    const response = await JdrApiService.playScenario(sessionId.value, {
      message: currentMessage.value.trim()
    });
    
    // Ajouter le message du joueur à l'historique
    history.value.push({
      role: 'user',
      content: currentMessage.value.trim(),
      timestamp: new Date().toISOString()
    });
    
    // Ajouter la réponse du MJ
    if (response.response) {
      history.value.push({
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        tool_calls: response.tool_calls
      });
    }
    
    // Réinitialiser le champ de saisie
    currentMessage.value = '';
    
    // Scroll vers le bas
    await nextTick();
    scrollToBottom();
    
  } catch (err) {
    console.error('Erreur lors de l\'envoi du message:', err);
    alert('Erreur lors de l\'envoi du message: ' + (err instanceof Error ? err.message : 'Erreur inconnue'));
  } finally {
    sendingMessage.value = false;
  }
};

// Utilitaires d'historique
const refreshHistory = () => {
  loadHistory();
};

const startHistoryRefresh = () => {
  // Rafraîchir l'historique toutes les 30 secondes
  historyRefreshInterval = window.setInterval(() => {
    if (!sendingMessage.value) {
      refreshHistory();
    }
  }, 30000);
};

const stopHistoryRefresh = () => {
  if (historyRefreshInterval) {
    clearInterval(historyRefreshInterval);
    historyRefreshInterval = null;
  }
};

const scrollToBottom = () => {
  if (historyContainer.value) {
    historyContainer.value.scrollTop = historyContainer.value.scrollHeight;
  }
};

// Système de dés
const rollDice = () => {
  showDiceModal.value = true;
  diceResult.value = null;
};

const performDiceRoll = () => {
  const result = Math.floor(Math.random() * selectedDie.value.sides) + 1;
  diceResult.value = {
    value: result,
    max: selectedDie.value.sides
  };
  
  // Ajouter le résultat à l'historique
  const diceMessage = `🎲 Lancement de dé D${selectedDie.value.sides}: **${result}**`;
  
  history.value.push({
    role: 'system',
    content: diceMessage,
    timestamp: new Date().toISOString(),
    type: 'dice_roll'
  });
  
  // Scroll vers le bas
  nextTick(() => scrollToBottom());
};

const closeDiceModal = () => {
  showDiceModal.value = false;
  diceResult.value = null;
};

// Actions de session
const closeSessionMenu = () => {
  showSessionMenu.value = false;
};

const saveSession = () => {
  console.log('Sauvegarde de la session...');
  closeSessionMenu();
  // TODO: Implémenter la sauvegarde
};

const exportHistory = () => {
  const historyText = history.value
    .map(msg => `[${formatMessageTime(msg.timestamp)}] ${getMessageAuthor(msg)}: ${formatMessageContent(msg)}`)
    .join('\n\n');
  
  const blob = new Blob([historyText], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = `session_${sessionId.value}_history.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  
  closeSessionMenu();
};

const pauseSession = () => {
  console.log('Mise en pause de la session...');
  closeSessionMenu();
  router.push('/sessions');
};

// Utilitaires de formatage
const formatScenarioName = (name: string) => {
  return JdrApiService.formatScenarioName(name);
};

const getMessageClass = (message: any) => {
  if (message.role) return message.role;
  if (message.type === 'dice_roll') return 'system';
  return 'assistant';
};

const getMessageIcon = (message: any) => {
  switch (message.role || message.type) {
    case 'user': return 'fas fa-user';
    case 'assistant': return 'fas fa-hat-wizard';
    case 'system': return 'fas fa-cog';
    case 'dice_roll': return 'fas fa-dice';
    default: return 'fas fa-comment';
  }
};

const getMessageAuthor = (message: any) => {
  switch (message.role || message.type) {
    case 'user': return 'Vous';
    case 'assistant': return 'Maître du Jeu';
    case 'system': return 'Système';
    case 'dice_roll': return 'Dé';
    default: return 'Message';
  }
};

const formatMessageContent = (message: any) => {
  let content = '';
  
  if (typeof message === 'string') {
    content = message;
  } else if (message.content) {
    content = message.content;
  } else if (message.parts && message.parts.length > 0) {
    content = message.parts.map((part: any) => part.content || '').join(' ');
  } else {
    content = 'Message vide';
  }
  
  // Conversion basique du Markdown
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>');
};

const formatMessageTime = (timestamp: string) => {
  if (!timestamp) return '';
  
  const date = new Date(timestamp);
  return date.toLocaleTimeString('fr-FR', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Directive pour fermer les menus
const vClickOutside = {
  mounted(el: HTMLElement, binding: any) {
    el.clickOutsideEvent = (event: Event) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value();
      }
    };
    document.addEventListener('click', el.clickOutsideEvent);
  },
  unmounted(el: HTMLElement) {
    document.removeEventListener('click', el.clickOutsideEvent);
  }
};
</script>

<style scoped>
.jeu-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
  height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.session-header {
  flex-shrink: 0;
}

.session-info {
  position: relative;
}

.session-details h1 {
  margin-bottom: 0.5rem;
}

.session-meta {
  display: flex;
  gap: 1.5rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--jdr-text-muted);
}

.session-menu {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 100;
  margin-top: 0.5rem;
}

.game-interface {
  flex: 1;
  display: grid;
  grid-template-rows: 1fr auto;
  gap: 1rem;
  min-height: 0;
}

.history-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.history-content {
  flex: 1;
  overflow-y: auto;
  max-height: 60vh;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: var(--jdr-text-muted);
  text-align: center;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.input-panel {
  flex-shrink: 0;
}

.message-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-actions {
  flex-wrap: wrap;
  gap: 1rem;
}

.input-help {
  flex: 1;
}

.action-buttons {
  flex-shrink: 0;
}

/* Styles pour les dés */
.dice-interface {
  text-align: center;
}

.dice-selection h4 {
  color: var(--jdr-text-primary);
  margin-bottom: 1rem;
}

.dice-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(60px, 1fr));
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.dice-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0.5rem;
  background: var(--jdr-bg-tertiary);
  border: 2px solid var(--jdr-border-color);
  border-radius: var(--jdr-border-radius);
  color: var(--jdr-text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.dice-button:hover {
  background: var(--jdr-bg-secondary);
  border-color: var(--jdr-accent);
}

.dice-button.active {
  background: var(--jdr-secondary);
  border-color: var(--jdr-secondary-dark);
  color: var(--jdr-text-dark);
}

.dice-button i {
  font-size: 1.5rem;
}

.dice-result h4 {
  color: var(--jdr-text-primary);
  margin-bottom: 1rem;
}

.result-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 2rem;
  font-weight: bold;
}

.result-value {
  color: var(--jdr-secondary);
  font-size: 3rem;
}

.result-description {
  color: var(--jdr-text-muted);
}

/* Scrollbar personnalisée */
.history-content::-webkit-scrollbar {
  width: 8px;
}

.history-content::-webkit-scrollbar-track {
  background: var(--jdr-bg-tertiary);
  border-radius: 4px;
}

.history-content::-webkit-scrollbar-thumb {
  background: var(--jdr-border-color);
  border-radius: 4px;
}

.history-content::-webkit-scrollbar-thumb:hover {
  background: var(--jdr-secondary);
}

/* Responsive design */
@media (max-width: 768px) {
  .jeu-container {
    padding: 0.5rem;
    height: 100vh;
  }
  
  .session-info {
    flex-direction: column;
    gap: 1rem;
  }
  
  .session-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .action-buttons {
    width: 100%;
    justify-content: stretch;
  }
  
  .dice-types {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .history-content {
    max-height: 50vh;
  }
}

@media (max-width: 480px) {
  .dice-types {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .result-display {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .result-value {
    font-size: 2.5rem;
  }
}
</style>
