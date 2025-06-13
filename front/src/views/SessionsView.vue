<template>
  <div>
    <h1>Sessions en cours</h1>
    <JdrSpinner v-if="loading" />
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
          </button>
          <button
            class="jdr-btn jdr-btn-primary"
            @click="selectSession(session)"
          >
            Reprendre la partie
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
      >
        <div>
          <!-- Ici, tu peux charger et afficher l'historique de la session -->
          <ChatMessage v-if="!loadingHistory"
           :show-debug-info="false"
           :messages="messages" />
           <JdrSpinner v-else="loadingHistory" />
        </div>
      </JdrModale>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import JdrApiService, { type GameSession } from "@/core/api";
import CardComponent from "@/components/CardComponent.vue";
import JdrSpinner from "@/components/JdrSpinner.vue";
import JdrModale from "@/components/JdrModale.vue";
import { formatDateShort } from "@/core/dateUtils";
import ChatMessage from "@/components/ChatMessage.vue";
import type { HistoryItem } from "@/core/interfaces";

const sessions = ref<GameSession[]>([]);
const loading = ref(true);
const loadingHistory = ref(false);
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

function selectSession(session: GameSession) {
  // À compléter selon la navigation souhaitée
  alert(`Session sélectionnée: ${session.session_id}`);
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
