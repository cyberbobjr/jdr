<template>
  <div>
    <h2>Étape 3 : Répartition des compétences</h2>
    
    <!-- Affichage des points disponibles -->
    <div class="points-info" v-if="skillsData">
      <div class="points-summary">
        <span class="points-label">Points de compétences disponibles :</span>
        <span class="points-value" :class="{ 'points-negative': remainingSkillPoints < 0 }">
          {{ remainingSkillPoints }} / {{ totalSkillPoints }}
        </span>
      </div>
      <div class="points-cost" v-if="totalSkillCost > 0">
        <span class="cost-label">Coût total :</span>
        <span class="cost-value">{{ totalSkillCost }} points</span>
      </div>
    </div>

    <!-- Affichage des bonus de culture -->
    <div v-if="cultureBonuses && Object.keys(cultureBonuses).length > 0" class="culture-bonuses">
      <h3>Bonus de culture ({{ props.initialData?.culture?.name }})</h3>
      <div class="bonus-list">
        <span v-for="(bonus, skill) in cultureBonuses" :key="skill" class="bonus-item">
          {{ skill }}: +{{ bonus }}
        </span>
      </div>
    </div>

    <div class="skills-container" v-if="skillsData?.skill_groups">
      <div v-for="(skillList, groupName) in skillsData.skill_groups" :key="groupName" class="skill-group">
        <h3 class="group-title">{{ groupName }}</h3>
        <div class="skills-list">
          <div
            v-for="skill in skillList"
            :key="skill.name"
            class="skill-item"
          >
            <JdrPopover>
              <span class="skill-label">{{ skill.name }}</span>
              <template #content>
                <div>
                  <strong>{{ skill.name }}</strong><br />
                  {{ skill.description }}<br />
                  <em>Caractéristiques : {{ skill.characteristics?.join(', ') || 'Non spécifiées' }}</em>
                  <div v-if="skill.examples && skill.examples.length > 0">
                    <br /><strong>Exemples :</strong>
                    <ul>
                      <li v-for="example in skill.examples" :key="example">{{ example }}</li>
                    </ul>
                  </div>
                </div>
              </template>
            </JdrPopover>            <div class="skill-input-container">
              <JdrPointInput
                v-model="skills[skill.name]"
                :min="0"
                :max="10"
                :can-increment="remainingSkillPoints > 0"
                :can-decrement="skills[skill.name] > 0"
                :increment-tooltip="remainingSkillPoints > 0 ? 'Augmenter cette compétence' : 'Plus de points disponibles'"
                :decrement-tooltip="skills[skill.name] > 0 ? 'Diminuer cette compétence' : 'Valeur minimale atteinte'"
              />
              
              <!-- Affichage du bonus de culture -->
              <div v-if="getCultureBonus(skill.name) > 0" class="culture-bonus">
                +{{ getCultureBonus(skill.name) }} (culture)
              </div>
              
              <!-- Affichage du niveau total -->
              <div class="skill-total" v-if="getTotalSkillValue(skill.name) > 0">
                Total: {{ getTotalSkillValue(skill.name) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="skills-actions">
      <button class="jdr-btn jdr-btn-secondary" @click="proposeSkillDistribution">Proposer une répartition</button>
      <button class="jdr-btn jdr-btn-primary" :disabled="!isValid || remainingSkillPoints < 0" @click="goToNextStep">Suivant</button>
    </div>

    <div v-if="!isValid" class="skills-error">La répartition des compétences n'est pas valide selon les règles du jeu.</div>
    <div v-if="remainingSkillPoints < 0" class="skills-error">Vous avez dépassé votre budget de points de compétences !</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, reactive } from 'vue';
import JdrApiService from '@/core/api';
import JdrPopover from '@/components/JdrPopover.vue';
import JdrPointInput from '@/components/JdrPointInput.vue';
import type { Character } from '@/core/interfaces';

const props = defineProps<{
  characterId?: string;
  initialData?: Character | null;
  skillsData?: any | null;
}>();
const emit = defineEmits(['next-step', 'update-character']);

const skills = reactive<Record<string, number>>({});
const isValid = ref(true);
const isInitialized = ref(false);
const isLoading = ref(true); // Flag pour indiquer qu'on est en train de charger/initialiser

// Points de compétences de base + bonus de culture
const baseSkillPoints = 27;

const cultureBonuses = computed(() => {
  return props.initialData?.culture?.skill_bonuses || {};
});

const freeSkillPointsFromCulture = computed(() => {
  return props.initialData?.culture?.free_skill_points || 0;
});

const totalSkillPoints = computed(() => {
  return baseSkillPoints + freeSkillPointsFromCulture.value;
});

// Calcul du coût total des compétences
const totalSkillCost = computed(() => {
  let cost = 0;
  Object.values(skills).forEach(value => {
    cost += value || 0;
  });
  return cost;
});

const remainingSkillPoints = computed(() => {
  return totalSkillPoints.value - totalSkillCost.value;
});

// Fonction pour obtenir le bonus de culture pour une compétence
function getCultureBonus(skillName: string): number {
  return cultureBonuses.value[skillName] || 0;
}

// Fonction pour obtenir la valeur totale d'une compétence
function getTotalSkillValue(skillName: string): number {
  const baseValue = skills[skillName] || 0;
  const cultureBonus = getCultureBonus(skillName);
  return baseValue + cultureBonus;
}

onMounted(() => {
  initializeSkills();
});

// Watch pour détecter quand les données arrivent
watch([() => props.initialData, () => props.skillsData], ([newInitialData, newSkillsData], [oldInitialData, oldSkillsData]) => {
  console.log('=== Watch combiné ===');
  console.log('InitialData disponible:', !!newInitialData);
  console.log('SkillsData disponible:', !!newSkillsData?.skill_groups);
  console.log('InitialData.competences:', newInitialData?.competences);
  
  // Ne réinitialiser que si :
  // 1. On n'était pas encore initialisé, OU
  // 2. Le characterId a changé (nouveau personnage)
  const shouldReinitialize = !isInitialized.value || 
    (oldInitialData?.id !== newInitialData?.id);
  
  if (newInitialData && newSkillsData?.skill_groups && shouldReinitialize) {
    console.log('Toutes les données sont disponibles et réinitialisation nécessaire...');
    isInitialized.value = false;
    initializeSkills();
  } else if (newInitialData && newSkillsData?.skill_groups) {
    console.log('🚫 Données disponibles mais réinitialisation non nécessaire');
  }
}, { immediate: true });

// Fonction pour initialiser les compétences
function initializeSkills() {
  if (isInitialized.value) {
    console.log('⏭️ Compétences déjà initialisées, on passe');
    return;
  }
    console.log('=== Initialisation des compétences ===');
  console.log('Props initialData:', props.initialData);
  console.log('Props skillsData disponible:', !!props.skillsData?.skill_groups);
  
  // Activer le mode chargement pour éviter les sauvegardes automatiques
  isLoading.value = true;
  
  // Vider les compétences existantes
  Object.keys(skills).forEach(key => {
    delete skills[key];
  });
  
  // Initialiser toutes les compétences à 0
  if (props.skillsData?.skill_groups) {
    Object.values(props.skillsData.skill_groups).forEach((skillArray: any) => {
      if (Array.isArray(skillArray)) {
        skillArray.forEach((skill: any) => {
          if (skill && skill.name) {
            skills[skill.name] = 0;
          }
        });
      }
    });
  }
    // Charger les données sauvegardées si elles existent
  if (props.initialData?.competences) {
    console.log('Chargement des compétences depuis initialData:', props.initialData.competences);
    Object.keys(props.initialData.competences).forEach(skillName => {
      if (skills.hasOwnProperty(skillName)) {
        skills[skillName] = props.initialData!.competences[skillName] || 0;
      }
    });
  }
    console.log('Compétences après initialisation:', skills);
  isInitialized.value = true;
    // Attendre un peu puis désactiver le mode chargement
  setTimeout(() => {
    isLoading.value = false;
    console.log('🟢 Mode chargement désactivé, watch actif');
    // Valider une seule fois après l'initialisation
    if (props.characterId) {
      validateSkills();
    }
  }, 100);
}

// Watch pour sauvegarder automatiquement (avec debounce)
let saveTimeout: NodeJS.Timeout | null = null;
watch(skills, () => {
  // Ne pas sauvegarder si on est en train de charger/initialiser
  if (isLoading.value) {
    console.log('🔵 Mode chargement actif, pas de sauvegarde');
    return;
  }
  
  if (isInitialized.value) {
    console.log('Compétences modifiées, sauvegarde différée...');
    
    // Annuler la sauvegarde précédente
    if (saveTimeout) {
      clearTimeout(saveTimeout);
    }
    // Programmer une nouvelle sauvegarde avec debounce
    saveTimeout = setTimeout(() => {
      onSkillChange();
    }, 300); // 300ms de délai (réduit pour meilleure réactivité)
  }
}, { deep: true });

async function proposeSkillDistribution() {
  console.log('Proposition de répartition des compétences à implémenter');
}

async function onSkillChange() {
  await saveSkills();
  await validateSkills();
}

async function saveSkills() {
  if (!props.characterId) {
    console.log('❌ Pas de characterId, sauvegarde impossible');
    return;
  }
  
  console.log('💾 Sauvegarde des compétences:', skills);
  
  const characterToSave = {
    id: props.initialData?.id,
    status: props.initialData?.status,
    name: props.initialData?.name,    
    race: props.initialData?.race,
    culture: props.initialData?.culture,
    caracteristiques: props.initialData?.caracteristiques,
    competences: { ...skills },
    hp: props.initialData?.hp,
    inventory: props.initialData?.inventory || [],
    spells: props.initialData?.spells || [],
    gold: props.initialData?.gold || 0,
    culture_bonuses: props.initialData?.culture_bonuses
  };
  
  try {
    const response = await JdrApiService.saveCharacter({
      character_id: props.characterId,
      character: characterToSave
    });
    
    console.log('✅ Compétences sauvegardées avec succès:', response);
    // NE PAS émettre update-character pour éviter la boucle
    // Le parent rechargera les données via le watch sur route.params si nécessaire
  } catch (error) {
    console.error('❌ Erreur lors de la sauvegarde des compétences:', error);
  }
}

async function validateSkills() {
  if (!props.characterId) return;
  
  try {
    const res = await JdrApiService.checkSkills({ 
      skills: skills
    });
    isValid.value = res.valid;
  } catch (error) {
    console.error('Erreur lors de la validation des compétences:', error);
    isValid.value = false;
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

.culture-bonuses {
  background: var(--jdr-primary-bg);
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  border-left: 4px solid var(--jdr-primary);
}

.culture-bonuses h3 {
  margin: 0 0 0.5rem 0;
  color: var(--jdr-primary);
  font-size: 1.1rem;
}

.bonus-list {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.bonus-item {
  background: var(--jdr-primary);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
}

.skills-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-bottom: 2rem;
}

.skill-group {
  background: var(--jdr-bg-secondary);
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid var(--jdr-border);
}

.group-title {
  margin: 0 0 1rem 0;
  color: var(--jdr-secondary);
  font-size: 1.2rem;
  font-weight: 700;
  border-bottom: 2px solid var(--jdr-secondary);
  padding-bottom: 0.5rem;
}

.skills-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.skill-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--jdr-bg-primary);
  border-radius: 6px;
  border: 1px solid var(--jdr-border);
}

.skill-label {
  font-weight: 600;
  color: var(--jdr-text-primary);
  cursor: pointer;
  flex: 1;
  margin-right: 1rem;
}

.skill-input-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  min-width: 100px;
}

.culture-bonus {
  font-size: 0.8rem;
  color: var(--jdr-primary);
  font-weight: 600;
  font-style: italic;
}

.skill-total {
  font-size: 0.85rem;
  color: var(--jdr-text-primary);
  font-weight: 600;
}

.skills-actions {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.skills-error {
  color: var(--jdr-danger);
  font-weight: 500;
  margin-top: 1rem;
  padding: 0.75rem;
  background: var(--jdr-danger-bg);
  border-radius: 4px;
  border-left: 4px solid var(--jdr-danger);
}
</style>
