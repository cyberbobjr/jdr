<template>
  <div>
    <h2>Étape 2 : Répartition des caractéristiques</h2>
    
    <!-- Affichage des points disponibles -->
    <div class="points-info" v-if="characteristicsData">
      <div class="points-summary">
        <span class="points-label">Points disponibles :</span>
        <span class="points-value" :class="{ 'points-negative': remainingPoints < 0 }">
          {{ remainingPoints }} / {{ characteristicsData.starting_points }}
        </span>
      </div>
      <div class="points-cost" v-if="totalCost > 0">
        <span class="cost-label">Coût total :</span>
        <span class="cost-value">{{ totalCost }} points</span>
      </div>
    </div>

    <div class="caracs-list">
      <div
        v-for="carac in caracNames"
        :key="carac"
        class="carac-item"
      >
        <JdrPopover>
          <span class="carac-label">{{ carac }}</span>
          <template #content>
            <div v-if="caracDetails[carac]">
              <strong>{{ carac }}</strong><br />
              {{ caracDetails[carac] }}
            </div>
          </template>
        </JdrPopover>        <div class="carac-input-container">
          <JdrPointInput
            v-model="caracs[carac]"
            :min="1"
            :max="105"
            :can-increment="remainingPoints > 0"
            :can-decrement="caracs[carac] > 1"
            :increment-tooltip="remainingPoints > 0 ? 'Augmenter cette caractéristique' : 'Plus de points disponibles'"
            :decrement-tooltip="caracs[carac] > 1 ? 'Diminuer cette caractéristique' : 'Valeur minimale atteinte'"
            @update:modelValue="onCaracChange"
          />
          
          <!-- Affichage du coût et du bonus -->
          <div class="carac-meta" v-if="characteristicsData">
            <span class="carac-cost">
              Coût: {{ getCharacteristicCost(caracs[carac] || 50) }}
            </span>
            <span class="carac-bonus" :class="getBonusClass(getFinalBonus(carac))">
              Bonus: {{ getBonusDisplay(getFinalBonus(carac)) }}
              <span v-if="getRaceCultureBonus(carac) !== 0" class="race-culture-bonus">
                ({{ getRaceCultureBonusDisplay(carac) }})
              </span>
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="caracs-actions">
      <button class="jdr-btn jdr-btn-secondary" @click="proposeDistribution">Proposer une répartition</button>
      <button class="jdr-btn jdr-btn-primary" :disabled="!isValid || remainingPoints < 0" @click="goToNextStep">Suivant</button>
    </div>
    
    <div v-if="!isValid" class="caracs-error">La répartition n'est pas valide selon les règles du jeu.</div>
    <div v-if="remainingPoints < 0" class="caracs-error">Vous avez dépassé votre budget de points !</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import JdrApiService from '@/core/api';
import JdrPopover from '@/components/JdrPopover.vue';
import JdrPointInput from '@/components/JdrPointInput.vue';
import type { Character, CharacteristicsData } from '@/core/interfaces';

const props = defineProps<{
  characterId?: string;
  initialData?: Character | null;
  characteristicsData?: CharacteristicsData | null;
}>();
const emit = defineEmits(['next-step', 'update-character']);

// Noms des caractéristiques et descriptions depuis l'API
const caracNames = computed(() => {
  if (!props.characteristicsData?.characteristics) {
    // Fallback si les données ne sont pas encore chargées
    return ['Force', 'Constitution', 'Agilité', 'Rapidité', 'Volonté', 'Raisonnement', 'Intuition', 'Présence'];
  }
  return Object.keys(props.characteristicsData.characteristics);
});

const caracDetails = computed(() => {
  if (!props.characteristicsData?.characteristics) {
    // Fallback descriptions
    return {
      'Force': "Détermine la puissance physique, la capacité à porter, soulever, frapper.",
      'Constitution': "Résistance aux maladies, fatigue, endurance physique.",
      'Agilité': "Souplesse, coordination, capacité à esquiver ou manipuler avec précision.",
      'Rapidité': "Vitesse de déplacement, réflexes, initiative.",
      'Volonté': "Force mentale, résistance à la peur, détermination.",
      'Raisonnement': "Logique, capacité d'analyse, résolution de problèmes.",
      'Intuition': "Perception instinctive, flair, capacité à anticiper.",
      'Présence': "Charisme, capacité à influencer, prestance."
    };
  }
    const details: Record<string, string> = {};
  Object.entries(props.characteristicsData.characteristics).forEach(([name, data]) => {
    details[name] = data.description + (data.examples && data.examples.length > 0 ? ` Exemples: ${data.examples.join(', ')}.` : '');
  });
  return details;
});

const caracs = ref<Record<string, number>>({});
const isValid = ref(true);
const isValidating = ref(false); // Flag pour éviter les appels redondants

// Calculs des coûts et bonus
const totalCost = computed(() => {
  if (!props.characteristicsData) return 0;
  
  let total = 0;
  Object.values(caracs.value).forEach(value => {
    total += getCharacteristicCost(value || 50);
  });
  return total;
});

