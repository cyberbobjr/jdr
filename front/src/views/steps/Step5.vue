<template>
  <div>
    <h2>Étape 5 : Personnalisation finale</h2>

    <!-- Section Nom -->
    <div class="section">
      <h3>Nom du personnage</h3>
      <div class="input-group">
        <input v-model="characterName" type="text" placeholder="Entrez le nom de votre personnage"
          class="character-input" />
        <button @click="generateName" :disabled="isGeneratingName" class="jdr-btn jdr-btn-secondary generate-btn">
          {{ isGeneratingName ? 'Génération...' : 'Générer un nom' }}
        </button>
      </div>
    </div>

    <!-- Section Background -->
    <div class="section">
      <h3>Histoire personnelle</h3>
      <div class="textarea-group">
        <textarea v-model="characterBackground" placeholder="Décrivez l'histoire et le passé de votre personnage..."
          class="character-textarea" rows="6"></textarea>
        <button @click="generateBackground" :disabled="isGeneratingBackground"
          class="jdr-btn jdr-btn-secondary generate-btn">
          {{ isGeneratingBackground ? 'Génération...' : 'Générer une histoire' }}
        </button>
      </div>
    </div>

    <!-- Section Description physique -->
    <div class="section">
      <h3>Apparence physique</h3>
      <div class="textarea-group">
        <textarea v-model="characterPhysicalDescription"
          placeholder="Décrivez l'apparence physique de votre personnage..." class="character-textarea"
          rows="4"></textarea>
        <button @click="generatePhysicalDescription" :disabled="isGeneratingPhysicalDescription"
          class="jdr-btn jdr-btn-secondary generate-btn">
          {{ isGeneratingPhysicalDescription ? 'Génération...' : 'Générer une description' }}
        </button>
      </div>
    </div>

    <!-- Section de validation -->
    <div class="validation-section">
      <div class="character-summary">
        <h3>Résumé du personnage</h3>
        <div class="summary-item" v-if="characterName">
          <strong>Nom :</strong> {{ characterName }}
        </div>
        <div class="summary-item" v-if="props.initialData?.race">
          <strong>Race :</strong> {{ props.initialData.race.name }}
        </div>
        <div class="summary-item" v-if="props.initialData?.culture">
          <strong>Culture :</strong> {{ props.initialData.culture.name }}
        </div>
        <div class="summary-item" v-if="props.initialData?.gold !== undefined">
          <strong>Or restant :</strong> {{ formatCurrency(props.initialData.gold) }}
        </div>
      </div>

      <div class="form-actions"> <button @click="saveAndFinalize" :disabled="!isValid || isSaving"
          class="jdr-btn jdr-btn-primary finalize-btn">
          {{ isSaving ? 'Finalisation...' : (isValid ? 'Finaliser le personnage' : 'Compléter les étapes manquantes') }}
        </button>
      </div>
      <div v-if="!isValid" class="validation-error">
        <p><strong>Pour finaliser le personnage, vous devez compléter :</strong></p>
        <ul>
          <li v-if="characterName.trim().length === 0">✗ Nom du personnage</li>
          <li v-if="characterPhysicalDescription.trim().length === 0">✗ Description physique</li>
          <li v-if="characterBackground.trim().length === 0">✗ Histoire personnelle</li>
          <li v-if="!props.initialData?.race">✗ Race (retournez à l'étape 1)</li>
          <li v-if="!props.initialData?.culture">✗ Culture (retournez à l'étape 1)</li>
          <li
            v-if="!props.initialData?.caracteristiques || Object.keys(props.initialData.caracteristiques).length === 0">
            ✗ Caractéristiques (retournez à l'étape 2)</li>
          <li v-if="!props.initialData?.competences || Object.keys(props.initialData.competences).length === 0">✗
            Compétences (retournez à l'étape 3)</li>
        </ul>
      </div>
    </div>

    <!-- Modales de sélection -->
    <JdrModale v-if="showNameModal" title="Choisissez un nom"
      subtitle="Sélectionnez le nom qui convient le mieux à votre personnage" :show-ok="false" :show-cancel="true"
      cancel-label="Annuler" @close="closeNameModal">
      <div class="choices-container">
        <div v-for="(name, index) in generatedNames" :key="index" class="choice-item" @click="selectName(name)">
          <div class="choice-content">
            <h4>{{ name }}</h4>
          </div>
        </div>
      </div>
    </JdrModale>

    <JdrModale v-if="showBackgroundModal" title="Choisissez une histoire"
      subtitle="Sélectionnez le background qui correspond le mieux à votre personnage" :show-ok="false"
      :show-cancel="true" cancel-label="Annuler" @close="closeBackgroundModal">
      <div class="choices-container">
        <div v-for="(background, index) in generatedBackgrounds" :key="index" class="choice-item"
          @click="selectBackground(background)">
          <div class="choice-content">
            <p>{{ background }}</p>
          </div>
        </div>
      </div>
    </JdrModale>

    <JdrModale v-if="showPhysicalDescriptionModal" title="Choisissez une apparence"
      subtitle="Sélectionnez la description physique qui vous plaît le plus" :show-ok="false" :show-cancel="true"
      cancel-label="Annuler" @close="closePhysicalDescriptionModal">
      <div class="choices-container">
        <div v-for="(description, index) in generatedPhysicalDescriptions" :key="index" class="choice-item"
          @click="selectPhysicalDescription(description)">
          <div class="choice-content">
            <p>{{ description }}</p>
          </div>
        </div>
      </div>
    </JdrModale>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import JdrApiService from '@/core/api';
import JdrModale from '@/components/JdrModale.vue';
import type { Character } from '@/core/interfaces';

const props = defineProps<{
  characterId?: string;
  initialData?: Character | null;
}>();

const emit = defineEmits(['next-step', 'update-character']);

// État local des champs
const characterName = ref('');
const characterBackground = ref('');
const characterPhysicalDescription = ref('');

// États de génération
const isGeneratingName = ref(false);
const isGeneratingBackground = ref(false);
const isGeneratingPhysicalDescription = ref(false);

// État des modales
const showNameModal = ref(false);
const showBackgroundModal = ref(false);
const showPhysicalDescriptionModal = ref(false);

// Données générées
const generatedNames = ref<string[]>([]);
const generatedBackgrounds = ref<string[]>([]);
const generatedPhysicalDescriptions = ref<string[]>([]);

// État de sauvegarde
const isSaving = ref(false);

// Validation complète
const isValid = computed(() => {
  if (!props.initialData) return false;

  // Vérifier que le nom n'est pas vide
  if (characterName.value.trim().length === 0) return false;

  // Vérifier que la description physique n'est pas vide
  if (characterPhysicalDescription.value.trim().length === 0) return false;

  // Vérifier que le background n'est pas vide
  if (characterBackground.value.trim().length === 0) return false;

  // Vérifier que la race et la culture sont choisis
  if (!props.initialData.race || !props.initialData.culture) return false;

  // Vérifier que les caractéristiques sont définies (au minimum)
  if (!props.initialData.caracteristiques || Object.keys(props.initialData.caracteristiques).length === 0) return false;

  // Vérifier que les compétences sont définies (au minimum)
  if (!props.initialData.competences || Object.keys(props.initialData.competences).length === 0) return false;

  return true;
});

// Fonction pour formater la devise
function formatCurrency(amount: number): string {
  if (amount === Math.floor(amount)) {
    return `${amount} po`;
  }
  return `${amount.toFixed(2)} po`;
}

// Initialisation des données
onMounted(() => {
  if (props.initialData) {
    characterName.value = props.initialData.name || '';
    characterBackground.value = props.initialData.background || '';
    characterPhysicalDescription.value = props.initialData.physical_description || '';
  }
});

// Génération du nom
async function generateName() {
  if (!props.initialData || isGeneratingName.value) return;

  try {
    isGeneratingName.value = true;
    generatedNames.value = await JdrApiService.generateCharacterName(props.initialData);
    showNameModal.value = true;
  } catch (error) {
    console.error('Erreur lors de la génération du nom:', error);
  } finally {
    isGeneratingName.value = false;
  }
}

// Génération du background
async function generateBackground() {
  if (!props.initialData || isGeneratingBackground.value) return;

  try {
    isGeneratingBackground.value = true;
    generatedBackgrounds.value = await JdrApiService.generateCharacterBackground(props.initialData);
    showBackgroundModal.value = true;
  } catch (error) {
    console.error('Erreur lors de la génération du background:', error);
  } finally {
    isGeneratingBackground.value = false;
  }
}

// Génération de la description physique
async function generatePhysicalDescription() {
  if (!props.initialData || isGeneratingPhysicalDescription.value) return;

  try {
    isGeneratingPhysicalDescription.value = true;
    generatedPhysicalDescriptions.value = await JdrApiService.generateCharacterPhysicalDescription(props.initialData);
    showPhysicalDescriptionModal.value = true;
  } catch (error) {
    console.error('Erreur lors de la génération de la description physique:', error);
  } finally {
    isGeneratingPhysicalDescription.value = false;
  }
}

// Sauvegarde et finalisation
async function saveAndFinalize() {
  if (!isValid.value || !props.characterId || isSaving.value) return;

  try {
    isSaving.value = true;    // Préparer les données mises à jour avec le statut approprié
    const updatedCharacter: Partial<Character> = {
      ...props.initialData,
      name: characterName.value.trim(),
      background: characterBackground.value.trim(),
      physical_description: characterPhysicalDescription.value.trim(),
      status: isValid.value ? 'done' : 'en_cours', // Statut "done" si tout est complété
    };// Sauvegarder via l'API
    await JdrApiService.saveCharacter({
      character_id: props.characterId,
      character: updatedCharacter
    });

    // Émettre la mise à jour du personnage
    emit('update-character', updatedCharacter);

    // Passer à l'étape suivante (finalisation)
    emit('next-step');

  } catch (error) {
    console.error('Erreur lors de la sauvegarde:', error);
  } finally {
    isSaving.value = false;
  }
}

// Fonctions de gestion des modales
function closeNameModal() {
  showNameModal.value = false;
}

function closeBackgroundModal() {
  showBackgroundModal.value = false;
}

function closePhysicalDescriptionModal() {
  showPhysicalDescriptionModal.value = false;
}

// Fonctions de sélection
function selectName(name: string) {
  characterName.value = name;
  showNameModal.value = false;
}

function selectBackground(background: string) {
  characterBackground.value = background;
  showBackgroundModal.value = false;
}

function selectPhysicalDescription(description: string) {
  characterPhysicalDescription.value = description;
  showPhysicalDescriptionModal.value = false;
}
</script>

<style scoped>
.section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--jdr-bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--jdr-border);
}

.section h3 {
  margin: 0 0 1rem 0;
  color: var(--jdr-text-primary);
  font-size: 1.2rem;
  font-weight: 600;
}

.input-group,
.textarea-group {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.character-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid var(--jdr-border);
  border-radius: 4px;
  background: var(--jdr-bg-primary);
  color: var(--jdr-text-primary);
  font-size: 1rem;
}

.character-input:focus {
  outline: none;
  border-color: var(--jdr-primary);
  box-shadow: 0 0 0 2px rgba(var(--jdr-primary-rgb), 0.2);
}

.character-textarea {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid var(--jdr-border);
  border-radius: 4px;
  background: var(--jdr-bg-primary);
  color: var(--jdr-text-primary);
  font-size: 1rem;
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
  line-height: 1.5;
}

.character-textarea:focus {
  outline: none;
  border-color: var(--jdr-primary);
  box-shadow: 0 0 0 2px rgba(var(--jdr-primary-rgb), 0.2);
}

.generate-btn {
  white-space: nowrap;
  min-width: 160px;
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.validation-section {
  margin-top: 2rem;
  padding: 2rem;
  background: var(--jdr-bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--jdr-border);
}

.character-summary {
  margin-bottom: 2rem;
}

.character-summary h3 {
  margin: 0 0 1rem 0;
  color: var(--jdr-text-primary);
  font-size: 1.2rem;
  font-weight: 600;
}

.summary-item {
  margin-bottom: 0.5rem;
  color: var(--jdr-text-secondary);
}

.summary-item strong {
  color: var(--jdr-text-primary);
}

.form-actions {
  text-align: center;
}

.finalize-btn {
  font-size: 1.1rem;
  padding: 1rem 2rem;
  min-width: 200px;
}

.finalize-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.validation-error {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 4px;
  color: var(--jdr-text-primary);
}

.validation-error p {
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.validation-error ul {
  margin: 0;
  padding-left: 1.5rem;
}

.validation-error li {
  margin: 0.25rem 0;
  color: #ef4444;
}

/* Styles pour les choix dans les modales */
.choices-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 60vh;
  overflow-y: auto;
}

.choice-item {
  padding: 1rem;
  border: 1px solid var(--jdr-border);
  border-radius: 4px;
  background: var(--jdr-bg-primary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.choice-item:hover {
  background: var(--jdr-bg-secondary);
  border-color: var(--jdr-primary);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.choice-item:active {
  transform: translateY(1px);
}

.choice-content h4 {
  margin: 0;
  color: var(--jdr-text-primary);
  font-size: 1.1rem;
  font-weight: 600;
}

.choice-content p {
  margin: 0;
  color: var(--jdr-text-primary);
  line-height: 1.5;
  font-size: 0.95rem;
}

@media (max-width: 768px) {

  .input-group,
  .textarea-group {
    flex-direction: column;
  }

  .generate-btn {
    align-self: stretch;
  }
}
</style>
