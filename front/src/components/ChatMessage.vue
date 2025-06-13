<template>
  <div class="chat-container">
    <div
      v-for="(message, index) in filteredMessages.values()"
      :key="`message-${index}-${message.timestamp}`"
      class="chat-message"
      :class="getMessageClass(message)"
    >
      <!-- Instructions (si présentes) -->
      <div v-if="message.instructions" class="message-instructions">
        <strong>Instructions:</strong> {{ message.instructions }}
      </div>

      <!-- Parties du message -->
      <div class="message-parts">
        <div
          v-for="(part, partIndex) in message.parts"
          :key="`part-${partIndex}-${part.timestamp}`"
          class="message-part"
          :class="getPartClass(part.part_kind)"
        >
          <div class="part-header">
            <span class="part-kind">{{ formatPartKind(part.part_kind) }}</span>
            <span v-if="part.timestamp" class="part-timestamp">{{
              formatTimestamp(part.timestamp)
            }}</span>
          </div>
          <div class="part-content">
            <pre
              v-if="isCodeContent(part.part_kind)"
              class="code-content"
              v-html="formatTextContent(part.content)"
            ></pre>
            <div
              v-else
              class="text-content"
              v-html="formatTextContent(part.content)"
            ></div>
          </div>
          <div v-if="part.dynamic_ref" class="dynamic-ref">
            <small>Référence: {{ part.dynamic_ref }}</small>
          </div>
        </div>
      </div>

      <!-- Détails d'usage (si présents et mode debug) -->
      <div v-if="message.usage && showDebugInfo" class="usage-details">
        <details>
          <summary>Détails d'usage</summary>
          <ul>
            <li>Requêtes: {{ message.usage.requests }}</li>
            <li>Tokens de requête: {{ message.usage.request_tokens }}</li>
            <li>Tokens de réponse: {{ message.usage.response_tokens }}</li>
            <li>Total: {{ message.usage.total_tokens }}</li>
          </ul>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { ConversationMessage } from "../core/interfaces";

interface Props {
  messages: ConversationMessage[];
  showDebugInfo?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showDebugInfo: false,
});

const filteredMessages = computed(() => {
  if (props.showDebugInfo) {
    return props.messages;
  }
  return props.messages.filter(
    (message) =>
      !message.parts.some(
        (part) =>
          part.part_kind === "system-prompt" || part.part_kind === "tool-call"
      )
  );
});

/**
 * Formate le type de partie pour l'affichage
 */
const formatPartKind = (partKind: string): string => {
  const partKindMap: Record<string, string> = {
    "system-prompt": "Prompt Système",
    "user-prompt": "Joueur",
    text: "Maitre de jeu",
    "tool-call": "Appel d'Outil",
    "tool-return": "Jet de dés",
  };
  return partKindMap[partKind] || partKind;
};

/**
 * Formate un timestamp pour l'affichage
 */
const formatTimestamp = (timestamp: string): string => {
  try {
    const date = new Date(timestamp);
    return date.toLocaleString("fr-FR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return timestamp;
  }
};

/**
 * Détermine la classe CSS pour un message selon son type
 */
const getMessageClass = (message: ConversationMessage): string => {
  console.log( message.parts.some(part => part.part_kind === "tool-return"));
  const classMap: Record<string, (message: ConversationMessage) => string> = {
    request: (message) =>
      message.parts.some(part => part.part_kind === "tool-return")
        ? "response-tool"
        : "message-request",
    response: (message) => "message-response",
    system: (message) => "message-system",
    error: (message) => "message-error",
  };
  return classMap[message.kind](message) || "message-default";
};

/**
 * Détermine la classe CSS pour une partie selon son type
 */
const getPartClass = (partKind: string): string => {
  const classMap: Record<string, string> = {
    "system-prompt": "part-system",
    "user-prompt": "part-user",
    text: "part-text",
    "tool-call": "part-tool-call",
    "tool-return": "part-tool-return",
  };
  return classMap[partKind] || "part-default";
};

/**
 * Détermine si le contenu doit être affiché comme du code
 */
const isCodeContent = (partKind: string): boolean => {
  return ["tool-call", "tool-return"].includes(partKind);
};

/**
 * Formate le contenu textuel (supporte le markdown basique)
 */
const formatTextContent = (content: string): string => {
  if (!content) return "";

  // Conversion basique du markdown
  return content
    .replace(/\*\*(.*?)\*\*/g, "<span class='jdr-bold'>$1</span>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");
};
</script>

<style scoped>
.jdr-bold {
  font-weight: bold;
  color: var(--jdr-text-primary, #1f2937);
}

.chat-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chat-message {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.message-request {
  background-color: var(--jdr-bg-primary);
  border-color: #bfdbfe;
}

.message-response {
  background-color: var(--jdr-bg-secondary);
  border-color: #bbf7d0;
}

.message-system {
  background-color: var(--jdr-bg-tertiary);
  border-color: #e5e7eb;
}

.message-error {
  background-color: var(--jdr-danger);
  border-color: #fecaca;
}

.message-default {
  background-color: var(--jdr-info);
  border-color: #e5e7eb;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.message-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.message-kind {
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  background-color: var(--jdr-bg-secondary);
}

.model-name {
  color: #4b5563;
  font-family: "Courier New", monospace;
  font-size: 0.75rem;
}

.timestamp {
  color: #6b7280;
  font-size: 0.75rem;
}

.token-usage {
  font-size: 0.875rem;
  color: #4b5563;
}

.token-count {
  font-family: "Courier New", monospace;
  background-color: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.message-instructions {
  background-color: #fefce8;
  border: 1px solid #fde047;
  border-radius: 0.25rem;
  padding: 0.5rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.message-parts {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.message-part {
  border-left: 4px solid #9ca3af;
  padding-left: 0.75rem;
}

.part-system {
  border-left-color: #a855f7;
}

.part-user {
  border-left-color: #3b82f6;
}

.part-text {
  border-left-color: #10b981;
}

.part-tool-call {
  border-left-color: #f59e0b;
}

.part-tool-return {
  border-left-color: #06b6d4;
}

.part-default {
  border-left-color: #9ca3af;
}

.part-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.part-kind {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  background-color: var(--jdr-bg-tertiary);
}

.part-timestamp {
  font-size: 0.75rem;
  color: #6b7280;
}

.part-content {
  margin-bottom: 0.5rem;
}

.text-content {
  line-height: 1.6;
  max-width: none;
}

.code-content {
  background-color: #1f2937;
  color: #f3f4f6;
  padding: 0.75rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-family: "Courier New", monospace;
  overflow-x: auto;
  white-space: pre-wrap;
}

.dynamic-ref {
  font-size: 0.75rem;
  color: #6b7280;
  font-style: italic;
}

.usage-details {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e5e7eb;
}

.usage-details details {
  font-size: 0.875rem;
}

.usage-details summary {
  cursor: pointer;
  font-weight: 500;
  color: var(--jdr-text-muted);
  transition: color 0.2s;
}

.usage-details summary:hover {
  color: var(--jdr-text-secondary);
}

.usage-details ul {
  margin-top: 0.5rem;
  margin-left: 1rem;
  font-size: 0.75rem;
  color: var(--jdr-text-muted);
}

.usage-details li {
  margin-bottom: 0.25rem;
}
</style>