const remainingPoints = computed(() => {
  if (!props.characteristicsData) return 0;
  return props.characteristicsData.starting_points - totalCost.value;
});

// Fonction pour calculer le coût d'une valeur de caractéristique (progressif)
function getCharacteristicCost(value: number): number {
  if (!props.characteristicsData?.cost_table) return value;
  
  let totalCost = 0;
  let currentValue = 1; // On commence à 1
  
  // Trier les plages de coût par ordre croissant
  const sortedRanges = Object.entries(props.characteristicsData.cost_table).sort((a, b) => {
    const minA = a[0].includes('-') ? parseInt(a[0].split('-')[0]) : parseInt(a[0]);
    const minB = b[0].includes('-') ? parseInt(b[0].split('-')[0]) : parseInt(b[0]);
    return minA - minB;
  });
  
  // Calculer le coût progressif pour chaque plage
  for (const [range, costPerPoint] of sortedRanges) {
    if (range.includes('-')) {
      const [min, max] = range.split('-').map(Number);
      
      if (currentValue > value) break; // On a déjà atteint la valeur cible
      
      const startInRange = Math.max(currentValue, min);
      const endInRange = Math.min(value, max);
      
      if (startInRange <= endInRange) {
        const pointsInThisRange = endInRange - startInRange + 1;
        totalCost += pointsInThisRange * costPerPoint;
        currentValue = endInRange + 1;
      }
    } else {
      // Valeur exacte
      const exactValue = Number(range);
      if (currentValue <= exactValue && exactValue <= value) {
        totalCost += costPerPoint;
        currentValue = exactValue + 1;
      }
    }
  }
  
  return totalCost;
}

// Fonction pour calculer le bonus d'une valeur de caractéristique
function getCharacteristicBonus(value: number): number {
  if (!props.characteristicsData?.bonus_table) return 0;
  
  // Chercher dans la table des bonus
  for (const [range, bonus] of Object.entries(props.characteristicsData.bonus_table)) {
    if (range.includes('-')) {
      const [min, max] = range.split('-').map(Number);
      if (value >= min && value <= max) {
        return bonus;
      }
    } else {
      const exactValue = Number(range);
      if (value === exactValue) {
        return bonus;
      }
    }
  }
  
  return 0;
}

// Fonction pour calculer le bonus de race/culture pour une caractéristique
function getRaceCultureBonus(characteristic: string): number {
  let bonus = 0;
  
  // Bonus de race
  if (props.initialData?.race?.characteristic_bonuses?.[characteristic]) {
    bonus += props.initialData.race.characteristic_bonuses[characteristic];
  }
  
  // Bonus de culture
  if (props.initialData?.culture?.characteristic_bonuses?.[characteristic]) {
    bonus += props.initialData.culture.characteristic_bonuses[characteristic];
  }
  
  return bonus;
}

// Fonction pour afficher le bonus de race/culture
function getRaceCultureBonusDisplay(characteristic: string): string {
  const bonus = getRaceCultureBonus(characteristic);
  if (bonus > 0) return `+${bonus}`;
  if (bonus < 0) return `${bonus}`;
  return '';
}

// Fonction pour obtenir le bonus final (table bonus + bonus de race/culture)
function getFinalBonus(characteristic: string): number {
  const baseValue = caracs.value[characteristic] || 50;
  const tableBonusFomBase = getCharacteristicBonus(baseValue);
  const raceCultureBonus = getRaceCultureBonus(characteristic);
  return tableBonusFomBase + raceCultureBonus;
}

// Fonction pour formater l'affichage du bonus
function getBonusDisplay(bonus: number): string {
  if (bonus > 0) return `+${bonus}`;
  if (bonus < 0) return `${bonus}`;
  return '0';
}

// Fonction pour obtenir la classe CSS du bonus
function getBonusClass(bonus: number): string {
  if (bonus > 0) return 'bonus-positive';
  if (bonus < 0) return 'bonus-negative';
  return 'bonus-neutral';
}

onMounted(() => {
  console.log('🔧 Step2 onMounted', { characterId: props.characterId, initialData: !!props.initialData });
  // Pré-remplissage si édition
  initializeCharacteristics();
  // Pas de validation ici - elle sera déclenchée par le watcher initialData
});

// Watch pour détecter quand les données initiales arrivent
watch(() => props.initialData, (newData) => {
  console.log('👀 watch initialData:', !!newData);
  if (newData) {
    initializeCharacteristics();
    // La validation sera déclenchée automatiquement par le watcher de caracs
  }
}, { immediate: true });

// Fonction pour initialiser les caractéristiques
function initializeCharacteristics() {
  if (props.initialData && props.initialData.caracteristiques) {
    console.log('Chargement des caractéristiques depuis initialData:', props.initialData.caracteristiques);
    caracs.value = { ...props.initialData.caracteristiques };
  } else {
    console.log('Initialisation avec valeurs par défaut (50)');
    caracNames.value.forEach((n: string) => caracs.value[n] = 50);
  }
}

