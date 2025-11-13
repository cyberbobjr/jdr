<template>
  <div v-if="character" class="info-card">
    <h3>
      <font-awesome-icon icon="user-shield" class="help-icon" />
      {{ character.name }}
    </h3>
    <br/>
    <!-- Informations de base -->
    <div class="character-basic-info">
      <div class="detail-item race-culture-row">
        <div class="race-culture-container">
          <div class="race-culture-item">
            <span class="detail-label">Race</span>
            <span class="detail-value">{{ character.race?.name || 'Non définie' }}</span>
          </div>
          <div class="race-culture-item">
            <span class="detail-label">Culture</span>
            <span class="detail-value">{{ character.culture?.name || 'Non définie' }}</span>
          </div>
        </div>
      </div>
      <div class="detail-item">
        <span class="detail-label">Points de vie</span>
        <span class="detail-value jdr-ml-2">{{ character.hp }}</span>
      </div>
      <div class="detail-item">
        <span class="detail-label">Or</span>
        <span class="detail-value jdr-ml-2">{{ character.gold }} po</span>
      </div>
    </div>

    <!-- Onglets -->
    <div class="character-tabs">
      <button 
        v-for="tab in characterTabs" 
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="['tab-button', { active: activeTab === tab.id }]"
      >
        <font-awesome-icon :icon="tab.icon" />
        {{ tab.name }}
      </button>
    </div>

    <!-- Contenu des onglets -->
    <div class="tab-content">
      <!-- Onglet Caractéristiques -->
      <div v-if="activeTab === 'characteristics' && character.caracteristiques" class="character-section">
        <div class="characteristics-grid">
          <div 
            v-for="(value, name) in character.caracteristiques" 
            :key="name"
            class="characteristic-item"
          >
            <span class="char-name">{{ name.substring(0, 3) }}</span>
            <span class="char-value">{{ value }}</span>
            <span class="char-bonus">{{ getCharacteristicBonus(value) }}</span>
          </div>
        </div>
      </div>

      <!-- Onglet Compétences -->
      <div v-if="activeTab === 'skills' && character.competences" class="character-section">
        <div class="skills-list">
          <div 
            v-for="(value, skill) in getMainSkills(character.competences)" 
            :key="skill"
            class="skill-item"
          >
            <span class="skill-name">{{ formatSkillName(skill) }}</span>
            <span class="skill-value">{{ value }}</span>
          </div>
        </div>
      </div>

      <!-- Onglet Équipement -->
      <div v-if="activeTab === 'equipment' && character.inventory" class="character-section">
        <div class="equipment-sections">
          <!-- Équipement équipé -->
          <div v-if="getEquippedItems(character.inventory).length > 0" class="equipment-subsection">
            <h5>Équipé</h5>
            <div class="equipment-list">
              <div 
                v-for="item in getEquippedItems(character.inventory)" 
                :key="item.id"
                class="equipment-item equipped"
              >
                <font-awesome-icon 
                  :icon="getItemIcon(item)" 
                  class="item-icon"
                />
                <span class="item-name">{{ item.name }}</span>
                <span class="item-equipped-badge">✓</span>
              </div>
            </div>
          </div>

          <!-- Inventaire -->
          <div v-if="getUnequippedItems(character.inventory).length > 0" class="equipment-subsection">
            <h5>Inventaire</h5>
            <div class="equipment-list">
              <div 
                v-for="item in getUnequippedItems(character.inventory)" 
                :key="item.id"
                class="equipment-item"
              >
                <font-awesome-icon 
                  :icon="getItemIcon(item)" 
                  class="item-icon"
                />
                <span class="item-name">{{ item.name }}</span>
                <span v-if="item.quantity > 1" class="item-quantity">x{{ item.quantity }}</span>
              </div>
            </div>
          </div>

          <!-- Message si aucun équipement -->
          <div v-if="character.inventory.length === 0" class="no-equipment">
            <font-awesome-icon icon="box-open" class="no-equipment-icon" />
            <p>Aucun équipement</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Message si aucun personnage -->
  <div v-else class="info-card">
    <div class="loading-character">
      <font-awesome-icon icon="spinner" spin class="jdr-text-accent" />
      <p>Chargement du personnage...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import type { Character } from '@/core/interfaces';
