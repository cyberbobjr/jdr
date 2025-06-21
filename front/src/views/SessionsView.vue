<template>
  <div class="jdr-container jdr-p-4">
    <!-- En-tête de la page -->
    <div class="jdr-text-center jdr-mb-4">
      <h1 class="jdr-title jdr-title-lg">Sessions en cours</h1>
      <p class="jdr-subtitle">Gérez vos parties actives et reprenez vos aventures</p>
    </div>

    <!-- Indicateur de chargement -->
    <div v-if="loading" class="jdr-text-center jdr-p-4">
      <div class="jdr-animate-pulse">
        <font-awesome-icon icon="gamepad" size="3x" class="jdr-text-accent" />
        <p class="jdr-mt-4">Chargement des sessions...</p>
      </div>
    </div>

    <!-- Liste des sessions -->
    <div v-else>
      <CardComponent
        v-for="session in sessions"
        :key="session.session_id"
        :title="session.scenario_name"
      >
        <template #default>
          <div>
            <strong>Personnage :</strong> {{ session.character_name }}<br />
            <strong>Status :</strong> {{ session.status }}<br />
            <strong>Dernière activité :</strong>
            {{ formatDateShort(session.last_activity) }}
          </div>
        </template>
        <template #footer>
          <button
            class="jdr-btn jdr-btn-secondary"
            @click="showHistory(session)"
          >
            Voir l'historique
          </button>          <button
            class="jdr-btn jdr-btn-primary"
            @click="selectSession(session)"
            :disabled="navigating === session.session_id"
          >
            <font-awesome-icon 
              v-if="navigating === session.session_id" 
              icon="spinner" 
              spin 
              class="jdr-mr-2" 
            />
            <span v-if="navigating === session.session_id">Chargement...</span>
            <span v-else>Reprendre la partie</span>
          </button>
        </template>
      </CardComponent>
      <JdrModale
        v-if="showModal"
        :title="modalSession?.scenario_name || ''"
        :subtitle="modalSession ? 'Historique de la session' : ''"
        :showOk="false"
        :showCancel="true"
        cancelLabel="Fermer"
        @close="closeModal"
      >        <div>
          <!-- Ici, tu peux charger et afficher l'historique de la session -->
          <ChatMessage v-if="!loadingHistory"
           :show-debug-info="false"
           :messages="messages" />
           <div v-else class="jdr-text-center jdr-p-4">
             <font-awesome-icon icon="spinner" spin size="2x" class="jdr-text-accent" />
             <p class="jdr-mt-4">Chargement de l'historique...</p>
           </div>
        </div>
      </JdrModale>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import JdrApiService, { type GameSession } from "@/core/api";
import CardComponent from "@/components/CardComponent.vue";
import JdrModale from "@/components/JdrModale.vue";
import { formatDateShort } from "@/core/dateUtils";
import ChatMessage from "@/components/ChatMessage.vue";
import type { HistoryItem } from "@/core/interfaces";

const router = useRouter();
const sessions = ref<GameSession[]>([]);
const loading = ref(true);
const loadingHistory = ref(false);
const navigating = ref<string | null>(null); // Pour indiquer quelle session est en cours de navigation
const showModal = ref(false);
const modalSession = ref<GameSession | null>(null);
const messages = ref<HistoryItem[]>([]); // Pour stocker les messages de l'historique

async function fetchSessions() {
  loading.value = true;
  try {
    sessions.value = await JdrApiService.getActiveSessions();
  } finally {
    loading.value = false;
  }
}

async function selectSession(session: GameSession) {
  try {
    navigating.value = session.session_id;
    // Navigation vers la page de jeu avec l'ID de session
    await router.push(`/jeu/${session.session_id}`);
  } catch (error) {
    console.error('Erreur lors de la navigation vers la session:', error);
  } finally {
    navigating.value = null;
  }
}

async function showHistory(session: GameSession) {
  loadingHistory.value = true;
  modalSession.value = session;
  showModal.value = true;
  messages.value = []; // Réinitialiser les messages
  try {
    // Appel à l'API pour récupérer l'historique de la session
    messages.value = await JdrApiService.getScenarioHistory(session.session_id);
  } catch (error) {
    console.error("Erreur lors de la récupération de l'historique :", error);
  } finally {
    loadingHistory.value = false;
  }
}

function closeModal() {
  showModal.value = false;
  modalSession.value = null;
}
onMounted(fetchSessions);
</script>
