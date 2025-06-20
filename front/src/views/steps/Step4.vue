<template>
  <div>
    <h2>Étape 4 : Équipement</h2>    <!-- Affichage du budget -->
    <div class="budget-info" v-if="gold !== null && gold !== undefined">
      <div class="money-summary">
        <span class="money-label">Budget disponible :</span>
        <span class="money-value" :class="{ 'money-negative': gold < 0 }">
          {{ formatCurrency(gold) }}
        </span>
      </div>
      <div class="cost-info" v-if="totalCost > 0">
        <span class="cost-label">Coût total :</span>
        <span class="cost-value">{{ formatCurrency(totalCost) }}</span>
      </div>
      <div class="weight-info" v-if="totalWeight > 0">
        <span class="weight-label">Poids total :</span>
        <span class="weight-value">{{ totalWeight.toFixed(1) }} kg</span>
      </div>
    </div>

    <div v-if="isLoading" class="loading">
      Chargement des équipements...
    </div>

    <div v-else-if="equipmentData" class="equipment-container">
      <!-- Armes -->
      <div class="equipment-category">
        <h3 class="category-title">Armes</h3>
        <div class="equipment-grid">
          <div
            v-for="(weapon, name) in equipmentData.weapons"
            :key="name"
            class="equipment-item"
            :class="{ 'selected': selectedEquipments.includes(name) }"
          >            <div class="equipment-header">
              <label class="equipment-name">
                <input
                  type="checkbox"
                  :value="name"
                  :checked="selectedEquipments.includes(name)"
                  @change="updateSelection"
                />
                {{ name }}
              </label>
              <span class="equipment-cost">{{ weapon.cost }} po</span>
            </div>
            <div class="equipment-details">
              <div class="equipment-stats">
                <span class="stat">Dégâts: {{ weapon.damage }}</span>
                <span class="stat">Catégorie: {{ weapon.category }}</span>
                <span v-if="weapon.range" class="stat">Portée: {{ weapon.range }}m</span>
                <span class="stat">Poids: {{ weapon.weight }}kg</span>
              </div>
              <p class="equipment-description">{{ weapon.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Armures -->
      <div class="equipment-category">
        <h3 class="category-title">Armures</h3>
        <div class="equipment-grid">
          <div
            v-for="(armor, name) in equipmentData.armor"
            :key="name"
            class="equipment-item"
            :class="{ 'selected': selectedEquipments.includes(name) }"
          >            <div class="equipment-header">
              <label class="equipment-name">
                <input
                  type="checkbox"
                  :value="name"
                  :checked="selectedEquipments.includes(name)"
                  @change="updateSelection"
                />
                {{ name }}
              </label>
              <span class="equipment-cost">{{ armor.cost }} po</span>
            </div>
            <div class="equipment-details">
              <div class="equipment-stats">
                <span class="stat">Protection: {{ armor.protection }}</span>
                <span class="stat">Poids: {{ armor.weight }}kg</span>
              </div>
              <p class="equipment-description">{{ armor.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Objets divers -->
      <div class="equipment-category">
        <h3 class="category-title">Objets divers</h3>
        <div class="equipment-grid">
          <div
            v-for="(item, name) in equipmentData.items"
            :key="name"
            class="equipment-item"
            :class="{ 'selected': selectedEquipments.includes(name) }"
          >            <div class="equipment-header">
              <label class="equipment-name">
                <input
                  type="checkbox"
                  :value="name"
                  :checked="selectedEquipments.includes(name)"
                  @change="updateSelection"
                />
                {{ name }}
              </label>
              <span class="equipment-cost">{{ item.cost }} po</span>
            </div>
            <div class="equipment-details">
              <div class="equipment-stats">
                <span class="stat">Type: {{ item.type }}</span>
                <span class="stat">Poids: {{ item.weight }}kg</span>
              </div>
              <p class="equipment-description">{{ item.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="equipment-actions">      <button class="jdr-btn jdr-btn-primary" :disabled="!isValid || gold < 0" @click="goToNextStep">
        Suivant
      </button>
    </div>

    <div v-if="!isValid" class="equipment-error">La sélection d'équipement n'est pas valide.</div>
    <div v-if="gold < 0" class="equipment-error">Vous avez dépassé votre budget !</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import JdrApiService from '@/core/api';
import type { Character, EquipmentData, AddEquipmentResponse, RemoveEquipmentResponse } from '@/core/interfaces';

const props = defineProps<{
  characterId?: string;
  initialData?: Character | null;
}>();
const emit = defineEmits(['next-step', 'update-character']);

const equipmentData = ref<EquipmentData | null>(null);
const selectedEquipments = ref<string[]>([]);
const isLoading = ref(true);
const isValid = ref(true);

// Copie réactive locale de l'or du personnage
const gold = ref<number>(0);

// Fonction pour formater la devise (affiche les décimales si nécessaire)
function formatCurrency(amount: number): string {
  // Si c'est un nombre entier, on n'affiche pas de décimales
  if (amount === Math.floor(amount)) {
    return `${amount} po`;
  }
  // Sinon, on affiche avec 2 décimales maximum
  return `${amount.toFixed(2)} po`;
}

// Calculs dérivés
const totalCost = computed(() => {
  if (!equipmentData.value) return 0;
  
  let cost = 0;
  selectedEquipments.value.forEach(equipmentName => {
    // Chercher dans toutes les catégories
    const weapon = equipmentData.value?.weapons[equipmentName];
    const armor = equipmentData.value?.armor[equipmentName];
    const item = equipmentData.value?.items[equipmentName];
    
    if (weapon) cost += weapon.cost;
    else if (armor) cost += armor.cost;
    else if (item) cost += item.cost;
  });
  
  return cost;
});

const totalWeight = computed(() => {
  if (!equipmentData.value) return 0;
  
  let weight = 0;
  selectedEquipments.value.forEach(equipmentName => {
    // Chercher dans toutes les catégories
    const weapon = equipmentData.value?.weapons[equipmentName];
    const armor = equipmentData.value?.armor[equipmentName];
    const item = equipmentData.value?.items[equipmentName];
    
    if (weapon) weight += weapon.weight;
    else if (armor) weight += armor.weight;
    else if (item) weight += item.weight;
  });
    return weight;
});

onMounted(async () => {
  await loadEquipmentData();
  initializeSelectedEquipments();
});

async function loadEquipmentData() {
  try {
    isLoading.value = true;
    equipmentData.value = await JdrApiService.getEquipmentsDetailed();
  } catch (error) {
    console.error('Erreur lors du chargement des équipements:', error);
  } finally {
    isLoading.value = false;
  }
}

function initializeSelectedEquipments() {
  // Utiliser inventory au lieu de equipment
  if (props.initialData?.inventory) {
    // Extraire les noms des équipements depuis l'inventaire
    selectedEquipments.value = props.initialData.inventory.map(item => item.name);
  }
  
  // Initialiser l'or avec la valeur du personnage
  if (props.initialData?.gold !== undefined) {
    gold.value = props.initialData.gold;
  }
}

async function updateSelection(event: Event) {
  if (!props.characterId) return;
  
  const target = event.target as HTMLInputElement;
  const equipmentName = target.value;
  const isChecked = target.checked;
  
  try {
    if (isChecked) {
      // Ajouter l'équipement
      const result: AddEquipmentResponse = await JdrApiService.addEquipment(props.characterId, equipmentName);
      console.log('Équipement ajouté:', result);
      
      // Mettre à jour les données locales avec les valeurs retournées par l'API
      if (!selectedEquipments.value.includes(equipmentName)) {
        selectedEquipments.value.push(equipmentName);
      }
      
      // Mettre à jour l'or avec la valeur retournée par l'API
      if (result.gold !== undefined) {
        console.log('Mise à jour de l\'or après ajout:', result.gold);
        gold.value = result.gold;
      }
      
    } else {
      // Retirer l'équipement (avec remboursement automatique)
      const result: RemoveEquipmentResponse = await JdrApiService.removeEquipment(props.characterId, equipmentName);
      console.log('Équipement retiré:', result);
      
      // Mettre à jour les données locales
      const index = selectedEquipments.value.indexOf(equipmentName);
      if (index > -1) {
        selectedEquipments.value.splice(index, 1);
      }
      
      // Mettre à jour l'or avec la valeur retournée par l'API
      if (result.gold !== undefined) {
        console.log('Mise à jour de l\'or après suppression:', result.gold);
        gold.value = result.gold;
      }
    }
    
    // Émettre les changements vers le composant parent
    emit('update-character', { 
      needsReload: true,
      updatedGold: gold.value
    });
    
  } catch (error) {
    console.error('Erreur lors de la mise à jour de l\'équipement:', error);
    // Annuler le changement en cas d'erreur
    target.checked = !isChecked;
  }
}

// Cette fonction n'est plus nécessaire car on utilise les routes individuelles
// async function saveEquipmentSelection() { ... }

function goToNextStep() {
  if (isValid.value && gold.value >= 0) {
    emit('next-step');
  }
}

// Watch pour détecter les changements dans les données initiales
watch([() => props.initialData], () => {
  initializeSelectedEquipments();
}, { immediate: true });

// Watch pour déboguer les changements d'or
watch(gold, (newValue, oldValue) => {
  console.log('gold a changé:', { ancien: oldValue, nouveau: newValue });
}, { immediate: true });
</script>

<style scoped>
.budget-info {
  background: var(--jdr-bg-secondary);
  border: 2px solid var(--jdr-border);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.money-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.money-label {
  font-weight: 600;
  color: var(--jdr-text-primary);
}

.money-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--jdr-success);
}

.money-negative {
  color: var(--jdr-danger) !important;
}

.cost-info, .weight-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  color: var(--jdr-text-secondary);
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--jdr-text-secondary);
}

.equipment-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.equipment-category {
  background: var(--jdr-bg-secondary);
  border-radius: 8px;
  padding: 1.5rem;
}

.category-title {
  margin: 0 0 1rem 0;
  color: var(--jdr-primary);
  font-size: 1.2rem;
  font-weight: 600;
  border-bottom: 2px solid var(--jdr-primary);
  padding-bottom: 0.5rem;
}

.equipment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.equipment-item {
  background: var(--jdr-bg-primary);
  border: 2px solid var(--jdr-border);
  border-radius: 6px;
  padding: 1rem;
  transition: all 0.2s ease;
}

.equipment-item:hover {
  border-color: var(--jdr-primary);
  box-shadow: 0 2px 8px var(--jdr-shadow);
}

.equipment-item.selected {
  border-color: var(--jdr-success);
  background: var(--jdr-success-bg);
}

.equipment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.equipment-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--jdr-text-primary);
  cursor: pointer;
}

.equipment-name input[type="checkbox"] {
  width: 18px;
  height: 18px;
}

.equipment-cost {
  font-weight: 600;
  color: var(--jdr-warning);
  font-size: 0.9rem;
}

.equipment-details {
  font-size: 0.9rem;
}

.equipment-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.stat {
  background: var(--jdr-bg-tertiary);
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  color: var(--jdr-text-secondary);
}

.equipment-description {
  color: var(--jdr-text-secondary);
  font-style: italic;
  margin: 0;
  line-height: 1.4;
}

.equipment-actions {
  margin-top: 2rem;
  text-align: right;
}

.equipment-error {
  color: var(--jdr-danger);
  font-weight: 600;
  margin-top: 1rem;
  text-align: center;
}
</style>