import JdrApiService from '@/core/api';

// Props
interface Props {
  sessionId: string;
  characterName?: string;
  refreshTrigger?: number;
}

const props = defineProps<Props>();

// Émissions
const emit = defineEmits<{
  characterLoaded: [character: Character];
  characterError: [error: string];
}>();

// Données réactives
const character = ref<Character | null>(null);
const activeTab = ref('characteristics');
const loading = ref(false);

const characterTabs = ref([
  { id: 'characteristics', name: 'Caract.', icon: 'user' },
  { id: 'skills', name: 'Compétences', icon: 'star' },
  { id: 'equipment', name: 'Équipement', icon: 'tools' }
]);

// Méthodes utilitaires pour les caractéristiques
const getCharacteristicBonus = (value: number): string => {
  const bonus = Math.floor((value - 10) / 2);
  return bonus >= 0 ? `+${bonus}` : `${bonus}`;
};

// Méthodes utilitaires pour les compétences
const getMainSkills = (competences: Record<string, any>): Record<string, number> => {
  // Filtrer pour ne garder que les compétences principales (avec des valeurs numériques)
  const mainSkills: Record<string, number> = {};
  
  for (const [key, value] of Object.entries(competences)) {
    if (typeof value === 'number' && value > 0) {
      mainSkills[key] = value;
    }
  }
  
  return mainSkills;
};

const formatSkillName = (skillName: string): string => {
  // Convertir le nom de compétence en format lisible
  return skillName
    .replace(/_/g, ' ')
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, str => str.toUpperCase())
    .trim();
};

// Méthodes utilitaires pour l'équipement
const getEquippedItems = (inventory: any[]): any[] => {
  return inventory.filter(item => item.equipped === true);
};

const getUnequippedItems = (inventory: any[]): any[] => {
  return inventory.filter(item => item.equipped !== true);
};

const getItemIcon = (item: any): string => {
  const itemType = item.type?.toLowerCase() || '';
  
  switch (itemType) {
    case 'weapon':
    case 'arme':
      return 'sword';
    case 'armor':
    case 'armure':
      return 'shield-alt';
    case 'shield':
    case 'bouclier':
      return 'shield';
    case 'potion':
      return 'flask';
    case 'tool':
    case 'outil':
      return 'hammer';
    case 'accessory':
    case 'accessoire':
      return 'ring';
    default:
      return 'box';
  }
};

// Méthode de chargement du personnage
const loadCharacter = async () => {
  if (!props.sessionId) return;

  try {
    loading.value = true;
    
    // Récupérer la liste des personnages et trouver celui de la session
    const characters = await JdrApiService.getCharacters();
    
    if (props.characterName) {
      const foundCharacter = characters.find(char => char.name === props.characterName);
      if (foundCharacter) {
        character.value = foundCharacter;
        emit('characterLoaded', foundCharacter);
      } else {
        emit('characterError', 'Personnage non trouvé');
      }
    } else if (characters.length > 0) {
      // Prendre le premier personnage si aucun nom spécifié
      character.value = characters[0];
      emit('characterLoaded', characters[0]);
    } else {
      emit('characterError', 'Aucun personnage disponible');
    }
  } catch (error) {
    console.error('Erreur lors du chargement du personnage:', error);
    emit('characterError', 'Erreur lors du chargement du personnage');
  } finally {
    loading.value = false;
  }
};

// Watcher pour recharger le personnage quand le trigger change
watch(() => props.refreshTrigger, () => {
  if (props.refreshTrigger !== undefined) {
    loadCharacter();
  }
});

// Chargement initial
onMounted(() => {
  loadCharacter();
});

// Exposer les méthodes publiques
defineExpose({
  loadCharacter,
  character
});
</script>

<style scoped>
/* Styles pour la fiche personnage */
.character-basic-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.race-culture-row {
  width: 100%;
}