// Watch avec debounce pour éviter les appels trop fréquents
let validateTimeout: NodeJS.Timeout | null = null;
watch(caracs, (newCaracs) => {
  console.log('👀 watch caracs changé:', Object.keys(newCaracs).length, 'caractéristiques');
  if (validateTimeout) {
    clearTimeout(validateTimeout);
  }
  validateTimeout = setTimeout(() => {
    console.log('⏰ timeout validation déclenché');
    validateCaracs();
  }, 300); // Attendre 300ms après le dernier changement
}, { deep: true });

async function proposeDistribution() {
  if (!props.initialData) return;
  const { race } = props.initialData;
  if (!race) return;
  // Correction : passer le nom de la race (string) au lieu de l'objet complet
  const result = await JdrApiService.allocateAttributes({ race: race.name });
  caracs.value = { ...result.attributes };
}

async function onCaracChange() {
  await saveCaracs();
}

async function saveCaracs() {
  if (!props.characterId) return;
  
  // On sauvegarde seulement les valeurs de base (sans les bonus de race/culture)
  // car les bonus sont recalculés automatiquement à partir de la race et culture
  const baseCharacteristics = { ...caracs.value };
  
  await JdrApiService.saveCharacter({
    character_id: props.characterId,
    character: {
      ...(props.initialData || {}),
      caracteristiques: baseCharacteristics
    }
  });
  
  // Pour l'émission vers le parent, on envoie aussi que les valeurs de base
  emit('update-character', {
    ...(props.initialData || {}),
    caracteristiques: baseCharacteristics
  } as Character);
}

async function validateCaracs() {
  console.log('🔍 validateCaracs appelée', { 
    characterId: props.characterId, 
    caracsLength: Object.keys(caracs.value).length,
    isValidating: isValidating.value 
  });
  
  if (!props.characterId) {
    console.log('❌ Pas de characterId');
    return;
  }
  
  // Vérifier que nous avons des données valides à valider
  if (Object.keys(caracs.value).length === 0) {
    console.log('❌ Pas de données de caractéristiques');
    return;
  }
  
  // Éviter les appels redondants
  if (isValidating.value) {
    console.log('❌ Validation déjà en cours');
    return;
  }
  
  try {
    isValidating.value = true;
    console.log('🚀 Appel API checkAttributes avec:', caracs.value);
    
    // Pour la validation, on utilise les valeurs de base uniquement
    // car les bonus de race/culture sont gérés côté backend
    const res = await JdrApiService.checkAttributes({ attributes: caracs.value });
    isValid.value = res.valid;
    console.log('✅ Réponse API:', res);
  } catch (error) {
    console.error('❌ Erreur lors de la validation des caractéristiques:', error);
    isValid.value = false;
  } finally {
    isValidating.value = false;
  }
}

function goToNextStep() {
  if (isValid.value) emit('next-step');
}
</script>

<style scoped>
.points-info {
  background: var(--jdr-bg-tertiary);
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.points-summary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.points-label, .cost-label {
  font-weight: 600;
  color: var(--jdr-text-secondary);
}

.points-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--jdr-success);
}

.points-value.points-negative {
  color: var(--jdr-danger);
}

.cost-value {
  font-weight: 600;
  color: var(--jdr-text-primary);
}

.caracs-list {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  margin-bottom: 2rem;
}

.carac-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 140px;
  padding: 1rem;
  background: var(--jdr-bg-secondary);
  border-radius: 8px;
  border: 2px solid transparent;
}

.carac-label {
  font-weight: 600;
  margin-bottom: 0.5rem;
  cursor: pointer;
  color: var(--jdr-secondary);
}

.carac-input-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
}

.carac-input {
  width: 80px;
  padding: 0.5rem;
  text-align: center;
  border: 2px solid var(--jdr-border);
  border-radius: 4px;
  font-size: 1.1rem;
  font-weight: 600;
}

.carac-input:focus {
  outline: none;
  border-color: var(--jdr-primary);
}

.carac-total-value {
  font-size: 0.9rem;
  color: var(--jdr-text-primary);
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.race-culture-bonus {
  color: var(--jdr-primary);
  font-style: italic;
  margin-left: 0.25rem;
}

.carac-meta {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.85rem;
  text-align: center;
}

.carac-cost {
  color: var(--jdr-text-secondary);
  font-weight: 500;
}

.carac-bonus {
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  min-width: 40px;
  text-align: center;
}

.bonus-positive {
  background: var(--jdr-success-bg);
  color: var(--jdr-success);
}

.bonus-negative {
  background: var(--jdr-danger-bg);
  color: var(--jdr-danger);
}

.bonus-neutral {
  background: var(--jdr-bg-tertiary);
  color: var(--jdr-text-secondary);
}

.race-culture-bonus {
  font-size: 0.85em;
  color: var(--jdr-primary);
  font-weight: 500;
  margin-left: 0.25rem;
}

.caracs-actions {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.caracs-error {
  color: var(--jdr-danger);
  font-weight: 500;
  margin-top: 1rem;
  padding: 0.75rem;
  background: var(--jdr-danger-bg);
  border-radius: 4px;
  border-left: 4px solid var(--jdr-danger);
}
</style>