.race-culture-container {
  display: flex;
  gap: 0.5rem;
  width: 100%;
}

.race-culture-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem;
  background: var(--jdr-bg-primary);
  border: 1px solid var(--jdr-border-color);
  border-radius: var(--jdr-border-radius);
  font-size: 0.8rem;
}

.race-culture-item .detail-label {
  font-size: 0.7rem;
  color: var(--jdr-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.race-culture-item .detail-value {
  font-weight: 600;
  color: var(--jdr-text-primary);
}

.character-section {
  margin-top: 1rem;
}

.character-section h4 {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--jdr-text-primary);
  margin: 0 0 0.5rem 0;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid var(--jdr-border-color);
}

.characteristics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}

.characteristic-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.5rem;
  background: var(--jdr-bg-primary);
  border: 1px solid var(--jdr-border-color);
  border-radius: var(--jdr-border-radius);
  font-size: 0.75rem;
}

.char-name {
  font-weight: 600;
  color: var(--jdr-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.char-value {
  font-size: 1rem;
  font-weight: 700;
  color: var(--jdr-text-primary);
  margin-bottom: 0.125rem;
}

.char-bonus {
  font-size: 0.75rem;
  color: var(--jdr-accent);
  font-weight: 600;
}

.skills-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.skill-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0.5rem;
  background: var(--jdr-bg-primary);
  border: 1px solid var(--jdr-border-color);
  border-radius: var(--jdr-border-radius);
  font-size: 0.8rem;
}

.skill-name {
  color: var(--jdr-text-primary);
  font-weight: 500;
}

.skill-value {
  color: var(--jdr-accent);
  font-weight: 600;
}

.equipment-sections {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.equipment-subsection {
  margin-bottom: 1rem;
}

.equipment-subsection h5 {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--jdr-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid var(--jdr-border-color);
}

.equipment-list {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.equipment-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
  background: var(--jdr-bg-primary);
  border: 1px solid var(--jdr-border-color);
  border-radius: var(--jdr-border-radius);
  font-size: 0.8rem;
}

.equipment-item.equipped {
  background: var(--jdr-bg-secondary);
  border-color: var(--jdr-accent);
}

.item-icon {
  color: var(--jdr-accent);
  width: 14px;
  flex-shrink: 0;
}

.item-name {
  color: var(--jdr-text-primary);
  font-weight: 500;
  flex: 1;
}

.item-equipped-badge {
  color: var(--jdr-accent);
  font-weight: 600;
  font-size: 0.75rem;
}

.item-quantity {
  color: var(--jdr-text-secondary);
  font-size: 0.75rem;
  font-weight: 500;
}

.no-equipment {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--jdr-text-muted);
}

.no-equipment-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  opacity: 0.5;
}

.no-equipment p {
  margin: 0;
  font-size: 0.9rem;
  font-style: italic;
}

/* Onglets de la fiche personnage */
.character-tabs {
  display: flex;
  gap: 0.25rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--jdr-border-color);
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--jdr-text-secondary);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-button:hover {
  color: var(--jdr-text-primary);
  background: var(--jdr-bg-secondary);
}

.tab-button.active {
  color: var(--jdr-accent);
  border-bottom-color: var(--jdr-accent);
  background: var(--jdr-bg-secondary);
}

.tab-content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.loading-character {
  text-align: center;
  padding: 2rem 1rem;
  color: var(--jdr-text-muted);
}

.loading-character p {
  margin-top: 0.5rem;
  font-size: 0.9rem;
}

/* Responsive pour les caractéristiques */
@media (max-width: 768px) {
  .characteristics-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 0.25rem;
  }
  
  .characteristic-item {
    padding: 0.375rem 0.25rem;
    font-size: 0.7rem;
  }
  
  .char-value {
    font-size: 0.9rem;
  }
  
  .char-bonus {
    font-size: 0.7rem;
  }
}

@media (max-width: 480px) {
  .race-culture-container {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .characteristics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .tab-button {
    padding: 0.375rem 0.5rem;
    font-size: 0.75rem;
  }
}
</style>
